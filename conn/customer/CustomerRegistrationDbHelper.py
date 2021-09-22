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
from db_helper import _get_user_db,_get_uid_db
from configs.freknur_settings import logger,mysql_params
from db_conn import DB,NoResultException

db = DB()

class CustomerDbHelper():

    """
    -=================================================
    -.create new customer.
    -=================================================
    """
    def _registration_db(self,content,conn):

        date   = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uid    = content.uid
        msisdn = content.msisdn
        passwd = content.passwd

        try:
            qry = """
                  INSERT
                  INTO
                 `tbl_wallet`
                  (`uid`,`msisdn`,`password`,`date_created`)
                  VALUES
                  ('%s','%s','%s','%s')
                  ON
                  DUPLICATE
                  KEY UPDATE `date_modified` = '%s' """ % (uid,msisdn,passwd,date,date)

            params = ()
                
            db.execute_query(conn, qry, params)
        except Exception, e:
            logger.error(e)
            raise
