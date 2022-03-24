import pdftotext
import os
import re
import regex_store
import csv
import datetime

PATH_TO_BROKERAGE_STATEMENTS = "../Brokerage Statements/Fidelity Statements/2021 Monthly/"

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
FIDELITY_ACCOUNT_VALUE_PAGE = 1 - 1

entries = {}

def bookkeep_month_entry(broker, date, account_value, deposits, withdraws):
    entries[date] = [deposits, withdraws, account_value]


def parse_statement(broker, pdf_path):
    # Load your PDF
    with open(pdf_path, "rb") as f:
        pdf = pdftotext.PDF(f)
        txt = pdf[FIDELITY_ACCOUNT_VALUE_PAGE]

        # get the 2nd line; ex: "February 1, 2022 - February 28, 2022"
        date_builder = []
        is_on_second_line = False
        for i in range(100):
            char = txt[i]
            if char == "\n":
                if is_on_second_line: 
                    break
                else: 
                    is_on_second_line = True
            if is_on_second_line:
                date_builder.append(char)
        
        raw_date = "".join(date_builder)
        ending_date = raw_date.split("-")[1] #the latter half

        formatted_date = datetime.datetime.strptime(ending_date, ' %B %d, %Y').strftime('%Y-%m')



        regex = "Beginning Account Value\n(Additions\n)?(Subtractions\n)?(Transaction Costs, Fees & Charges\n)?Change in Investment Value[\* ]*\nEnding Account Value[\* ]*\n(Accrued Interest \(AI\)\n)?(Ending Account Value Incl. AI\n)?"

        line_entries = re.findall(regex, txt)

        # print(line_entries)
        subtractions_entry = False
        additions_entry = False
        transactions_costs_fees_charges_entry = False
        accured_interest_entry = False
        ending_account_val_including_accured_interest_entry = False


        if len(line_entries) == 0:
            # the statement has a different format; try other regex
            regex = "Beginning Account Value|Additions|Subtractions|Transaction Costs, Fees & Charges|Change in Investment Value|Ending Account Value|Accrued Interest \(AI\)|Ending Account Value Incl. AI"

            line_entries = re.findall(regex, txt)
        else:
            line_entries = line_entries[0]

        # determine if there is an entry for subtractions, additions, and transactions_costs_fees_charges
        for entry in line_entries:
            entry = entry.replace("\n", "")

            if entry == "Additions":
                additions_entry = True
            elif entry == "Subtractions":
                subtractions_entry = True
            elif entry == "Transaction Costs, Fees & Charges":
                # note, this debit is already included in subtractions
                transactions_costs_fees_charges_entry = True
            elif entry == "Accrued Interest (AI)":
                accured_interest_entry = True
            elif entry == "Ending Account Value Incl. AI":
                ending_account_val_including_accured_interest_entry = True

        # grab the #s associated with each entry
        entry_data_regex = "This Period\n\nYear-to-Date\n\n([\s\S]*)$"
        target_text = re.findall(entry_data_regex, txt)
        
        if not target_text:
            # if "This Period" text is found elsewhere
            entry_data_regex = "Year-to-Date\n\n([\s\S]*)$"
            target_text = re.findall(entry_data_regex, txt)

        digits_regex = "\-?\$?([\d,]*\.\d\d)|\n-\n"
        # prepending "\n" to the search text is because the digits_regex will not pick up the first "-" unless it's there
        # however, this is an edge case because only on the first account statement (there, the Beginning Account value
        # is going to be 0, so it's represented with a "-")
        digits = re.findall(digits_regex, "\n" + target_text[0])

        # print(digits)
        next_digit_iterator = iter(digits)


        begn_account_val_this_period = next(next_digit_iterator)
        begn_account_val_ytd = next(next_digit_iterator)

        additions_this_period, additions_ytd = 0, 0
        if additions_entry:
            additions_this_period = next(next_digit_iterator)
            additions_ytd = next(next_digit_iterator)
        
        subtractions_this_period, subtractions_ytd = 0, 0
        if subtractions_entry:
            subtractions_this_period = next(next_digit_iterator)
            subtractions_ytd = next(next_digit_iterator)

            if transactions_costs_fees_charges_entry:
                transactions_costs_fees_charges_this_period = next(next_digit_iterator)
                transactions_costs_fees_charges_ytd = next(next_digit_iterator)

        change_in_investment_val_this_period = next(next_digit_iterator)
        change_in_investment_val_ytd = next(next_digit_iterator)

        ending_account_val_this_period = next(next_digit_iterator)
        ending_account_val_ytd = next(next_digit_iterator)

        # both of these should be true, but separating them just in case
        accured_interest, ending_account_val_including_accured_interest = 0, 0
        if accured_interest_entry:
            accured_interest = next(next_digit_iterator)
        if ending_account_val_including_accured_interest_entry:
            ending_account_val_including_accured_interest = next(next_digit_iterator)


        def verify_and_float_num(num):
            if num:
                return float(num)
            else:
                return 0

        # note: the regex did not take into account (+) or (-) nums; this is because their signs are all intuitive
        beginning_account_val = verify_and_float_num(begn_account_val_this_period)
        account_val_change = verify_and_float_num(change_in_investment_val_this_period)
        contributions = verify_and_float_num(additions_this_period)
        withdrawals = verify_and_float_num(subtractions_this_period) * -1
        account_val = verify_and_float_num(ending_account_val_this_period)

        added_together = beginning_account_val + account_val_change + contributions + withdrawals
        if round(added_together, 2) == account_val:
            print("check")
        else:
            added_together = beginning_account_val - account_val_change + contributions + withdrawals
            if round(added_together, 2) == account_val:
                print("check 2")
            else:
                print("didn't add up")

        print(contributions, withdrawals, account_val)

    bookkeep_month_entry(broker, formatted_date, account_val, contributions, withdrawals)


files = os.listdir(PATH_TO_BROKERAGE_STATEMENTS)
print(files)

for file in files:
    try:
        if file[-4:] == ".pdf": #last 4 chars
            # continue
            print("now parsing {}, which is found at {}".format(file, PATH_TO_BROKERAGE_STATEMENTS + file))
            parse_statement("Fid", PATH_TO_BROKERAGE_STATEMENTS + file)
    except ValueError as err:
        print("opening file")
        print(err.args)


header = ['year-month', 'deposits', 'withdrawals', 'ending_balance']

with open('data-fidelity.csv', 'w') as csv_writer:
    writer = csv.writer(csv_writer)
    writer.writerow(header)

    # write the data
    for date, data in sorted(entries.items()):
        payload = data
        payload.insert(0, date)
        writer.writerow(payload)