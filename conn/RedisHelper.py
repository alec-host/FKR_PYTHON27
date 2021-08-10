#!/usr/bin/python
"""
developer skype: alec_host
"""
import os
import redis
import logging

from configs.freknur_settings import redis_params,redis_key_params

log = logging.getLogger()

class RedisHelper():
	
    """
    -=================================================
    -.write to redis.
    -=================================================
    """
    def _save_to_redis_cache(self,key,data,conn):
        status = "fail"
        try:
            conn.set(key,data)
            staus = "success"
        except Exception,e:
            log.error(e)
            raise
        
        return status
	
	
    """
    -=================================================
    -.read redis.
    -=================================================
    """
    def _read_redis_cache(self,key,conn):
        msg = None
        try:
            msg = conn.get(key)
        except Exception,e:
            log.error(e)
            raise
    
        return msg


    """
    -=================================================
    -.delete data from redis.
    -=================================================
    """
    def _delete_from_redis_cache(self,key,conn):
        status = "fail"
        try:
            conn.delete(key)
            staus = "success"
        except Exception,e:
            log.error(e)
            raise
        
        return status


    """
    -=================================================
    -.redis subscriber.
    -=================================================
    """
    def _subscribe_redis(self,topic_channel,conn):
        try:
            pubsub = conn.pubsub()
            pubsub.subscribe(topic_channel)
            
            return pubsub
        except Exception,e:
            log.error(e)
            raise


    """
    -=================================================
    -.redis publisher.
    -=================================================
    """
    def _publish_redis(self,topic_channel,payload,conn):
        try:
            conn.publish(topic_channel,str(payload))
        except Exception,e:
            log.error(e)
            raise
	
    """
    -=================================================
    -.redis connection
    -=================================================
    """
    def create_redis_connection(self):
        try:
            connection = redis.StrictRedis(host=redis_params['host'], port=redis_params['port'], password=redis_params['passwd'], decode_responses=True)
        except Exception as e:
            log.error(e)
            raise
        
        return connection
		
		
    """
    -=================================================
    -.redis key.
    -=================================================
    """
    def redis_access_key(self):
        return redis_key_params['USER_WALLET_BAL_KEY'], redis_key_params['USER_PORTFOLIO_KEY'], redis_key_params['USER_GRAIN_STMT'], redis_key_params['USER_LOAN_STMT'],\
               redis_key_params['USER_WALLET_STMT'], redis_key_params['SHOP_LIST'], redis_key_params['ASSET_LIST'], redis_key_params['PUSH_NOTIFICATION_KEY']

