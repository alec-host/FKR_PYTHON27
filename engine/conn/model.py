#!/usr/bin/python

import os
import sys


from db_helper import _record_unsecured_loan_request_db,_loan_request_list_db,_loan_dispatch_list_db,_registration_extra_db,\
                      _vet_loan_request_db,_get_loan_request_db,_mark_loan_request_processed_db,_get_action_on_temp_db,_delete_action_on_temp_db,\
                      _queue_loan_db,_registration_db,_get_loan_payout_db,_dispatch_loan_db,_record_loan_transaction_db,\
                      _record_loan_fee_db,_get_comprehensive_wallet_statement_db ,_get_general_account_list_db,_get_debtor_list_db,_get_defaulter_list_db,_get_account_summary_db,\
                      _withdraw_electronic_cash_db,_get_customer_bal_db,_get_loan_arrears_db,_loan_payment_db,_get_payment_list_db,_PAYMENT_TEST_db,\
                      _loan_due_list_db,_loan_due_alert_handler_db,_defaulter_list_db,_calc_loan_penalty_db,_flag_as_defaulter_db,_get_customer_portfolio_db,\
                      _get_asset_list_db,_add_new_asset_db,_add_purchase_request_db,_add_sale_request_db,_modify_asset_db,_get_asset_config_list_db,_create_asset_config_db,\
                      _get_asset_trend_list_db,_get_sale_request_list_db,_get_bid_list_db,_get_asset_config_params_db,_get_asset_purchase_request_db,\
                      _get_asset_master_db,_get_customer_bal_db,_book_keeping_db,_get_handling_fee_db,_modify_asset_config_db,_place_bid_db,_get_accepted_bid_db,\
                      _acitivity_log_db,_accept_bid_db,_get_activity_log_db,_log_dispatched_loan_db,_purchase_asset_on_market_db,_alert_to_seller_on_market_db,\
                      _purchase_on_alternate_market_db,_get_sell_request_on_market_db,_inventory_list_db,_record_secured_loan_request_db,\
                      _get_sales_record_list_db,_create_inventory_record_db,_create_sale_record_db,_modify_sale_record_db,_get_collateral_log_db,_peer_wallet_transfer_db,\
                      _read_collateral_portfolio_temp_list_db,_get_loan_settings_configs,_delete_alternative_market_request_db,_wallet_deposit_db,\
                      _calc_loan_amount_with_interest_rebate,_delete_own_sell_requet_db,_save_to_redis_cache,_read_redis_cache,_delete_from_redis_cache,\
                      _get_customer_list_db,_save_inventory_image_path_db,_get_mini_loan_statement_db,_get_mini_asset_statement_db

def _record_unsecured_loan_request_api(json,conn=None):
	db_response = 'None'
	if(json is not None):
		"""
		-.extract json values.
		"""
		msisdn = json['msisdn']
		amount = json['amount']
                #-.collateral_percentage = json['collateral_percentage']
                #-.has_collateral = json['has_collateral']
		"""
		-.write loan request to db.
		"""
		db_response = _record_unsecured_loan_request_db(msisdn,amount,conn)
		
	return db_response 

def _registration_api(json,conn=None):
	db_response = 'None'
	if(json is not None):
		"""
		-.extract json values.
		"""
		msisdn = json['msisdn']
		passwd = json['passwd']
		"""
		-.write loan request to db.
		"""
		db_response = _registration_db(msisdn,passwd,conn)
		
	return db_response 


def _registration_extra_sys(msisdn,fname,sname,dob,mail,code,conn=None):
        if(conn is not None):
               db_response = _registration_extra_db(msisdn,fname,sname,dob,mail,code,conn)

        
        return db_response
	
def _get_comprehensive_wallet_statement_api(msisdn,conn=None):
	db_response = 'None'
	if(msisdn is not None):
		db_response = _get_comprehensive_wallet_statement_db (msisdn,conn)
	
	return db_response

def _get_mini_loan_statement_api(msisdn,conn=None):
        db_response = 'None'
        if(msisdn is not None):
                db_response = _get_mini_loan_statement_db(msisdn,conn)

        return db_response

