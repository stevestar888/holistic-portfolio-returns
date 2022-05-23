import yfinance as yf
import datetime


def calculate_scenario_analysis(cash_flows, benchmark, starting_date):
    starting_year = int(starting_date.split("-")[0])
    starting_month = int(starting_date.split("-")[1])
    starting_date = 1

    start = datetime.datetime(starting_year, starting_month, starting_date)

    

    # get historical market data
    ticker = yf.Ticker(benchmark)
    returns_hist = ticker.history(start=start, interval = "1mo") # returns a pandas.core.frame.DataFrame

    # cash_flows.append(0.0) #add a remaining cash flow so the calculation just in case the benchmark pays a dividend in the last time period
    
    cash_flow_index = 0
    num_shares = 0

    for date, row in returns_hist.iterrows():
        if cash_flow_index > len(cash_flows) - 1:
            break

        if row['Dividends'] != 0.0:
            divd_per_share = row['Dividends']
            num_shares += (num_shares * divd_per_share) / closing_price
        else:
            closing_price = round(row['Close'], 2)
            num_shares += cash_flows[cash_flow_index] / closing_price
            cash_flow_index += 1

        date_time_object = date.date()
        formatted_date = date_time_object.strftime('%Y-%m')

        benchmark_ending_balance = round(num_shares * closing_price, 2)

        print("At {}, you have {} shares, worth {} each, for a total of ${}\n".format(formatted_date, num_shares, closing_price, benchmark_ending_balance))

    return benchmark_ending_balance