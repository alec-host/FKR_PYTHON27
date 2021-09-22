#!/usr/bin/python
  
"""
developer skype: alec_host
"""

import os
import sys

import DataGrid

from DataGridDbHelper import DataGridDbHelper

class DataGridModel():
    """
    -=================================================
    -.method: customer list.
    -=================================================
    """
    def _get_customer_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_customer_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string


    """
    -=================================================
    -.method: account summary list.
    -=================================================
    """
    def _get_account_summary_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_account_summary_db(DataGrid.DataGrid(0,content['lower_min'],content['lower_max'],0,0),conn)

        return j_string


    """
    -=================================================
    -.method: stock account summary list.
    -=================================================
    """
    def _get_stock_account_summary_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_stock_account_summary_db(DataGrid.DataGrid(0,content['lower_min'],content['lower_max'],0,0),conn)

        return j_string


    """
    -=================================================
    -.method: loan request list.
    -=================================================
    """
    def _get_loan_request_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_loan_request_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string



    """
    -=================================================
    -.method: debtor list.
    -=================================================
    """
    def _get_debtor_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_debtor_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string


    """
    -=================================================
    -.method: defaulter list.
    -=================================================
    """
    def _get_defaulter_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_defaulter_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string


    """
    -=================================================
    -.method: loan dispatch list.
    -=================================================
    """
    def _get_loan_dispatch_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_loan_dispatch_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string



    """
    -=================================================
    -.method: general accounts.
    -=================================================
    """
    def _get_general_account_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_general_account_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],content['code'],0),conn)

        return j_string


    """
    -=================================================
    -.method: system activity list.
    -=================================================
    """
    def _get_activity_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_activity_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string



    """
    -=================================================
    -.method: inventory list.
    -=================================================
    """
    def _inventory_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._inventory_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string


    """
    -=================================================
    -.method: inventory list.
    -=================================================
    """
    def _get_sale_inventory_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper.get_sale_inventory_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string


    """
    -=================================================
    -.method: asset configuration list.
    -=================================================
    """
    def _get_asset_config_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_asset_config_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string


    """
    -=================================================
    -.method: asset configuration list.
    -=================================================
    """
    def _get_asset_list_api(self,content,conn):

        j_string = None

        data_grid_db_helper = DataGridDbHelper()

        if(conn is not None):
            #-.routine call.
            j_string = data_grid_db_helper._get_asset_list_db(DataGrid.DataGrid(content['search'],content['lower_min'],content['lower_max'],0,0),conn)

        return j_string
