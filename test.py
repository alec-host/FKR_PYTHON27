import os

import ast
import json

from multiprocessing import Process

from conn.RedisHelper import RedisHelper
from conn.configs.freknur_settings import redis_pubsub_params

redis_helper = RedisHelper()


def _shopping_cart():
    rd = redis_helper.create_redis_connection()
    pubsub = redis_helper._subscribe_redis(redis_pubsub_params['SHOP_PUBSUB'],rd)

    for message in pubsub.listen():

        msg = json.loads(json.dumps(message.get("data")).encode('unicode-escape').decode('utf-8'))

        if(msg  != 1):

            s = ast.literal_eval(msg)
            cart   = s.get("cart")
            msisdn = s.get("msisdn")
            total  = s.get("grand_total")

            for items in cart:
                product_name = items.get("name")
                price = items.get("price")
                product_id = items.get("product_id")
                qty = items.get("qty")
                #-.routine call.
                print(str(product_name) +" "+ str(price) +"  "+ str(product_id) +" "+str(qty)+"  "+str(msisdn))
        

if __name__ == "__main__":
    try:
        Process(target=_shopping_cart, args=()).start()
    except KeyboardInterrupt:
        pass
    finally:
        print("app exiting...")
