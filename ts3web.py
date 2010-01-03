#!/usr/bin/env python
import json
import web
from ts3query import TsConverser, Config

# Constants. You will need to change these to reflect your configuration.
ADDRESS = 'ts.da-shiz.net'
VOICE_PORT = Config.DEFAULT_VOICE_PORT


# web.py miscellany.
URL_PREFIX = '/ts'
urls = (
  URL_PREFIX + '/',                        'ChannelAndClientList',
  URL_PREFIX + '/channels.json',           'ChannelAndClientListJson',
  URL_PREFIX + '/populated_channels.json', 'PopulatedChannelAndClientListJson',
  URL_PREFIX + '/client/(\d+)',            'ClientDetails',
  URL_PREFIX + '/client/(\d+).json',       'ClientDetailsJson'
)

def create_template_helpers():
  def boolean_int_to_human_readable(b):
    return (b == 1) and 'Yes' or 'No'

  def make_milliseconds_human_readable(seconds):
    seconds /= 1000
    periods = (
      ('day',    24*60*60),
      ('hour',   60*60),
      ('minute', 60),
      ('second', 1)
    )                  
    readable_lengths = []
    for period_name, length in periods:
      if seconds == 0:
        return '0 seconds'
      if seconds >= length:
        num_periods = int(seconds / length) 
        seconds -= num_periods*length
        readable_lengths.append('%s %s%s' % (num_periods, period_name, ('s', '')[num_periods == 1]))
    return ', '.join(readable_lengths)

  from datetime import datetime
  def make_posix_timestamp_human_readable(timestamp):
    timestamp = 1262476312
    return datetime.fromtimestamp(timestamp).strftime('%b %d, %Y')

  template_helpers = {}
  l = locals()
  for f in locals().values():
    if callable(f):
      template_helpers[f.__name__] = f
  return template_helpers

render = web.template.render('templates/', globals=create_template_helpers())
app = web.application(urls, globals())


class BaseRequest:
  def __init__(self):
    self._tsc = TsConverser(ADDRESS, VOICE_PORT)


class JsonRequest(BaseRequest):
  def __init__(self):
    BaseRequest.__init__(self)
    web.header('Content-Type', 'application/json')


class ChannelAndClientList(BaseRequest):
  '''Displays populated channels, as well as the clients within each.'''

  def GET(self):
    return render.channel_and_client_list(self._generate_server_name(),
      self._tsc.list_populated_channels())

  def _generate_server_name(self):
    server_name = ADDRESS
    if VOICE_PORT != Config.DEFAULT_VOICE_PORT:
      server_name = '%s:%s' % (server_name, VOICE_PORT)
    return server_name


class ChannelAndClientListJson(JsonRequest):
  '''Displays JSON-formatted list of all channels, as well as clients within each.'''

  def GET(self):
    return json.dumps(self._tsc.list_channels())


class PopulatedChannelAndClientListJson(JsonRequest):
  '''Displays JSON-formatted list of populated channels, as well as clients within each.'''

  def GET(self):
    return json.dumps(self._tsc.list_populated_channels())


class ClientDetails(BaseRequest):
  '''Displays details for particular client.'''

  def GET(self, client_id):
    return render.client_details(self._tsc.list_client_details(client_id))


class ClientDetailsJson(JsonRequest):
  '''Displays JSON-formatted details for given client.'''

  def GET(self, client_id):
    return json.dumps(self._tsc.list_client_details(client_id))


if __name__ == '__main__':
  app.run()
