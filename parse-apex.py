import pdftotext
import os
import re
import regex_store
import csv
import datetime

# apex is the clearing firm for Public, Firstrade, M1, Sofi, Webull, Ally, Bettermint, Axos, Wealthsimple, etc
# for the full list, see https://investorjunkie.com/stock-brokers/broker-clearing-firms/
PATH_TO_BROKERAGE_STATEMENTS = "../Brokerage Statements/Public Statements/"

#subtract 1 b/c PDF pages are 1-indexed
ACCOUNT_VALUE_PAGE = 1 - 1

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
        account_value_pdf_page = pdf[ACCOUNT_VALUE_PAGE]

        # get the first line
        date_builder = []
        for i in range(100):
            char = account_value_pdf_page[i]
            if char == "\n":
                break
            date_builder.append(char)
        
        raw_date = "".join(date_builder)
        ending_date = raw_date.split("-")[1] #the latter half

        formated_date = datetime.datetime.strptime(ending_date, ' %B %d, %Y').strftime('%Y-%m')

        digit_with_dollar = "\$[\d,]*\.\d\d"
        digit = "-?[\d,]*\.\d\d"

        # regexes get more and more specific

        # use "?:" for non-capturing group
        account_regex = "{}\n\n{}\n\n{}\n\n\$({})\n\n(?:NET ACCOUNT BALANCE|Total Equity Holdings)".format(digit, digit, digit_with_dollar, digit)
        account_value = re.findall(account_regex, account_value_pdf_page)

        if not account_value:
            account_regex = "{}\n{}\n\n{}\n{}\n\n{}\n{}\n\n{}\n\n\$({})\n\nTHIS PERIOD".format(digit_with_dollar, digit, digit, digit, digit, digit, digit_with_dollar, digit)
            account_value = re.findall(account_regex, account_value_pdf_page)

        if not account_value:
            account_regex = "{}\n{}\n\n{}\n{}\n\n{}\n\n\$({})".format(digit, digit, digit, digit, digit_with_dollar, digit)
            account_value = re.findall(account_regex, account_value_pdf_page)

        if not account_value:
            account_regex = "{}\n\n{}\n\n{}\n\n\$({})".format(digit, digit, digit_with_dollar, digit)
            account_value = re.findall(account_regex, account_value_pdf_page)

        account_value = account_value[0]

    except ValueError as err:
        print("Error with account value, date")
        print(err.args)


    try:
        withdrawal_amount = 0
        deposit_amount = 0
        has_triggered = False

        for page in range(pages - 1, -1, -1):
            text = pdf[page]

            digit = "[\d,]*\.\d\d"

            # deposits
            deposits_regex = "ACH DEPOSIT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*\$?({})".format(digit)
            deposits_list = re.findall(deposits_regex, text)
            
            # withdrawls
            withdrawls_regex = "ACH DISBURSEMENT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*\$?({})".format(digit)
            withdrawls_list = re.findall(withdrawls_regex, text)

            if withdrawls_list or deposits_list:
                has_triggered = True
                withdrawal_amount += sum(map(float, withdrawls_list))
                deposit_amount += sum(map(float, deposits_list))
            elif has_triggered: #if there are no more withdrawls or deposits listed, and we're already seen the section for them, no more need to look
                break
            

    except ValueError as err:
        print("deposit / withdraw")
        print(err.args)

    bookkeep_month_entry(broker, formated_date, account_value, deposit_amount, withdrawal_amount)


files = os.listdir(PATH_TO_BROKERAGE_STATEMENTS)
print(files)

for file in files:
    try:
        if file[-4:] == ".pdf": #last 4 chars
            # continue
            print("now parsing {}, which is found at {}".format(file, PATH_TO_BROKERAGE_STATEMENTS + file))
            parse_statement("Schwab", PATH_TO_BROKERAGE_STATEMENTS + file)
    except ValueError as err:
        print("opening file")
        print(err.args)


header = ['year-month', 'deposits', 'withdrawals', 'ending_balance']

with open('data-apex.csv', 'w') as csv_writer:
    writer = csv.writer(csv_writer)
    writer.writerow(header)

    # write the data
    for date, data in sorted(entries.items()):
        payload = data
        payload.insert(0, date)
        writer.writerow(payload)