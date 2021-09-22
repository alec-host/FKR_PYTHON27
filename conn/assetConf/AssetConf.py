#!/usr/bin/python
"""
developer skype: alec_host
"""

class AssetConf():
    def __init__(self,uid,transaction_fee,minimum_limit,maximum_limit,currency):
        self.uid = uid
        self.transaction_fee = transaction_fee
        self.minimum_limit = minimum_limit
        self.maximum_limit = maximum_limit
        self.currency = currency
