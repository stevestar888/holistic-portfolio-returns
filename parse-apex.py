import pdftotext
import os
import re
import regex_store
import csv
import datetime

# Apex is the clearing firm for Public, Firstrade, M1, Sofi, Webull, Ally, Bettermint, Axos, Wealthsimple, etc
# for the full list, see https://investorjunkie.com/stock-brokers/broker-clearing-firms/
PATH_TO_BROKERAGE_STATEMENTS = "../Brokerage Statements/Firstrade Statements/"

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

        formatted_date = datetime.datetime.strptime(ending_date, ' %B %d, %Y').strftime('%Y-%m')

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

            deposits_list = []
            withdrawls_list = []
            digit_with_optional_dollar = "\$?[\d,]*\.\d\d"

            # deposits
            normal_deposits_regex = "[^(XFER FFS TO CASH)|(XFER CASH FROM FFS)]\nACH DEPOSIT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*({})".format(digit_with_optional_dollar)
            deposits_list = re.findall(normal_deposits_regex, text)

            if not deposits_list:
                deposits_with_ffs_regex = "[(XFER FFS TO CASH)|(XFER CASH FROM FFS)]\nACH DEPOSIT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*{}\n({})".format(digit_with_optional_dollar, digit_with_optional_dollar)
                deposits_list = re.findall(deposits_with_ffs_regex, text)
            
            # withdrawls
            normal_withdrawls_regex = "[^(XFER FFS TO CASH)|(XFER CASH FROM FFS)]\nACH DISBURSEMENT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*({})".format(digit_with_optional_dollar)
            withdrawls_list = re.findall(normal_withdrawls_regex, text)

            if not withdrawls_list:
                dwithdrawls_with_ffs_regex = "[(XFER FFS TO CASH)|(XFER CASH FROM FFS)]\nACH DISBURSEMENT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*{}\n({})".format(digit_with_optional_dollar, digit_with_optional_dollar)
                withdrawls_list = re.findall(dwithdrawls_with_ffs_regex, text)

            # ingest data
            if withdrawls_list or deposits_list:
                has_triggered = True
                
                formatted_withdrawls_list = [float(amount.replace(",", "").replace("$", "")) for amount in withdrawls_list]
                formatted_deposits_list = [float(amount.replace(",", "").replace("$", "")) for amount in deposits_list]
                withdrawal_amount += sum(formatted_withdrawls_list)
                deposit_amount += sum(formatted_deposits_list)
            elif has_triggered: #if there are no more withdrawls or deposits listed, and we're already seen the section for them, no more need to look
                break
            

    except ValueError as err:
        print("deposit / withdraw")
        print(err.args)

    bookkeep_month_entry(broker, formatted_date, account_value, deposit_amount, withdrawal_amount)


files = os.listdir(PATH_TO_BROKERAGE_STATEMENTS)
print(files)

for file in files:
    try:
        if file[-4:] == ".pdf": #last 4 chars
            # continue
            print("now parsing {}, which is found at {}".format(file, PATH_TO_BROKERAGE_STATEMENTS + file))
            parse_statement("Apex", PATH_TO_BROKERAGE_STATEMENTS + file)
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
        # print(date, data)