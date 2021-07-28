#!/usr/bin/python2

import os
import re
import sys
import json
import MySQLdb
import logging
import signal
import Queue

from conn.model import _read_collateral_portfolio_temp_sys,_get_collateral_log_sys,_calc_loan_amount_with_interest_rebate_sys

from conn.configs.freknur_settings import loan_params,accounting_params

from conn.db_helper import create_connection,close_connection,NoResultException

log = logging.getLogger()

def handleLoanBackedByCollateral():
        try:
                while True:
                        db = create_connection()
                        """
                        -.get portfolio list.
                        """
                        items = json.loads(_read_collateral_portfolio_temp_sys(db))
                        """
                        -.loop through each in the list.
                        """
                        if(len(items) > 0):
                                for item in items:
                                        msisdn            = item['msisdn']
                                        collateral_amount = float(item['total_cost'])
                                """
                                -.routine call.
                                """
                                collateral_log = _get_collateral_log_sys(msisdn,db)

                                loan_amount              = float(collateral_log[0])
                                collateral_percentage    = float(collateral_log[1])
                                loan_interest_rate       = float(loan_params[0])
                                interest_adjustment_rate = float(loan_params[1])  

                                interest = _calc_loan_amount_with_interest_rebate_sys(collateral_amount,loan_amount,interest_adjustment_rate,loan_interest_rate)
                        else:

                                collateral_amount = 552.75
                                loan_amount = 1000
                                loan_interest_rate       = float(loan_params[0])
                                interest_adjustment_rate = float(loan_params[1])

                                interest = _calc_loan_amount_with_interest_rebate_sys(collateral_amount,loan_amount,interest_adjustment_rate,loan_interest_rate)
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
                handleLoanBackedByCollateral()
        except KeyboardInterrupt:
                exit(0)                
