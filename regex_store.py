# note: in the examples, the last line is where the captures groups are capturing (unless otherwise noted)

ACCOUNT_VALUE = "Account Value as of (\d\d\/\d\d\/\d\d\d\d):\$ ([\d,]*.\d\d)"
"""
Ex:

Account Value as of 11/30/2021:$ 36,600.61
capture groups:     ^            ^
"""


DEPOSITS = "Deposits and other Cash Credits\n\n([\d,]*.\d\d)"
"""
Ex: 2020-08

Deposits and other Cash Credits

0.00
"""

DEPOSITS2 = "Deposits and other Cash Credits\nInvestments Sold\n\nThis Period\n\nYear to Date\n\n\$ [\d,]*.\d\d\n\n\$ [\d,]*.\d\d\n\n([\d,]*.\d\d)"
"""
Ex:

Deposits and other Cash Credits
Investments Sold

This Period

Year to Date

$ 677.37

$ 0,00

2,000.00
"""


WITHDRAWS = "Withdrawals and other Debits\n\n([\d,]*.\d\d)"
"""
Ex: 2020-08

Withdrawals and other Debits

0.00
"""


WITHDRAWS2 = "Investments Purchased\n\n([\d,]*.\d\d)"
"""
Ex:

Investments Purchased

0.00
"""


WITHDRAWS3 = "([\d,]*.\d\d)\n\n[\d,]*.\d\d\n\nTotal Cash Transaction Detail\n\n\([\d,]*.\d\d\)\n\n\([\d,]*.\d\d\)\n\nEnding Cash \*\n\n\$ "
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

DIGIT_WITH_OPTIONAL_DOLLAR = "\$?[\d,]*\.\d\d"
DIGIT_WITH_OPTIONAL_NEGATIVE_SIGN = "-?[\d,]*\.\d\d"

# the first regex should catch the majority of the account values.
# however, it's not perfect, so we need additional regexes.
# as the regex versions progress, they get more and more specific to catch edge cases.

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