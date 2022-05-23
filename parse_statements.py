import parse_schwab
import parse_fidelity
import parse_robinhood
import parse_apex

import calculate_holistic_returns

import os
import constants
import csv

# currently supported brokerages:
SCHWAB = "Schwab"
FIDELITY = "Fidelity"
ROBINHOOD = "Robinhood"

# "Apex Clearing" is the clearing firm for these brokerages:
PUBLIC = "Public.com"
FIRSTRADE = "Firstrade"
SOFI = "Sofi"
WEBULL = "Webull"


class StatementParser:
    def __init__(self, broker, nickname, files_path):
        self.broker = broker
        self.account_nickname = nickname
        self.files_path = files_path
        self.entries = {}

        self.parse_statements()


    def parse_statements(self):
        files = os.listdir(self.files_path)
        for file in files:
            try:
                if file[-4:] == ".pdf": #ensure it's a pdf file
                    print("Parsing {} statement \"{}\", which is found at \"{}\"".format(
                        self.broker, file, self.files_path + file))
                    
                    if self.broker == SCHWAB:
                        entry = parse_schwab.parse_statement(self.files_path + file)
                    elif self.broker == FIDELITY:
                        entry = parse_fidelity.parse_statement(self.files_path + file)
                    elif self.broker in [PUBLIC, WEBULL, FIRSTRADE, SOFI]:
                        entry = parse_apex.parse_statement(self.files_path + file)
                    elif self.broker == ROBINHOOD:
                        entry = parse_robinhood.parse_statement(self.files_path + file)
                    else:
                        print("Broker not supported")
                        exit()

                    key = entry[0]
                    payload = entry[1]
                    # print(key)
                    # print(payload)
                    # print("\n")

                    self.entries[key] = payload

            except ValueError as err:
                print("Error opening file: " + err.args)


    def info(self):
        print("\"{}\" is a(n) {} account and has {} total entries".format(self.account_nickname, self.broker, len(self.entries)))


    def calculate_returns(self):
        calculate_holistic_returns.calc_returns(self.entries, self.broker, self.account_nickname)


    def export_data_to_csv(self):
        csv_file_name = "account-data_{}.csv".format(self.account_nickname)
        with open(csv_file_name, 'w') as csv_writer:
            writer = csv.writer(csv_writer)
            writer.writerow(constants.CSV_HEADER)

            # write the data
            for key, data in sorted(self.entries.items()):
                col1 = key
                if self.broker == FIDELITY:
                    account_num, date = key
                    col1 = "{} {}".format(account_num, date)

                payload = data
                payload.insert(0, col1)
                writer.writerow(payload)


SCHWAB_RIRA_STATEMENTS = "../Brokerage Statements/Schwab Roth IRA Statements/"
SCHWAB_DAD_TAXABLE_STATEMENTS = "../Brokerage Statements/Dad Taxable/"
SCHWAB_401K_STATEMENTS = "../Brokerage Statements/Schwab 401k Statements/"

FIDELITY_2021_STATEMENTS = "../Brokerage Statements/Fidelity Statements/2021 Monthly/"
FIDELITY_2022_STATEMENTS = "../Brokerage Statements/Fidelity Statements/2022 Monthly/"
PUBLIC_STATEMENTS = "../Brokerage Statements/Public Statements/"
FIRSTRADE_STATEMENTS = "../Brokerage Statements/Firstrade Statements/"
ROBINHOOD_STATEMENTS = "../Brokerage Statements/Robinhood Statements/"


# EXAMPLE
# variable_for_account = StatementParser(SCHWAB FIDELITY ROBINHOOD etc, "nickname", "path_to_the_folder_containing_statements")
# variable_for_account.export_data_to_csv()

# REAL EXAMPLE
schwab_roth_ira = StatementParser(SCHWAB, "Schwab Roth IRA", SCHWAB_RIRA_STATEMENTS)
schwab_roth_ira.export_data_to_csv()
schwab_roth_ira.calculate_returns()

# test = StatementParser(PUBLIC, "test", "../Brokerage Statements/test/")
# test.export_data_to_csv()
# test.calculate_returns()


# fid = StatementParser(FIDELITY, "Fid2021", "../Brokerage Statements/Fidelity Statements/2021 Monthly/")
# fid.export_data_to_csv()
# fid.info()


# pub = StatementParser(PUBLIC, "public.com", PUBLIC_STATEMENTS)
# pub.export_data_to_csv()
# pub.info()


# rh = StatementParser(ROBINHOOD, "rh", ROBINHOOD_STATEMENTS)
# rh.export_data_to_csv()
# rh.info()