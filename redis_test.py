import redis





redis_host = "localhost"
redis_port =  6379
redis_password = "*freknur2030"



def message_box():
    try:

        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

        r.set("msisdn","Hello Redis!!!")


        #msg = r.get("msidn")

        print("Writing to redis")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    message_box()
