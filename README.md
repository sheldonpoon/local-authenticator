# local-authenticator

a simple python app that loads a desktop authenticator so that i can stop constantly checking my phone

# warning

i'm doing zero security setup here (to start) so use at your own risk ... or don't ... whatever, i'm not your mom

# usage

1. install python
2. install pyotp and pyperclip using pip
3. create "otp_secrets.json" file in the following format:

[
    {
        "name": "NAME",
        "secret": "SECRETSECRETSECRET",
        "pinned": false
    }
]