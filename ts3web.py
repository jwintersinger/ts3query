#!/usr/bin/env python
import web
from ts3query import TsConverser, Config

# Constants. You will need to change these to reflect your configuration.
ADDRESS = 'ts.da-shiz.net'
VOICE_PORT = Config.DEFAULT_VOICE_PORT


# web.py miscellany.
urls = (
  '/', 'ChannelAndClientList'
)
render = web.template.render('templates/')
app = web.application(urls, globals())


class ChannelAndClientList:
  '''Displays populated channels, as well as the clients within each.'''

  def GET(self):
    tsc = TsConverser(ADDRESS, VOICE_PORT)
    return render.channel_and_client_list(self._generate_server_name(), tsc.list_populated_channels())

  def _generate_server_name(self):
    server_name = ADDRESS
    if VOICE_PORT != Config.DEFAULT_VOICE_PORT:
      server_name = '%s:%s' % (server_name, VOICE_PORT)
    return server_name


if __name__ == '__main__':
  app.run()
