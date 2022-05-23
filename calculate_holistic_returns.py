import constants
import yahoo_finance
import calc_money_weighted_returns

# import calc_scenario_analysis

# CSV_FILE_TO_READ = "data-schwab.csv"
# CSV_FILE_TO_READ = "account-data_public.com.csv"

SHOW_DEFINITIONS = True
SHOW_EXAMPLES = True


def convert_to_float(text):
    try: 
        text = str(text)
        text = text.replace("$", "").replace(",", "")
        return float(text)
    except: #probably the number was 0 (or blank)
        print("error converting to float")
        return 0


def calc_returns(entries, broker, account_nickname="investment-account"):
    inflows = []
    outflows = []
    cash_flows = []
    monthly_HPRs = []
    num_of_months = 0

    starting_balance = None
    ending_balance = None

    starting_date = None
    ending_date = None

    num_of_months = len(entries)

    count = 0
    for date, row in sorted(entries.items()):
        count += 1
        # if broker == FIDELITY:
        #     account_num, date = key
        #     col1 = "{} {}".format(account_num, date)

        payload = row #the rows here already have the date as a column

        if not starting_balance:
            starting_balance = convert_to_float(payload[constants.HEADER_ACCOUNT_VALUE_INDEX])
            starting_date = payload[constants.HEADER_DATE_INDEX]
            prev_month_balance = convert_to_float(payload[constants.HEADER_ACCOUNT_VALUE_INDEX])
            continue

        if count == num_of_months:
            ending_balance = convert_to_float(payload[constants.HEADER_ACCOUNT_VALUE_INDEX])
            ending_date = payload[constants.HEADER_DATE_INDEX]

        inflow = convert_to_float(payload[constants.HEADER_DEPOSIT_INDEX])
        outflow = convert_to_float(payload[constants.HEADER_WITHDRAWALS_INDEX])
        
        inflows.append(inflow)
        outflows.append(outflow)
        cash_flows.append(inflow - outflow)

        # for Arithmetic Mean return
        if prev_month_balance > 0:
            holding_period_return = convert_to_float(payload[constants.HEADER_ACCOUNT_VALUE_INDEX]) / prev_month_balance - 1
            monthly_HPRs.append(holding_period_return)
        else: # HPR cannot be calculated
            monthly_HPRs.append(0)
        prev_month_balance = convert_to_float(payload[constants.HEADER_ACCOUNT_VALUE_INDEX])

        # return (starting_balance, ending_balance, starting_date, ending_date)


    output_name = "returns_{}.txt".format(account_nickname)
    with open(output_name, 'w') as writer:
        def write(text, newlines=1):
            for _ in range(newlines):
                writer.write("\n")
                print("\n")

            print(text)
            writer.write(text)

        write("Calculating your portfolio's holistic returns...!", 0)
        write("---------------------------")

        # Calculate deposit & withdrawals
        write("Inflows: {}".format(inflows), 3)
        write("Outflows: {}".format(outflows), 2)
        write("Net cash flows: {}".format(cash_flows), 2)

        write("Account Starting Value: {}".format(starting_balance), 3)
        if SHOW_DEFINITIONS:
            write("  (the initial value of the account at {})".format(starting_date))

        write("Account Ending Value: {}".format(ending_balance), 2)
        if SHOW_DEFINITIONS:
            write("  (the ending value of the account at {})".format(ending_balance))

        write("Total change in account value: {}".format(ending_balance - starting_balance), 2)
        if SHOW_DEFINITIONS:
            write("  (change in the account's value over {} months)".format(num_of_months))


        contributions = sum(inflows)
        withdrawals = sum(outflows)
        net_contributions = contributions - withdrawals
        ending_balance_net_of_contributions = ending_balance - net_contributions

        write("Total contributions: {}".format(contributions), 2)
        if SHOW_DEFINITIONS:
            write("  (all of the $ that was deposited into the account)")

        write("Total withdrawals: {}".format(withdrawals), 2)
        if SHOW_DEFINITIONS:
            write("  (all of the $ that was withdrawn from the account)")

        write("Net withdrawals/contributions: {}".format(net_contributions), 2)
        if SHOW_DEFINITIONS:
            write("  (total amount of contributions subtracted against total amount of withdrawals)")

        write("Account Ending Value, net of withdrawals/contributions: {}".format(ending_balance_net_of_contributions), 2)
        if SHOW_DEFINITIONS:
            write("  (account balance at the end of {}, after subtracting contributions of {} and adding back in withdrawals of {})".format(
                ending_balance, contributions, withdrawals
            ))
        

        # Calculate returns
        write("---------------------------")
        write("Now calculating returns...", 3)

        write("All returns are based off of account values as described in the monthly brokerage statements. Most brokerages calculate the account value as all securities + cash in the account. As a result, all returns are pre-tax (i.e., gross of tax) and in nominal terms (i.e., not adjusted for inflation) but do factor in transaction fees (more on this later).", 2)

        write("Depositing money into the account is treated as a “contribution”, while withdrawing  is considered a “withdrawal”. In almost all cases, dividends, interest on uninvested funds, free stocks from referral bonuses, etc. are already factored into the account value (just double checked this is the case for Public/Apex), and not considered as an inflow. Similarly, trading commissions, ADR fees, ADR dividend reductions, etc. are a deduction to the account balance, not an outflow. However, in some cases (e.g., Schwab’s 401k bookkeeping fee) can be considered as inflows/outflows.", 2)

        write("The terms “holding period” and “holding period return” (HPR) are used frequently. A holding period is a period of time, and can be as long as the entire history of an account (i.e., # of holding period = 1), or an arbitrary length of time. For example, in some calculations, a holding period of 1 month is used. In this case, the starting account balance of a period is the ending account balance of the previous period. Put another way, the ending balance at time = 0 is also the starting balance at time = 1. The Holding Period Return is the % return required to go from the Starting Balance value to the Account Ending value.", 2)

        write("For these 2 calculations, there is 1 holding period, the time period from {} to {}:".format(
            starting_date, ending_date
        ), 2)

        holding_period_return = ending_balance / starting_balance - 1
        write("Holding Period Return (HPR): {}%".format(holding_period_return), 2)
        if SHOW_DEFINITIONS:
            write("  (% change of the account balance from the beginning of the holding period ({}) to the end of the holding period({}))".format(
                starting_date, ending_date
            ))

        adjusted_HPR = ending_balance_net_of_contributions / starting_balance - 1
        write("Adjusted HPR (ending balance is adjusted for deposits/withdrawals): {}%".format(adjusted_HPR), 2)
        if SHOW_DEFINITIONS:
            write("  (% change of the account balance from the holding period return like above, but adjusted so that the ending balance is adjusted for deposits/withdrawals)")


        write("For the following calculations, every holding period is 1 month (making for a total of {} periods). As such, we need to multiply each holding period return by 12 to annualize it".format(num_of_months), 4)

        arith_return = (sum(monthly_HPRs) / num_of_months) * 12 #TODO - this seems too low??
        write("Arithmetic Mean return (annualized): {}%".format(arith_return))
        if SHOW_DEFINITIONS:
            write("(formula (non-annualized): Σ(holding period return) / number of holding periods)")
            write("The holding_period_returns for {} months are: {}".format(num_of_months, monthly_HPRs))


        money_weighted_return = calc_money_weighted_returns.calc_money_weighted_return(starting_balance, cash_flows, ending_balance)
        write("Money-Weighted return: {}%".format(money_weighted_return), 2)

        if SHOW_DEFINITIONS:
            write("MWR takes into consideration the timing and size of inflows and outflows.")
            write("Formula (non-annualized): PresentValue(inflows) = PresentValue(outflows), where the MWR is the discount rate (i.e., IRR)")
            write("All subsequent deposits are treated as inflows, while all withdrawals are treated as outflows. The Starting Balance occurs at time=0 so it’s not discounted, while the Ending Balance is discounted by the total number of holding periods + 1.")

        if SHOW_EXAMPLES:
            write(constants.MONEY_WEIGHTED_RETURNS_EXAMPLE)


        time_weighted_return = 1
        for hpr in monthly_HPRs:
            time_weighted_return *= (1 + hpr)

        time_weighted_return = time_weighted_return ** (1 / len(monthly_HPRs))
        time_weighted_return -= 1

        write("Time-Weighted return: {}%".format(time_weighted_return * 100), 2) #TODO - check the decimals

        if SHOW_DEFINITIONS:
            write("  TWR measures the rate of compounding by taking the geometric mean of the Holding Period Returns. Here, each Holding Period Return is calculated as the % return required to go from the account beginning balance to the ending balance net of contributions/withdrawals. For example, if the balance at the beginning of a holding period were 100 and the holding period’s ending balance were 200 but there was a contribution of 75, the holding period return would be the return required to go from 100 → 200-75 (so (125-100)/100 = 25% return). In a way, the TWR is a hybrid between the “Holding Period Return (adjusted)” and “Geometric Mean” returns. “Holding Period Return (adjusted)” only had 1 holding period and the “Geometric Mean” used holding period returns whose ending period balance did not net out contributions/withdrawals.")
            write("  formula (non-annualized): (same as Geometric Mean return)")
            write("  = ([(1 + HPR_1) * (1 + HPR_2) * ... * (1 + HPR_n)] ^ 1/number of holding periods) - 1")
            write("  = (∏(1 + holding the average) ^ 1/number of holding periods) - 1")
    
        
        write("---------------------------")
        write("Scenario Analysis")

        write("How much what you have if you bought/sold an arbitrary ETF or stock every time your portfolio had an inflow/outflow?")
        write("You can run those scenarios here! Try comparing your portfolio against the S&P 500 ($VOO), the Nasdaq ($QQQ), or an individual stocks like $BRK.B, $MSFT, $AAPL, etc.")
        write("Details: every inflow (outflow), including the initial account balance, is considered a buy (sell) which is executed at the closing ETF/stock price on the 15th of that month. If the \"benchmark\" you are comparing your portfolio against received a dividend, it is reinvested at the price of the day of receipt.")

        benchmark = "VOO"
        scenario_analysis_ending_balance = yahoo_finance.calculate_scenario_analysis(cash_flows, benchmark, starting_date)
        write("Had you invested in your benchmark of {}, you would have ended with ${}".format(benchmark, scenario_analysis_ending_balance), 2)

    print("")
    print("")
    print("Finished with computation...")
    print("Please see \"{}\".txt to see account returns.".format(output_name))