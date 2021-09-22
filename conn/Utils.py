#!/usr/bin/python

import json
import decimal

"""
developer skype: alec_host
"""

class Utils():

    def is_number(self,input_string):
        try:
            float(input_string)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(input_string)

            return True
        except(TypeError, ValueError):
            pass
    
        return False

    def decimal_default(self,obj):
        if isinstance(obj,decimal.Decimal):
            return float(obj)

        raise TypeError

"""
-.class: encode decimal value.
"""
class DecimalEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return (str(o))
        return json.JSONEncoder.default(self,o)


"""
-.class: combine two json obj.
"""
class JsonManager():
    def conbine(jObj1,jObj2):
        for k, v in jObj1.items():
                if k in jObj2:
                    if isinstance(v, dict):
                        combine(jObj1[k],jObj2[k])
                    else:
                        jObj1[k] = jObj1[k] + jObj2[k]

