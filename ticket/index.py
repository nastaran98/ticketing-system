import os.path
import torndb
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import os
import datetime
from binascii import hexlify
import tornado.web
from tornado.options import define, options
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

define("port", default=3000, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="ticket", help="database name")
define("mysql_user", default="nastaran", help="database user")
define("mysql_password", default="2024", help="database password")


class Application(Application):
    def __init__(self):
        urls = [
            (r"/signup", SignUp),
            (r"/login", Login),
            (r"/logout", Logout),
            (r"/sendticket", sendticket),
            (r"/getticketcli", getticketcli),
            (r"/getticketmod", getticketmod),
            (r"/closeticket", closeticket),
            (r"/changestatus", changestatus),
            (r"/restoticketmod", restoticketmod)

        ]
        settings = dict()
        super(Application, self).__init__(urls, **settings)
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    def check_user(self, user):
        checkuser = self.db.get("SELECT * from user where username = %s", user)
        if checkuser:
            return True
        else:
            return False

    def check_auth(self, username, password):
        resuser = self.db.get("SELECT * from user where username = %s and password = %s", username, password)
        if resuser:
            return True
        else:
            return False

    def check_token(self, username):
        hastoken = self.db.get("SELECT * from user where username= %s ", username)

        if not hastoken.token:
            return True
        else:
            return False

    def get_token(self, token):
        result = self.db.get("SELECT * from user where token= %s ", token)
        if result:
            return True
        else:
            return False


class defaulthandler(BaseHandler):
    def get(self):
        output = {'status': 'Wrong Command'}
        self.write(output)

    def post(self, *args, **kwargs):
        output = {'status': 'Wrong Command'}
        self.write(output)


class SignUp(BaseHandler):
    def post(self):
        first_name = last_name = ""
        username = self.get_argument('username')
        password = self.get_argument('password')
        first_name = self.get_argument('firstname')
        last_name = self.get_argument('lastname')
        if not self.check_user(username):

            if username and password and first_name and last_name:
                id = self.db.execute("INSERT INTO user (username,password,firstname,lastname)"
                                     "values(%s,%s,%s,%s)"
                                     , username, password, first_name, last_name)
                output = {"message": "Signed Up Successfully",
                          "code": "200"}
            else:
                id = self.db.execute("INSERT INTO user (username,password)"
                                     "values(%s,%s)"
                                     , username, password)
                output = {"message": "Signed Up Successfully",
                          "warning": "empty firstname or lastname",
                          "code": "200"}

            self.write(output)

        else:
            output = {'status': 'User Exist', 'code': '201'}
            self.write(output)


class Login(BaseHandler):
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        if self.check_auth(username, password):

            if self.check_token(username):
                token = str(hexlify(os.urandom(16)))

                self.db.execute("UPDATE user SET token "
                                "= %s where username = %s"
                                , token, username)

                output = {
                    "message": "Logged in Successfully",
                    "code": "200",
                    "token": token
                }
                self.write(output)


            else:

                output = {'status': 'You are already logged in', 'code': '201'}
                self.write(output)

        else:
            output = {'status': 'wrong username or password', 'code': '202'}
            self.write(output)


class Logout(BaseHandler):
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        if self.check_auth(username, password):

            if not self.check_token(username):

                self.db.execute("UPDATE user SET token "
                                "= NULL where username = %s"
                                , username)

                output = {
                    "message": "Logged out Successfully",
                    "code": "200"

                }
                self.write(output)


            else:

                output = {'status': 'You have not logged in yet', 'code': '201'}
                self.write(output)

        else:
            output = {'status': 'wrong username or password', 'code': '202'}
            self.write(output)


class sendticket(BaseHandler):
    def post(self):
        token = self.get_argument('token')
        if self.get_token(token):
            user_info = self.db.get("SELECT * from user where token=%s ", token)
            username = user_info.username;
            subject = self.get_argument('subject')
            body = self.get_argument('body')
            now = datetime.datetime.now()

            self.db.execute("INSERT INTO message (sender,subject,body,status,date)"
                            "values(%s,%s,%s,%s,%s)", username, subject, body, "open", now)
            output = {"message": "Ticket Sent Successfully",

                      "code": "200"
                      }
            self.write(output)

        else:
            output = {'status': 'token not found,try again', 'code': '201'}
            self.write(output)


