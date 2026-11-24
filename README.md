# local-authenticator

a simple python app that loads a desktop authenticator so that i can stop constantly checking my phone

# warning

i'm doing zero security setup here (to start) so use at your own risk ... or don't ... whatever, i'm not your mom

# usage

1. install python
2. install pyotp and pyperclip using pip
3. create "otp_secrets.json" file in the following format:

```json
[
    {
        "name": "NAME",
        "secret": "SECRETSECRETSECRET",
        "pinned": false
    }
]
```

# building the executable

turns `authenticator.py` into a standalone `authenticator.exe` so it runs without python installed. these are the exact commands (windows, powershell).

## one-time setup

install the build tool alongside the app's dependencies:

```powershell
py -m pip install pyotp pyperclip pyinstaller
```

## build it

a `authenticator.spec` already exists, so just feed it to pyinstaller — no flags needed:

```powershell
py -m PyInstaller authenticator.spec
```

the finished exe lands in `dist\authenticator.exe`.

if the `.spec` is ever lost and you need to regenerate it from scratch, build directly from the script instead (`--noconsole` hides the stray black terminal window behind the GUI):

```powershell
py -m PyInstaller --onefile --noconsole authenticator.py
```

## run it

put `otp_secrets.json` in the **same folder** as the exe (the app looks for it next to the executable), then double-click `authenticator.exe`.

> note: windows smartscreen / antivirus may flag the unsigned exe the first time — click "more info" then "run anyway".