#!/usr/bin/env python

import os
import sys

ROOT_PATH = os.path.abspath( os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert( 0, os.path.join(ROOT_PATH, 'libs'))
sys.path.insert( 0, os.path.join(ROOT_PATH, 'apps'))

from datetime import timedelta

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.template

from md_gateway import  config
from views import MdGatewayHandler

from order_matcher_client import OrderMatcherClient

class MdGatewayApplication(tornado.web.Application):
  def __init__(self):
    handlers = [
      (r'/market_data', MdGatewayHandler)
    ]
    settings = dict(
      cookie_secret=config.cookie_secret
    )

    self.order_matcher_client = OrderMatcherClient( 'wss://localhost:8443/trade', 'rodrigo', 'abc123', ['BRLBTC'] )
    self.order_matcher_client.signal_recv.connect( self.slot_receive_msg )
    self.order_matcher_client.start()

    tornado.web.Application.__init__(self, handlers, **settings)

    tornado.ioloop.IOLoop.instance().add_timeout(timedelta(seconds=1), self.cron_check_md_updates)

  def cron_check_md_updates(self):
    # run it again 5 seconds later...
    tornado.ioloop.IOLoop.instance().add_timeout(timedelta(milliseconds=500), self.cron_check_md_updates)


  def slot_receive_msg(self, sender, data):
    print 'receiving :', data


def main():


  application = MdGatewayApplication()
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8000)

  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()