#!/usr/bin/python

class Loan():
    def __init__(self,uid,msisdn,amount,collateral_size,has_collateral):
        self.uid = uid
        self.msisdn = msisdn
        self.amount = amount
        self.collateral_size = collateral_size
        self.has_collateral = has_collateral
