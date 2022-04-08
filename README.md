# holistic_portfolio_returns

Parses monthly portfolio statements from brokerages!

Input: PDFs of monthly brokerage statements \
Output: csv of date, deposit, withdrawal, and balance value 

Currently, it supports supports: \
• Schwab \
• Robinhood (only account value and date, not withdrawals or contributions) \
• Apex brokers*



*Apex is the clearing firm for Public, Firstrade, M1, Sofi, Webull, Ally, Bettermint, Axos, Wealthsimple, etc. For the full list, see https://investorjunkie.com/stock-brokers/broker-clearing-firms/


Planning to support: \
• TDAmeritrade \
• Vanguard


Just update PATH_TO_BROKERAGE_STATEMENTS with the folder containing the PDFs of Schwab statements (they can have any name)



stage 2 of the project: calculating returns. We can benchmark the portfolio against an index (I’ll use SPY or QQQ) by simulating what the value of the portfolio would be if you bought or sold SPY or QQQ instead of your portfolio.


# Credits

PDF extraction via the pdf-to-text library:
https://pypi.org/project/pdftotext/#description

Financial Data pull (for Index-tracking ETFs):
https://github.com/ranaroussi/yfinance