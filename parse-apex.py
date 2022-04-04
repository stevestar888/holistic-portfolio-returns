import pdftotext
import os
import re
import constants
import csv
import datetime


PATH_TO_BROKERAGE_STATEMENTS = "../Brokerage Statements/Public Statements/"

entries = {}

def bookkeep_month_entry(broker, date, account_value, deposits, withdraws):
    entries[date] = [deposits, withdraws, account_value]
    

def parse_statement(broker, pdf_path):
    # Load your PDF
    with open(pdf_path, "rb") as f:
        pdf = pdftotext.PDF(f)
        pages = len(pdf)

    # get account value & date
    try:
        account_value_pdf_page = pdf[constants.APEX_ACCOUNT_VALUE_PAGE]

        # get the first line; ex: "January 1, 2021 - January 31, 2021"
        date_builder = []
        for i in range(100):
            char = account_value_pdf_page[i]
            if char == "\n":
                break
            date_builder.append(char)
        
        raw_date = "".join(date_builder)
        ending_date = raw_date.split("-")[1] #the latter half

        formatted_date = datetime.datetime.strptime(ending_date, ' %B %d, %Y').strftime('%Y-%m')


        account_value = re.findall(constants.APEX_ACCOUNT_VALUE_VERSION_1, account_value_pdf_page)
        if not account_value:
            account_value = re.findall(constants.APEX_ACCOUNT_VALUE_VERSION_2, account_value_pdf_page)
        if not account_value:
            account_value = re.findall(constants.APEX_ACCOUNT_VALUE_VERSION_3, account_value_pdf_page)
        if not account_value:
            account_value = re.findall(constants.APEX_ACCOUNT_VALUE_VERSION_4, account_value_pdf_page)
        
        if account_value:
            account_value = account_value[0]
        else:
            # TODO
            pass

    except ValueError as err:
        print("Error with account value or date")


    # get withdrawals & deposits amount
    try:
        withdrawal_amount = 0
        deposit_amount = 0
        has_triggered = False

        # the subsection detailing "Total Funds Paid And Received" is towards the end of the statement,
        # parse page by page starting from the back
        for page in range(pages - 1, -1, -1):
            text = pdf[page]

            deposits_list = []
            withdrawals_list = []

            # deposits
            deposits_list = re.findall(constants.APEX_DEPOSITS_NORMAL_VERSION, text)
            if not deposits_list:
                deposits_list = re.findall(constants.APEX_DEPOSITS_FFS_VERSION, text)
            
            # withdrawals
            withdrawals_list = re.findall(constants.APEX_WITHDRAWALS_NORMAL_VERSION, text)
            if not withdrawals_list:
                withdrawals_list = re.findall(constants.APEX_WITHDRAWALS_FFS_VERSION, text)

            # tally deposits & withdrawals
            if withdrawals_list or deposits_list:
                has_triggered = True
                
                #clean list element and also turn them into floats
                formatted_withdrawals_list = [float(amount.replace(",", "").replace("$", "")) for amount in withdrawals_list]
                formatted_deposits_list = [float(amount.replace(",", "").replace("$", "")) for amount in deposits_list]
                
                withdrawal_amount += sum(formatted_withdrawals_list)
                deposit_amount += sum(formatted_deposits_list)
            elif has_triggered: #if there are no more withdrawals or deposits listed, and we're already seen the section for them, no more need to look
                break
            
    except ValueError as err:
        print("Error with getting the deposit / withdraw: statement for {}".format(formatted_date))

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
        print("Error opening file '{}'".format(file))


with open('data-apex.csv', 'w') as csv_writer:
    writer = csv.writer(csv_writer)
    writer.writerow(constants.CSV_HEADER)

    # write the data
    for date, data in sorted(entries.items()):
        payload = data
        payload.insert(0, date)
        writer.writerow(payload)
        # print(date, data)