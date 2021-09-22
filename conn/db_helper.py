#!/usr/bin/python

"""
developer skype: alec_host
"""

import os
import sys
import time
import signal
import json
import decimal
import ast
import uuid
import eventlet
import logging
import MySQLdb
import MySQLdb.cursors

import redis

from collections import OrderedDict
from datetime import datetime
from configs.freknur_settings import loan_params,logger,mysql_params,redis_params,redis_key_params
from db_conn import DB,NoResultException,NoServiceIDException

from json_tricks import dumps

eventlet.monkey_patch()

db = DB()

"""
-=================================================
-.record new loan request.
-=================================================
"""	
def _record_unsecured_loan_request_db(msisdn,amount,conn):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	j_string = None
        rd = create_redis_connection()
	try:
                #-.routine call to check whether user has existing loan.
                has_loan = _get_has_loan_db(msisdn,conn)
                #-.routine call to generate a unique loan id.
                loan_uid = _get_loan_uid_db(conn)
                #-.routine call to check whether user exist.
                exist = _get_user_db(msisdn,conn)
                #-.routine call: existing request.
                has_request = _has_loan_request_db(msisdn,conn)
                #-.delete logs.
                #-._del_loan_approved_processed_log(conn)

                min_allowed_loan = int(loan_params['min_loan'])
                max_allowed_loan = int(loan_params['max_loan'])

                if(int(exist) == 1):
                        if(int(has_loan) == 0):
                                if(int(has_request[0]) == 0):
                                        if(int(amount) >= min_allowed_loan and int(amount) <= max_allowed_loan):

		                                sql = """INSERT
                                                         INTO
                                                        `db_freknur_loan`.`tbl_loan_request`
                                                         (`msisdn`,`reference_no`,`amount`,`requested_by`,`date_created`)
                                                         VALUES
                                                         ('%s','%s','%s','%s','%s')
                                                         ON 
                                                         DUPLICATE KEY
                                                         UPDATE `date_modified` = '%s' """ % (msisdn,str(loan_uid).upper(),amount,msisdn,date,date)

		                                params = ()

                                                db.execute_query(conn, sql, params)

                                                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Loan request was successful."}

		                                conn.commit()
                                                #-.get keys.
                                                key_1 = redis_access_key()[0]+str(msisdn)
                                                key_2 = redis_access_key()[1]+str(msisdn)
                                                #-.reset cache.
                                                _delete_from_redis_cache(key_1,rd)
                                                _delete_from_redis_cache(key_2,rd)
                                        else:
                                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Loan limits: MINIMUM : "+str(min_allowed_loan)+" MAXIMUM : "+str(max_allowed_loan)}
                                else:
                                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have loan request of "+str(has_request[1])+" pending approval."}
                        else:
                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have an existing loan."}
                else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You are not a registered user."}
	except Exception, e:
		logger.error(e)
		raise	
	
	return j_string

"""
-=================================================
-.loan request queue.
-=================================================
"""
def _has_loan_request_db(msisdn,conn):  

        size = 0
        amt  = 0
        try:
                sql = """
                      SELECT
                      COUNT(`id`) AS CNT,`amount`
                      FROM
                     `db_freknur_loan`.`tbl_loan_request`
                      WHERE
                     `msisdn` = %s AND `is_processed` = 0
                      """

                param = (msisdn,)

                output = db.retrieve_all_data_params(conn,sql,param)

                for data in output:
                        size = data['CNT']
                        amt  = data['amount']

        except Exception,e:
                logger.error(e)
                raise

        return [size,amt]

"""
-=================================================
-.record new loan request.
-=================================================
"""
def _registration_db(msisdn,passwd,conn):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	j_string = None
	try: 
                #-.routine call to check whether user exist.
                exist = _get_user_db(msisdn,conn)
                #-.routine call to generate unique uid.
                user_uid = _get_uid_db(conn)

                if(exist == 0):
                        sql = """
                              INSERT 
                              INTO 
                             `tbl_wallet` 
                              (`uid`,`msisdn`,`password`,`date_created`) 
                              VALUES 
                              ('%s','%s','%s','%s') 
                              ON 
                              DUPLICATE 
                              KEY UPDATE `date_modified` = '%s' """ % (user_uid,msisdn,passwd,date,date)

		        params = ()
		    
                        db.execute_query(conn, sql, params)
		            
                        j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Wallet activated successful"}

                        conn.commit()
                else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Already registered"}
	except Exception, e:
		logger.error(e)
		raise	
	
	return j_string


"""
-=================================================
-.record extra registration info.
-=================================================
"""
def _registration_extra_db(msisdn,fname,sname,dob,mail,code,conn):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
                sql = """
                      INSERT
                      INTO
                     `db_freknur_loan`.`tbl_wallet_extra`
                      (`msisdn`,`first_name`,`second_name`,`birth_date`,`mail`,`country_code`)
                      VALUES
                      ('%s','%s','%s','%s','%s','%s')
                      ON
                      DUPLICATE
                      KEY UPDATE `time_stamp` = '%s' """ % (msisdn,fname,sname,dob,mail,code,date)

                params = ()

                db.execute_query(conn, sql, params)

                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"User information has been updated."}

                conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.queue loan.
