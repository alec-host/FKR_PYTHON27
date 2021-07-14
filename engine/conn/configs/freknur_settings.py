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


balance_key   = config.get("redis_key", "user_wallet_balance_key")
portfolio_key = config.get("redis_key", "user_asset_portfolio_key")
message_key   = config.get("redis_key", "push_message_key")

redis_key_params = {'USER_WALLET_BAL_KEY': balance_key, 'USER_PORTFOLIO_KEY' : portfolio_key, 'PUSH_NOTIFICATION_KEY' : message_key} 
