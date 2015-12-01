#!/usr/bin/python

import os
import sys
import subprocess
import httplib
import urllib
import time

conf = {
  'apiurl': 'api.pushover.net:443',
	'userkey': 'xxx',
	'token': 'xxx',
  'timestamp_file': '/tmp/pushover',
  'sendlimit': {
    'messages': 5,
    'timeperiod': 60
  }
}

trigger = {
	'to': str(sys.argv[1]),
	'subject': str(sys.argv[3]).split(" ")[-2],
	'message': str(sys.argv[3])
}

def getPriority(str):
  if str == 'PROBLEM':
    return 1
  else:
    return 0

def createLogFile():
  if not os.path.exists(conf['timestamp_file']):
    f = open(conf['timestamp_file'], 'w')
    f.close()

def writeTimestamp():
  f = open(conf['timestamp_file'],'a+')
  f.write(str(time.time()) + '\n')
  f.close()

def getLimitTimestamp():
  lines = []
  for l in open(conf['timestamp_file'], 'r'):
    lines.append(l)

  if len(lines) < conf['sendlimit']['messages'] + 1:
    return conf['sendlimit']['timeperiod'] + 1
  else:
    return lines[-5].rstrip('\n')

def lastSentMessage():
  return (int(time.time()) - int(float(getLimitTimestamp())))

def notify(to, subject, message):
  createLogFile()
  try:
    if lastSentMessage() > conf['sendlimit']['timeperiod']:
      conn = httplib.HTTPSConnection(conf['apiurl'])
      conn.request("POST", "/1/messages.json",
        urllib.urlencode({
          "token": conf['token'],
          "user": conf['userkey'],
          "title": trigger['subject'],
          "message": trigger['message'],
          "priority": getPriority(subject)
        }), { "Content-type": "application/x-www-form-urlencoded" })
      conn.getresponse()
      writeTimestamp()
      print('Trigger has been successfully sent!')
    else:
      print('Messaging limit has been reeach! (%i messages within %i seconds)\nNext message can be send in %i seconds.' % (conf['sendlimit']['messages'], conf['sendlimit']['timeperiod'], conf['sendlimit']['timeperiod'] - lastSentMessage()))
  except IOError:
    print('Log file %s not found!' % (conf['timestamp_file']))
    sys.exit(1)

notify(trigger['to'], trigger['subject'], trigger['message'])