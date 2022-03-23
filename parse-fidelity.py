import pdftotext
import os
import re
import regex_store
import csv

PATH_TO_BROKERAGE_STATEMENTS = "../Brokerage Statements/Fidelity Statements/2021 Monthly"

"""




Luckily, all of the account value and withdrawal/deposit information is on the first page.
Unfortunately, the statements has some inconsistencies. Some statements have this near the top:
    Envelope # BLRJWCBBCCJJS

    $42.25

    Change from Last Period:


Some statements have this section, followed by the #s associated with them
    Beginning Account Value
    Additions
    Subtractions
    Transaction Costs, Fees & Charges
    Change in Investment Value *
    Ending Account Value **
    Accrued Interest (AI)
    Ending Account Value Incl. AI

After some entries, there could be an asterisk. 
The `Accrued Interest (AI)` and `Ending Account Value Incl. AI` are only on some statements.

There could be entries for `Additions` and `Subtractions`. If Subtractions is an entry, then there could be also an entry for “Transaction Costs, Fees & Charges”

The account value is from the entry for “Ending Account Value”

"""

#subtract 1 b/c PDF pages are 1-indexed
SCHWAB_ACCOUNT_VALUE_PAGE = 1 - 1

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
        if IS_PCRA:
            account_value_pdf_page = pdf[SCHWAB_PCRA_401K_ACCOUNT_VALUE_PAGE]
        else: 
            account_value_pdf_page = pdf[SCHWAB_ACCOUNT_VALUE_PAGE]
        result = re.search(regex_store.ACCOUNT_VALUE, account_value_pdf_page) #using capture groups
        date, account_value = result.groups()
        sort_friendly_date = parse_date(date)

    except ValueError as err:
        print("Error with account value, date")
        print(err.args)

    try:
        for page in range(pages - 1, -1, -1):
            text = pdf[page]

            withdrawal_amount = 0
            deposit_amount = 0

            digit = "[($]?[\d,]*\.\d\d\)?"
            
            purchases_sales = re.findall("Transaction Detail - Purchases & Sales", text)
            deposits = re.findall("The total deposits activity for the statement period was ({})".format(digit), text)
            withdrawals = re.findall("The total withdrawals activity for the statement period was ({})".format(digit), text)

            if withdrawals and deposits:
                withdrawal_amount = withdrawals[0]
                deposit_amount = deposits[0]
                break

            if purchases_sales:
                # the statement doesn't have a section for Deposits / withdrawals; stop parsing
                break

    except ValueError as err:
        print("deposit / withdraw")
        print(err.args)

    bookkeep_month_entry(broker, sort_friendly_date, account_value, deposit_amount, withdrawal_amount)


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

with open('schwab-data.csv', 'w') as csv_writer:
    writer = csv.writer(csv_writer)
    writer.writerow(header)

    # write the data
    for date, data in sorted(entries.items()):
        payload = data
        payload.insert(0, date)
        writer.writerow(payload)