-=================================================
"""	
def _queue_loan_db(reference_no,msisdn,amount,approved_by,has_collateral,conn):
	j_string = None
	try:
		sql = """CALL """+mysql_params['db']+""".`sProcQueueLoan`(%s,%s,%s,%s,%s)"""
		params = (reference_no,msisdn,amount,approved_by,has_collateral,)
		output = db.retrieve_all_data_params(conn,sql,params)	
		
		for data in output:
			j_string = json.loads(data.get('_JSON'))
			
		#conn.commit()
	except Exception, e:
		logger.error(e)
		raise	
	
	return j_string
	
"""
-=================================================
-.queue loan.
-=================================================
"""	
def _dispatch_loan_db(reference_no,msisdn,amount,loan_amount,repayment_amount,interest_amount,loan_duration,notify_1,conn):
	j_string = None
	try:
		sql = """CALL """+mysql_params['db']+""".`sProcLoanDispatch`(%s,%s,%s,%s,%s,%s,%s,%s)"""
		params = (reference_no,msisdn,amount,loan_amount,repayment_amount,interest_amount,loan_duration,notify_1)
		output = db.retrieve_all_data_params(conn,sql,params)	
		
		for data in output:
		        j_string = json.loads(data.get('_JSON'))
			
		#conn.commit()
	except Exception, e:
		logger.error(e)
		raise	
	
	return j_string
	
"""
-=================================================
-.log book keeping transaction.
-=================================================
"""	
def _record_loan_transaction_db(amount,msisdn,reference_no,account_name,transaction_type,conn):
	j_string = None
	try:
		sql = """CALL """+mysql_params['db']+""".`sProcLogTransactions`(%s,%s,%s,%s,%s)"""
		params = (amount,msisdn,reference_no,account_name,transaction_type)
		output = db.retrieve_all_data_params(conn,sql,params)	
		
		for data in output:
			j_string = json.loads(data.get('_JSON'))
			
		#conn.commit()
	except Exception, e:
		logger.error(e)
		raise	
	
	return j_string
	
"""
-=================================================
-.log loan fee.
-=================================================
"""	
def _record_loan_fee_db(msisdn,reference_no,loan_fee,account_name,conn):
	j_string = None
	try:
		sql = """CALL """+mysql_params['db']+""".`sProcLogLoanFee`(%s,%s,%s,%s)"""
		params = (msisdn,reference_no,loan_fee,account_name)
		output = db.retrieve_all_data_params(conn,sql,params)	
		
		for data in output:
			j_string = json.loads(data.get('_JSON'))
			
		#conn.commit()
	except Exception, e:
		logger.error(e)
		raise	
	
	return j_string

"""
-=================================================
-.queued loan payout list.
-=================================================
"""
def _loan_dispatch_list_db(search,lower_min,lower_max,conn):
	is_processsed = 0
	j_string = None
	try:
		if(search == '0'):
			sql  =   """
				 SELECT 
				`reference_no`,`msisdn`,`amount`,`status`,`approved_by`,CONCAT("",`date_created`,"") AS date_created,CONCAT("",`date_modified`,"") AS date_modified
				 FROM 
				`db_freknur_general`.`tbl_loan_payout`
				 WHERE 
				`is_processed` = %s
				 ORDER BY `date_created` DESC
				 LIMIT %i, %i 
				 """ % (is_processsed,int(lower_min),int(lower_max))
		else:
			sql  =   """
				 SELECT 
				`reference_no`,`msisdn`,`amount`,`status`,`approved_by`,CONCAT("",`date_created`,"") AS date_created,CONCAT("",`date_modified`,"") AS date_modified
				 FROM 
				`db_freknur_general`.`tbl_loan_payout`
				 WHERE 
				`is_processed` = %s
				 ORDER BY `date_created` DESC
				 LIMIT %i, %i 
				 """ % (is_processsed,int(lower_min),int(lower_max))
				 
		params = ()
		
		recordset = db.retrieve_all_data_params(conn,sql,params)
		
		jsonArray = ast.literal_eval(json.dumps(recordset))
		jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})
				
	except Exception, e:
		logger.error(e)
		raise	
	
	return j_string
	
"""
-=================================================
-.get loan request list.
-=================================================
"""
def _loan_request_list_db(search,lower_min,lower_max,conn):
	is_processed  = 0
	j_string = None
	try:
		if(search == '0'):
			sql  =   """
				 SELECT 
				`reference_no`,`msisdn`,`amount`,`requested_by`,IFNULL(`task_flag`,0) AS task_flag,CONCAT("",`date_created`,"") AS date_created,
                                 CONCAT("",`date_modified`,"") AS date_modified
				 FROM 
				`tbl_loan_request`
				 WHERE 
				`is_processed` = %s 
				 ORDER BY `date_created` DESC
				 LIMIT %i, %i 
				 """ % (is_processed,int(lower_min),int(lower_max))
		else:
			sql  =   """
				 SELECT 
				`reference_no`,`msisdn`,`amount`,`requested_by`,IFNULL(`task_flag`,0) AS task_flag,CONCAT("",`date_created`,"") AS date_created,
                                 CONCAT("",`date_modified`,"") AS date_modified
				 FROM 
				`tbl_loan_request`
				 WHERE 
				`is_processed` = %s AND `msisdn` = '%s'
				 ORDER BY `date_created` DESC
				 LIMIT %i, %i 
				 """ % (is_processed,search,int(lower_min),int(lower_max))		
				 
		params = ()
		
		recordset = db.retrieve_all_data_params(conn,sql,params)
		
		jsonArray = ast.literal_eval(json.dumps(recordset))
		jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})
				
	except Exception, e:
		logger.error(e)
		raise	
	
	return j_string
	
"""
-=================================================
-.accounts log.
-=================================================	
"""	
def _get_general_account_list_db(code,search,lower_min,lower_max,conn):
	status  = 0
	j_string = None
	try:
		if(str(code) == 'GEN'):
			if(search == '0'):
				sql = """
				      SELECT 
				     `account_code`,`reference_no`,`msisdn`,`cr`,`dr`,`balance`,`narration`,CONCAT("",`date_created`,"") AS date_created
				      FROM 
				     `tbl_transaction`
				      WHERE
				     `is_archived` = %s AND `account_code` != '%s' 
				      ORDER BY 
				     `date_created` DESC
				      LIMIT %i, %i  
				      """ % (status,str(code),int(lower_min),int(lower_max))
			else:
				sql = """
				      SELECT 
				     `account_code`,`reference_no`,`msisdn`,`cr`,`dr`,`balance`,`narration`,CONCAT("",`date_created`,"") AS date_created
				      FROM 
				     `tbl_transaction`
				      WHERE
				     `is_archived` = %s AND `account_code` != '%s' AND `msisdn` = '%s'
				      ORDER BY 
				     `date_created` DESC
				      LIMIT %i, %i  
				      """ % (status,str(code),search,int(lower_min),int(lower_max))			
		elif(str(code) == 'STMT'):
			sql = """
			      SELECT 
			     'SELF' AS account_code,`reference_no`,`msisdn`,`cr`,`dr`,`balance`,`narration`,CONCAT("",`date_created`,"") AS date_created
			      FROM 
			     `tbl_wallet_transaction`
			      WHERE
			     `is_archived` = %s AND `msisdn` = '%s' 
			      ORDER BY 
			     `date_created` DESC
			      LIMIT %i, %i  
			      """ % (status,search,int(lower_min),int(lower_max))
		else:
			if(search == '0'):
				sql = """
				      SELECT 
				     `account_code`,`reference_no`,`msisdn`,`cr`,`dr`,`balance`,`narration`,CONCAT("",`date_created`,"") AS date_created
				      FROM 
				     `tbl_transaction`
			              WHERE
				     `is_archived` = %s AND `account_code` = '%s'
				      ORDER BY 
				     `date_created` DESC
				      LIMIT %i, %i  
				      """ % (status,str(code),int(lower_min),int(lower_max))
			else:
				sql = """
				      SELECT 
				     `account_code`,`reference_no`,`msisdn`,`cr`,`dr`,`balance`,`narration`,CONCAT("",`date_created`,"") AS date_created
				      FROM 
				     `tbl_transaction`
				      WHERE
				     `is_archived` = %s AND `account_code` = '%s' AND `msisdn` = '%s'
				      ORDER BY 
				     `date_created` DESC
				      LIMIT %i, %i  
				      """ % (status,str(code),search,int(lower_min),int(lower_max))			
			  
		params = ()
	
		recordset = db.retrieve_all_data_params(conn,sql,params)
		
		jsonArray = ast.literal_eval(json.dumps(recordset,default=decimal_default))
		jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)},default=decimal_default)
	
	except Exception,e:
		logger.error(e)
		raise
	
	return j_string


"""
-=================================================
-.activity log.
-=================================================
"""
def _get_activity_log_db(search,lower_min,lower_max,conn):
        j_string = None
        try:
                if(search == '0'):
                        sql = """
                              SELECT 
                             `_id`,`msisdn`,`activity`,CONCAT("",`time_stamp`,"") AS time_stamp,`flag`
                              FROM
                             `db_freknur_general`.`tbl_activity_log`
                              WHERE
                             `flag` = 0
                              ORDER BY 
                             `time_stamp` DESC
                              LIMIT %i, %i 
                              """ % (int(lower_min),int(lower_max))
                else:
                        sql = """
                              SELECT 
                             `_id`,`msisdn`,`activity`,CONCAT("",`time_stamp`,"") AS time_stamp,`flag`
                              FROM
                             `db_freknur_general`.`tbl_activity_log`
                              WHERE
                             `flag` = 0 AND `msisdn` = '%s'
                              ORDER BY 
                             `time_stamp` DESC
                              LIMIT %i, %i 
                              """ % (search,int(lower_min),int(lower_max))                    

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                jsonArray = ast.literal_eval(json.dumps(recordset))
                jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})

        except Exception,e:
                logger.error(e)
                raise

        return j_string
    
"""
-=================================================
-.debtor list.
-=================================================	
"""	
def _get_debtor_list_db(search,lower_min,lower_max,conn):
	status  = 0
	j_string = None
	try:
		if(search == '0'):
			sql = """
			      SELECT 
			     `id`,`reference_no`,`msisdn`,`amount_requested`,`amount_disbursed`,`repayment_amount`,CONCAT("",`repayment_date`,"") AS repayment_date,
                              CONCAT("",`date_created`,"") AS date_created
			      FROM 
			     `tbl_debtor`
			      WHERE
			     `is_archived` = %s AND `is_repaid` = 0 
			      ORDER BY
			     `date_created` DESC
			      LIMIT %i, %i  
			      """ % (status,int(lower_min),int(lower_max))
		else:
			sql = """
			      SELECT 
			     `id`,`reference_no`,`msisdn`,`amount_requested`,`amount_disbursed`,`repayment_amount`,CONCAT("",`repayment_date`,"") AS repayment_date,
                              CONCAT("",`date_created`,"") AS date_created
			      FROM 
			     `tbl_debtor`
			      WHERE
			     `is_archived` = %s AND `msisdn` = '%s' AND AND `is_repaid` = 0 
			      ORDER BY 
			     `date_created` DESC
			      LIMIT %i, %i  
			      """ % (status,search,int(lower_min),int(lower_max))
			  
		params = ()
	
		recordset = db.retrieve_all_data_params(conn,sql,params)
		
		jsonArray = ast.literal_eval(json.dumps(recordset))
		jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})
	
	except Exception,e:
		logger.error(e)
		raise
	
	return j_string

"""
-=================================================
-.defaulter list.
-=================================================	
"""	
def _get_defaulter_list_db(search,lower_min,lower_max,conn):
	status  = 0
	j_string = None
	try:
		if(search == '0'):
			sql = """
			      SELECT 
			     `id`,`msisdn`,`loan_amount`,`amount_repaid`,CONCAT("",`expected_repayment_date`,"") AS repayment_date,
                              (CASE WHEN (`date_repaid` IS NULL) THEN 'Loan outstanding' ELSE CONCAT("",`date_repaid`,"") END) AS date_repaid,
                             `roll_count`,CONCAT("",`date_created`,"") AS date_created
			      FROM 
			     `db_freknur_general`.`tbl_defaulter`
			      WHERE
			     `is_archived` = %s
			      LIMIT %i, %i  
			      """ % (status,int(lower_min),int(lower_max))
		else:
			sql = """
			      SELECT 
			     `id`,`msisdn`,`loan_amount`,`amount_repaid`,CONCAT("",`expected_repayment_date`,"") AS repayment_date,
                              (CASE WHEN (`date_repaid` IS NULL) THEN 'Loan outstanding' ELSE CONCAT("",`date_repaid`,"") END) AS date_repaid,
                             `roll_count`,CONCAT("",`date_created`,"") AS date_created
			      FROM 
			     `db_freknur_general`.`tbl_defaulter`
			      WHERE
			     `is_archived` = %s AND `msisdn` = '%s'
			      LIMIT %i, %i  
			      """ % (status,search,int(lower_min),int(lower_max))
				  
		params = ()
	
		recordset = db.retrieve_all_data_params(conn,sql,params)
		
		jsonArray = ast.literal_eval(json.dumps(recordset))
		jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})
	
	except Exception,e:
		logger.error(e)
		raise
	
	return j_string

"""
-=================================================
-.account summary.
-=================================================	
"""	
def _get_account_summary_db(lower_min,lower_max,conn):
	status  = 0
	j_string = None
	try:
		sql = """
		      SELECT 
		     `id`,`account_code`,`account_name`,`balance`,CONCAT("",`date_created`,"") AS date_created
		      FROM 
		     `tbl_account`
		      LIMIT %i, %i  
		      """ % (int(lower_min),int(lower_max))
			  
		params = ()
	
		recordset = db.retrieve_all_data_params(conn,sql,params)
		
		jsonArray = ast.literal_eval(json.dumps(recordset))
		jsonArraySize = len(jsonArray)
		
		j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})
	
	except Exception,e:
		logger.error(e)
		raise
	
	return j_string


"""
-=================================================
-.user exist?
-=================================================
"""
def _get_user_db(msisdn,conn):
        size = 0
        try:
                sql = """
                      SELECT
                      COUNT(`id`) AS CNT
                      FROM
                     `db_freknur_loan`.`tbl_wallet`
                      WHERE
                     `msisdn` = %s 
                      """

                param = (msisdn,)

                output = db.retrieve_all_data_params(conn,sql,param)

                for data in output:
                        size = data['CNT']

        except Exception,e:
                logger.error(e)
                raise

        return size


"""
-=================================================
-.user suspended?
-=================================================
"""
def _is_wallet_suspended_db(msisdn,conn):
        size = 0
        try:
                sql = """
                      SELECT
                      COUNT(`id`) AS CNT
                      FROM
                     `db_freknur_loan`.`tbl_wallet`
                      WHERE
                     `msisdn` = %s AND `is_suspended` = '1'
                      """

                param = (msisdn,)

                output = db.retrieve_all_data_params(conn,sql,param)

                for data in output:
                        size = data['CNT']

        except Exception,e:
                logger.error(e)
                raise

        return size

"""
-=================================================
-.existing loan?
-=================================================
"""
def _get_has_loan_db(msisdn,conn):
        has_loan = 0
        try:
                sql = """
                      SELECT
                      COUNT(`msisdn`) AS CNT
                      FROM
                     `db_freknur_general`.`tbl_loan_temp_list`
                      WHERE
                     `msisdn` = %s
                      """

                param = (msisdn,)

                output = db.retrieve_all_data_params(conn,sql,param)

                for data in output:
                        has_loan = data['CNT']

        except Exception,e:
                logger.error(e)
                raise

        return has_loan

"""
-=================================================
-.generate loan uid.
-=================================================
"""
def _get_loan_uid_db(conn):
        loan_uid = 0
        j_string = None
        try:
                sql = """
                      SELECT 
                      CONCAT(CHAR(ROUND(RAND()*25)+97),
                      CHAR(ROUND(RAND()*25)+97),
                      ROUND((RAND()*9)),
                      CHAR(ROUND(RAND()*25)+97),
                      CHAR(ROUND(RAND()*25)+97),
                      CHAR(ROUND(RAND()*25)+97),
                      ROUND((RAND()*9)),
                      CHAR(ROUND(RAND()*25)+97),
                      CHAR(ROUND(RAND()*25)+97),
                      CHAR(ROUND(RAND()*25)+97)) AS loan_uid
                      FROM 
                      dual
                      """
                params = ()
                output = db.retrieve_all_data_params(conn,sql,params)

                for data in output:
                        loan_uid = 'LNR-'+data['loan_uid']

                conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return loan_uid

"""
-=================================================
-.get unique uid.
-=================================================
"""
def _get_uid_db(conn):
        db_uid = 0
        j_string = None
        try:
                sql = """
                      SELECT 
                      uuid_short() AS db_uid
                      FROM 
                      dual
                      """
                params = ()
                output = db.retrieve_all_data_params(conn,sql,params)

                for data in output:
                        db_uid = data['db_uid']

                conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return db_uid

"""
-=================================================
-.method: screen a loan request.
-=================================================
"""	
def _vet_loan_request_db(reference_no,msisdn,approved_by,remarks,head,conn):
	task_flag = 2
	date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	j_string = None
	try:
                if(str(head) == 'approval_operation'):
                        #-.routine call.
                        available = _get_loan_ref_no_db(reference_no,conn)

                        if(available == 1):
	                        sql = """
		                      UPDATE 
		                     `db_freknur_loan`.`tbl_loan_request` 
		                      SET  
		                     `task_flag` = %s, 
		                     `approved_by` = '%s',
		                     `date_modified` = '%s'
		                      WHERE 
		                     `reference_no` = '%s' AND `msisdn` = '%s' AND `is_processed` = '0'
		                      """ % (task_flag,approved_by,date,reference_no,msisdn)

	                        params = ()

		                db.execute_query(conn, sql, params)
		
                                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Loan approval successful."}
		
	                        conn.commit()
                        else:
                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Action cannot be completed."}
                else:
                        amount = "0"
                        #-.routine call.
                        _record_rejected_loan_request_db(msisdn,remarks,conn)
	except Exception, e:
		logger.error(e)
		raise

	return j_string

"""
-=================================================
-.log rejected loans.
-=================================================
"""
def _record_rejected_loan_request_db(msisdn,remarks,conn):

        j_string = None
        try:
                sql = """CALL """+mysql_params['db']+""".`sProcLogRejectedLoanRequest`(%s,%s)"""
                params = (msisdn,remarks,)
                output = db.retrieve_all_data_params(conn,sql,params)
                for data in output:
                        j_string = json.loads(data.get('_JSON'))

                #conn.commit()
        except Exception, e:
            logger.error(e)
            raise

        return j_string

"""
-=================================================
-.delete loan approval & processed log.
-=================================================
"""
def _del_loan_approved_processed_log(conn):
        try:
                sql = """
                      DELETE
                      FROM
                     `db_freknur_loan`.`tbl_loan_request`
                      WHERE
                     `task_flag` = 2 AND `is_processed` = 1
                      """

                params = ()
                
                db.execute_query(conn, sql, params)
                
                conn.commit()
        except Exception, e:
                logger.error(e)
                raise

"""
-=================================================
-.loan approval operation.
-=================================================	
"""	
def _get_loan_request_db(conn,limit=1000):
	is_processed = 0
	task_flag = 2
	j_string = None
	try:
		sql = """
		      SELECT 
		     `id`,`msisdn`,`reference_no`,`amount`,`collateral_percentage`,`approved_by`,CONCAT("'",`date_created`,"'") AS date_created,`has_collateral`
		      FROM 
		     `db_freknur_loan`.`tbl_loan_request`
		      WHERE
		     `is_processed` = %s AND `task_flag` = %s
		      LIMIT %s		  
		      """
			  
		params = (is_processed,task_flag,limit)
	
		recordset = db.retrieve_all_data_params(conn,sql,params)
		
		j_string = json.dumps(recordset)
	
	except Exception,e:
		logger.error(e)
		raise
	
	return j_string
	
"""
-=================================================
-.loan approval operation.
-=================================================	
"""	
def _get_loan_payout_db(conn,limit=1000):
	is_processed = 0
	status  = 0
	j_string = None
	try:
		sql = """
		      SELECT 
		     `id`,`reference_no`,`msisdn`,`amount`,`has_collateral`
		      FROM 
		     `db_freknur_general`.`tbl_loan_payout`
		      WHERE
		     `is_processed` = %s AND `status` = %s
		      LIMIT %s		  
		      """
			  
		params = (is_processed,status,limit)
	
		recordset = db.retrieve_all_data_params(conn,sql,params)
		
		j_string = json.dumps(recordset)
	
	except Exception,e:
		logger.error(e)
		raise
	
	return j_string	
			
"""
-=================================================
-.mark load as queued.
-=================================================	
"""	
def _mark_loan_request_processed_db(_id,msisdn,ref_no,conn):
	processed = 0
	is_processed = 1
	task_flag = 2
	j_string = None
	date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	try:
		sql = """
		      UPDATE
		     `db_freknur_loan`.`tbl_loan_request`
		      SET
		     `is_processed` = %s,
		     `date_modified` = '%s',
		     `task_flag` = %s
		      WHERE
		     `is_processed` = %s AND `id` = %s AND `msisdn` = '%s' AND `reference_no` = '%s'	  
		      """ % (processed,date,task_flag,is_processed,_id,msisdn,ref_no)
		
		params = ()
	
		db.execute_query(conn, sql, params)
		
                j_string = {"RESULT":"SUCCESS","MESSAGE":"Approval complete."}
		
		conn.commit()
	
	except Exception,e:
		logger.error(e)
		raise
	
	return j_string
	
"""
-=================================================
-.get customer statement.
-=================================================	
"""	
def _get_comprehensive_wallet_statement_db(msisdn,conn,limit=500):
	status  = 0
	j_string = None
	try:
		sql = """
		      SELECT 
		     `reference_no` AS Receipt_No,CONCAT("",`date_created`,"") AS Transaction_Date,`narration` AS Details,`cr` AS CR,`dr` AS DR,`balance` AS Balance
		      FROM 
		     `tbl_wallet_transaction`
		      WHERE
		     `is_archived` = %s AND `msisdn` = %s
                      ORDER BY `date_created` DESC
		      LIMIT %s		  
		      """
			  
		params = (status,msisdn,limit)
	
		recordset = db.retrieve_all_data_params(conn,sql,params)
             
                if(len(recordset) == 0):
                        j_string = json.dumps({"ERROR":"1","RESULT":"FAIL","DATA":recordset,"MESSAGE":"No statement"})
                else:
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"User has a statement"},default=decimal_default)
	
	except Exception,e:
		logger.error(e)
		raise
	
	return j_string


"""
-=================================================
-.get mini loan statement.
-=================================================
"""
def _get_mini_loan_statement_db(msisdn,conn,limit=500):
        status  = 0
        j_string = None
        search_1 = 'LNR-%'
        search_2 = 'LNRE-%'
        try:
                sql = """
                      SELECT
                     `reference_no` AS Receipt_No,CONCAT("",`date_created`,"") AS Transaction_Date,`narration` AS Details,`cr` AS CR,`dr` AS DR,`balance` AS Balance
                      FROM
                     `tbl_wallet_transaction`
                      WHERE
                      (`reference_no` LIKE %s OR `reference_no` LIKE %s) AND `is_archived` = %s AND `msisdn` = %s
                      ORDER BY `date_created` DESC
                      LIMIT %s
                      """

                params = (("%%" + search_1 + "%%"),("%%" + search_2 + "%%"),status,msisdn,limit)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                if(len(recordset) == 0):
                        j_string = json.dumps({"ERROR":"1","RESULT":"FAIL","DATA":recordset,"MESSAGE":"No statement"})
                else:
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"User has a loan mini statement"},default=decimal_default)

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get mini asset statement.
-=================================================
"""
def _get_mini_asset_statement_db(msisdn,conn,limit=500):
        status  = 0
        j_string = None
        search_1 = 'GRN%'
        search_2 = 'BID%'
        try:
                sql = """
                      SELECT
                     `reference_no` AS Receipt_No,CONCAT("",`date_created`,"") AS Transaction_Date,`narration` AS Details,`cr` AS CR,`dr` AS DR,`balance` AS Balance
                      FROM
                     `tbl_wallet_transaction`
                      WHERE
                      (`reference_no` LIKE %s OR `reference_no` LIKE %s) AND `is_archived` = %s AND `msisdn` = %s
                      ORDER BY `date_created` DESC
                      LIMIT %s
                      """

                params = (("%%" + search_1 + "%%"),("%%" + search_2 + "%%"),status,msisdn,limit)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                if(len(recordset) == 0):
                        j_string = json.dumps({"ERROR":"1","RESULT":"FAIL","DATA":recordset,"MESSAGE":"No statement"})
                else:
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"User has an asset mini statement"},default=decimal_default)

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.withdraw routine.
-=================================================	
"""	
def _withdraw_electronic_cash_db(msisdn,amount,conn):
	j_string = None
	try:      
                #-.routine call.
		balance,reference = _get_customer_bal_db(msisdn,conn)
                #-.redis conn.
                rd = create_redis_connection()

                if(int(float(balance)) >= int(amount)):
                        #-.routine call.
                        _record_cashout_transaction(amount,msisdn,conn)
                        #-.routine call.
                        result = _log_requested_cashout(msisdn,amount,reference,conn)
                        #-.get keys.
                        key = redis_access_key()[0]+str(msisdn)
                        #-.reset cache.
                        _delete_from_redis_cache(key,rd)

                        if(result is not None):
                                j_string = _update_wallet_balance(msisdn,amount,conn)
		else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Insufficient Balance:."}
	except Exception, e:
		logger.error(e)
		raise	
	
	return j_string

"""
-=================================================
-.deposit routine.
-=================================================
"""
def _wallet_deposit_db(amount,msisdn,conn):

        j_string = {"ERROR":"0","RESULT":"SUCESS","MESSAGE":"Under construction"}


        return j_string

"""
-=================================================
-.get user wallet bal.
-=================================================
"""
def _get_customer_bal_db(msisdn,conn):
        balance   = 0.00
        reference = 0
        try:
                sql = """
                      SELECT
                      IFNULL(`balance`,'0') AS balance,IFNULL(`reference_no`,'0') AS reference_no
                      FROM
                     `tbl_wallet`
                      WHERE
                     `is_active` = '1' AND `is_suspended` = '0'	AND `msisdn` = '%s'
                      """ % (msisdn)

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for data in recordset:
                        balance   = data['balance']
                        reference = data['reference_no']

        except Exception,e:
                logger.error(e)
                raise

        return balance, reference

"""
-=================================================
-.log cashout activiity
-=================================================
"""
def _log_requested_cashout(msisdn,amount,reference,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
                sql = """
                      INSERT 
                      INTO
                     `db_freknur_general`.`tbl_mpesa_receipt`
                      (`msisdn`,`amount`,`reference_no`,`date_created`)
                      VALUES
                      ('%s','%s','%s','%s')
                      ON 
                      DUPLICATE KEY
                      UPDATE `date_created` = '%s'     
                      """ % (msisdn,amount,reference,date,date)

                params = ()

                db.execute_query(conn, sql, params)

                j_string = {"RESULT":"SUCCESS","MESSAGE":"Approval complete."}

                conn.commit()

        except Exception,e:
                logger.error(e)
                raise
        
        return j_string
  
"""
-=================================================
-.log cashout transaction.
-=================================================
"""
def _record_cashout_transaction(amount,msisdn,conn):

        j_string = None
        try:
                sql = """CALL """+mysql_params['db']+""".`sProcWithdrawECash`(%s,%s)"""
                params = (amount,msisdn,)
                output = db.retrieve_all_data_params(conn,sql,params)
                for data in output:
                        j_string = json.loads(data.get('_JSON'))

                #conn.commit()
        except Exception, e:
            logger.error(e)
            raise

        return j_string

"""
-=================================================
-.withdraw operation.
-=================================================
"""
def _update_wallet_balance(msisdn,amount,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
                sql = """
                      UPDATE
                     `tbl_wallet`
                      SET
                     `balance` = (`balance` - '%s'),`date_modified` = '%s' 
                      WHERE 
                     `is_active` = '1' AND `is_suspended` = '0' AND `msisdn` = '%s'
                      """ % (amount,date,msisdn)

                params = ()

                db.execute_query(conn, sql, params)

                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Withdraw complete, patiently wait for the cash to be credited to your mobile wallet."}

                conn.commit()

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get loan reference.
-=================================================
"""
def _get_loan_ref_no_db(reference,conn):
        exist = 0
        try:
                sql = """
                      SELECT
                      COUNT(`msisdn`) AS CNT
                      FROM
                     `db_freknur_loan`.`tbl_loan_request`
                      WHERE
                     `reference_no` = %s AND `is_processed` = '0'
                      """

                param = (reference,)

                output = db.retrieve_all_data_params(conn,sql,param)

                for data in output:
                        exist = data['CNT']

        except Exception,e:
                logger.error(e)
                raise

        return exist

