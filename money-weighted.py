ACCEPTABLE_ERROR = 0.01 #1% error

def discount(cash_flow, discount_rate, period):
    return cash_flow / (1 + discount_rate) ** period


def apply_discount_rate(starting_balance, cash_flows, ending_balance, r):
    cumulative = starting_balance
    r = r / 100 #convert percent into decimal
    t = 1 #TODO - decide when to discount first

    for cf in cash_flows:
        cumulative += discount(cf, r, t)
        t += 1

    ending = discount(ending_balance, r, t)

    return(cumulative, ending)


# solve for discount rate (r) using binary search
# 1. establish upper and lower bounds for r
# 2. continuously find mid and reset upper and lower bounds
# 3. stop when starting and ending values are within 1% of each other

# starting_balance = 40.0
# cash_flows = [49.0]
# ending_balance = 122.0

starting_balance = 100.0
cash_flows = [1000.0, -50.0, -100.0, -180]
ending_balance = 1000.0
"""
Ex1: Starting Balance = 100, Ending Balance = 1000
Holding Period #		Deposits		Withdrawals
1							1000				0
2							0					50
3							0					100
4							20					200

inflows: 100 + 1000 + 20 = 1120
outflows: -50 + -100 + -200 + -1000 = -1350
"""


# step 1
lower = 0.0 #lower bound of returns, measured in %
upper = 50.0 #upper bound of returns, measured in %

if ending_balance > starting_balance + sum(cash_flows): #positive return: lower > 0, but ensure upper is big enough
    cumulative, ending = apply_discount_rate(starting_balance, cash_flows, ending_balance, upper)

    # determine upper bound
    while cumulative < ending:
        cumulative, ending = apply_discount_rate(starting_balance, cash_flows, ending_balance, upper)
        upper += 50.0

else: #negative return: upper < 0, but find lower that's small enough
    upper = 0.0
    lower = -10.0
    cumulative, ending = apply_discount_rate(starting_balance, cash_flows, ending_balance, lower)

    # determine lower bound
    while cumulative > ending:
        cumulative, ending = apply_discount_rate(starting_balance, cash_flows, ending_balance, lower)
        lower -= 10.0

# step 2
while lower <= upper:
    mid = lower + (upper - lower) / 2
    cumulative, ending = apply_discount_rate(starting_balance, cash_flows, ending_balance, mid)
    print("mid, lower, upper", mid, lower, upper)
    diff = abs(ending - cumulative)

    # within 1% of ending
    current_error = abs(abs(ending - cumulative)/ending)
    if current_error < ACCEPTABLE_ERROR:
        print("finished with error of {}".format(current_error))
        print("rate of return of {}%".format(mid))
        print("cumulative, ending", cumulative, ending)
        break

    if cumulative > ending: #r is too high
        upper = mid
    else: #r is not high enough
        lower = mid