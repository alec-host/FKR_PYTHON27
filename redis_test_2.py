import redis
  

redis_host = "localhost"
redis_port =  6379
redis_password = "*freknur2030"


def message_box():
    try:

        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

        msg = r.get("msisdn")

        r.delete("msisdn")

        print(msg)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    message_box()                        
