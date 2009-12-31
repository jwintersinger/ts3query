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
  URL_PREFIX + '/client/(\d+).json',       'ClientDetailsJson'
)
render = web.template.render('templates/')
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


class ClientDetailsJson(JsonRequest):
  '''Displays JSON-formatted details for given client.'''

  def GET(self, client_id):
    return json.dumps(self._tsc.list_client_details(client_id))


if __name__ == '__main__':
  app.run()