def _get_mini_asset_statement_api(msisdn,conn=None):
        db_response = 'None'
        if(msisdn is not None):
                db_response = _get_mini_asset_statement_db(msisdn,conn)

        return db_response    

def _get_loan_arrears_api(msisdn,conn=None):
        if(conn is not None):
                db_response = _get_loan_arrears_db(msisdn,conn)

        return db_response

def _get_loan_request_list_api(search,min,max,conn=None):
	db_response = 'None'
	if(conn is not None):
		db_response = _loan_request_list_db(search,min,max,conn)
	
	return db_response

def _get_loan_dispatch_list_api(search,min,max,conn=None):	
	db_response = 'None'
	if(conn is not None):
	
		db_response = _loan_dispatch_list_db(search,min,max,conn)
		
	return db_response

def _get_general_account_list_api(code,search,min,max,conn=None):
	if(conn is not None):
		db_response = _get_general_account_list_db(code,search,min,max,conn)		
	
	return db_response
 
def _get_activity_log_api(search,min,max,conn=None):
        if(conn is not None):
                db_response = _get_activity_log_db(search,min,max,conn)

        return db_response 
	
def _get_debtor_list_api(search,min,max,conn=None):
	if(conn is not None):
		db_response = _get_debtor_list_db(search,min,max,conn)		
	
	return db_response

def _get_defaulter_list_api(search,min,max,conn=None):
	if(conn is not None):
		db_response = _get_defaulter_list_db(search,min,max,conn)		
	
	return db_response
	
def _get_account_summary_api(min,max,conn=None):
	if(conn is not None):
		db_response = _get_account_summary_db(min,max,conn)		
	
	return db_response	
	
def _vet_loan_request_api(data,conn=None):
        db_response = None
	if(data is not None):
                loan_id = data.get("id",None)
                user    = data.get("user",None)
                mobile  = data.get("mobile",None)
                notes   = data.get("notes",None)
                head    = data.get("head",None) 
		db_response = _vet_loan_request_db(loan_id,mobile,user,notes,head,conn)

	return db_response

def _withdraw_electronic_cash_api(msisdn,amount,conn=None):
        db_response = None
	if(conn is not None and msisdn is not None):
		db_response = _withdraw_electronic_cash_db(msisdn,amount,conn)
	
	return db_response

def _read_loan_request_queue_sys(conn=None):
	if(conn is not None):
		db_response = _get_loan_request_db(conn)		
	
	return db_response
	
def _mark_loan_request_processed_sys(_id,msisdn,ref_no,conn=None):
	if(conn is not None and _id is not None and msisdn is not None and ref_no is not None):
		db_response = _mark_loan_request_processed_db(_id,msisdn,ref_no,conn)		
	
	return db_response
	
def _read_loan_payout_queue_sys(conn=None):
	if(conn is not None):
		db_response = _get_loan_payout_db(conn)		
	
	return db_response	
	
def _queue_loan_sys(reference_no,msisdn,loan_amount,approved_by,has_collateral,conn=None):
	if(conn is not None and reference_no is not None and msisdn is not None and loan_amount is not None):
		db_response = _queue_loan_db(reference_no,msisdn,loan_amount,approved_by,has_collateral,conn)
		
	return db_response
	
def _dispatch_loan_sys(reference_no,msisdn,amount,loan_amount,repayment_amount,interest_amount,loan_duration,notify_1,conn=None):
	if(conn is not None and reference_no is not None and msisdn is not None and amount is not None and loan_amount is not None and repayment_amount is not None and interest_amount is not None):
		db_response = _dispatch_loan_db(reference_no,msisdn,amount,loan_amount,repayment_amount,interest_amount,loan_duration,notify_1,conn)
		
	return db_response
	
def _record_loan_transaction_sys(amount,msisdn,reference_no,account_name,transaction_type,conn=None):
	if(conn is not None and amount is not None and msisdn is not None and reference_no is not None and account_name is not None and transaction_type is not None):
		db_response = _record_loan_transaction_db(amount,msisdn,reference_no,account_name,transaction_type,conn)
		
	return db_response