"""
-=================================================
-.loan arrear amount.
-=================================================	
"""	
def _get_loan_arrears_db(msisdn,conn):
	loan_amount = 0.00
	try:
		sql = """
		      SELECT 
                     `msisdn`,`loan_amount`
                      FROM
		     `db_freknur_general`.`tbl_loan_temp_list`
		      WHERE
		     `msisdn` = %s		  
		      """
			  
		params = (msisdn,)
	
		output = db.retrieve_all_data_params(conn,sql,params) 
		
		for data in output:
		        loan_amount = data['loan_amount']	
	
	except Exception,e:
		logger.error(e)
		raise
	
	return loan_amount

"""
-=================================================
-.payment queue.
-=================================================
"""
def _get_payment_list_db(conn,limit=1000):
	j_string = None
	try:
		sql = """
		      SELECT
		     `id`,`msisdn`,`amount`,`transaction_no`
		      FROM
		     `db_freknur_general`.`tbl_loan_repayment`
		      WHERE
		     `is_processed` = 0
		      LIMIT %s
		      """
		params = (limit,)

		recordset = db.retrieve_all_data_params(conn,sql,params)

		j_string = json.dumps(recordset)

	except Exception,e:
		logger.error(e)
		raise

	return j_string

"""
-=================================================
-.handle loan payment.
-=================================================
"""
def _loan_payment_db(msisdn,amount,transaction_no,conn):
	j_string = None
	try:
		sql = """CALL """+mysql_params['db']+""".`sProcLoanRepayment`(%s,%s,%s)"""
		params = (msisdn,amount,transaction_no,)
		output = db.retrieve_all_data_params(conn,sql,params)
		for data in output:
			j_string = json.loads(data.get('_JSON'))

		#conn.commit()
	except Exception, e:
            logger.error(e)
	    raise

	return j_string

