# holistic_portfolio_returns

If you have multiple brokerage accounts, you know it can be difficult to calculate t total performance across all of your portfolios. And even within a particular account, if you have made deposits or withdrawals, then the graph of returns may look strange...

![A very odd looking returns chart as a result of a complete withdrawal followed by deposits](assets/example_return.jpg)

This project attempts to give you a holistic view of how your investment portfolios are doing by parsing the monthly portfolio statements that you receive from your brokerages! You can also see the aggregate deposit and withdrawal numbers. 

Input: PDFs of monthly brokerage statements \
Output: a .csv file containing the deposit, withdrawal, and balance value for every given month + a summary of portfolio returns

Portfolio return calculations are based off of the same information in the .csv file described above (so monthly data on deposits, withdrawals, and the account value). As a result, returns are not precise, but are still reflective of a portfolio’s long-term trend. One interesting feature (that is still WIP) is you can benchmark the portfolio against a market index by simulating what the value of the portfolio would be if you bought or sold SPY or QQQ instead of your portfolio.

Currently, it supports supports: \
• Schwab \
• Robinhood (only account value and date, not withdrawals or contributions) \
• Brokers who use Apex Clearing (which includes Public, Firstrade, M1, Sofi, Webull, Ally, Bettermint, Axos, Wealthsimple, etc.; for the full list, see https://investorjunkie.com/stock-brokers/broker-clearing-firms/)

Planning to support: \
• TDAmeritrade \
• Vanguard

The only file you need to interface with is `parse_statements.py`, where you need to add the path to the folder that contains your broker’s portfolio statements; note, the statements can have nay name, bb they need to have come from the same brokerage.




# Libraries used

PDF extraction via the pdf-to-text library \
(You probably don't have this and should consult this website for installation instructions: https://pypi.org/project/pdftotext/) \
`pip3 install pdftotext`

Financial Data pull (for Index-tracking ETFs):
https://github.com/ranaroussi/yfinance \ 
`pip3 install yfinance`