def _record_loan_fee_sys(msisdn,reference_no,loan_fee,account_name,conn=None):
	if(conn is not None and msisdn is not None and reference_no is not None and loan_fee is not None and account_name is not None):
		db_response = _record_loan_fee_db(msisdn,reference_no,loan_fee,account_name,conn)
		
	return db_response

def _get_customer_bal_api(msisdn,conn=None):
        if(conn is not None):
                db_response = _get_customer_bal_db(msisdn,conn)
        
        return db_response

def _read_payment_list_sys(conn=None):
	if(conn is not None):
		db_response = _get_payment_list_db(conn)		
	
	return db_response

def _loan_payment_sys(msisdn,amount,transaction_no,conn=None):
	if(conn is not None):
		db_response = _loan_payment_db(msisdn,amount,transaction_no,conn)		
	
	return db_response 

def  _PAYMENT_TEST_sys(trx,amount,msisdn,conn=None):
        if(conn is not None):
            db_response = _PAYMENT_TEST_db(trx,amount,msisdn,conn)

        return db_response

def _acitivity_log_sys(msisdn,activity_description,conn=None):
        if(conn is not None):
                db_response  = _acitivity_log_db(msisdn,activity_description,conn)

        return db_response 

def _loan_due_list_sys(conn=None):
	if(conn is not None):
		db_response = _loan_due_list_db(conn)

	return db_response

def _loan_due_alert_handler_sys(recid,seconds,notification_cnt,hr,msisdn,amount,expected_payment_date,conn=None):
	if(conn is not None):
		db_response = _loan_due_alert_handler_db(recid,seconds,notification_cnt,hr,msisdn,amount,expected_payment_date,conn)

	return db_response

def _defaulter_list_sys(conn=None):
	if(conn is not None):
		db_response = _defaulter_list_db(conn)

	return db_response

def _calc_loan_penalty_sys(amount,loan_duration,rate,msisdn,conn=None):
	if(conn is not None):
		db_response = _calc_loan_penalty_db(amount,loan_duration,rate,msisdn,conn)

	return db_response

def _flag_as_defaulter_sys(recid,msisdn,loan_amount,expected_pay_day,duration,conn=None):
        if(conn is not None):
                db_response = _flag_as_defaulter_db(recid,msisdn,loan_amount,expected_pay_day,duration,conn)

        return db_response      

def _log_dispatched_loan_sys(msisdn,repayment_amount,interest,conn=None):
        if(conn is not None):
                db_response = _log_dispatched_loan_db(msisdn,repayment_amount,interest,conn)

        return db_response

def _get_action_on_temp_sys(conn=None):
        if(conn is not None):
                db_response = _get_action_on_temp_db(conn)

        return db_response

def _delete_action_on_temp_sys(msisdn,conn=None):
        if(conn is not None):
                db_response = _delete_action_on_temp_db(msisdn,conn)

        return db_response

#============================================================================================================
#------------------------------------FREKNUR INVESTMENT.
#============================================================================================================

def _get_asset_config_params_api(conn=None):
        if(conn is not None):
                db_response = _get_asset_config_params_db(conn)

        return db_response

def _get_customer_portfolio_api(msisdn,conn=None):
        if(conn is not None):
                db_response = _get_customer_portfolio_db(msisdn,conn)

        return db_response

def _get_asset_list_api(lower_min,lower_max,conn=None):
        if(conn is not None):
                db_response = _get_asset_list_db(lower_min,lower_max,conn)

        return db_response

def _get_customer_list_api(search,lower_min,lower_max,conn=None):
        if(conn is not None):
                db_response = _get_customer_list_db(search,lower_min,lower_max,conn)

        return db_response    

def _get_asset_trend_list_api(msisdn,conn=None):
        if(conn is not None):
                db_response = _get_asset_trend_list_db(msisdn,conn)

        return db_response

def _add_new_asset_api(acronym,name,price,total,conn=None):
        if(conn is not None):
                db_response = _add_new_asset_db(acronym,name,price,total,conn)

        return db_response

def _modify_asset_api(uid,acroynm,name,price,unit,conn=None):
        if(conn is not None):
                db_response = _modify_asset_db(uid,acroynm,name,price,unit,conn)

        return db_response

