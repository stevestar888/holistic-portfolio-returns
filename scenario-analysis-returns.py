import constants
import csv
import datetime

DRIP = True

with open('data-schwab.csv', 'r') as csv_reader:
    reader = csv.reader(csv_reader)
    
    header = next(reader)
    print(header)

    balance = 0
    shares = 0.0
    encountered_first_row = False

    for row in reader:
        date = row[constants.HEADER_DATE_INDEX]
        year = datetime.datetime.strptime(date, '%Y-%m').strftime('%Y')
        month = datetime.datetime.strptime(date, '%Y-%m').strftime('%m')
        
        deposits = row[constants.HEADER_DEPOSIT_INDEX]
        withdrawals = row[constants.HEADER_WITHDRAWALS_INDEX]
        account_val = row[constants.HEADER_ACCOUNT_VALUE_INDEX]

        if not encountered_first_row:
            balance = account_val - withdrawals
            encountered_first_row = True

        # what if you bought $XYZ with the entire deposit?
        
        # what if you sold $XYZ with the entire withdrawal?

        # any dividends pay in period?
        if DRIP:
            shares += 0