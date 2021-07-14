import os
import sys
import json
import MySQLdb
import logging
import signal
import Queue

from flask import Flask, request, jsonify

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

log = logging.getLogger()

app = Flask(__name__)

"""
-.test api.
"""
@app.route('/test/', methods = ['GET', 'POST'])
def testOperation():
    if(request.method == 'GET'):
	return 'GET Method not allowed'
    else:
        content = request.get_json()

        return str(content)
"""
-.exit method.
"""
def sig_exit():
    IOLoop.instance().add_callback_from_signal(do_stop)

"""
-.stop tornado method.
"""
def do_stop():
    IOLoop.instance().stop()

"""
-.main method.
"""
if(__name__ == '__main__'):
    try:
        print('tornado started...')
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(5000)
        signal.signal(signal.SIGINT,sig_exit)
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
    finally:
        log.info("Application is exiting...")
        IOLoop.instance().stop()
        IOLoop.instance().close(True)
        exit();
