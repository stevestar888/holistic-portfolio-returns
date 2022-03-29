import yfinance as yf
import datetime


TICKER = "SPY"
start = datetime.datetime(2018, 6, 1)

# get historical market data
ticker = yf.Ticker(TICKER)
returns_hist = ticker.history(start=start, interval = "1mo") # returns a pandas.core.frame.DataFrame

for date, row in returns_hist.iterrows():
    date_time_object = date.date()
    formatted_date = date_time_object.strftime('%Y-%m')

    print(formatted_date)
    if row['Dividends'] != 0.0:
        print("dividend paid:")
        print(row['Dividends'])
    else:
        print("closing price:")
        print(round(row['Close'], 4))
    print("")