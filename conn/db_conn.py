#!/usr/bin/python

import MySQLdb

class NoResultException(Exception):
    """ Exception raised when no result is obtained from cursor.execute
    statement"""
    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message

class NoServiceIDException(Exception):
    """ Exception raised when no ServiceID while sendSms"""
    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message

class DB():               
    def execute_query(self, db_connection, sql, params):
        """ Insert data into the database
        Keyword arguments:
            db_connection -- The connection to the database.
            sql -- The sql to be executed.
            params -- A parameter list holding values to be used in the sql.        
        """
        try:
            cursor = db_connection.cursor()
            result = cursor.execute(sql, params)
            if not result:
                sql_stmt = sql % params
                raise NoResultException('SQL Execution Error',\
                        'SQL:%s' % sql_stmt)
        except MySQLdb.DatabaseError:
            raise
        except TypeError:
            raise
        except Exception:
            raise
			

    def retrieve_all_data_params(self, db_connection, sql, params):
        """ Retrieve Data from the database
        
            Retrieve data from the database, returns a dictionary that 
            holds the results.
        
            Keyword arguments:
            db_connection -- The connection to the database.
            sql -- The sql to be executed.
            params -- A parameter list holding values to be used in the sql.
        
        """
        results = None
        try:
            cursor = db_connection.cursor()
            cursor.execute(sql, params)
            results = cursor.fetchall()
        except MySQLdb.DatabaseError:
            raise
        return results
    
    def retrieve_all_data(self, db_connection, sql):
        """ Retrieve Data from the database
        
            Retrieve data from the database, returns a dictionary that 
            holds the results.
        
            Keyword arguments:
            db_connection -- The connection to the database.
            sql -- The sql to be executed.
        
        """
        results = None
        try:
            cursor = db_connection.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
        except MySQLdb.DatabaseError:
            raise
        return results
