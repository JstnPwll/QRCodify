# QRCodify
QR Code bot for Reddit

**MAKE SURE YOU DON'T COMMIT YOUR USERNAME OR PASSWORD TO GITHUB AFTER SETTING UP config_bot.py!**

This code depends on [PRAW](https://pypi.python.org/pypi/praw) to connect with Reddit, and [pyqrcode](https://pypi.python.org/pypi/PyQRCode) to generate the QR code data based on input.

The bot will wait for username mentions and then convert any data occuring after the username into a QR code. 
The code is posted as a followup comment using ASCII characters. Due to inconsistencies in subreddit CSS and browser defaults for monospace fonts, the QR codes may not display properly.

More information can be found at http://www.qrcodify.io
