DIGIT = "[\d,]*\.\d\d"
DIGIT_WITH_OPTIONAL_DOLLAR = "\$?[\d,]*\.\d\d"
DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN = "-?[\d,]*\.\d\d"

CSV_HEADER = ['year-month', 'deposits', 'withdrawals', 'ending_balance']

HEADER_DATE_INDEX = 0
HEADER_DEPOSIT_INDEX = 1
HEADER_WITHDRAWALS_INDEX = 2
HEADER_ACCOUNT_VALUE_INDEX = 3

# note: the examples under regexes demonstrate one instance of the regex match;
#   the last line is where the captures groups are capturing (unless otherwise noted)

# where you see multiple regexes for deposits or withdraws (e.g., SCHWAB_DEPOSITS_VER1, SCHWAB_DEPOSITS_VER2),
# that's because the order of the actual text after converting from PDF to text can be jumbled around.
# As a result, the location of #s are not always consistent. Through manual testing, I've found
# that there are certain locations where deposits or withdraws are most likely to be found. For example,
# with Schwab, deposits are often right after "Deposits and other Cash Credits"; however, when that's not
# the case, I've had to create a more general regex to capture the value. The more general regex has the potential of capturing the wrong value, so it's a trade off. Overall, I start with a very specific regex. If nothing is captured, then more general regexes are used to find the right value.

################################
# ----------- Schwab -----------
################################

SCHWAB_ACCOUNT_VALUE_PAGE = 3 - 1 # subtract 1 b/c PDF pages are 1-indexed
SCHWAB_PCRA_401K_ACCOUNT_VALUE_PAGE = 4 - 1


SCHWAB_ACCOUNT_VALUE = "Account Value as of (\d\d\/\d\d\/\d\d\d\d):\$ ([\d,]*.\d\d)"
"""
Account Value as of 11/30/2021:$ 36,600.61
capture groups:     ^            ^
"""


SCHWAB_DEPOSITS = "Deposits and other Cash Credits\n\n([\d,]*.\d\d)"
""" (from 2020-08)
Deposits and other Cash Credits

0.00
"""

SCHWAB_DEPOSITS2 = "Deposits and other Cash Credits\nInvestments Sold\n\nThis Period\n\nYear to Date\n\n\$ [\d,]*.\d\d\n\n\$ [\d,]*.\d\d\n\n([\d,]*.\d\d)"
"""
Deposits and other Cash Credits
Investments Sold

This Period

Year to Date

$ 677.37

$ 0,00

2,000.00
"""


SCHWAB_WITHDRAWS = "Withdrawals and other Debits\n\n([\d,]*.\d\d)"
""" (from 2020-08)
Withdrawals and other Debits

0.00
"""

SCHWAB_WITHDRAWS2 = "Investments Purchased\n\n([\d,]*.\d\d)"
"""
Investments Purchased

0.00
"""

SCHWAB_WITHDRAWS3 = "([\d,]*.\d\d)\n\n[\d,]*.\d\d\n\nTotal Cash Transaction Detail\n\n\([\d,]*.\d\d\)\n\n\([\d,]*.\d\d\)\n\nEnding Cash \*\n\n\$ "
"""
Ex: 2020-09

0.00        #capture group

0.00

Total Cash Transaction Detail

(189.74)

(521.84)

Ending Cash *

$ 
"""

#################################
# -------- Apex Brokers ---------
#################################

APEX_ACCOUNT_VALUE_PAGE = 1 - 1 # subtract 1 b/c PDF pages are 1-indexed

# The first regex should catch the majority of the account values.
# However, some cases will not be caugh, so we need additional regexes.
# As the regex versions progress, they get less specific (and therefore more prone to error),
# so that's why the regexes are introduced in a specific order.

# use "?:" for non-capturing group
APEX_ACCOUNT_VALUE_VERSION_1 = "{}\n\n{}\n\n{}\n\n\$({})\n\n(?:NET ACCOUNT BALANCE|Total Equity Holdings)".format(DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_DOLLAR, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN)

APEX_ACCOUNT_VALUE_VERSION_2 = "{}\n{}\n\n{}\n{}\n\n{}\n{}\n\n{}\n\n\$({})\n\nTHIS PERIOD".format(DIGIT_WITH_OPTIONAL_DOLLAR, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_DOLLAR, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN)

APEX_ACCOUNT_VALUE_VERSION_3 = "{}\n{}\n\n{}\n{}\n\n{}\n\n\$({})".format(DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_DOLLAR, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN)

APEX_ACCOUNT_VALUE_VERSION_4 = "{}\n\n{}\n\n{}\n\n\$({})".format(DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN, DIGIT_WITH_OPTIONAL_DOLLAR, DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN)


# Apex participates in what's called the Securities Lending Program (SLP), which is when
# Apex lends out the shares you have for others to short. Sometimes, you may receive a 
# kickback. So `XFER FFS TO CASH` and `XFER CASH FROM FFS` are journal entries for the back end, 
# and do not impact the cash balance.

# "FFS is the record of our delivery company. Since you have participated in the securities lending income program, 
# our delivery company will need to make some adjustments. There will be no impact on your account itself. 
# You will see a negative balance and a positive balance in your account. These two strokes are offset."

APEX_DEPOSITS_NORMAL_VERSION = "[^(XFER FFS TO CASH)|(XFER CASH FROM FFS)]\nACH DEPOSIT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*({})".format(DIGIT_WITH_OPTIONAL_DOLLAR)
APEX_DEPOSITS_FFS_VERSION = "[(XFER FFS TO CASH)|(XFER CASH FROM FFS)]\nACH DEPOSIT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*{}\n({})".format(DIGIT_WITH_OPTIONAL_DOLLAR, DIGIT_WITH_OPTIONAL_DOLLAR)

APEX_WITHDRAWALS_NORMAL_VERSION = "[^(XFER FFS TO CASH)|(XFER CASH FROM FFS)]\nACH DISBURSEMENT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*({})".format(DIGIT_WITH_OPTIONAL_DOLLAR)
APEX_WITHDRAWALS_FFS_VERSION = "[(XFER FFS TO CASH)|(XFER CASH FROM FFS)]\nACH DISBURSEMENT(?:\n|SEN\(\d*\)|CREDIT|DEBIT|PRICE|)*{}\n({})".format(DIGIT_WITH_OPTIONAL_DOLLAR, DIGIT_WITH_OPTIONAL_DOLLAR)

"""
XFER CASH FROM FFS
ACH DEPOSIT

$0.84
250.00



XFER FFS TO CASH
ACH DEPOSIT

0.84
250.00
"""


MONEY_WEIGHT_RETURNS_EXAMPLE = """
Ex1: Starting Balance = 100, Ending Balance = 1000
Holding Period #		Deposits		Withdrawals
1						1000			0
2						0				50
3						0				100
4						20				200

inflows: 100 + 1000 + 20 = 1120
outflows: -50 + -100 + -200 + -1000 = -1350

Calculations
100 						# initial account balance
+ 1000 / (1 + IRR)^1 
- 50 / (1 + IRR)^2
- 100 / (1 + IRR)^3
+ 20 / (1 + IRR)^4  -  200 / (1 + IRR)^4
=
1000 / (1 + IRR)^5	        # ending account balance


Ex2: Starting Balance = 0, Ending Balance = 264
Holding Period #		Deposits		Withdrawals
1						100				0
2						118				0

Calculations
100 						# initial account balance
+ 118 / (1 + IRR)^1 
=
264 / (1 + IRR)^2		    # ending account balance

IRR = 13.86%
"""