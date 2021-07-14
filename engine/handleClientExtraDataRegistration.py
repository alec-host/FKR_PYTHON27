#!/usr/bin/python2
  
import os
import re
import sys
import json
import requests
import MySQLdb
import logging
import signal
import Queue

from conn.model import _get_action_on_temp_sys,_delete_action_on_temp_sys,_registration_extra_sys

from conn.configs.freknur_settings import loan_params,accounting_params

from conn.db_helper import create_connection,close_connection,NoResultException

log = logging.getLogger()

def logClientExtraInfo():
        try:
                while True:
                        db = create_connection()
                        """
                        -.get portfolio list.
                        """
                        items = json.loads(_get_action_on_temp_sys(db))
                        """
                        -.loop through each in the list.
                        """
                        if(len(items) > 0):
                                for item in items:
                                        msisdn = item['_action']
                                """
                                -routine call.
                                """
                                response = requests.get("https://api.betvantage.ke/user/"+str(msisdn))
                                r = json.loads(response.content)
                                db_response = None
                                if(str(r['msg']) != "[]"):
                                        msisdn = str(r['msg'][0]['phoneNumber'])
                                        fname  = str(r['msg'][0]['firstName'])
                                        sname  = str(r['msg'][0]['lastName'])
                                        dob    = str(r['msg'][0]['birthDate'])
                                        mail   = str(r['msg'][0]['emailAddress'])
                                        code   = str(r['msg'][0]['countryCode'])
                                        #-.routine call.
                                        db_response = _registration_extra_sys(msisdn,fname,sname,dob,mail,code,db)
                                #-.routine call.
                                _delete_action_on_temp_sys(msisdn,db)

                                print(db_response)
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
                                close connection.
                                """
                                if(db is not None):
                                        close_connection(db)
                except MySQLdb.Error, e:
                        log.error(e)

"""
-.main method.
"""
if __name__ == '__main__':
        try:
                logClientExtraInfo()
        except KeyboardInterrupt:
                exit(0)
