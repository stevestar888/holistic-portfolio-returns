ACCEPTABLE_ERROR = 0.01 #1% error
INITIAL_LOWER_RETURN_BOUND = 0.0 #lower bound of returns, measured in %
INITIAL_UPPER_RETURN_BOUND = 50.0 #upper bound of returns, measured in %


# solve for discount rate (r) using binary search:
# 1. establish upper and lower bounds for r (`estab_initial_return_bounds`)
# 2. continuously find mid and reset upper and lower bounds (`calc_money_weighted_return`)
#     -> stop when starting and ending values are within 1% of each other

# example
"""
This comes from CFA level 1, Kaplan book 5 page #17-18. 
t0: purchase 1 share for $100
t1: purchase another share for $120, but share from t0 paid a $2 dividend
    -> inflow of $120-$118=$2
t2: sale of two shares for $130 each, and both paid a dividend of $2
    -> outflow of 2 * $130 = $260 + $4 = $264

In math:
    100 / (1+r)^0 + 120 / (1+r)^1 = 264 / (1+r)^2

In variables:
    starting_balance = 100
    cash_flows = [118]
    ending_balance = 264

r = 13.86%

This is a good example to show how MWR works, but here, dividends are counted as outflows. 
This project doesn't have that insight, so the monthly deposits/withdrawals as cash flows. 
As a result, the MWR that is calculated here lumps all the entire value of the account together, 
regardless of how much it is comprised of securities or cash. This shouldn't be too big of a deal.
You can use these scenarios as a test (both will have a MWR of 0%):

    starting_balance = 900.0
    cash_flows = [100,0,0,0,0,0,0]
    ending_balance = 1000

    starting_balance = 900.0
    cash_flows = [100, -100, 100, -100, 100, -100,]
    ending_balance = 900.0
"""


def apply_discount_rate(cash_flow, discount_rate, period):
    return cash_flow / (1 + discount_rate) ** period


def calc_discounted_cash_flows(starting_balance, cash_flows, ending_balance, r):
    cumulative = starting_balance
    r = r / 100 #convert percent into decimal
    t = 1 #starts at 1 because starting_balance was t=0

    for cf in cash_flows:
        cumulative += apply_discount_rate(cf, r, t)
        t += 1

    ending = apply_discount_rate(ending_balance, r, t)
    return(cumulative, ending)


def estab_initial_return_bounds(starting_balance, cash_flows, ending_balance):
    lower = INITIAL_LOWER_RETURN_BOUND #lower bound of returns, measured in %
    upper = INITIAL_UPPER_RETURN_BOUND #upper bound of returns, measured in %

    if ending_balance > starting_balance + sum(cash_flows): #positive return: lower > 0, but ensure upper is big enough
        cumulative, ending = calc_discounted_cash_flows(starting_balance, cash_flows, ending_balance, upper)

        # determine upper bound
        while cumulative < ending:
            cumulative, ending = calc_discounted_cash_flows(starting_balance, cash_flows, ending_balance, upper)
            upper += 50.0

    else: #negative return: upper < 0, but find lower that's small enough
        upper = 0.0
        lower = -10.0
        cumulative, ending = calc_discounted_cash_flows(starting_balance, cash_flows, ending_balance, lower)

        # determine lower bound
        while cumulative > ending:
            cumulative, ending = calc_discounted_cash_flows(starting_balance, cash_flows, ending_balance, lower)
            lower -= 10.0

    return (lower, upper)


def calc_money_weighted_return(starting_balance, cash_flows, ending_balance):
    lower, upper = estab_initial_return_bounds(starting_balance, cash_flows, ending_balance)

    while lower <= upper:
        mid = lower + (upper - lower) / 2
        cumulative, ending = calc_discounted_cash_flows(starting_balance, cash_flows, ending_balance, mid)

        # stop iteration if we are within error bound
        current_error = abs(ending - cumulative)
        if current_error < ACCEPTABLE_ERROR:
            # print("finished with error of {}".format(current_error))
            # print("rate of return of {}%".format(mid))
            # print("cumulative, ending", cumulative, ending)
            return round(mid, 2)

        if cumulative > ending: #r is too high
            upper = mid
        else: #r is not high enough
            lower = mid



# starting_balance = 900.0
# cash_flows = [100, -1004, 1020, -1500, 1200, -1001]
# ending_balance = 900.0

# money_weighted_return = calc_money_weighted_return(starting_balance, cash_flows, ending_balance)
# print(money_weighted_return, "%")