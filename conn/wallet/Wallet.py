#!/usr/bin/python
"""
developer skype: alec_host
"""

class Wallet():
    def __init__(self,uid,msisdn,amount,beneficiary_msisdn,activity):
        self.uid = uid
        self.msisdn = msisdn
        self.amount = amount
        self.beneficiary_msisdn = beneficiary_msisdn
        self.activity = activity
