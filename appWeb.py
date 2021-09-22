#!/usr/bin/env python2

import os
import sys
import json
import MySQLdb
import logging
import signal
import Queue
import requests

from threading import Thread
from urllib import unquote

from flask import Flask, request, jsonify

from flask_selfdoc import Autodoc

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from conn.model import _PAYMENT_TEST_sys,_wallet_deposit_api,\
                       _get_loan_settings_configs_api,_get_asset_trend_list_api,_accept_bid_api,_get_accepted_bid_api,_get_bid_list_api,_place_bid_api,\
                       _modify_asset_api,_add_new_asset_api,_get_customer_list_api,_get_asset_list_api

from conn.db_helper import create_connection,close_connection,NoResultException,create_redis_connection,redis_access_key

from conn.RedisHelper import RedisHelper

from conn.dataGrid.DataGridModel import DataGridModel
#from conn.customer.CustomerModel import CustomerModel

#from conn.loan.LoanModel import LoanModel
#from conn.wallet.WalletModel import WalletModel
#from conn.sellGrain.SellGrainModel import SellGrainModel
#from conn.purchaseGrain.PurchaseGrainModel import PurchaseGrainModel
#from conn.shop.ShopModel import ShopModel
#from conn.frk.FRKTokenModel import FRKTokenModel
#from conn.helperUtils.JsonAddElement import JsonElementManager
#from conn.assetConf.AssetConfModel import AssetConfModel

#-pip install tornado.

log = logging.getLogger()

app = Flask(__name__)

auto = Autodoc(app)


#=====================================================================
#-.documentation class
#=====================================================================
class Post():
    def __init__(dself, title, content, author):
        self.title = title
        self.content = content
        posts.append(self)
        self.id = posts.index(self)

    def __repr__(self):
        return dumps(self.__dict__)


