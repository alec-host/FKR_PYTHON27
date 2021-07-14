#!/usr/bin/python

class Loan():
    def __init__(self,amount,msisdn,collateral_size,has_collateral):
        self.amount = amount
        self.msisdn = msisdn
        self.collateral_size = collateral_size
        self.has_collateral = has_collateral
