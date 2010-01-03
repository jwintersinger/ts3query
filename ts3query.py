#!/usr/bin/env python
import re
import socket
import sys
from optparse import OptionParser

def debug(msg):
  if debug.verbose:
    sys.stderr.write('%s\n' % msg)
debug.verbose = False

class Coder:
  '''Encode and decode strings as per ServerQuery specification.'''

  _SUB = (
    ('\\', '\\\\'),
    (' ',  '\\s'),
    ('/',  '\\/'),
    ('|',  '\\p'),
    ('\a', '\\a'),
    ('\b', '\\b'),
    ('\f', '\\f'),
    ('\n', '\\n'),
    ('\r', '\\r'),
    ('\t', '\\t'),
    ('\v', '\\v'),
  )

  def _code(self, s, do_encode):
    for decoded, encoded in self._SUB:
      params = do_encode and (decoded, encoded) or (encoded, decoded)
      s = str(s).replace(*params)
    return s

  def encode(self, s):
    return self._code(s, True)

  def decode(self, s):
    return self._code(s, False)


class Config:
  '''Miscellaneous defaults used throughout. You should have no need to change these.'''
  DEFAULT_VOICE_PORT = 9987
  DEFAULT_QUERY_PORT  = 10011


class CommandFailedError(Exception):
  pass

class TsQuery:
  '''Low-level interface to TS server.'''

  _BUFFER_SIZE = 4096
  _EOL = '\n\r'

  def __init__(self, address, server_port=Config.DEFAULT_VOICE_PORT,
    query_port=Config.DEFAULT_QUERY_PORT):
    self._address, self._server_port, self._query_port = address, server_port, query_port
    self._coder = Coder()
    self._connect()

  def _connect(self):
    '''Connect to server and prepare ServerQuery session.'''
    # Arguments to socket.socket() not necessary, but I like being explicit.
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._socket.connect((self._address, self._query_port))
    # Retrieve 'TS3\n\r' header.
    if self._recv() != 'TS3%s' % self._EOL:
      raise Exception('Improper header returned upon connection')
    self._select_server()

  def _select_server(self):
    '''Select virtual server based on its port.'''
    response = self.query('serveridgetbyport', params={'virtualserver_port': self._server_port})
    sid = response[0]['server_id']
    self.query('use', params={'sid': sid})

  def _recv(self):
    'Read from socket.'
    response = self._socket.recv(self._BUFFER_SIZE)
    debug('Recv: %s' % repr(response))
    return response
  
  def _retrieve_response(self):
    '''Read from socket, returning response as a list of lines.'''
    response = ''
    while True:
      response += self._recv()
      # Call split() rather than splitlines(), as latter does not properly handle TS3's '\n\r' EOL.
      # Strip to remove extraneous empty element on end of list due to terminal EOL sequence.
      lines = response.strip().split(self._EOL)
      # Response to command not complete until "error ..." line indicating command status returned.
      if re.search('^error ', lines[-1]):
        break
    return lines

  def _exec(self, cmd, params, options):
    '''Execute command, returning response as list of lines.
    
    Keyword arguments:
    params -- dictionary of parameters.
    options -- tuple of options. Do not prefix elements with "-".
    '''
    if params:
      params_str = ' '.join(['%s=%s' % (k, self._coder.encode(params[k])) for k in params])
      cmd = '%s %s' % (cmd, params_str)
    if options:
      options_str = ' '.join(['-%s' % option for option in options])
      cmd = '%s %s' % (cmd, options_str)
    cmd += self._EOL

    debug('Send: %s' % repr(cmd))
    self._socket.send(cmd)
    return self._retrieve_response()

  def query(self, cmd, params=None, options=()):
    '''Execute cmd and check its return status to ensure success.

    Keyword arguments:
    params -- optional dictionary of parameters.
    options -- optional tuple of options. Do not prefix elements with "-".

    Examples:
    query('channellist')
    query('login', {'client_login_name': 'serveradmin', 'client_login_password': 'pass'})
    query('clientlist', options=('away',)) # Note command after 'away' -- distinguishes 1-tuple from
                                           # string in parentheses.
    query('clientdbfind', {'pattern': 'Jeff'}, ('away',))

    Return value:
    If no response (other than command's status) is made by the server, return None. If a response
    is made (other than commannd's status), return a list where each element is a dictionary
    representing one item of the response (e.g., a single client or channel).
    '''
    # Can't specify params={} in method definition, as dictionaries are mutable -- if defined
    # as empty dictionary in method definition, it would accumulate values across multiple calls. 
    if not params:
      params = {}

    response_lines = self._exec(cmd, params, options)
    if len(response_lines) > 2:
      raise Exception('Too many lines in response for %s' % cmd)

    cmd_status = self._decode(response_lines.pop())[0] # "[0]" as only one item should be returned.
    if not (cmd_status['msg'] == 'ok' and cmd_status['id'] == 0):
      raise CommandFailedError('"%s" failed with error %s (%s)' % (cmd, cmd_status['id'], cmd_status['msg']))

    if response_lines: # Response other than command status made.
      return self._decode(response_lines[-1])
    else:              # No response other than command status.
      return None

  def _decode(self, response):
    '''Split response string into list, where each element is a dictionary representing one item of
    the response (e.g., a single client or channel). If a given response parameter has no value
    associated with it, it will be set to True.
    '''
    items = []
    for item in response.split('|'):
      items.append({})
      for param in item.split(' '):
        # Split only on first equal sign, as parameter value may include equal signs.
        tokens = param.split('=', 1)
        key = tokens[0]
        if len(tokens) > 1:
          value = self._decode_value(tokens[1])
        else:
          value = True
        items[-1][key] = value
    return items

  def _decode_value(self, value):
    '''Decode value off wire as per ServerQuery specification. Change type if appropriate.'''
    value = self._coder.decode(value)
    if re.match('^\d+$', value):
      value = int(value)
    return value


