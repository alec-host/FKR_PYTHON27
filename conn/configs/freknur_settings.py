#!/usr/bin/python

import os
import sys
import logging
import ConfigParser

"""
current_dir = os.path.join("C:/", "Python27/workspace")
CONFIG_FILE = current_dir + '/freknur/conn/configs/freknur.conf'
"""

CONFIG_FILE = '/usr/local/lib/freknur/engine/conn/configs/freknur.conf'

config = ConfigParser.ConfigParser()
config.read(CONFIG_FILE)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("freknur")
logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
hdlr = logging.FileHandler(config.get("logger", "log_file"))
hdlr = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

host   = config.get("mysql", "host")
port   = config.get("mysql", "port")
user   = config.get("mysql", "user")
passwd = config.get("mysql", "password")
db     = config.get("mysql", "database")
connection_timeout = config.get("mysql", "connection_timeout")
mysql_params = {'host':host, 'port':port, 'user':user, 'passwd':passwd, 'db':db, 'connection_timeout':connection_timeout}

min_loan = config.get("loan_settings", "min_loan")
max_loan = config.get("loan_settings", "max_loan")
interest = config.get("loan_settings", "interest")
duration = config.get("loan_settings", "duration")
loan_fee = config.get("loan_settings", "loan_fee")
notify_1 = config.get("loan_settings", "notify_1")
notify_2 = config.get("loan_settings", "notify_2")
notify_3 = config.get("loan_settings", "notify_3")
notify_4 = config.get("loan_settings", "notify_4")
roll_cnt = config.get("loan_settings", "roll_cnt")
rebase   = config.get("loan_settings", "rebase")

loan_params = {'min_loan' :min_loan, 'max_loan' :max_loan, 'interest' :interest, 'duration' :duration, 'loan_fee':loan_fee, 'notify_1' :notify_1, 'notify_2' :notify_2, 'notify_3' :notify_3, 'notify_4' :notify_4, 'roll_cnt' :roll_cnt, 'rebase' :rebase}

accounts = config.get("book_keeping", "accounts");
credit   = config.get("book_keeping", "credit")
debit    = config.get("book_keeping", "debit")
accounting_params = {'accounts' :accounts, 'credit' :credit, 'debit' :debit}

host   = config.get("redis", "host")
port   = config.get("redis", "port")
passwd = config.get("redis", "password")
redis_params = {'host' :host, 'port' :port, 'passwd' :passwd}

balance_key     = config.get("redis_key", "user_wallet_balance_key")
portfolio_key   = config.get("redis_key", "user_asset_portfolio_key")
grain_stmt_key  = config.get("redis_key", "user_grain_stmt_key")
loan_stmt_key   = config.get("redis_key", "user_loan_stmt_key")
wallet_stmt_key = config.get("redis_key", "user_wallet_stmt_key")
shop_list_key   = config.get("redis_key", "shop_list_key")
asset_list_key  = config.get("redis_key", "asset_list_key")
message_key     = config.get("redis_key", "push_message_key")

redis_key_params = {'USER_WALLET_BAL_KEY' : balance_key, 'USER_PORTFOLIO_KEY' : portfolio_key, 'USER_GRAIN_STMT' : grain_stmt_key, 'USER_LOAN_STMT' : loan_stmt_key, 'USER_WALLET_STMT' : wallet_stmt_key, 'SHOP_LIST' : shop_list_key, 'ASSET_LIST' : asset_list_key, 'PUSH_NOTIFICATION_KEY' : message_key} 

shop_pubsub           = config.get("redis_pubsub", "shop_sale_channel")
loan_pubsub           = config.get("redis_pubsub", "loan_channel")
asset_pubsub          = config.get("redis_pubsub", "asset_channel")
asset_sale_pubsub     = config.get("redis_pubsub", "asset_sale_channel")
asset_purchase_pubsub = config.get("redis_pubsub", "asset_purchase_channel")

redis_pubsub_params = {'SHOP_PUBSUB' : shop_pubsub, 'LOAN_PUBSUB': loan_pubsub, 'ASSET_PUBSUB' : asset_pubsub, 'SALE_PUBSUB' : asset_sale_pubsub, 'PURCHASE_PUBSUB' : asset_purchase_pubsub}