"""
-=================================================
-. wallet cashoutt.
-=================================================
"""
def _wallet_cashout_to_settle_db(amount,msisdn,trx_type,conn):
        j_string = None
        try:
                sql = """CALL """+mysql_params['db']+""".`sProcWalletCashOutForSettlement`(%s,%s,%s)"""
                params = (amount,msisdn,trx_type,)
                output = db.retrieve_all_data_params(conn,sql,params)
                for data in output:
                        j_string = json.loads(data.get('_JSON'))

                #conn.commit()
        except Exception, e:
            logger.error(e)
            raise

        return j_string

"""
-=================================================
-.TEST PAYMENT.
-=================================================      
"""
def _PAYMENT_TEST_db(trx,amount,msisdn,conn):
        j_string = None
        trx_type = 0
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #-.routine call.
        payment_exist = _payment_queue_db(msisdn,conn)
        #-.routine call.
        user_exist = _get_user_db(msisdn,conn)
        #-.routine call.
        has_loan = _get_has_loan_db(msisdn,conn)
        bal,ref = _get_customer_bal_db(msisdn,conn)

        if(int(user_exist) == 1):
                if(int(has_loan) == 1):
                        if(int(payment_exist) == 0):
                                if(float(bal) >= float(amount)):
                                        result = _wallet_cashout_to_settle_db(amount,msisdn,trx_type,conn)
                                        if(result['ERROR'] == "0"):
                                                try:
                                                        sql = """
                                                              INSERT
                                                              INTO
                                                             `db_freknur_general`.`tbl_loan_repayment`
                                                              (`msisdn`,`amount`,`transaction_no`,`date_created`)
                                                              VALUES
                                                              ('%s','%s','%s','%s')      
                                                              ON DUPLICATE KEY
                                                              UPDATE `date_modified` = NOW()
                                                              """ % (msisdn,amount,trx,date)

                                                        params = ()

                                                        db.execute_query(conn, sql, params)

                                                        j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Payment received."}

                                                        conn.commit()
                                                except Exception,e:
                                                        logger.error(e)
                                                        raise
                                        else:
                                                j_string = result
                                else:
                                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have a pending payment awaiting processing. Please wait and try later."}
                        else:
                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have a pending payment awaiting processing. Please wait and try later."}
                else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Payment refused. you do not have a loan."}
        else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Payment refused. User does not exist"}

        return j_string

"""
-=================================================
-.size of payment queue.
-=================================================
"""
def _payment_queue_db(msisdn,conn):
        cnt=0
        try:
                sql = """
                      SELECT
                      COUNT(`id`) AS cnt
                      FROM 
                     `db_freknur_general`.`tbl_loan_repayment`
                      WHERE 
                     `msisdn` = '%s' AND `is_processed` = 0
                      """ %  (msisdn)

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for record in recordset:
                        cnt = record['cnt']

        except Exception,e:
                logger.error(e)
                raise

        return cnt
"""
-=================================================
-.record user activity log.
-=================================================
"""
def _acitivity_log_db(msisdn,activity_description,conn):
        j_string = None
        try:
                #-.routine call to check whether user exist.
                exist = _get_user_db(msisdn,conn)
            
                if(exist == 1):
                        sql = """
                              INSERT 
                              INTO 
                             `db_freknur_general`.`tbl_activity_log` 
                              (`msisdn`,`activity`) 
                              VALUES 
                              ('%s','%s') 
                              """ % (msisdn,activity_description)

                        params = ()

                        db.execute_query(conn, sql, params)

                        j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Activity logged successful"}

                        conn.commit()
                else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Not a registered user"}
        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.loan due list.
-=================================================
"""
def _loan_due_list_db(conn,limit=1000):
	j_string = None
	try:
		sql = """
		      SELECT
		     `id`,
		      TIMESTAMPDIFF(SECOND,`next_notification_date`,NOW()) AS diff,
		     `notification_count`,
		     `msisdn`,
		     `repayment_amount`,
		      CONCAT("'",`expected_repayment_date`,"'") AS expected_repayment_date
		      FROM
		     `tbl_debtor`
		      WHERE
		     `is_repaid` = 0 AND `is_archived` = 0
		      LIMIT %s
		      """
		params = (limit,)

		recordset = db.retrieve_all_data_params(conn,sql,params)

		j_string = json.dumps(recordset)

	except Exception,e:
		logger.error(e)
		raise

	return j_string

"""
-=================================================
-.handle loan due alert.
-=================================================	
"""
def _loan_due_alert_handler_db(recid,seconds,notification_cnt,hr,msisdn,amount,expected_payment_date,conn):
	j_string = None
	try:
		sql = """CALL """+mysql_params['db']+""".`sProcHandleLoanNotification`(%s,%s,%s,%s,%s,%s,%s)"""
		params = (recid,seconds,notification_cnt,hr,msisdn,amount,expected_payment_date,)
		output = db.retrieve_all_data_params(conn,sql,params)

		for data in output:
			jsString = json.loads(data.get('_JSON'))
			
		#conn.commit()
	except Exception, e:
		logger.error(e)
		raise	
		
	return j_string	

"""
-=================================================
-.defaulter list.
-=================================================
"""
def _defaulter_list_db(conn,limit=1000):
	j_string = None
	try:
		sql = """
		      SELECT
		      (`loan_amount`-`amount_repaid`) AS principle,
		     `msisdn`,
		     `roll_count`
		      FROM
		     `db_freknur_general`.`tbl_defaulter`
		      WHERE
		     `date_repaid` is NULL  AND `is_archived` = 0 AND TIMESTAMPDIFF(MINUTE,`notification_date`,NOW()) >= 0
		      LIMIT %s
		      """
		params = (limit,)

		recordset = db.retrieve_all_data_params(conn,sql,params)

		j_string = json.dumps(recordset)

	except Exception,e:
		logger.error(e)
		raise

	return j_string

"""
-=================================================
-.calc penalty.
-=================================================
"""
def _calc_loan_penalty_db(amount,loan_duration,rate,msisdn,conn):
	j_string = None
	try:
		sql = """CALL """+mysql_params['db']+""".`sProcHandleSimpleInterestCalc`(%s,%s,%s,%s)"""
		params = (amount,loan_duration,rate,msisdn,)
		output = db.retrieve_all_data_params(conn,sql,params)

		for data in output:
			jsString = json.loads(data.get('_JSON'))

		#conn.commit()
	except Exception, e:
		logger.error(e)
		raise

	return j_string

"""
-=================================================
-.defaulter.
-=================================================
"""
def _flag_as_defaulter_db(recid,msisdn,loan_amount,expected_pay_day,duration,conn):
        j_string = None
        try:
                sql = """CALL """+mysql_params['db']+""".`sProcFlagLoaneeAsDefaulter`(%s,%s,%s,%s,%s)"""
                params = (recid,msisdn,loan_amount,expected_pay_day,duration,)
                output = db.retrieve_all_data_params(conn,sql,params)

                for data in output:
                        jsString = json.loads(data.get('_JSON'))

                #conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.log dipatched loan into a lookup table.
-=================================================
"""
def _log_dispatched_loan_db(msisdn,repayment_amount,interest,conn):
        j_string = None
        try:
                sql = """
                      INSERT 
                      INTO 
                     `db_freknur_general`.`tbl_loan_temp_list` 
                      (`msisdn`,`loan_amount`,`interest`) 
                      VALUES 
                      ('%s','%s','%s') 
                      """ % (msisdn,repayment_amount,interest)

                params = ()

                db.execute_query(conn,sql,params)

                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"loan loaned"}

                conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return j_string  


"""
-=================================================
-.delete loan log  from a lookup table.
-=================================================
"""
def _delete_dispatched_loan_log_db(msisdn,conn):
        j_string = None
        try:
                sql = """
                      DELETE
                      FROM
                     `db_freknur_general`.`tbl_loan_temp_list`
                     `msisdn` = %s
                      """ % (msisdn)

                params = ()

                db.execute_query(conn,sql,params)

                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"loan log deleted"}

                conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get action from tbl_temp.
-=================================================
"""
def _get_action_on_temp_db(conn,limit=1000):
        j_string = None
        try:
                sql = """
                      SELECT
                     `_id`, 
                     `_action`
                      FROM
                     `db_freknur_general`.`tbl_temp`
                      LIMIT %s
                      """

                params = (limit,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                j_string = json.dumps(recordset)

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.delete actions.
-=================================================
"""
def _delete_action_on_temp_db(msisdn,conn):
        j_string = None
        try:
                sql = """
                      DELETE
                      FROM
                     `db_freknur_general`.`tbl_temp`
                      WHERE
                     `_action` = %s
                      """ % (msisdn)

                params = ()

                db.execute_query(conn,sql,params)

                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"loan log deleted"}

                conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return j_string

#============================================================================================================
#------------------------------------FREKNUR INVESTMENT.
#============================================================================================================
"""
-=================================================
-.get config params.
-=================================================
"""
def _get_asset_config_params_db(conn):
        j_string = None
        try:
                sql = """
                      SELECT
                     `trx_fee` AS fee,`min_limit`,`max_limit`,`currency`
                      FROM 
                     `db_freknur_investment`.`tbl_config` 
                      """
                params = ()

                
                recordset = db.retrieve_all_data_params(conn,sql,params)
                
                if(len(recordset) == 0):
                        j_string = json.dumps({"ERROR":"1","RESULT":"FAIL","DATA":recordset,"MESSAGE":"No configs has been setup."})
                else:
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"System configs found."})
                
        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get customer asset portfolio.