#=====================================================================
#-.route: customer list. (web)
#=====================================================================
@app.route('/GenerateCustomerListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateCustomerList():
    "Generate customer list via dashboard."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            data_grid_model = DataGridModel()
            
            search    = request.args.get('search')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            content = {"search": str(search),"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            resp = data_grid_model._get_customer_list_api(content,db)
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: asset list. (web)
#=====================================================================
@app.route('/GenerateAssetListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateAssetList():
    "Generate asset list via dashboard."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            
            data_grid_model = DataGridModel()
            
            search    = request.args.get('search')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            content = {"search": str(search),"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            resp = data_grid_model._get_asset_list_api(content,db)
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: sale list. (web)
#=====================================================================
@app.route('/GenerateSaleListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateSaleList():
    "Generate sales list via dashboard"
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            
            search    = request.args.get('search')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            data_grid_model = DataGridModel()
            
            content = {"search": search,"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_sale_inventory_list_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: loan request list(web)
#=====================================================================
@app.route('/GenerateLoanRequestListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateLoanRequestList():
    "Generate loan request list."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):

            data_grid_model = DataGridModel()
            
            search = request.args.get('search')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            content = {"search": search,"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_loan_request_list_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
            
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: dispatch loan list(web)
#=====================================================================
@app.route('/GenerateDispatchedLoanApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateDispatchedLoan():
    "Generate dispatched loan list."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):

            data_grid_model = DataGridModel()
            
            search = request.args.get('flag')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            content = {"search": search,"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_loan_dispatch_list_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
            
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: general accounts(web)
#=====================================================================
@app.route('/GenerateGeneralAccountListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateGeneralAccountList():
    "Generate general accounts list via dashboard."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            
            data_grid_model = DataGridModel()
            
            code = request.args.get('account_code')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            search = request.args.get('search')
            
            content = {"search": search,"lower_max": int(lower_max),"lower_min": int(lower_min),"code": str(code)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_general_account_list_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: debtor list(web)
#=====================================================================
@app.route('/GenerateDebtorListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateDebtorList():
    "Generate debtor list via the dashboard."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            
            data_grid_model = DataGridModel()
            
            search = request.args.get('flag')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            content = {"search": search,"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_debtor_list_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
            
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: defaulter list(web)
#=====================================================================
@app.route('/GenerateDefaulterListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateDefaulterList():
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            
            data_grid_model = DataGridModel()
            
            search = request.args.get('flag')
            lower_max = request.args.get('max')
            lower_min  = request.args.get('min')
            
            content = {"search": search,"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_defaulter_list_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: account summary list(web)
#=====================================================================
@app.route('/GenerateAccountSummaryReportApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateAccountSummaryReport():
    "Generate accounts summary report via the dashboard."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            
            data_grid_model = DataGridModel()
            
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            content = {"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_account_summary_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: stock account summary list(web)
#=====================================================================
@app.route('/GenerateStockAccountSummaryReportApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateStockAccountSummaryReport():
    "Generate accounts summary report via the dashboard."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            
            data_grid_model = DataGridModel()
            
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            content = {"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_stock_account_summary_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: activity logs(web)
#=====================================================================
@app.route('/GenerateActivityLogsApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateActivityLogs():
    "Generate activity logs via the dashboard."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            
            data_grid_model = DataGridModel()
            
            search = request.args.get('search')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            content = {"search": search,"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_activity_list_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
            
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: approve loan(web)
#=====================================================================
@app.route('/VetLoanRequestApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def VetLoanRequest():
    "Provides a means to screen loan requests via dashboard."
    db = create_connection()
    try:
        if(request.method == 'GET'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
        elif(request.method == 'POST'):
            content = request.get_json()
            if(content):
                
                loan_model = LoanModel()
                que = Queue.Queue()
                
                t = Thread(target=lambda q, (arg1,arg2): q.put(loan_model._vet_loan_request_api(arg1,arg2)), args=(que,(content,db)))
                t.start()
                t.join()
                
                resp = que.get()
            else:
                resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST data must be SET."}
                return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: dashboard login incomplete. (web)
#=====================================================================
@app.route('/DashboardLogin/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','private'])
def DashboardLogin():
    "Provides a means of user control & authentication to the dashboard."
    db = create_connection()
    try:
        if(request.method == 'GET'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
        elif(request.method == 'POST'):
            req_data = request.get_json()
            
            resp = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Authentication successful."}
        
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: inventory list. (web)
#=====================================================================
@app.route('/GenerateInventoryListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateInventoryList():
    "Generate an inventory list via dashboard."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):

            search    = request.args.get('search')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            data_grid_model = DataGridModel()
            
            content = {"search": search,"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._inventory_list_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.route: get configs.(web)
#=====================================================================
@app.route('/GenerateAssetConfigsListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def GenerateAssetConfigsList():
    "Generate asset configuration information via dashboard."
    db = create_connection()
    try:
        if(request.method == 'POST'):
            resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):
            
            data_grid_model = DataGridModel()
            
            search    = request.args.get('search')
            lower_max = request.args.get('max')
            lower_min = request.args.get('min')
            
            content = {"search": search,"lower_max": int(lower_max),"lower_min": int(lower_min)}
            
            que = Queue.Queue()
            
            t = Thread(target=lambda q,(arg1,arg2): q.put(data_grid_model._get_asset_config_list_api(arg1,arg2)), args=(que,(content,db)))
            t.start()
            t.join()
            
            resp = que.get()
        return resp
    except MySQLdb.Error, e:
        log.error(e)
    except Exception, e:
        log.error(e)
    finally:
        try:
            if(not db):
                exit(0)
            else:
                """
                close MySQL connection.
                """
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)


#=====================================================================
#-.exit tornado method.
#=====================================================================
def sig_exit():
    IOLoop.instance().add_callback_from_signal(do_stop)


#=====================================================================
#-.stop tornado method.
#=====================================================================
def do_stop():
    IOLoop.instance().stop()


#=====================================================================
#-.main method.
#=====================================================================
if(__name__ == '__main__'):
    try:
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(5001)
        signal.signal(signal.SIGINT,sig_exit)
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
    finally:
        log.info("web app is exiting...")
        IOLoop.instance().stop()
        IOLoop.instance().close(True)
        exit();
