#!/usr/bin/env python3
import sys, os
import timeit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

s = """\
import seneca.smart_contract_tester as sct
import seneca.test as test

test.clear_database()
sct.set_up()

send_one_sc_str = '''
import currency
currency.transfer_coins('FALCON', 1.0)
'''

sct.run_contract_file_as_user('./seneca/example_contracts/currency.seneca', '1234', 'currency')

for i in range(0,100):
    sct.run_contract_as_user(send_one_sc_str, 'STU', i)
"""


t = timeit.timeit(stmt=s, number=1)
print(100 / t)
