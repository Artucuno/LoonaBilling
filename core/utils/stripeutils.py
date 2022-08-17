import sys, os
import json
import stripe

def getPaymentCustomer(intent):
    for f in os.listdir('data/user'):
        if intent in os.listdir(f'data/user/{f}/payments'):
            return f