class getticketcli(BaseHandler):
    def get(self):
        token = self.get_argument('token')
        if self.get_token(token):
            user_info = self.db.get("SELECT * from user where token=%s ", token)
            if user_info.username != 'nastaran':
                msg = self.db.query("SELECT * from message where sender=%s ", user_info.username)

                tickets = 0
                for x in msg:
                    tickets += 1
                output = {
                    "tickets": tickets,
                    "code": "200",

                }
                counter = 0

                for messages in msg:
                    pvmsg = {
                        'block ' + str(counter): messages
                    };
                    counter += 1
                    output = dict(output.items() + pvmsg.items())

                self.write(output)



            else:
                output = {'status': 'You are manager , use manager get method', 'code': '201'}
                self.write(output)


        else:
            output = {'status': 'token not found,try again', 'code': '202'}
            self.write(output)


class getticketmod(BaseHandler):
    def get(self):
        token = self.get_argument('token')
        if self.get_token(token):
            user_info = self.db.get("SELECT * from user where token=%s ", token)

            if user_info.username == 'nastaran':
                msg = self.db.query("SELECT * from message where sender=%s ", user_info.username)

                tickets = 0
                for x in msg:
                    tickets += 1
                output = {
                    "tickets": tickets,
                    "code": "200",

                }
                counter = 0

                for messages in msg:
                    pvmsg = {
                        'block ' + str(counter): messages
                    };
                    counter += 1
                    output = dict(output.items() + pvmsg.items())

                self.write(output)
            else:
                output = {'status': 'you are not manager','code':'201'}
                self.write(output)



        else:
            output = {'status': 'not found','code':'201'}
            self.write(output)


class closeticket(BaseHandler):
    def post(self):
        token = self.get_argument('token')
        userid = self.get_argument('id')
        if self.get_token(token):
            user_info = self.db.get("SELECT * from user where token=%s ", token)

            self.db.execute("UPDATE message SET status "
                            "= %s where id = %s"
                            , "close", userid)

            output = {'status': 'message closed', 'code': '200'}
            self.write(output)

        else:
            output = {'status': 'token not found', 'code': '201'}
            self.write(output)


class changestatus(BaseHandler):
    def post(self):
        token = self.get_argument('token')
        userid = self.get_argument('id')
        status = self.get_argument('status')
        if self.get_token(token):
            user_info = self.db.get("SELECT * from user where token=%s ", token)

            if user_info.username == 'nastaran':
                self.db.execute("UPDATE message SET status "
                                "= %s where id = %s"
                                , status, userid)
                output = {'status': 'status changed', 'code': '200', 'username': user_info.username}
                self.write(output)

            else:
                output = {'status': 'you are not manager','code':'202'}
                self.write(output)



        else:
            output = {'status': 'not found','code':'202'}
            self.write(output)


class restoticketmod(BaseHandler):
    def post(self):
        token = self.get_argument('token')
        userid = int(self.get_argument('id'))
        body = self.get_argument('body')
        receiver = self.db.get("SELECT * from message where id=%s ", userid)

        if self.get_token(token):
            user_info = self.db.get("SELECT * from user where token=%s ", token)
            now = datetime.datetime.now()

            if user_info.username == 'nastaran':
                self.db.execute("INSERT INTO message (sender,receiver,subject,body,status,date)"
                                "values(%s,%s,%s,%s,%s,%s)", user_info.username, receiver.sender, "reply", body, "open",
                                now)
                output = {'status': 'message sent', 'code': '200'}
                self.write(output)
            else:
                output = {'status': 'you are not manager', 'code': '201'}
                self.write(output)



        else:
            output = {'status': 'not found', 'code': '202'}
            self.write(output)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
