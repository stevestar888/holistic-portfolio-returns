# holistic_portfolio_returns

Parses monthly portfolio statements from brokerages!

Input: PDFs of monthly brokerage statements \
Output: csv of date, deposit, withdrawal, and balance value 

Currently, it supports supports: \
• Schwab \
• Robinhood (only account value and date, not withdrawals or contributions) \
• Apex brokers*



*Apex is the clearing firm for Public, Firstrade, M1, Sofi, Webull, Ally, Bettermint, Axos, Wealthsimple, etc. For the full list, see https://investorjunkie.com/stock-brokers/broker-clearing-firms/




Just update PATH_TO_BROKERAGE_STATEMENTS with the folder containing the PDFs of Schwab statements (they can have any name)


# Credits

PDF extraction via the pdf-to-text library:
https://pypi.org/project/pdftotext/#description