def _add_purchase_request_api(msisdn,uid,description,price,no_of_unit,cost,conn=None):
        if(conn is not None):
                db_response = _add_purchase_request_db(msisdn,uid,description,price,no_of_unit,cost,conn)

        return db_response

def _add_sale_request_api(msisdn,uid,description,price,no_of_unit,cost,conn=None):
        if(conn is not None):
                db_response = _add_sale_request_db(msisdn,uid,description,price,no_of_unit,cost,conn)

        return db_response

def _get_asset_config_list_api(lower_min,lower_max,conn=None):
        if(conn is not None):
                db_response = _get_asset_config_list_db(lower_min,lower_max,conn)

        return db_response

def _create_asset_config_api(fee,min_limit,max_limit,xes,conn=None):
        if(conn is not None):
                db_response = _create_asset_config_db(fee,min_limit,max_limit,xes,conn)

        return db_response

def _modify_asset_config_api(cnf_id,fee,min_limit,max_limit,xes,conn=None):
        if(conn is not None):
                db_response = _modify_asset_config_db(cnf_id,fee,min_limit,max_limit,xes,conn)

        return db_response

def _get_sale_request_list_api(msisdn,is_owner,conn=None):
        if(conn is not None):
                db_response = _get_sale_request_list_db(msisdn,is_owner,conn)

        return db_response

def _place_bid_api(asset_id,asset_name,owner_msisdn,bidder_msisdn,qty,bid_price,conn=None):
        if(conn is not None):
                db_response = _place_bid_db(asset_id,asset_name,owner_msisdn,bidder_msisdn,qty,bid_price,conn)
        
        return db_response

def _get_bid_list_api(msisdn,conn=None):
        if(conn is not None):
                db_response = _get_bid_list_db(msisdn,conn)
        
        return db_response

def _get_accepted_bid_api(msisdn,conn=None):
        if(conn is not None):
                db_response = _get_accepted_bid_db(msisdn,conn)

        return db_response

def _accept_bid_api(bid_id,asset_id,conn=None):
        if(conn is not None):
                db_response = _accept_bid_db(bid_id,asset_id,conn)

        return db_response

def _read_purchase_request_queue_sys(conn=None):
        if(conn is not None):
                db_response = _get_asset_purchase_request_db(conn)

        return db_response

def _get_asset_master_sys(uid,conn=None):
        if(conn is not None):
                db_response = _get_asset_master_db(uid,conn)

        return db_response

def _get_customer_bal_sys(msisdn,conn=None):
        if(conn is not None):
                db_response = _get_customer_bal_db(msisdn,conn)

        return db_response

def _book_keeping_sys(msisdn,uid,description,unit_price,qty,wallet_bal,total_cost,handling_fee,conn=None):
        if(conn is not None):
                db_response = _book_keeping_db(msisdn,uid,description,unit_price,qty,wallet_bal,total_cost,handling_fee,conn)

        return db_response

def _get_handling_fee_sys(conn=None):
        if(conn is not None):
                db_response = _get_handling_fee_db(conn)

        return db_response

def _purchase_asset_on_market_sys(msisdn,qty,asset_name,asset_uid,price,current_wallet_bal,total_cost,fee_earned,conn=None):
        if(conn is not None):
                db_response = _purchase_asset_on_market_db(msisdn,qty,asset_name,asset_uid,price,current_wallet_bal,total_cost,fee_earned,conn)

        return db_response

def _purchase_on_alternate_market_api(asset_id,msisdn,asset_name,unit_price,qty,total_cost,conn=None):
        if(conn is not None):
                db_response = _purchase_on_alternate_market_db(asset_id,msisdn,asset_name,unit_price,qty,total_cost,conn)

        return db_response

def _alert_to_seller_on_market_sys(msisdn,asset_name,duration,offer_price,message,conn=None):
        if(conn is not None):
                db_response = _alert_to_seller_on_market_db(msisdn,asset_name,duration,offer_price,message,conn)

        return db_response

