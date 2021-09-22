#!/usr/bin/python

"""
developer skype: alec_host
"""

import os
import sys
import json
import logging
import MySQLdb
import MySQLdb.cursors

from datetime import datetime

sys.path.append('/usr/local/lib/freknur/engine/conn')
from db_helper import _get_last_insert_id_db,_acitivity_log_db
from configs.freknur_settings import logger,mysql_params
from db_conn import DB,NoResultException

db = DB()

class FRKTokenDbHelper():

    """
    -=================================================
    -.method: .
    -=================================================
    """
    def _record_frk_transaction_db(self,this,conn):

        j_string = None
        msisdn = this.msisdn
        amount = this.amount
        unique_id = this.uid
        account_type = this.account_type

        try:

            sql = """CALL `db_freknur_investment`.`sProcFreknurTokenTransaction`(%s,%s,%s,%s)"""
            params = (msisdn,amount,unique_id,account_type,)
            output = db.retrieve_all_data_params(conn,sql,params)

            for data in output:
                j_string = json.loads(data.get('_JSON'))

                #conn.commit()
        except Exception, e:
            logger.error(e)
            raise

        return j_string