class TsConverser:
  '''High-level interface to TS server.'''

  def __init__(self, address, server_port=Config.DEFAULT_VOICE_PORT,
    query_port=Config.DEFAULT_QUERY_PORT):
    self._query = TsQuery(address, server_port, query_port)

  def list_clients(self):
    '''Returns list of all clients that aren't SeverQuery users.'''
    clients = self._query.query('clientlist', options=('away', 'voice'))
    # Remove ServerQuery clients from list.
    return [client for client in clients if client['client_type'] != 1]

  def list_channels(self):
    '''Returns list of all channels, as well as which client is in each chanel.'''
    clients = self.list_clients()
    channels = self._query.query('channellist')
    for channel in channels:
      channel['clients'] = [client for client in clients if client['cid'] == channel['cid']]
    return channels

  def list_populated_channels(self):
    '''Returns list of channels with clients in them, as well as which client is in each chanel.'''
    # Can't rely on channel['total_clients'], as it counts ServerQuery clients.
    return [channel for channel in self.list_channels() if len(channel['clients']) > 0]

  def login(self, username, password):
    '''Login to ServerQuery interface. With the default server permissions in place, if one wants
    only to list the channels and clients, one need not login. Returns None.
    '''
    return self._query.query('login', {'client_login_name': username, 'client_login_password': password})

  def list_client_details(self, client_id):
    return self._query.query('clientinfo', {'clid': client_id})[0]


class Printer:
  '''Base class for all output types used by command-line interface.'''

  def __init__(self, ts_converser):
    self._ts_converser = ts_converser


class HumanPrinter(Printer):
  '''Human-formatted printer. Used for command-line interface.'''

  def _generate_header(self, s):
    '''Returns string with equal signs above and below s.'''
    s = str(s)
    separator = len(s)*'='
    return '\n'.join((separator, s, separator))

  def print_channels_and_clients(self):
    '''Prints all channels with clients in them.'''
    channels = self._ts_converser.list_populated_channels()
    for i in range(len(channels)):
      channel = channels[i]
      print self._generate_header(channel['channel_name'])
      for client in channel['clients']:
        postamble = (client['client_away'] == 1) and ' (away)' or ''
        print '%s%s' % (client['client_nickname'], postamble)
      if i < len(channels) - 1: # Print blank line between channels unless on last channel.
        print ''


class JsonPrinter(Printer):
  '''JSON-formatted printer. Potentially useful for interfacing with other programming
  environments.
  '''
  def print_channels_and_clients(self):
    '''Returns JSON-formatted listing of all channels with clients in them. Requires Python 2.6+.'''
    # Do import here as JSON was made part of standard library only with Python 2.6. Users with
    # Python 2.5 who want to call this method will need to install simplejson and change the import statement to
    # "import simplejson as json".
    import json
    channels = self._ts_converser.list_populated_channels()
    print json.dumps(channels)
      

if __name__ == '__main__':
  '''Execute command-line interface.'''

  def parse_options():
    parser = OptionParser(usage='usage: %prog [options] server_address')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
      default=False, help='print debugging messages')
    parser.add_option('-j', '--print-json', dest='print_json', action='store_true',
      default=False, help='make output JSON-formatted rather than human-readable')
    parser.add_option('-p', '--port', dest='query_port', type='int',
      default=Config.DEFAULT_VOICE_PORT, help='server voice port')
    parser.add_option('-q', '--query-port', dest='query_port', type='int',
      default=Config.DEFAULT_QUERY_PORT, help='server query port')

    options, args = parser.parse_args()
    if len(args) != 1:
      sys.exit(parser.print_help())
    debug.verbose = options.verbose
    return (options, args)

  options, args = parse_options()

  tsc = TsConverser(args[0])
  printer = options.print_json and JsonPrinter(tsc) or HumanPrinter(tsc)
  printer.print_channels_and_clients()
