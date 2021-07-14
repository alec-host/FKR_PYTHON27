#!/usr/bin/python

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
    
        return Fals

import json
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self).default(o)