-=================================================
"""  
def _get_customer_portfolio_db(msisdn,conn,limit=1000):
        j_string = None
        cnt = _get_size_customer_porfolio_temp_db(msisdn,conn)
        try:
                if(int(cnt) == 0):
                        sql = """
                              SELECT
                             `msisdn`,`asset_id` AS uid,`asset_acronym` AS name,`number_of_asset`,(SELECT `unit_price` FROM `db_freknur_investment`.`tbl_asset` WHERE `uid` = asset_id) AS unit_price,'0' AS has_secured_loan,CONCAT("",`date_created`,"") AS purchase_date 
                              FROM 
                             `db_freknur_investment`.`tbl_owner_portfolio` 
                              WHERE 
                             `msisdn` = %s AND `lock` = 0             
                              LIMIT %s
                              """
                else:
                        sql = """
                              SELECT
                             `msisdn`,`asset_id` AS uid,`asset_acronym` AS name,`number_of_asset`,(SELECT `unit_price` FROM `db_freknur_investment`.`tbl_asset` WHERE `uid` = asset_id) AS unit_price,'1' AS has_secured_loan,CONCAT("",`date_created`,"") AS purchase_date 
                              FROM 
                             `db_freknur_investment`.`tbl_owner_portfolio_temp_list`` 
                              WHERE 
                             `msisdn` = %s AND `lock` = 0             
                              LIMIT %s
                              """
                params = (msisdn,limit,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                if(len(recordset) == 0):
                        j_string = json.dumps({"ERROR":"1","RESULT":"FAIL","DATA":recordset,"MESSAGE":"User has no investments"},default=decimal_default)
                else:
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"User has investments"},default=decimal_default)

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get size customer asset portfolio temp.
-=================================================
"""
def _get_porfolio_temp_size_db(msisdn,conn):
        cnt = 0
        try:
                sql = """
                      SELECT
                      COUNT(`msisdn`) AS cnt
                      FROM 
                     `db_freknur_investment`.`tbl_owner_portfolio_temp_list` 
                      WHERE 
                     `msisdn` = %s AND `lock` = 0             
                      """
                params = (msisdn,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for record in recordset:
                        cnt = record['cnt'] 

        except Exception,e:
                logger.error(e)
                raise

        return cnt

"""
-=================================================
-.get asset details.
-=================================================
"""
def _get_asset_owner_db(msisdn,asset_uid,conn):
        uid=0
        qty=0
        try:
                sql = """
                      SELECT
                     `asset_id`,`number_of_asset`
                      FROM 
                     `db_freknur_investment`.`tbl_owner_portfolio` 
                      WHERE 
                     `msisdn` = %s AND `asset_id` = %s AND `lock` = 0
                      """
                params = (msisdn,asset_uid,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for record in recordset:
                        uid = record['asset_id']
                        qty = record['number_of_asset']

        except Exception,e:
                logger.error(e)
                raise

        return [qty,uid]

"""
-=================================================
-.get client asset worth.
-=================================================
"""
def _get_client_porfolio_worth_db(msisdn,conn):
        total=0
        try:
                sql = """
                      SELECT SUM(`number_of_asset` * (SELECT `unit_price` FROM `db_freknur_investment`.`tbl_asset` WHERE `uid` = `asset_id`)) AS total
                      FROM
                     `db_freknur_investment`.`tbl_owner_portfolio`
                      WHERE
                     `msisdn` = %s AND `lock` = 0
                      """
                params = (msisdn,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for record in recordset:
                        total = record['total']

        except Exception,e:
                logger.error(e)
                raise

        return total
        
"""
-=================================================
-.asset list.
-=================================================
"""
def _get_asset_list_db(lower_min,lower_max,conn):
        status  = 0
        j_string = None
        try:
                sql = """
                      SELECT
                     `_id`,`uid`,`asset_acronym`,`asset_name`,`unit_price`,CONCAT("",`total`,"") AS total,`asset_trend`,CONCAT("",`date_created`,"") AS date_created,CONCAT("",`date_modified`,"") AS date_modified
                      FROM
                     `db_freknur_investment`.`tbl_asset`
                      LIMIT %i, %i
                      """ % (int(lower_min),int(lower_max))

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                jsonArray = ast.literal_eval(json.dumps(recordset))
                jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.customer list.
-=================================================
"""
def _get_customer_list_db(search,lower_min,lower_max,conn):
        status  = 0
        j_string = None
        try:
                if(search == '0'):
                        sql = """
                              SELECT
                             `_id`,`msisdn`,`first_name`,`second_name`,`birth_date`,`mail`,`country_code`,CONCAT("",`time_stamp`,"") AS time_stamp
                              FROM
                             `db_freknur_loan`.`tbl_wallet_extra`
                              LIMIT %i, %i
                              """ % (int(lower_min),int(lower_max))
                else:
                        sql = """
                              SELECT
                             `_id`,`msisdn`,`first_name`,`second_name`,`birth_date`,`mail`,`country_code`,CONCAT("",`time_stamp`,"") AS time_stamp
                              FROM
                             `db_freknur_loan`.`tbl_wallet_extra`
                              WHERE
                             `msisdn` = '%s' 
                              LIMIT %i, %i
                              """ % (search,int(lower_min),int(lower_max))

                params = ()
                recordset = db.retrieve_all_data_params(conn,sql,params)

                jsonArray = ast.literal_eval(json.dumps(recordset))
                jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get asset details.
-=================================================
"""
def _get_asset_master_db(asset_uid,conn):
        qty=0
        price=0
        try:
                sql = """
                      SELECT
                     `uid`,`asset_acronym`,`asset_name`,`unit_price`,`total`
                      FROM
                     `db_freknur_investment`.`tbl_asset`
                      WHERE
                     `uid` = %s AND (`is_suspended` = 0 OR `is_deleted` = 0)
                      """
                params = (asset_uid,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for record in recordset:
                        qty   = record['total']
                        price = record['unit_price']

        except Exception,e:
                logger.error(e)
                raise

        return [price,qty]

"""
-=================================================
-.asset tread list.
-=================================================
"""
def _get_asset_trend_list_db(msisdn,conn):
        status  = 0
        j_string = None
        #-.routine call.
        fee,lower,upper,markup,offer = _get_handling_fee_db(conn)
        try:
                sql = """
                      SELECT
                     `uid`,`asset_acronym` AS acronym,`asset_name` AS name,`unit_price` + (`unit_price` * """+str(markup)+""") AS price,`asset_trend` AS trend,CONCAT("",`date_created`,"") AS date_created
                      FROM
                     `db_freknur_investment`.`tbl_asset`
                      LIMIT 1000
                      """

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"Asset list"},default=decimal_default)

        except Exception,e:
                logger.error(e)
                raise

        return j_string    

"""
-=================================================
-.create new asset.
-=================================================      
"""
def _add_new_asset_db(acronym,name,price,total,conn):
        asset_uid = str(uuid.uuid4().fields[-1])[:5]
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
                sql = """
                      INSERT
                      INTO
                     `db_freknur_investment`.`tbl_asset`
                      (`uid`,`asset_acronym`,`asset_name`,`unit_price`,`total`,`date_created`)
                      VALUES
                      ('%s','%s','%s','%s','%s','%s')      
                      ON DUPLICATE KEY
                      UPDATE `date_modified` = NOW()
                      """ % (asset_uid,acronym,name,price,total,date)

                params = ()

                db.execute_query(conn, sql, params)

                conn.commit()

                last_record = _get_last_record_db("asset",conn)

                j_string = last_record

        except Exception,e:
                logger.error(e)
                raise

        return j_string  

"""
-=================================================
-.modify asset.
-=================================================
"""
def _modify_asset_db(_id,acroynm,name,price,unit,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        trend = 0
        #-.routine call.
        output = _get_asset_master_db(_id,conn)
        try:
                if(unit != 0 or unit != ''):
                        if(int(price) < int(output[0])):
                                price = ((float(price)) + (float(output[0])))/2
                                trend = 2
                        else:
                                price = price
                                trend = 1

                        sql = """
                              UPDATE
                             `db_freknur_investment`.`tbl_asset`
                              SET
                             `asset_acronym` = '%s',`asset_name` = '%s',`unit_price` = '%s',`total` = (`total` + '%s'),`asset_trend` = '%s'
                              WHERE
                             `_id` = '%s'
                              """ % (acroynm,name,price,unit,trend,_id)

                        params = ()

                        db.execute_query(conn, sql, params)

                        j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"UPDATE success."}

                        conn.commit()

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.new asset purchase request.
-=================================================
"""
def _add_purchase_request_db(msisdn,uid,description,unit_price,qty,total_cost,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #-.routine call.
        processed_cnt = _existing_purchase_request(msisdn,uid,"1",conn)
        if(int(processed_cnt) > 0):
                #-.routine call.
                _del_processed_purchase_request(msisdn,conn)
        #-.routine call.
        exist = _get_user_db(msisdn,conn)
        #-.routine call.
        asset_data = _get_asset_master_db(uid,conn)
        #-.routine call.
        unprocessed_cnt =_existing_purchase_request(msisdn,uid,"0",conn)
        #-.routine call.
        fee,lower,upper,markup,offer = _get_handling_fee_db(conn)
        #-.get customer wallet bal.
        bal,ref = _get_customer_bal_db(msisdn,conn)
        #-.is the transaction within limits?
        if(int(float(qty)) >= int(lower) and int(float(qty)) <= int(upper)):
                #-.do we have enough qty?
                if(int(float(qty)) <= int(asset_data[1])):
                        #-.can the transaction proceed?
                        if(float(bal) >= float(total_cost)):
                                if(int(unprocessed_cnt) == 0):
                                        if(int(exist) == 1):
                                                try:
                                                        sql = """
                                                              INSERT
                                                              INTO
                                                             `db_freknur_investment`.`tbl_purchase_request`
                                                              (`msisdn`,`uid`,`description`,`unit_price`,`no_of_grain_purchased`,`cost`,`date_created`)
                                                              VALUES
                                                              ('%s','%s','%s','%s','%s','%s','%s')
                                                              """ % (msisdn,uid,description,unit_price,qty,total_cost,date)

                                                        params = ()

                                                        db.execute_query(conn, sql, params)

                                                        conn.commit()

                                                        j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Request has been received & queued for processing."}

                                                except Exception,e:
                                                        logger.error(e)
                                                        raise
                                        else:
                                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}
                                else:
                                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have a similar pending purchase request. Kindly wait for it to be processed."}
                        else:
                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Transaction cannot be completed. Insufficient balance."}
                else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Transaction cannot be completed."}
        else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"The minimum and maximum shares that can be bought is."+str(lower)+", "+str(upper)+" respectively."} 

        return j_string

"""
-=================================================
-.check duplicate purchase request.
-=================================================
"""
def _existing_purchase_request(msisdn,uid,flag,conn):
        has_request = 0
        try:
                sql = """
                      SELECT 
                      COUNT(`_id`) AS has_request
                      FROM
                     `db_freknur_investment`.`tbl_purchase_request`
                      WHERE
                     `msisdn` = %s AND `uid` = %s AND `is_processed` = %s
                      """
                params = (msisdn,uid,flag,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for data in recordset:
                        has_request = data['has_request']

        except Exception,e:
                logger.error(e)
                raise

        return has_request

"""
-=================================================
-.new sell request.
-=================================================
"""
def _add_sale_request_db(msisdn,uid,description,price,no_of_unit,cost,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #-.routine call.
        asset_data = _get_asset_master_db(uid,conn)
        #-.routine call.
        data = _get_asset_owner_db(msisdn,uid,conn)
        #-.routine call.
        fee,lower,upper,markup,offer = _get_handling_fee_db(conn)
        #-.new price incusive of markup.
        price_markup = (float(price) + (float(price) * float(markup)))
        #-.discription.
        activity = "INTENTION TO SELL "+str(no_of_unit)+" "+str(description)+" SHARE[S] @ COST OF "+str(cost)+" THROUGH THE ALTERNATIVE MARKET."
        #-.validate asset qty.
        if(int(float(data[0])) >= int(float(no_of_unit))):
                #-.routine call.
                has_request   = _existing_sell_request(msisdn,uid,conn)
                current_price = asset_data[0]
                total_cost    = (float(price_markup) * float(no_of_unit))
                if(int(has_request) == 0):
                        try:
                                sql = """
                                      INSERT
                                      INTO
                                     `db_freknur_investment`.`tbl_sale_request`
                                      (`msisdn`,`uid`,`description`,`unit_price`,`no_of_grain_sold`,`cost`,`date_created`)
                                      VALUES
                                      ('%s','%s','%s','%s','%s','%s','%s')
                                      ON DUPLICATE KEY
                                      UPDATE `date_modified` = NOW()
                                      """ % (msisdn,uid,description,price_markup,no_of_unit,total_cost,date)

                                params = ()

                                db.execute_query(conn, sql, params)
  
                                conn.commit()

                                #-.routine call.
                                _acitivity_log_db(msisdn,activity,conn)
 
                                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Your sell request of "+str(description)+" has been received successfully."}

                        except Exception,e:
                                logger.error(e)
                                raise
                else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Operation cannot be completed, you have a similar pending sell request of "+str(description)+"."}

        else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Invalid, transaction has failed."+str(int(data[0]))+"  "+str(int(float(no_of_unit)))}

        return j_string

"""
-=================================================
-.update user asset portfolio.
-=================================================
"""
def _update_asset_portfolio(qty,uid,msisdn,conn):

        try:
                sql = """
                      UPDATE 
                     `db_freknur_investment`.`tbl_owner_portfolio`
                      SET 
                     `number_of_asset` = (`number_of_asset` - %s)
                      WHERE
                     `msisdn` = '%s' AND `asset_id` = '%s'  AND `lock` = 0
                      """ % (qty,msisdn,uid)

                params = ()

                db.execute_query(conn, sql, params)

                conn.commit()

        except Exception,e:
                logger.error(e)
                raise

"""
-=================================================
-.remove process buy request
-=================================================
"""
def _del_processed_purchase_request(msisdn,conn):
        
        try:
                sql = """
                      DELETE 
                      FROM
                     `db_freknur_investment`.`tbl_purchase_request`
                      WHERE
                     `msisdn` = %s AND `is_processed` = 1
                      """ % (msisdn)

                params = ()

                db.execute_query(conn, sql, params)

                conn.commit()

        except Exception,e:
                logger.error(e)
                raise

"""
-=================================================
-.check there if existing sell request.
-=================================================
"""    
def _existing_sell_request(msisdn,uid,conn):
        has_request = 0
        try:
                sql = """
                      SELECT 
                      COUNT(`_id`) AS has_request
                      FROM
                     `db_freknur_investment`.`tbl_sale_request`
                      WHERE
                     `msisdn` = %s AND `uid` = %s
                      """
                params = (msisdn,uid,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for data in recordset:
                        has_request = data['has_request']
                
        except Exception,e:
                logger.error(e)
                raise

        return has_request

"""
-=================================================
-.asset record.
-=================================================
"""
def _get_last_record_db(action,conn):
        j_string = None
        try:
                if(action == "asset"):
                        sql = """
                              SELECT
                             `_id`,`uid`,`asset_acronym`,`asset_name`,`unit_price`,`total`,`asset_trend`,CONCAT("",`date_created`,"") AS date_created
                              FROM
                             `db_freknur_investment`.`tbl_asset`
                              ORDER BY
                             `_id` DESC
                              LIMIT 1
                              """
                elif(action == "config"):      
                        sql = """
                              SELECT
                             `cnf_id`,`trx_fee`,`min_limit`,`max_limit`,`currency`,CONCAT("",`time_stamp`,"") AS time_stamp
                              FROM
                             `db_freknur_investment`.`tbl_config`
                              ORDER BY
                             `cnf_id` DESC
                              LIMIT 1
                              """                    
                elif(action == "inventory"):
                        sql = """
                              SELECT
                             `_id`,`item_uid`,`item_name`,`qty_in`,CONCAT("",`unit_price`,"") AS unit_price,CONCAT("",`date_created`,"") AS date_created
                              FROM
                             `db_freknur_inventory`.`tbl_inventory`
                              ORDER BY
                             `_id` DESC
                              LIMIT 1
                              """                        
                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                jsonArray = ast.literal_eval(json.dumps(recordset))

                j_string = {"Result":"OK","Record":[json.dumps(recordset,default=decimal_default)]}                

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.asset config list.
-=================================================
"""
def _get_asset_config_list_db(lower_min,lower_max,conn):
        status  = 0
        j_string = None
        try:
                sql = """
                      SELECT
                     `cnf_id`,`trx_fee`,`min_limit`,`max_limit`,`equity_markup`,`currency`,CONCAT("",`time_stamp`,"") AS time_stamp
                      FROM
                     `db_freknur_investment`.`tbl_config`
                      LIMIT %i, %i
                      """ % (int(lower_min),int(lower_max))

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                jsonArray = ast.literal_eval(json.dumps(recordset))
                jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.create configuration information.
-=================================================
"""
def _create_asset_config_db(fee,min_limit,max_limit,xes,conn):
        config_id = str(uuid.uuid4().fields[-1])[:5]
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
                sql = """
                      INSERT
                      INTO
                     `db_freknur_investment`.`tbl_config`
                      (`trx_fee`,`min_limit`,`max_limit`,`currency`,`time_stamp`)
                      VALUES
                      ('%s','%s','%s','%s','%s')
                      """ % (fee,min_limit,max_limit,xes,date)

                params = ()

                db.execute_query(conn, sql, params)

                conn.commit()

                last_record = _get_last_record_db("config",conn)

                j_string = last_record

        except Exception,e:
                logger.error(e)
                raise

        return j_string
"""
-=================================================
-.modify configuration information.
-=================================================
"""
def _modify_asset_config_db(cnf_id,fee,min_limit,max_limit,xes,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
                sql = """
                      UPDATE
                     `db_freknur_investment`.`tbl_config`
                      SET 
                     `trx_fee` = '%s', `min_limit` = '%s', `max_limit` = '%s',`currency` = '%s',`time_stamp` = '%s'
                      WHERE
                     `cnf_id` = '%s'
                      """ % (fee,min_limit,max_limit,xes,date,cnf_id)

                params = ()

                db.execute_query(conn, sql, params)

                conn.commit()

                j_string = {"Result":"OK"}

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.sell request list.
-=================================================
"""
def _get_sale_request_list_db(msisdn,is_owner,conn,limit=1000):
        status  = 0
        j_string = None
        try:
                if(int(is_owner) == 1):
                        sql = """
                              SELECT
                              SUM(`no_of_grain_sold`) AS QTY,`description`,`uid`,`unit_price`,sum((`no_of_grain_sold`*`unit_price`)) AS total_cost
                              FROM
                             `db_freknur_investment`.`tbl_sale_request`
                              WHERE
                             `msisdn` = %s 
                              GROUP BY `uid`,`description`,`unit_price`,`uid`
                              -- GROUP BY `uid`,`description`,`uid`
                              LIMIT %s;
                              """
                else:
                        sql = """
                              SELECT
                              SUM(`no_of_grain_sold`) AS QTY,`description`,`uid`,`unit_price`,sum((`no_of_grain_sold`*`unit_price`)) AS total_cost
                              FROM
                             `db_freknur_investment`.`tbl_sale_request`
                              WHERE
                             `msisdn` != %s 
                              GROUP BY `uid`,`description`,`unit_price`,`uid`
                              -- GROUP BY `uid`,`description`,`uid`
                              LIMIT %s;
                              """
                params = (msisdn,limit,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                if(len(recordset) > 0):
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"Sell request list"},default=decimal_default)
                else:
                        j_string = json.dumps({"ERROR":"1","RESULT":"FAIL","DATA":recordset,"MESSAGE":"The list is empty."})

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.make a bid.
-=================================================
"""
def _place_bid_db(asset_id,asset_name,owner_msisdn,bidder_msisdn,qty,bid_price,conn):
        j_string = None
        date     = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        bid_id   = "B_"+str(uuid.uuid4().fields[-1])[:5] 
        try:
                sql = """
                      INSERT
                      INTO
                     `db_freknur_investment`.`tbl_sale_bid`
                      (`bid_id`,`asset_id`,`asset_name`,`owner_msisdn`,`bidder_msisdn`,`qty`,`bid_price`)
                      VALUES
                      ('%s','%s','%s','%s','%s','%s','%s')      
                      ON DUPLICATE KEY
                      UPDATE `time_stamp` = NOW()
                      """ % (bid_id,asset_id,asset_name,owner_msisdn,bidder_msisdn,qty,bid_price)

                params = ()

                db.execute_query(conn, sql, params)

                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Bid has been received."}

                conn.commit()

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get bid list.
-=================================================
"""
def _get_bid_list_db(msisdn,conn,limit=1000):

        j_string = None
        
        try:
                sql = """
                      SELECT
                     `bid_id`,`asset_id`,`asset_name`,`owner_msisdn`,`bidder_msisdn`,`bid_price`,CONCAT("",`time_stamp`,"") AS time_stamp
                      FROM
                     `db_freknur_investment`.`tbl_sale_bid`
                      WHERE
                     `owner_msisdn` = %s AND `is_accepted` = 0 AND `is_deleted` = 0 
                      LIMIT %s
                      """

                sqd = """
                      SELECT 
                      CAST(SUM(`qty`) AS UNSIGNED) AS total,`asset_name`,(SELECT `unit_price` FROM `db_freknur_investment`.`tbl_asset` WHERE `uid`=asset_id) AS price 
                      FROM 
                     `db_freknur_investment`.`tbl_sale_bid`
                      WHERE 
                     `owner_msisdn` != %s AND `is_accepted` = 0 AND `is_deleted` = 0 
                      GROUP BY `asset_id`,`asset_name` 
                      HAVING `price` IS NOT NULL
                      LIMIT %s
                      """

                params = (msisdn,limit,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                if(len(recordset) > 0):
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"Placed bid[s]"},default=decimal_default)
                else:
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"The list is empty"})

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get accepted bids.
-=================================================
"""
def _get_accepted_bid_db(msisdn,conn,limit=1000):

        j_string = None

        try:
                sql = """
                      SELECT
                     `bid_id`,`asset_id`,`asset_name`,`owner_msisdn`,`bidder_msisdn`,`bid_price`,CONCAT("",`time_stamp`,"") AS time_stamp
                      FROM
                     `db_freknur_investment`.`tbl_sale_bid`
                      WHERE
                     `bidder_msisdn` = %s AND `is_accepted` = 1 AND `is_deleted` = 0 
                      LIMIT %s
                      """

                params = (msisdn,limit,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                if(len(recordset) > 0):
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"Accepted bid[s]"})
                else:
                        j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"The list is empty."})

        except Exception,e:
                logger.error(e)
                raise

        return j_string


"""
-=================================================
-.accept a bid.
-=================================================
"""
def _accept_bid_db(bid_id,asset_id,conn):

        j_string = None

        cnt = _get_bid_info_db(bid_id,asset_id,conn)

        try:
                if(int(cnt) == 1):            
                        sql = """
                              UPDATE
                             `db_freknur_investment`.`tbl_sale_bid`
                              SET
                             `is_accepted` = '1'
                              WHERE
                             `bid_id` = '%s' AND `asset_id` = '%s'
                              """ % (bid_id,asset_id)

                        params = ()

                        db.execute_query(conn, sql, params)

                        j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"You have accepted the bid."}

                        conn.commit()
                else:
                        j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Bid does not exist."}
        except Exception,e:
                logger.error(e)
                raise

        return j_string


"""
-=================================================
-.get bid info.
-=================================================
"""
def _get_bid_info_db(bid_id,asset_id,conn):
        cnt=0
        try:
                sql = """
                      SELECT
                      COUNT(`bid_id`) AS cnt
                      FROM
                     `db_freknur_investment`.`tbl_sale_bid`
                      WHERE
                     `bid_id` = '%s' AND `asset_id` = '%s' AND `is_accepted` = 0 AND `is_deleted` = 0
                      """ % (bid_id,asset_id)

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for record in recordset:
                        cnt = record['cnt']

        except Exception,e:
                logger.error(e)
                raise

        return cnt

"""
-=================================================
-.track book keeping.
-=================================================
"""
def _book_keeping_db(msisdn,asset_id,asset_name,unit_price,qty,wallet_bal,total_cost,fee_earned,conn):
        j_string = None
        try:
                sql = """CALL `db_freknur_investment`.`sProcLogAssetPurchaseTrx`(%s,%s,%s,%s,%s,%s,%s,%s)"""
                params = (msisdn,asset_id,asset_name,unit_price,qty,wallet_bal,total_cost,fee_earned,)
                output = db.retrieve_all_data_params(conn,sql,params)

                for data in output:
                        jsString = json.loads(data.get('_JSON'))

                #conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.purchase asset on alternate market.
-================================================
"""
def _purchase_on_alternate_market_db(asset_id,msisdn,asset_name,unit_price,qty,cost,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #-.routine call.
        exist = _get_user_db(msisdn,conn)
        #-.get customer wallet bal.
        bal,ref = _get_customer_bal_db(msisdn,conn)
        #-.routine call.
        fee,lower,upper,markup,offer = _get_handling_fee_db(conn)
        #-.routine call.
        unprocessed_cnt = _alternate_existing_request(msisdn,asset_id,"0",conn)
        #-..
        if(int(exist) == 1):
                if(float(qty) >= float(lower) and float(qty) <= float(upper)):
                        if(int(unprocessed_cnt) == 0):
                                if(float(bal) >= float(cost)):
                                        try:
                                                sql = """
                                                      INSERT 
                                                      INTO
                                                     `db_freknur_investment`.`tbl_alternate_market_bid`
                                                      (`asset_id`,`msisdn`,`asset_name`,`unit_price`,`qty`,`cost`,`date_created`)
                                                      VALUES
                                                      ('%s','%s','%s','%s','%s','%s','%s')
                                                      """ % (asset_id,msisdn,asset_name,unit_price,qty,cost,date)
                                                params = ()
                                                
                                                db.execute_query(conn, sql, params)
                                                
                                                conn.commit()
                                                
                                                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Request has been received."}
                                        except Exception,e:
                                                logger.error(e)
                                                raise
                                else:
                                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Transaction cannot be completed. Insufficient balance."}
                        else:
                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have a similar pending purchase request. Kindly wait for it to be processed."}
                else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"The minimum and maximum shares that can be bought is."+str(lower)+", "+str(upper)+" respectively."}
        else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}

        return j_string

"""
-===============================================
-.check request on alternate market exist.
-===============================================
"""
def _alternate_existing_request(msisdn,asset_id,flag,conn):
        has_request = 0
        try:
                sql = """
                      SELECT 
                      COUNT(`_id`) AS has_request
                      FROM
                     `db_freknur_investment`.`tbl_alternate_market_bid`
                      WHERE
                     `msisdn` = %s AND `asset_id` = %s AND `is_processed` = %s
                      """
                params = (msisdn,asset_id,flag,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for data in recordset:
                        has_request = data['has_request']

        except Exception,e:
                logger.error(e)
                raise

        return has_request    
        
"""
-=================================================
-.get asset purchase queue.
-=================================================
"""
def _get_asset_purchase_request_db(conn,limit=1000):
        is_processed = 0
        j_string = None
        try:
                sql = """
                      SELECT
                     `_id`,`uid`,`msisdn`,`description`,`unit_price`,`no_of_grain_purchased`,`cost`,CONCAT("",`date_created`,"") AS date_created
                      FROM
                     `db_freknur_investment`.`tbl_purchase_request`
                      WHERE
                     `is_processed` = %s
                      LIMIT %s
                      """

                params = (is_processed,limit)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                j_string = json.dumps(recordset,default=decimal_default)

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.buy asset on alternative market.
-=================================================
"""
def _purchase_asset_on_market_db(msisdn,qty,asset_name,asset_uid,price,current_wallet_bal,total_cost,fee_earned,conn):
        j_string = None
        #-.redis connection.
        rd = create_redis_connection()
        try:
                sql = """CALL `db_freknur_investment`.`sProcHandlePurchaseRequestFromAltMarket`(%s,%s,%s,%s,%s,%s,%s,%s)"""
                params = (msisdn,qty,asset_name,asset_uid,price,current_wallet_bal,total_cost,fee_earned,)
                output = db.retrieve_all_data_params(conn,sql,params)
                #-.get keys.
                key_1 = redis_access_key()[0]+str(msisdn)
                key_2 = redis_access_key()[1]+str(msisdn)
                #-.reset cache.
                _delete_from_redis_cache(key_1,rd)
                _delete_from_redis_cache(key_2,rd)

                for data in output:
                        j_string = json.loads(data.get('_JSON'))

                #conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.alert to seller on alternative market.
-=================================================
"""
def _alert_to_seller_on_market_db(msisdn,asset_name,duration,offer_price,message,conn):
        j_string = None
        try:
                sql = """CALL `db_freknur_investment`.`sProcSysAlternativeMarketAlertToSeller`(%s,%s,%s,%s,%s)"""
                params = (msisdn,asset_name,duration,offer_price,message,)
                output = db.retrieve_all_data_params(conn,sql,params)

                for data in output:
                        j_string = json.loads(data.get('_JSON'))

                #conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get sell request queue on alternative market.
-=================================================
"""
def _get_sell_request_on_market_db(conn,limit=1000):
        is_processed = 0
        j_string = None
        try:
                sql = """
                      SELECT
                     `_id`,`asset_id`,`msisdn`,`asset_name`,`unit_price`,`qty`,`cost`,CONCAT("",`date_created`,"") AS date_created
                      FROM
                     `db_freknur_investment`.`tbl_alternate_market_bid`
                      WHERE
                     `is_processed` = %s
                      LIMIT %s
                      """

                params = (is_processed,limit)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                j_string = json.dumps(recordset)

        except Exception,e:
                logger.error(e)
                raise

        return j_string


"""
-=================================================
-.delete alt market purchase request.
-=================================================
"""
def _delete_alternative_market_request_db(msisdn,conn):
        try:
                sql = """DELETE
                         FROM
                        `db_freknur_investment`.`tbl_alternate_market_bid`
                         WHERE
                        `msisdn` = %s """

                params = (msisdn,)

                db.execute_query(conn, sql, params)

                conn.commit()
        except Exception, e:
                logger.error(e)
                raise
"""
-=================================================
-.create a new secured loan.
-=================================================
"""
def _record_secured_loan_request_db(msisdn,amount,collateral_size,has_collateral,conn):
        date     = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        j_string = None
        #-.open cache.
        rd = create_redis_connection()
        try:
                #-.routine call.
                collateral_amount = _get_client_porfolio_worth_db(msisdn,conn)
                #-.routine call to check whether user has existing loan.
                has_loan = _get_has_loan_db(msisdn,conn)
                #-.routine call to generate a unique loan id.
                loan_uid = _get_loan_uid_db(conn)
                #-.routine call to check whether user exist.
                exist = _get_user_db(msisdn,conn)
                #-.routine call: existing request.
                has_request = _has_loan_request_db(msisdn,conn)
                #-.delete logs.
                #-._del_loan_approved_processed_log(conn)

                min_allowed_loan  = int(loan_params['min_loan'])
                max_allowed_loan  = int(loan_params['max_loan'])

                if(int(exist) == 1):
                        if(int(has_loan) == 0):
                                if(int(has_request[0]) == 0):
                                        if(int(amount) >= min_allowed_loan and int(amount) <= max_allowed_loan):
                                                sql = """
                                                      INSERT
                                                      INTO
                                                     `db_freknur_loan`.`tbl_loan_request`
                                                      (`msisdn`,`reference_no`,`amount`,`collateral_percentage`,`requested_by`,`date_created`,`has_collateral`)
                                                      VALUES
                                                      ('%s','%s','%s','%s','%s','%s','%s')
                                                      ON
                                                      DUPLICATE KEY
                                                      UPDATE `date_modified` = '%s' 
                                                      """ % (msisdn,str(loan_uid).upper(),amount,float(collateral_size),msisdn,date,has_collateral,date)

                                                params = ()

                                                db.execute_query(conn, sql, params)

                                                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Loan request was successful."}

                                                conn.commit()
                                                #-.routine call.
                                                _log_client_collateral_db(msisdn,amount,collateral_amount,collateral_size,conn)
                                                #-.routine call.
                                                #-_copy_client_asset_portfolio(msisdn,conn)
                                                #-.routine call.
                                                _lock_user_asset_portfolio(msisdn,conn)
                                                #-.reset cache.
                                                key_1 = redis_access_key()[0]+str(msisdn)
                                                key_2 = redis_access_key()[1]+str(msisdn)
                                                #-.reset cache.
                                                _delete_from_redis_cache(key_1,rd)
                                                _delete_from_redis_cache(key_2,rd)
                                        else:
                                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Loan limits: MINIMUM : "+str(min_allowed_loan)+" MAXIMUM : "+str(max_allowed_loan)}
                                else:
                                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have loan request of "+str(has_request[1])+" pending approval."}
                        else:
                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have an existing loan."}
                else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You are not a registered user."}
        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.log collateral percentage seeded.
-=================================================
"""
def _log_client_collateral_db(msisdn,loan_amount,portfolio_worth,cover_as_fraction,conn):
        try:
                sql = """INSERT 
                         INTO 
                        `db_freknur_general`.`tbl_loan_collateral`
                         (`msisdn`,`loan_amount`,`portfolio_worth`,`collateral_percentage`)
                         VALUES
                         ('%s','%s','%s','%s')
                         ON
                         DUPLICATE KEY 
                         UPDATE `is_processed` = 0 """ % (msisdn,loan_amount,portfolio_worth,cover_as_fraction)

                params = ()

                db.execute_query(conn, sql, params)

                conn.commit()
        except Exception, e:
                logger.error(e)
                raise

"""
-=================================================
-.get collateral size.
-=================================================
"""
def _get_collateral_log_db(msisdn,conn):
        size = 0
        amount = 0
        portfolio = 0
        is_processed = 0
        j_string = None
        try:
                sql = """
                      SELECT
                     `loan_amount`,`portfolio_worth`,`collateral_percentage`
                      FROM
                     `db_freknur_general`.`tbl_loan_collateral`
                      WHERE
                     `msisdn` = %s AND `is_processed` = %s
                      """

                params = (msisdn,is_processed)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for data in recordset:
                        amount    = data['loan_amount']
                        portfolio = data['portfolio_worth']
                        size      = data['collateral_percentage']

        except Exception,e:
                logger.error(e)
                raise

        return amount,portfolio,size

"""
-=================================================
-.lock asset committed to a loan.
-=================================================
"""
def _lock_user_asset_portfolio(msisdn,conn):
        try:
                sql = """
                      UPDATE 
                     `db_freknur_investment`.`tbl_owner_portfolio` 
                      SET 
                     `lock` = 1
                      WHERE 
                     `msisdn` = '%s' AND `lock` = 0
                      """ % (msisdn)

                params = ()

                db.execute_query(conn, sql, params)
                conn.commit()

        except Exception,e:
                logger.error(e)
                raise

"""
-=================================================
-.get loan settings.
-=================================================
"""
def _get_loan_settings_configs():

        loan_settings = {"min_loan": loan_params['min_loan'],"max_loan": loan_params['max_loan'],"interest_on_loan": loan_params['interest'],"duration": loan_params['duration'],"loan_handling_fee": loan_params['loan_fee'],"loan_interest_adjustment": loan_params['rebase']}

        j_string  = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE": loan_settings}

        return j_string

"""
-=================================================
-.collateral temp list.
-=================================================
"""        
def _read_collateral_portfolio_temp_list_db(conn,limit=1000):
        j_string = None
        try:
                sql = """
                      SELECT 
                      SUM(`number_of_asset` * (SELECT `unit_price` FROM db_freknur_investment.tbl_asset WHERE `uid` = asset_id)) AS total_cost, SUM(number_of_asset) AS total_qty, `msisdn`
                      FROM 
                     `db_freknur_investment`.`tbl_owner_portfolio_backup`
                      WHERE
                     `lock` = 0
                      GROUP BY `msisdn`
                      LIMIT %s
                      """
                params = (limit,)

                recordset = db.retrieve_all_data_params(conn,sql,params)

                j_string = json.dumps(recordset,default=decimal_default)

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-.===============================================
-.get snapshot of client asset portfolio
-.===============================================
"""
def _copy_client_asset_portfolio(msisdn,conn):
        sql = """
              INSERT
              INTO
             `db_freknur_investment.tbl_owner_portfolio_backup` (`msisdn`,`asset_id`,`asset_acronym`,`date_created`)
              SELECT
             `msisdn`,`asset_id`,`asset_acronym`,`date_created`
              FROM
             `db_freknur_investment.tbl_owner_portfolio` 
              WHERE 
             `msisdn` = %s AND `lock` = 0
              """ % (msisdn,)

        params = ()

        db.execute_query(conn, sql, params)

        conn.commit()    

"""
-=================================================
-.delete own sell request
-=================================================
"""
def _delete_own_sell_requet_db(asset_id,msisdn,conn):
        j_string = None
        #-.routine call.
        exist = _pending_cnt_request_db(asset_id,msisdn,conn)
        #-.particulars.
        activity = "A SELL REQUEST HAS BEEN WITHDRAWN BY OWNER."
        try:
                if(exist == 1):
                        sql = """
                              DELETE
                              FROM
                             `db_freknur_investment`.`tbl_sale_request_queue`
                              WHERE
                             `uid` = '%s' AND `msisdn` = '%s'
                              """ % (asset_id,msisdn)
                        params = ()
                        db.execute_query(conn, sql, params)

                        j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"The request has been deleted."}
                        
                        conn.commit()

                        #-.routine call.
                        _delete_own_sell_requet_main_db(asset_id,msisdn,conn)
                        #-.log activity.
                        _acitivity_log_db(msisdn,activity,conn)
                else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You do not have any requests."}

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.delete own sell request 2
-=================================================
"""
def _delete_own_sell_requet_main_db(asset_id,msisdn,conn):
        try:
                sql = """
                      DELETE
                      FROM
                     `db_freknur_investment`.`tbl_sale_request`
                      WHERE
                     `uid` = '%s' AND `msisdn` = '%s'
                      """ % (asset_id,msisdn)

                params = ()
                db.execute_query(conn, sql, params)
                
                conn.commit()

        except Exception,e:
                logger.error(e)
                raise

"""
-=================================================
-.get bid info.
-=================================================
"""
def _pending_cnt_request_db(asset_id,msisdn,conn):
        cnt=0
        try:
                sql = """
                      SELECT
                      COUNT(`uid`) AS cnt
                      FROM
                     `db_freknur_investment`.`tbl_sale_request_queue`
                      WHERE
                     `uid` = '%s' AND `msisdn` = '%s'
                      """ % (asset_id,msisdn)

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for record in recordset:
                        cnt = record['cnt']

        except Exception,e:
                logger.error(e)
                raise

        return cnt

"""
-=================================================
-.interest on collateral.
-=================================================
"""
def _calc_loan_amount_with_interest_rebate(collateral_amount,loan_amount,interest_adjustment_rate,loan_interest_rate,collateral_percent):

        step_1  =  ((collateral_amount*collateral_percent) / loan_amount)*interest_adjustment_rate

        interest_adjustment = (float(loan_interest_rate) - step_1)

        return (interest_adjustment * loan_amount) 

#===================================================================================================
#-.                                 START WALLERT TRANSAFER
#===================================================================================================

"""
-.===============================================
-.peer to peer wallet transfer.
-.===============================================
"""
def _peer_wallet_transfer_db(msisdn,beneficiary_msisdn,amount,conn):
        j_string = None
        try:
                #-.routine call.
                exist_1 = _get_user_db(msisdn,conn)
                #-.routine call.
                exist_2 = _get_user_db(beneficiary_msisdn,conn)
                #-.wallet bal.
                bal,ref = _get_customer_bal_db(msisdn,conn)
                #-.redis conn.
                rd = create_redis_connection()
                #-.particulars.
                activity = str(amount)+" HAS BEEN MOVED FROM: "+str(msisdn)+" TO BENEFICIARY:"+str(beneficiary_msisdn)
                #-.do a/c exist?
                if(int(exist_1) == 1 and int(exist_2) == 1):
                        sql = """CALL `db_freknur_loan`.`sProcWalletToWalletTransfer`(%s,%s,%s,%s)"""
                        params = (amount,bal,msisdn,beneficiary_msisdn,)
                        output = db.retrieve_all_data_params(conn,sql,params)

                        #-.get keys.
                        key_1 = redis_access_key()[0]+str(msisdn)
                        key_2 = redis_access_key()[0]+str(beneficiary_msisdn)
                        #-.reset cache.
                        _delete_from_redis_cache(key_1,rd)
                        _delete_from_redis_cache(key_2,rd)
                        #-.log activity.
                        _acitivity_log_db(msisdn,activity,conn)

                        for data in output:
                                j_string = json.loads(data.get('_JSON'))
                else:
                        j_string = {"ERROR":"1","RESULT":"FAILED","MESSAGE":"Either SENDER or BENEFICIARY account do not exist."}
                    
                #conn.commit()
        except Exception, e:
                logger.error(e)
                raise

        return j_string

#===================================================================================================
#-.                                 END WALLERT TRANSAFER
#===================================================================================================


#===================================================================================================
#-.                                     START   FREKNUR COMMERCE
#===================================================================================================
"""
"""
def _inventory_list_db(search,lower_min,lower_max,conn):
        available = 0
        j_string = None
        try:
                if(search == '0'):
                        sql  =   """
                                 SELECT 
                                `_id`,`item_uid`,`item_name`,`item_image`,`qty_in`,`qty_out`,CONCAT("",`unit_price`,"") AS unit_price,CONCAT("",`date_created`,"") AS date_created,CONCAT("",`date_modified`,"") AS date_modified,`is_available`
                                 FROM 
                                `db_freknur_inventory`.`tbl_inventory`
                                 WHERE 
                                `is_available` = %s
                                 ORDER BY `date_created` DESC
                                 LIMIT %i, %i 
                                 """ % (available,int(lower_min),int(lower_max))
                else:
                        sql  =   """
                                 SELECT 
                                `_id`,`item_uid`,`item_name`,`item_image`,`qty_in`,`qty_out`,CONCAT("",`unit_price`,"") AS unit_price,CONCAT("",`date_created`,"") AS date_created,CONCAT("",`date_modified`,"") AS date_modified,`is_available`
                                 FROM 
                                `db_freknur_inventory`.`tbl_inventory`
                                 WHERE 
                                `is_available` = %s AND `item_name` LIKE '%s'
                                 ORDER BY `date_created` DESC
                                 LIMIT %i, %i 
                                 """ % (available,("%%" + search + "%%"),int(lower_min),int(lower_max))

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                jsonArray = ast.literal_eval(json.dumps(recordset))
                jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)},default=decimal_default)

        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.create a inventory record.
-=================================================
"""
def _create_inventory_record_db(name,qty,price,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item_uid = str(uuid.uuid4().fields[-1])[:5]
        try:
                sql = """
                      INSERT 
                      INTO
                     `db_freknur_inventory`.`tbl_inventory`
                      (`item_uid`,`item_name`,`qty_in`,`unit_price`,`date_created`)
                      VALUES
                      ('%s','%s','%s','%s','%s')
                      ON
                      DUPLICATE KEY
                      UPDATE `date_modified` = '%s'
                      """ % (item_uid,name,qty,price,date,date)

                params = ()

                db.execute_query(conn, sql, params)

                #-.j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Request has been received."}

                conn.commit()

                last_record = _get_last_record_db("inventory",conn)

                j_string = last_record

        except Exception,e:
                logger.error(e)
                raise

        return j_string    


"""
-=================================================
-.save image path.
-=================================================
"""
def _save_inventory_image_path_db(record_id,path,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
                sql = """
                      UPDATE
                     `db_freknur_inventory`.`tbl_inventory`
                      SET
                     `item_image` = '%s',
                     `date_modified` = '%s'
                      WHERE
                     `item_uid` = '%s'
                      """ % (path,date,record_id)

                params = ()

                db.execute_query(conn, sql, params)

                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Image path has been saved."}

                conn.commit()

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.get sale record list.
-=================================================
"""
def _get_sales_record_list_db(search,lower_min,lower_max,conn):
        is_archived = 0
        j_string = None
        try:
                if(search == '0'):
                        sql  =   """
                                 SELECT
                                `_id`,`product_uid`,`qty`,`total`,CONCAT("",`date_created`,"") AS date_created
                                 FROM
                                `db_freknur_inventory`.`tbl_sales`
                                 WHERE
                                `is_archived` = %s
                                 ORDER BY `date_created` DESC
                                 LIMIT %i, %i
                                 """ % (is_archived,int(lower_min),int(lower_max))
                else:
                        sql  =   """
                                 SELECT
                                `_id`,`product_uid`,`qty`,`total`,CONCAT("",`date_created`,"") AS date_created
                                 FROM
                                `db_freknur_inventory`.`tbl_sales`
                                 WHERE
                                `is_archived` = %s
                                 ORDER BY `date_created` DESC
                                 LIMIT %i, %i
                                 """ % (is_archived,int(lower_min),int(lower_max))

                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                jsonArray = ast.literal_eval(json.dumps(recordset))
                jsonArraySize = len(jsonArray)

                j_string = json.dumps({"Result":"OK","Records":recordset,"TotalRecordCount":str(jsonArraySize)})

        except Exception, e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.create a sale record.
-=================================================
"""
def _create_sale_record_db(product_uid,qty,total,msisdn,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
                sql = """
                      INSERT 
                      INTO
                     `db_freknur_inventory`.`tbl_sales`
                      (`product_uid`,`qty`,`total`,`msisdn`,`date_created`)
                      VALUES
                      ('%s','%s','%s','%s')
                      """ % (product_uid,qty,total,msisdn,date)
                params = ()

                db.execute_query(conn, sql, params)

                #-.j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Request has been received."}

                conn.commit()

                last_record = _get_last_record_db("inventory",conn)

                j_string = last_record

        except Exception,e:
                logger.error(e)
                raise

        return j_string

"""
-=================================================
-.modify sale record.
-=================================================
"""
def _modify_sale_record_db(qty,total,product_uid,conn):

        j_string = None

        try:
                sql = """
                      UPDATE
                     `db_freknur_inventory`.`tbl_sales`
                      SET
                     `qty` = %s,
                     `total` = %s
                      WHERE
                     `product_uid` = '%s' AND `is_archived` = '0'
                      """ % (qty,total,product_uid)

                params = ()
                
                db.execute_query(conn, sql, params)
                
                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"You chrrge."}
                
                
                conn.commit()
        except Exception,e:
                logger.error(e)
                raise
        
        return j_string

#===================================================================================================
#-.                                  END  FREKNUR COMMERCE
#===================================================================================================

"""
-=================================================
-.get last insert id.
-=================================================
"""
def _get_last_insert_id_db(conn):
        rec_id = 0
        try:
                sql = """
                      SELECT LAST_INSERT_ID() AS rec_id
                      """
                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for record in recordset:
                        rec_id = record['rec_id']

        except Exception,e:
                logger.error(e)
                raise

        return rec_id

"""
-=================================================
-.get config info.
-=================================================
"""
def _get_handling_fee_db(conn):
        fee=0
        low=0
        upp=0
        markup=0
        offer=0
        try:
                sql = """
                      SELECT
                     `trx_fee`,`min_limit`,`max_limit`,`equity_markup`,`equity_offer_rate`
                      FROM
                     `db_freknur_investment`.`tbl_config`
                      """
                params = ()

                recordset = db.retrieve_all_data_params(conn,sql,params)

                for record in recordset:
                        fee    = record['trx_fee']
                        low    = record['min_limit']
                        upp    = record['max_limit']
                        markup = record['equity_markup']
                        offer  = record['equity_offer_rate']

        except Exception,e:
                logger.error(e)
                raise

        return fee,low,upp,markup,offer
  
"""
-=================================================
-.write to redis.
-=================================================
"""
def _save_to_redis_cache(key,data,conn):
        status = "fail"
        try:
                conn.set(key,data)
                staus = "success"
        except Exception,e:
                logger.error(e)
                raise

        return status

"""
-=================================================
-.read redis.
-=================================================
"""
def _read_redis_cache(key,conn):
        msg = None
        try:
                msg = conn.get(key)
        except Exception,e:
                logger.error(e)
                raise
        
        return msg
   
"""
-=================================================
-.delete data from redis.
-=================================================
"""
def _delete_from_redis_cache(key,conn):
        status = "fail"
        try:
                conn.delete(key)
                staus = "success"
        except Exception,e:
                logger.error(e)
                raise

        return status 
   

"""
-=================================================
-.serialize deciaml value.
-=================================================
"""
def decimal_default(obj):
        if isinstance(obj,decimal.Decimal):
                return float(obj)
        raise TypeError

"""
-========================================================================================================================================================================================================

-========================================================================================================================================================================================================
"""
					
"""
#-.db routine connection.
"""
def create_connection():
        ex = None
	try:
		connection = MySQLdb.connect(host=mysql_params['host'],\
                             user=mysql_params['user'], passwd=mysql_params['passwd'],\
                             db=mysql_params['db'], cursorclass=MySQLdb.cursors.DictCursor)
	except(MySQLdb.Error, ex):
		logger.error(ex)

		raise

	return connection
"""	
#-.db close connection.
"""
def close_connection(connection):
	try:
		connection.close()
	except(MySQLdb.Error, e):
		logger.error(e)

		raise

"""
#-.redis connection
"""
def create_redis_connection():
        try:
                #-.connection = redis.ConnectionPool(host=redis_params['host'], port=redis_params['port'], password=redis_params['passwd'])
                connection = redis.StrictRedis(host=redis_params['host'], port=redis_params['port'], password=redis_params['passwd'], decode_responses=True)
        except Exception as e:
                logger.error(e)

                raise

        return connection

"""
#-.redis key.
"""
def redis_access_key():

        return redis_key_params['USER_WALLET_BAL_KEY'], redis_key_params['USER_PORTFOLIO_KEY'], redis_key_params['USER_GRAIN_STMT'], redis_key_params['USER_LOAN_STMT'], \
                      redis_key_params['USER_WALLET_STMT'], redis_key_params['SHOP_LIST'], redis_key_params['ASSET_LIST'], redis_key_params['PUSH_NOTIFICATION_KEY']
