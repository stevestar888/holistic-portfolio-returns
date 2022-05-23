import pdftotext
import re
import constants

IS_PCRA = False


def parse_date(date):
    try:
        parts = date.split("/")
        month, day, year = parts
        return "{}-{}".format(year, month)
    except:
        raise ValueError("failed splitting date")


def parse_statement(pdf_path):
    # Load your PDF
    with open(pdf_path, "rb") as f:
        pdf = pdftotext.PDF(f)
        pages = len(pdf)

    try:
        # get account value & date
        if IS_PCRA:
            account_value_pdf_page = pdf[constants.SCHWAB_PCRA_401K_ACCOUNT_VALUE_PAGE]
        else: 
            account_value_pdf_page = pdf[constants.SCHWAB_ACCOUNT_VALUE_PAGE]
        result = re.search(constants.SCHWAB_ACCOUNT_VALUE, account_value_pdf_page) #using capture groups

        if result:
            date, account_value = result.groups()
            parsed_date = parse_date(date)
        else:
            date = "-"
            account_value = "-"
            parsed_date = "-"

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

    return (parsed_date, [deposit_amount, withdrawal_amount, account_value])