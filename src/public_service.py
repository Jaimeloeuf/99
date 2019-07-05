import tornado.web
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import tornado.log
import tornado.options
import sqlite3
import logging
import json
import time


async def async_fetch(req):
    http_client = AsyncHTTPClient()
    try:
        response = await http_client.fetch(req)
    except Exception as e:
        print("Error: %s" % e)
    else:
        return response.body


class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, obj, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(obj))


# /public-api/ping
class PingHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.write("pong!")


def make_app(options):
    return tornado.web.Application([
        (r"/public-api/ping", PingHandler),
        (r"/public-api/listings", ListingsHandler),
        (r"/public-api/users", UsersHandler),
    ], debug=options.debug)


if __name__ == "__main__":
    # Define settings/options for the web app
    # Specify the port number to start the web app on (default value is port 6000)
    tornado.options.define("port", default=6000)
    # Specify whether the app should run in debug mode
    # Debug mode restarts the app automatically on file changes
    tornado.options.define("debug", default=True)

    # Read settings/options from command line
    tornado.options.parse_command_line()

    # Access the settings defined
    options = tornado.options.options

    # Create web app
    app = make_app(options)
    app.listen(options.port)
    logging.info("Starting public service. PORT: {}, DEBUG: {}".format(options.port, options.debug))

    try:
        # Start event loop in a Try/Except to kill the service when SIGINT is caught
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        print("Exit sucess")
