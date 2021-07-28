#!/usr/bin/python

import redis



class RD():
        def __init__(self):
                self.pool = redis.ConnectionPool()
              
        def rd_connection(self,params):
                return redis.Redis(connection_pool= self.pool)
            


