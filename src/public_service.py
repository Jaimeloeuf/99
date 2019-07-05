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


# /public-api/listings
class ListingsHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        # Parsing pagination params
        page_num = self.get_argument("page_num", 1)
        page_size = self.get_argument("page_size", 10)

        arguements = []

        try:
            page_num = int(page_num)
            arguements.append("page_num=" + str(page_num))
        except:
            logging.exception("Error while parsing page_num: {}".format(page_num))
            self.write_json({"result": False, "errors": "invalid page_num"}, status_code=400)
            return

        try:
            page_size = int(page_size)
            arguements.append("page_size=" + str(page_size))
        except:
            logging.exception("Error while parsing page_size: {}".format(page_size))
            self.write_json({"result": False, "errors": "invalid page_size"}, status_code=400)
            return

        # Parsing user_id param
        user_id = self.get_argument("user_id", None)
        if user_id is not None:
            try:
                user_id = int(user_id)
                arguements.append("user_id=" + str(user_id))
            except:
                self.write_json({"result": False, "errors": "invalid user_id"}, status_code=400)
                return

        # The URL is hardcoded, this should be fed in or taken from a "service discovery" service
        url = "http://localhost:6001/listings"

        if len(arguements) > 0:
            url += "?" + "&".join(arguements)
            print(url)

        req = HTTPRequest(url)

        res = yield async_fetch(req)

        # Send back the response as json
        self.set_header("Content-Type", "application/json")
        self.write(res)
        

# /public-api/users
class UsersHandler(BaseHandler):
    @tornado.gen.coroutine
    def post(self):
        # URL encoded  form data to be submitted, but json is received

        # Convert the JSON body for name into a name query
        name = "name=" + json.loads(self.request.body.decode())['name']

        # The URL is hardcoded, this should be fed in or taken from a "service discovery" service
        req = HTTPRequest(
            url="http://localhost:6002/users",
            method="POST",
            body=name
        )

        res = yield async_fetch(req)

        # Send back the response as json
        self.set_header("Content-Type", "application/json")
        self.write(res)


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
