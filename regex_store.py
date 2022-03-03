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