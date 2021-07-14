#!/usr/bin/python

"""
developer skype: alec_host
"""

import os
import datetime
import signal
from json import JSONEncoder


"""
-=================================================
-.class.
-=================================================
"""
def date_time_encoder(JSONEncoder):
        
        def default(self, obj):
                if isinstance(obj,(datetime.date,datetime.datetime)):
                        return obj.isoformat()
