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

from random import randint
from flask import Flask, request, jsonify
from flask_swagger import swagger

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
from conn.customer.CustomerModel import CustomerModel

from conn.loan.LoanModel import LoanModel
from conn.wallet.WalletModel import WalletModel
from conn.sellGrain.SellGrainModel import SellGrainModel
from conn.purchaseGrain.PurchaseGrainModel import PurchaseGrainModel
from conn.shop.ShopModel import ShopModel
from conn.frk.FRKTokenModel import FRKTokenModel
from conn.helperUtils.JsonAddElement import JsonElementManager
from conn.assetConf.AssetConfModel import AssetConfModel

#-pip install tornado.

log = logging.getLogger()

app = Flask(__name__)

auto = Autodoc(app)

class Post():
        def __init__(dself, title, content, author):
                self.title = title
                self.content = content
                posts.append(self)
                self.id = posts.index(self)

        def __repr__(self):
                return dumps(self.__dict__)

"""
-.spec document.
"""
@app.route('/')
@app.route('/getSwaggerApiSpec/')
def spec():
        swag = swagger(app)
        swag['info']['version'] = "1.0"
        swag['info']['title'] = "Freknur API"

        return jsonify(swag)

#=====================================================================
#-.route: loan_without_collateral api
#=====================================================================
@app.route('/UnsecuredLoanApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def UnsecuredLoanApi():
        "Handles unsecured loan request. Params: @amount,@msisdn"
        db = create_connection()
	try:
		resp = 'Ok'
		if(request.method == 'GET'):
			resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
		elif(request.method == 'POST'):	
			if(request.data):

                                loan_model = LoanModel()

				content = json.loads(request.data)

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(loan_model._record_unsecured_loan_request_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
			else:
				resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}
					
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
#-.route: registration api
#=====================================================================
@app.route('/RegistrationApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def Registration():
        "Handle customer registration."
	db = create_connection()
	try:
		if(request.method == 'GET'):
			resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
		elif(request.method == 'POST'):	
			if(request.data):

                                customer_model = CustomerModel()
                                
                                content = json.loads(request.data)

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(customer_model._registration_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
			else:
				resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data received"}
			
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
#-.route: statement api
#=====================================================================
@app.route('/ComprenhensiveWalletStatementApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def ComprenhensiveWalletStatement():
        "Generate a comprehensive wallet statement."
	db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
	try:
		if(request.method == 'POST'):
			resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
		elif(request.method == 'GET'):
                        if(request.data):

                                msisdn = request.data
                                
                                #-.resp = _get_comprehensive_wallet_statement_api(msisdn,db)

                                key = redis_helper.redis_access_key()[4]+str(msisdn)
                                #-.read cache.
                                cache = redis_helper._read_redis_cache(key,rd)
                                    
                                if(cache is None):

                                        customer_model = CustomerModel()

                                        que = Queue.Queue()

                                        t = Thread(target=lambda q,(arg1,arg2): q.put(customer_model._get_comprehensive_wallet_statement_api(arg1,arg2)), args=(que,(msisdn,db)))

                                        t.start()
                                        t.join()

                                        resp = que.get()
                                        #-.save response.
                                        redis_helper._save_to_redis_cache(key,str(resp),rd)
                                else:
                                        resp = cache
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data received"}
			
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
#-.route: loan mini statement api
#=====================================================================
@app.route('/LoanMiniStatementApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def LoanMiniStatement():
        "Generate a mini loan statement."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        if(request.data):
                            
                                msisdn = request.data

                                key = redis_helper.redis_access_key()[3]+str(msisdn)

                                #-.read cache.
                                cache = redis_helper._read_redis_cache(key,rd)

                                if(cache is None):

                                        customer_model = CustomerModel()

                                        que = Queue.Queue()

                                        t = Thread(target=lambda q,(arg1,arg2): q.put(customer_model._get_mini_loan_statement_api(arg1,arg2)), args=(que,(msisdn,db)))

                                        t.start()
                                        t.join()

                                        resp = que.get()
                                        #-.save response.
                                        redis_helper._save_to_redis_cache(key,str(resp),rd)
                                else:
                                        resp = cache

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
#-.route: asset mini statement api
#=====================================================================
@app.route('/AssetMiniStatementApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def AssetMiniStatement():
        "Generate a mini asset statement."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):

                        if(request.data):

                                msisdn  = request.args.get('msisdn')
                                msisdn = request.data

                                key = redis_helper.redis_access_key()[2]+str(msisdn)
                    
                                #-.read cache.
                                cache = redis_helper._read_redis_cache(key,rd)

                                if(cache is None):

                                        customer_model = CustomerModel()

                                        que = Queue.Queue()

                                        t = Thread(target=lambda q,(arg1,arg2): q.put(_get_mini_asset_statement_api(arg1,arg2)), args=(que,(msisdn,db)))
                                        t.start()
                                        t.join()

                                        resp = que.get()
                                        #-.save response.
                                        redis_helper._save_to_redis_cache(key,str(resp),rd)
                                else:
                                        resp = cache
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
#-.route: wallet balanace api
#=====================================================================
@app.route('/CurrentWalletBalanceApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def CurrentWalletBalance():
        "Query for current wallet balance."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        if(request.data):

                                msisdn = request.data

                                key = redis_helper.redis_access_key()[0]+str(msisdn)

                                #-._delete_from_redis_cache_api(key,rd)
                                
                                #-.read cache.
                                cache = redis_helper._read_redis_cache(key,rd)

                                if(cache is None):

                                        customer_model = CustomerModel()

                                        que = Queue.Queue()

                                        t = Thread(target=lambda q,(arg1,arg2): q.put(customer_model._get_customer_balance_api(arg1,arg2)), args=(que,(msisdn,db)))

                                        t.start()
                                        t.join()

                                        customer_wallet = que.get()
                                        resp = json.dumps({"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"BALANCE#"+str(customer_wallet[0])})                  
                                        #-.save output
                                        redis_helper._save_to_redis_cache(key,str(resp),rd)
                                else:
                                        resp = cache
                        else:

                                resp = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"MSISDN must be checked."}
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
#-.route: withdraw app.
#=====================================================================
@app.route('/WithdrawRequestApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def WithdrawRequest():
        "Handles client withdraw operation."
	db = create_connection()
	try:
		if(request.method == 'GET'):
			resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}		
		elif(request.method == 'POST'):
                        if(request.data):

                                wallet_model = WalletModel()

                                content = json.loads(request.data)
                                
                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(wallet_model._record_withdraw_transaction_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"MSISDN|AMOUNT must be SET."}
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
#-.route: get outstanding loan bal.
#=====================================================================
@app.route('/OutstandingLoanApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def OutstandingLoan():
        "Queries for current outstanding loan balance."
        db = create_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        if(request.data):

                                msisdn = request.data

                                loan_model = LoanModel()

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(loan_model._get_loan_arrears_api(arg1,arg2)), args=(que,(msisdn,db)))

                                t.start()
                                t.join()

                                resp = que.get()            
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"MSISDN must be SET."}
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
#-.route: otp generator incomplete.
#=====================================================================
@app.route('/OTPGeneratorApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','private'])
def OTPGenerator():
        db = create_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        if(request.data):
                                msisdn = request.data

                                otp = 1234

                                resp = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"OTP#" + str(otp) + ""}
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"MSISDN must be SET."}
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
#-.route: sms gateway.
#=====================================================================
@app.route('/SMSGatewayApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','private'])
def SMSGatewayApi():
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)
                                url = 'http://localhost/olivetree/incomingsms/bulksms.php'
                                headers = {
                                    'Content-Type': 'application/json'        
                                }    
                                resp = requests.request("POST", url, headers=headers, data=request.data)
                                if(resp.text == "<Response [200]>"):
                                    resp = {"ERROR":"0","RESULT":"SUCCESS" ,"MESSAGE":"Message queued"}
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}

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
#-.route: custom notification incomplete
#=====================================================================
@app.route('/CreateNotificationApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','private'])
def CustomNotification():
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):

                                content = json.loads(request.data)

                                key = redis_helper.redis_access_key()[7]+str(content['msisdn'])

                                cache = redis_helper._read_redis_cache(key,rd)

                                json_element_manager = JsonElementManager()

                                if(cache is None):
                                        notification = json_element_manager._append_1st_element(content['message'])
                                        #-.save message.
                                        redis_helper._save_to_redis_cache(key,str(notification),rd)
                                else:
                                        notification = json_element_manager._append_nth_element(cache,content['message'])
                                        #-.save message.
                                        redis_helper._save_to_redis_cache(key,str(notification),rd)
                                        
                                resp = {"ERROR":"0","STATUS":"SUCCESS","MESSAGE": "Message has been stored."}
                        else:
                                resp = {"ERROR":"1","STATUS":"FAIL","MESSAGE":"MSISDN,MESSAGE has to be set."}
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
#-.route: download notification.
#=====================================================================
@app.route('/DownloadNotificationApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','private'])
def GetNotification():
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):

                        key = redis_helper.redis_access_key()[7]+str(request.data)
                        #-.read cache.
                        message = redis_helper._read_redis_cache(key,rd)

                        if(message is not None):
                                resp = (message)
                        else:
                                resp = {"ERROR":"1","STATUS":"FAIL","MESSAGE":"No message to download"}

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
#-.route: assets configuration params. (app)
#=====================================================================
@app.route('/GenerateAssetConfigParamsListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateAssetConfigParamsList():
        "Generate asset configuration params list."
        db = create_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        msisdn = request.data
                        
                        asset_conf_model = AssetConfModel()

                        que = Queue.Queue()

                        t = Thread(target=lambda q,(arg1): q.put(asset_conf_model._get_asset_config_params_api(arg1)), args=(que,(db)))
                        
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
#-.route: customer portfolio.
#=====================================================================
@app.route('/GenerateCustomerPortfolioApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateCustomerPortfolio():
        "Generate customer's asset portfolio."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        msisdn = request.data

                        key = redis_helper.redis_access_key()[1]+str(msisdn)
                        
                        #-._delete_from_redis_cache_api(key,rd)

                        #-.read cache.
                        cache = redis_helper._read_redis_cache(key,rd)

                        if(cache is None):
                                customer_model = CustomerModel()

                                content = {"msisdn": msisdn}

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(customer_model._get_customer_portfolio_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                                #-.save output.
                                redis_helper._save_to_redis_cache(key,str(resp),rd)
                        else:
                                resp = cache
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
#-.route: add new asset. (web)
#=====================================================================
@app.route('/AddAssetApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def AddAsset():
        "Add new asset(grain) entry via dashboard."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()        
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)

                                resp = _add_new_asset_api(content['acronym'],content['name'],content['price'],content['total'],db)
                                #-.get key.
                                key = redis_helper.redis_access_key()[6]+str("asset_list")
                                #-.reset cache.
                                redis_helper._delete_from_redis_cache(key,rd)
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}
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
#-.route: modify asset. (web)
#=====================================================================
@app.route('/ModifyAssetApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def ModifyAsset():
        "Modify asset record via dashboard."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)
                            
                                resp = _modify_asset_api(content['uid'],content['acronym'],content['name'],content['price'],content['total'],db)
                                #-.get key.
                                key = redis_helper.redis_access_key()[6]+str("asset_list")
                                #-.reset cache.
                                redis_helper._delete_from_redis_cache(key,rd)
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}
                print(resp)
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
#-.route: purchase asset request. app
#=====================================================================
@app.route('/PurchaseAssetRequestApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def PurchaseAssetRequest():
        "Handles customer asset purchase requests."
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)
                                
                                if(len(content) == 6):
                                        purchase_grain_model = PurchaseGrainModel()
                                        qty  = content['no_of_unit'].replace(",","")

                                        que = Queue.Queue()

                                        t = Thread(target=lambda q,(arg1,arg2): q.put(purchase_grain_model._record_purchase_request_api(arg1,arg2)), args=(que,(content,db)))

                                        t.start()
                                        t.join()

                                        resp = que.get()
                                else:
                                        resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Params expected: msisdn,uid,description,price,no_of_unit,cost"}

                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Purchase request has failed"}
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
#-.route: sell asset request. app
#=====================================================================
@app.route('/SaleAssetRequestApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def SaleAssetRequest():
        "Handles customer sale requests."
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)
                                
                                if(len(content) == 6):
                                        sell_grain_model = SellGrainModel()

                                        que = Queue.Queue()

                                        t = Thread(target=lambda q,(arg1,arg2): q.put(sell_grain_model._record_sell_request_api(arg1,arg2)), args=(que,(content,db)))

                                        t.start()
                                        t.join()

                                        resp = que.get()
                                else:
                                        resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Params expected: msisdn,uid,description,price,no_of_unit,cost"}
    
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Sell request has failed"}
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
#-.route: get own asset . app
#=====================================================================
@app.route('/GenerateAssetSaleListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateAssetSaleList():
        "Generate asset sale request list."
        db = create_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        if(request.data):

                                msisdn = request.data
                                is_owner = 0

                                content = {"msisdn": msisdn, "is_owner": is_owner}

                                sell_grain_model = SellGrainModel()

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(sell_grain_model._get_sale_request_list_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Action has failed"}
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
#-.route: buy request. app - REMOVE
#=============i========================================================
@app.route('/PlacePurchaseIntentApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def PlacePurchaseIntentApi():
        "Place a purchase intent & originate a notification."
        db   = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)

                                r_key = content['owner_msisdn']
                                r_msg = 'A bid has been to made.'

                                #-.delete key from redis.
                                redis_helper._delete_from_redis_cache(r_key,rd)
                                #-.write key & message to redis.        
                                redis_helper._save_to_redis_cache(r_key,r_msg,rd)
                            
                                resp = _place_bid_api(content['asset_id'],content['asset_name'],content['owner_msisdn'],content['bidder_msisdn'],content['qty'],content['bid_price'],db)
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Operation has failed."}
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
#-.route: system buy offer . app  - REMOVE
#=====================================================================
@app.route('/GeneratePurchaseOfferListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GeneratePurchaseOfferList():
        db = create_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        msisdn = request.data

                        resp = _get_bid_list_api(msisdn,db)
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
#-.route: to be revised.
#=====================================================================
@app.route('/GenerateAcceptedBidListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def GenerateAcceptedBidList():
        "Note: operation not available."
        db = create_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        msisdn = request.data

                        resp = _get_accepted_bid_api(msisdn,db)
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
#-.route: to be revised. REMOVE
#=====================================================================
@app.route('/AcceptBidApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def AcceptBidApi():
        "Note: operation not available."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                        
                                content = json.loads(request.data)
                                r_msg = 'Your bid has been accepted.'
                                r_key = content['bidder_msisdn']

                                #-.delete key from redis.
                                redis_helper._delete_from_redis_cache(r_key,rd)
                                #-.write key & message to redis.
                                redis_helper._save_to_redis_cache(r_key,r_msg,rd)
                                
                                resp = _accept_bid_api(content['bid_id'],content['asset_id'],db)

                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Operation has failed."}

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
#-.route: buy asset from alt market.(app)
#=====================================================================
@app.route('/PurchaseAssetOnAlternativeMarketApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['public','private'])
@auto.doc(description='freknur')
def PurchaseAssetOnAlternativeMarket():
        "Handle asset purchase from alternative market."
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)

                                if(len(content) == 6):
                                        purchase_grain_model = PurchaseGrainModel()
                                    
                                        que = Queue.Queue()

                                        t = Thread(target=lambda q,(arg1,arg2): q.put(purchase_grain_model._record_alt_purchase_request_api(arg1,arg2)), args=(que,(content,db)))

                                        t.start()
                                        t.join()

                                        resp = que.get()
                                else:
                                        resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Params expected: uid,msisdn,description,price,no_of_unit,cost"}

                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Sell request has failed"}
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
#-.route: add configs.(web)
#=====================================================================
@app.route('/AddAssetConfigsApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def AddAssetConfigs():
        "Add asset configuration information via dashbaord."
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)

                                asset_conf_model = AssetConfModel()
                                
                                resp = asset_conf_model._create_asset_config_api(content,db)
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Config setup has failed"}
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
#-.route: edit asset config.(web)
#=====================================================================
@app.route('/ModifyAssetConfigsApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def ModifyAssetConfigs():
        "Handles modification of assets configuration information via dashboard."
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)

                                asset_conf_model = AssetConfModel()

                                resp = asset_conf_model._modify_asset_config_api(content,db)
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Config setup has failed"}
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
#-.route: get asset movement.(app)
#=====================================================================
@app.route('/GenerateAssetTradeListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateAssetTradeList():
        "Generate asset trade list."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()        
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        msisdn = request.args.get('msisdn')

                        key = redis_helper.redis_access_key()[6]+str("asset_list")
                        #-.read cache.
                        cache = redis_helper._read_redis_cache(key,rd)

                        if(cache is None):
                                resp = _get_asset_trend_list_api(msisdn,db)
                                #-.save response.
                                redis_helper._save_to_redis_cache(key,str(resp),rd)
                        else:
                                resp = cache

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
#-.route: get loan settings.(web)
#=====================================================================
@app.route('/GenerateLoanSettingsApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateLoanSettingsApi():
        if(request.method == 'POST'):
                resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
        elif(request.method == 'GET'):

                settings = request.args.get('settings')

                resp = _get_loan_settings_configs_api()

        return resp


#=====================================================================
#-.route: loan with collateral.(app)
#=====================================================================
@app.route('/SecuredLoanApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def SecuredLoan(): 
        "Handles loan request secured with collateral."
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                loan_model = LoanModel()
                                content = json.loads(request.data)                    
                                
                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(loan_model._record_secured_loan_request_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}
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
#-.route: get own asset sell request.(app)
#=====================================================================
@app.route('/GeneratetOwnSaleRequestListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GeneratetOwnSellRequestList():
        "Generate custmer own sale request list."
        db = create_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        if(request.data):

                                msisdn = request.data
                                is_owner = 1

                                content = {"msisdn": msisdn, "is_owner": is_owner}

                                sell_grain_model = SellGrainModel()

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(sell_grain_model._get_sale_request_list_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Action has failed"}

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
#-.route: edit own asset sell request.(app)
#=====================================================================
@app.route('/ModifyOwnSaleRequestApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def ModifyOwnSaleRequest():
        "Handles modification of customer sales requests."
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)
                                
                                if(len(content) == 6):
                                        
                                        sell_grain_model = SellGrainModel()
                        
                                        sell_grain_model._delete_own_sale_requet_api(content,db)

                                        que = Queue.Queue()

                                        t = Thread(target=lambda q,(arg1,arg2): q.put(sell_grain_model._record_sell_request_api(arg1,arg2)), args=(que,(content,db)))

                                        t.start()
                                        t.join()

                                        resp = que.get()                                        
                                else:
                                        resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Params expected: uid,msisdn,description,price,no_of_unit,cost"}
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Modify Sell Request has failed"}
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
#-.route: delete own asset sell request.(app)
#=====================================================================
@app.route('/DeleteOwnSellRequestListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def DeleteOwnSellRequestList():
        "Handles deletion of customer sale request."
        db = create_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):
                        if(request.data):

                                content = json.loads(request.data)

                                sell_grain_model = SellGrainModel()

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(sell_grain_model._delete_own_sale_requet_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Operation has failed."}
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
#-.route: memory cache. incomplete
#=====================================================================
@app.route('/IOMemoryCacheApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','private'])
def IOMemoryCache():
        "Note: implementation is not available."
        rd = create_redis_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                    resp = {"ERROR":"0","RESULT":"FAIL","MESSAGE":"open connection: "+str(rd.get("msisdn"))}
                
                return resp
        except Exception, e:
                log.error(e)                


#=====================================================================
#-.route: peer to peer transfer.
#=====================================================================
@app.route('/PeerWalletTransferApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def PeerWalletTransfer():
        "Handles inter wallet transfers."
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                wallet_model = WalletModel()
                                content = json.loads(request.data)
            
                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(wallet_model._peer_2_peer_wallet_transfer_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}
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
#-.route: wallet deposit.
#=====================================================================
@app.route('/WalletDepositApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def WalletDeposit():
        "Handles customer deposit."
        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)

                                resp = _wallet_deposit_api(content['amount'],content['msisdn'],db)
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}
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
#-.route: shop inventory list. (app)
#=====================================================================
@app.route('/GenerateShopInventoryListApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['get','public','private'])
def GenerateShopInventoryList():
        "Generate a shop inventory list."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'POST'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"POST method not allowed"}
                elif(request.method == 'GET'):

                        msisdn = request.data

                        content = {"msisdn":msisdn}

                        key = redis_helper.redis_access_key()[5]+str("shop_catalogue")
                        
                        #-.read cache.
                        cache = redis_helper._read_redis_cache(key,rd)

                        if(cache == "null" or cache is None):

                                customer_model = CustomerModel()

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(customer_model._shop_inventory_list_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                                #-.save response.
                                redis_helper._save_to_redis_cache(key,str(resp),rd)
                        else:
                                resp = cache
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
#-.route: add an inventory item. (web)
#=====================================================================
@app.route('/CreateInventoryItemApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def AddInventory():
        "Add a new inventory item via dashboard."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):

                                shop_model = ShopModel()

                                content = json.loads(request.data)

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(shop_model._create_inventory_item_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()
                                    
                                #-.get redis key.
                                key = redis_helper.redis_access_key()[5]+str("shop_catalogue")
                                #-.reset cache.
                                redis_helper._delete_from_redis_cache(key,rd)

                                resp = que.get()
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"sales recorded successful"}
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
#-.route: edit an inventory item. (web)
#=====================================================================
@app.route('/ModifyInventoryItemApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def ModifySale():
        "Modify a sale entry via dashboard."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):

                                shop_model = ShopModel()

                                content = json.loads(request.data)

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(shop_model._modify_inventory_item_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()

                                key = redis_helper.redis_access_key()[5]+str("shop_catalogue")
                                #-.reset cache.
                                redis_helper._delete_from_redis_cache(key,rd)
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"modification successful"}
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
#-.route: upload image file. (web)
#=====================================================================
@app.route('/SaveInventoryImagePathApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def PostInventoryImagePath():
        "Handles inventory item image path update."
        db = create_connection()

        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                
                                shop_model = ShopModel()

                                content = json.loads(request.data)

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(shop_model._post_inventory_item_image_path_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                                
                                key = redis_helper.redis_access_key()[5]+str("shop_catalogue")
                                #-.reset cache.
                                redis_helper._delete_from_redis_cache(key,rd)
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"Operation has failed."}
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
#-.route: record shop sales. (app cart)
#=====================================================================
@app.route('/RecordShopSaleApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
def RecordShopSaleApi():
        "Records sales list from shop cart."
        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()

        db = create_connection()
        try:
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):

                                shop_model = ShopModel()

                                content = json.loads(request.data)

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(shop_model._record_shop_sale_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"modification successful"}
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
#-.route: loan repyment. (app)
#=====================================================================
@app.route('/LoanRepaymentTestApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
@auto.doc(args=['amount','msisdn'])
def LoanRepaymentTest():
        db = create_connection()
        try:
                resp = 'Ok'
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                trx = str(randint(100000000,999999999)) 
                                content = json.loads(request.data)

                                resp = _PAYMENT_TEST_sys(trx,content['amount'],content['msisdn'],db)
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}
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
#-.route: FKR wallet transaction. (app)
#=====================================================================
@app.route('/FRKTokenWalletTransactionApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
@auto.doc(args=['amount','msisdn'])
def FRKTokenWalletTransaction():
        db = create_connection()
        redis_helper = RedisHelper()
        rd = redis_helper.create_redis_connection()
        try:
                resp = 'Ok'
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                            
                                frk_token_model = FRKTokenModel()

                                content = json.loads(request.data)
                               
                                key_1 = redis_helper.redis_access_key()[0]+str(content['msisdn'])
                                key_2 = redis_helper.redis_access_key()[1]+str(content['msisdn'])

                                redis_helper._delete_from_redis_cache(key_1,rd)
                                redis_helper._delete_from_redis_cache(key_2,rd)                               

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(frk_token_model._record_frk_transaction_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()
                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}
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
#-.route: suspend wallet. (web)
#=====================================================================
@app.route('/SuspendWalletApi/', methods = ['GET', 'POST'])
@auto.doc(groups=['posts','public','private'])
@auto.doc(args=['amount','msisdn'])
def SuspendWallet():
        db = create_connection()
        try:
                resp = 'Ok'
                if(request.method == 'GET'):
                        resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"GET method not allowed"}
                elif(request.method == 'POST'):
                        if(request.data):
                                content = json.loads(request.data)

                                wallet_model = WalletModel()

                                que = Queue.Queue()

                                t = Thread(target=lambda q,(arg1,arg2): q.put(wallet_model._suspend_wallet_account_api(arg1,arg2)), args=(que,(content,db)))

                                t.start()
                                t.join()

                                resp = que.get()

                                resp = content

                        else:
                                resp = {"ERROR":"1","RESULT":"FAIL" ,"MESSAGE":"No data posted"}
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
#-.route: documentation (web)
#=====================================================================
@app.route('/doc')
@app.route('/doc/', methods = ['GET', 'POST'])
def documentation():
        #return auto.html(groups=['public'],title='Freknur Documentation',author='alex')
        
        return jsonify(auto.generate('public'))
        #return auto.html('public')


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
		http_server.listen(5000)
		signal.signal(signal.SIGINT,sig_exit)
		IOLoop.instance().start()
	except KeyboardInterrupt:
		pass
	finally:
		log.info("app is exiting...")
		IOLoop.instance().stop()
		IOLoop.instance().close(True)
		exit();
		
