import tornado.web
import tornado.log
import tornado.options
import sqlite3
import logging
import json
import time

class App(tornado.web.Application):

    def __init__(self, handlers, **kwargs):
        super().__init__(handlers, **kwargs)

        # Initialising db connection
        self.db = sqlite3.connect("db/users.db")
        self.db.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        cursor = self.db.cursor()

        # Create table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS 'users' ("
            + "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
            + "name TEXT NOT NULL,"
            + "created_at INTEGER NOT NULL,"
            + "updated_at INTEGER NOT NULL"
            + ");"
        )
        self.db.commit()

class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, obj, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(obj))

# /users
class UsersHandler(BaseHandler):
    """ Get All Users based on parameters endpoint """
    @tornado.gen.coroutine
    def get(self):
        # Parsing pagination params
        page_num = self.get_argument("page_num", 1)
        page_size = self.get_argument("page_size", 10)
        try:
            page_num = int(page_num)
        except:
            logging.exception("Error while parsing page_num: {}".format(page_num))
            self.write_json({"result": False, "errors": "invalid page_num"}, status_code=400)
            return

        try:
            page_size = int(page_size)
        except:
            logging.exception("Error while parsing page_size: {}".format(page_size))
            self.write_json({"result": False, "errors": "invalid page_size"}, status_code=400)
            return

        # Building select statement
        select_stmt = "SELECT * FROM users"
        # Order by and pagination
        limit = page_size
        offset = (page_num - 1) * page_size
        select_stmt += " ORDER BY created_at DESC LIMIT ? OFFSET ?"

        # Create the SQL arguement tuple
        args = (limit, offset)
        cursor = self.application.db.cursor()
        results = cursor.execute(select_stmt, args)

        users = []
        for row in results:
            fields = ["id", "name", "created_at", "updated_at"]
            user = {
                field: row[field] for field in fields
            }
            users.append(user)

        self.write_json({"result": True, "users": users})

    """ Create User endpoint """
    @tornado.gen.coroutine
    def post(self):
        # Collecting required params
        name = self.get_argument("name")

        # Create the microS timestamp
        time_now = int(time.time() * 1e6) # Converting current time to microseconds

        # Proceed to store the users in our db
        cursor = self.application.db.cursor()

        cursor.execute(
            "INSERT INTO 'users' "
            + "('name', 'created_at', 'updated_at') "
            + "VALUES (?, ?, ?)",
            (name, time_now, time_now)
        )

        self.application.db.commit()

        # Error out if we fail to retrieve the newly created user
        if cursor.lastrowid is None:
            self.write_json({"result": False, "errors": ["Error while adding listing to db"]}, status_code=500)
            return

        user = dict(
            id=cursor.lastrowid,
            name=name,
            created_at=time_now,
            updated_at=time_now
        )

        self.write_json({"result": True, "user": user})


# /users/{id}
class UserHandler(BaseHandler):
    """ Get specific user endpoint """
    @tornado.gen.coroutine
    def get(self, id=None):
        # Building select statement filtering for selected user
        select_stmt = "SELECT * FROM users WHERE id=?"

        cursor = self.application.db.cursor()
        results = cursor.execute(select_stmt, (id,))

        users = []
        for row in results:
            fields = ["id", "name", "created_at", "updated_at"]
            user = {
                field: row[field] for field in fields
            }
            users.append(user)

        # Send back results, if user does not exist, send back as error
        if len(users):
            self.write_json({"result": True, "users": users})
        else:
            self.write_json({"error": True, "users": None})


# /users/ping
class PingHandler(tornado.web.RequestHandler):
    """ Standard ping based status endpoint """
    @tornado.gen.coroutine
    def get(self):
        self.write("pong!")

def make_app(options):
    return App([
        (r"/users/ping", PingHandler),
        (r"/users", UsersHandler),
        (r"/users/([^/]+)?", UserHandler)
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
    logging.info("Starting user service. PORT: {}, DEBUG: {}".format(options.port, options.debug))

    try:
        # Start event loop in a Try/Except to kill the service when SIGINT is caught
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
        print("Exit sucess")