# from money_weighted import *
import money_weighted

SHOW_DEFINITIONS = True
SHOW_EXAMPLES = True

starting_balance = 900.0
cash_flows = [100, -1004, 1020, -1500, 1200, -1001]
ending_balance = 900.0

money_weighted_return = money_weighted.calc_money_weighted_return(starting_balance, cash_flows, ending_balance)
print("Money Weighted return: {}%".format(money_weighted_return))

if SHOW_DEFINITIONS:
    print("MWR takes into consideration the timing and size of inflows and outflows.")
    print("Formula (non-annualized): PresentValue(inflows) = PresentValue(outflows), where the MWR is the discount rate (i.e., IRR)")

