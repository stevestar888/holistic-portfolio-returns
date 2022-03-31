import pdftotext
import os
import re
import constants
import csv

# unable to support deposit & withdrawls right now -- only account value

PATH_TO_BROKERAGE_STATEMENTS = "../Brokerage Statements/Robinhood Statements/"

entries = {}

def bookkeep_month_entry(broker, date, account_value, deposits, withdraws):
    entries[date] = [deposits, withdraws, account_value]


def parse_date(date):
    try:
        parts = date.split("/")
        month, day, year = parts
        return "{}-{}".format(year, month)
    except:
        raise ValueError("failed splitting date")


def parse_statement(broker, pdf_path):
    # Load your PDF
    with open(pdf_path, "rb") as f:
        pdf = pdftotext.PDF(f)
        pages = len(pdf)

    try:
        # get account value & date
        page = pdf[0]

        date_regex = "\d\d\/\d\d\/\d\d\d\d to (\d\d)\/(\d\d)\/(\d\d\d\d)"        
        date = re.findall(date_regex, page)

        month, day, year = date[0]
        friendly_date = "{}-{}".format(year, month)

        # 2 ways to find account value
        # the first method is most accurate, but doesn't work all the time

        account_value_regex = "Portfolio Value\n\n\$[\d,]*\.\d\d\n\n(\$[\d,]*\.\d\d)"
        account_value_list = re.findall(account_value_regex, page)

        if account_value_list:
            account_value = account_value_list[0]
        else:
            # known issue: 2021-06.pdf -- the order of the 4 x 2 is not same as others
            account_value_regex = "\$[\d,]*\.\d\d"
            account_value_list = re.findall(account_value_regex, page)
            
            if account_value_list:
                # all statements before March 2020 have a different 3 rows x 2 cols;
                # after then, it has 4 rows x 2 cols; 
                # the entry on the bottom right shows last month's ending balance 

                if int(year) < 2020 or (int(year) == 2020 and int(month) < 3):
                    account_value = account_value_list[5]
                else:
                    account_value = account_value_list[7]


    except ValueError as err:
        print("Error with account value, date")
        print(err.args)

    ### too difficult to extract deposits / withdrawls ###

    bookkeep_month_entry(broker, friendly_date, account_value, 0, 0)


files = os.listdir(PATH_TO_BROKERAGE_STATEMENTS)
print(files)

for file in files:
    try:
        # if file[-4:] == ".pdf" and file[:4] != "2019": #last 4 chars & not 2019
        if file[-4:] == ".pdf": #last 4 chars
            # continue
            print("now parsing {}, which is found at {}".format(file, PATH_TO_BROKERAGE_STATEMENTS + file))
            parse_statement("Schwab", PATH_TO_BROKERAGE_STATEMENTS + file)
    except ValueError as err:
        print("opening file")
        print(err.args)


header = ['year-month', 'deposits', 'withdrawals', 'ending_balance']

with open('robinhood-data.csv', 'w') as csv_writer:
    writer = csv.writer(csv_writer)
    writer.writerow(header)

    # write the data
    for date, data in sorted(entries.items()):
        payload = data
        payload.insert(0, date)
        writer.writerow(payload)