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
import time
import platform
import sys
import requests
import json

username = password = ""
host = "localhost"
port = "3000"
token = ""


def instructions():
    print ("Enter your choice : \n 1.sign up \n 2.login \n 3.logout \n" "4.send ticket \n" "5.get tickets client \n"
           "6.close ticket \n" "7.get tickets manager \n " "8.response to ticket (manager)\n"
           "9.change ticket status (manager)\n"
           "10.Exit \n")


instructions()
choice = sys.stdin.readline()[:-1]

while choice != '10':

    if choice == '1':
        print("enter your username:  \n")
        username = sys.stdin.readline()[:-1]
        print ("enter your password:  \n")
        password = sys.stdin.readline()[:-1]
        print ("enter your first name \n")
        first_name = sys.stdin.readline()[:-1]
        print ("enter your last name \n")
        last_name = sys.stdin.readline()[:-1]
        args = {'username': username, 'password': password}

        userinfo = {"username": username,
                    "password": password,
                    "firstname": first_name,
                    "lastname": last_name
                    }
        r = requests.post("http://localhost:3000/signup?", data=userinfo).json()
        if r['code'] == '200':
            print("Signed Up Seccessfully")
        else:
            print(json.dumps(r))


    elif choice == '2':
        if not token:
            print("enter your username:  \n")
            username = sys.stdin.readline()[:-1]
            print ("enter your password:  \n")
            password = sys.stdin.readline()[:-1]
            userinfo = {"username": username,
                        "password": password
                        }
            r = requests.post("http://localhost:3000/login?", data=userinfo).json()
            if r['code'] == "200":
                print("Logged in Seccessfully \n ")
                token = r['token']

            else:
                print(json.dumps(r))

        else:
            print("you should log out first")

    elif choice == '3':
        print("enter your username:  \n")
        username = sys.stdin.readline()[:-1]
        print ("enter your password:  \n")
        password = sys.stdin.readline()[:-1]

        userinfo = {"username": username,
                    "password": password

                    }
        r = requests.post("http://localhost:3000/logout?", data=userinfo).json()
        if r['code'] and r['code'] == "200":
            print("Logged out Seccessfully \n ")

        else:
            print(json.dumps(r))

    elif choice == '4':
        print("enter message's subject:  \n")
        sub = sys.stdin.readline()[:-1]
        print ("enter message's body:  \n")
        body = sys.stdin.readline()[:-1]

        string = "token=" + token + "&" + "subject=" + sub + "&" + "body=" + body
        msginfo = {"token": token,
                   "subject": sub,
                   "body": body
                   }
        r = requests.post("http://localhost:3000/sendticket?", data=msginfo).json()
        if r['code'] and r['code'] == "200":
            print("message sent  \n ")

        else:
            print(json.dumps(r))

    elif choice == '5':
        string = "token=" + token
        r = requests.get("http://localhost:3000/getticketcli?" + string).json()
        if r['code'] and r['code'] == "200":
            j = 0
            while (j < int(r['tickets'])):
                print(json.dumps(r['block ' + str(j)]))
                j += 1



        else:
            print("Error")
            print(json.dumps(r))

    elif choice == '6':
        print("enter message's id:  \n")
        msgid = sys.stdin.readline()[:-1]

        string = "token=" + token + "&" + "id=" + msgid
        userinfo = {"token": token,
                    "id": msgid

                    }
        r = requests.post("http://localhost:3000/closeticket?", data=userinfo).json()
        if r['code'] == "200":
            print("message closed  \n ")

        else:
            print(json.dumps(r))

    elif choice == '7':
        string = "token=" + token

        r = requests.get("http://localhost:3000/getticketmod?" + string).json()
        if r['code'] and r['code'] == "200":
            j = 0
            while (j < int(r['tickets'])):
                print(json.dumps(r['block ' + str(j)]))
                j += 1

        else:
            print("Error")
            print(json.dumps(r))

    elif choice == '8':
        print("enter message's id:  \n")
        msgid = sys.stdin.readline()[:-1]
        print ("enter message's body:  \n")
        body = sys.stdin.readline()[:-1]

        string = "token=" + token + "&" + "id=" + msgid + "&" + "body=" + body
        userinfo = {"token": token,

                    "id": msgid,
                    "body": body
                    }
        r = requests.post("http://localhost:3000/restoticketmod?", data=userinfo).json()
        if r['code'] and r['code'] == "200":
            print("message sent  \n ")

        else:
            print(json.dumps(r))

    elif choice == '9':
        print("enter message's id:  \n")
        msgid = sys.stdin.readline()[:-1]
        print("enter new status:  \n")
        status = sys.stdin.readline()[:-1]

        string = "token=" + token + "&" + "id=" + msgid + "&" + "status=" + status
        userinfo = {"token": token,
                    "id": msgid,
                    "status": status

                    }
        r = requests.post("http://localhost:3000/changestatus?", data=userinfo).json()
        if (r['code'] == "200"):
            print("status changed  \n ")
        else:
            print(json.dumps(r))

    instructions()
    choice = sys.stdin.readline()[:-1]


userinfo = {"username": username,
            "password": password
            }
r = requests.post("http://localhost:3000/logout?", data=userinfo).json()
if r['code'] and r['code'] == "200":
    print("Logged out Seccessfully \n ")
else:
    print(json.dumps(r))