def _record_secured_loan_request_api (msisdn,amount,collateral,has_collateral,conn=None):
        if(conn is not None):
                db_response = _record_secured_loan_request_db(msisdn,amount,collateral,has_collateral,conn)

        return db_response

def _get_collateral_log_sys(msisdn,conn=None):
        if(conn is not None):
                db_response = _get_collateral_log_db(msisdn,conn)

        return db_response

def _get_loan_settings_configs_api():
        db_response = _get_loan_settings_configs()

        return db_response

def _read_collateral_portfolio_temp_sys(conn=None):
        if(conn is not None):
                db_response = _read_collateral_portfolio_temp_list_db(conn)

        return db_response  

def _delete_own_sell_requet_api(asset_id,msisdn,conn=None):
        if(conn is not None):
                db_response = _delete_own_sell_requet_db(asset_id,msisdn,conn)

        
        return db_response


def _calc_loan_amount_with_interest_rebate_sys(collateral_amount,loan_amount,interest_adjustment_rate,loan_interest_rate,collateral_percent):
        db_response = _calc_loan_amount_with_interest_rebate(collateral_amount,loan_amount,interest_adjustment_rate,loan_interest_rate,collateral_percent)

        return db_response


#===================================================================================================
#-.                                 END FREKNUR INVESTMENT
#===================================================================================================


#===================================================================================================
#-.                                 START DESPOSIT
#===================================================================================================
def _wallet_deposit_api(amount,msisdn,conn):
        if(conn is not None):
                db_response = _wallet_deposit_db(amount,msisdn,conn)

        return db_response

#===================================================================================================
#-.                                 END DEPOSIT
#===================================================================================================


#===================================================================================================
#-.                                 START WALLET TRANSFER
#===================================================================================================
def _peer_wallet_transfer_api(msisdn,beneficiary_msisdn,amount,conn):
        if(conn is not None):
                db_response = _peer_wallet_transfer_db(msisdn,beneficiary_msisdn,amount,conn)

        return db_response
#===================================================================================================
#-.                                 END WALLET TRANSFER
#===================================================================================================

#===================================================================================================
#-.                                  START FREKNUR COMMERCE
#===================================================================================================

def _inventory_list_api(search,lower_min,lower_max,conn=None):
        if(conn is not None):
                db_response = _inventory_list_db(search,lower_min,lower_max,conn)

        return db_response

def _get_sales_record_list_api(search,lower_min,lower_max,conn=None):
        if(conn is not None):
                db_response = _get_sales_record_list_db(search,lower_min,lower_max,conn)

        return db_response

def _create_inventory_record_api(name,qty,price,conn=None):
        if(conn is not None):
                db_response = _create_inventory_record_db(name,qty,price,conn)

        return db_response

def _save_inventory_image_path_api(record_id,path,conn=None):
        if(conn is not None):
                db_response = _save_inventory_image_path_db(record_id,path,conn)

        return db_response

def _create_sale_record_api(product_uid,qty,total,msisdn,conn=None):
        if(conn is not None):
                db_response = _create_sale_record_db(product_uid,qty,total,msisdn,conn)

        return db_response

def _modify_sale_record_api(qty,total,uid,conn=None):
        if(conn is not None):
                db_response = _modify_sale_record_db(qty,total,uid,conn)

        return db_response
#===================================================================================================
#-.                                  END  FREKNUR COMMERCE
#===================================================================================================    


def _read_sell_request_on_market_queue_sys(conn=None):
        if(conn is not None):
                db_response = _get_sell_request_on_market_db(conn)

        return db_response

def _delete_alternative_market_request_sys(msisdn,conn=None):
        if(conn is not None):
                db_response = _delete_alternative_market_request_db(msisdn,conn)

        return db_response    

def _save_to_redis_cache_api(key,data,conn):
        if(conn is not None):
                db_response = _save_to_redis_cache(key,data,conn)

        return db_response

def _read_redis_cache_api(key,conn):
        if(conn is not None):
                db_response = _read_redis_cache(key,conn)

        return db_response

def _delete_from_redis_cache_api(key,conn):
        if(conn is not None):
                db_response = _delete_from_redis_cache(key,conn)

        return db_response
