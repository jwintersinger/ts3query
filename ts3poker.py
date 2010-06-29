#!/usr/bin/env python
# Usage ts3poker.py <clid>
import random
import sys
import time
import ts3query

class Ts3Poker:
  _MESSAGES = (
    'You were poked.',
    'Hail fellow well met!',
    'I am poking you with my two-inch penis.',
    'Bonners? I\'m all out of bonners, I have only cheese.',
    'HELLO THERE',
    'Good evening, gentlemen.',
    'I know  you\'re there, man. Stop playing hide the salami.',
    'I can keep this up all day. Heck, I can keep it up all week.',
    'You might say we\'re playing POKE-R! HA!',
    'This is getting monotonous, don\'t you think? Good thing I\'m a computer.'
  )

  def __init__(self):
    self._query = ts3query.TsQuery('ts.da-shiz.net')
    print self._query.query('login', {'client_login_name': 'serveradmin', 'client_login_password': 'my_password'})
    while True:
      time.sleep(2)
      self._query.query('clientpoke', {'clid': sys.argv[1], 'msg': random.choice(self._MESSAGES)})
    self._query.query('quit')


def main():
  Ts3Poker()

if __name__ == '__main__':
  main()
