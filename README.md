# Accountx

#### Video Demo: https://youtu.be/o4yLRhvQves

#### Description:
<p>Accountx is a smallscale book-keeping app , It will help you keep track of your daily transcations.
It will help you to organise your personal finance. it will give you easy overview of total money you have recieved or paid 
and how much money currently avilable.
</p>
<p>
if you have gravatar account then your profile image automtically update.After creating account when you login first time then you can choose your currency symbol and time zone.
</p>
<p>
accounts page:
Accountx supports multiple accounts so you can create as much as required accounts by default three accounts(self,bank,cash) are created when you signup.
you can edit accounts details cliking on Edit button anytime.if you want to delete account you can delete but if you have created entry for this
account you cann't delete. 
</p>
<p>
Entries page:
you can add entries clicking on create entry button.you will see entry form where you find your added account in From and To field.
you can download transactions of any specific person or total transactions as csv file.on entries page search is avilable.
</p>
<p>
Dashboard page:
Dashboard page is overview of transactions.
On dashboard you will find latest 5 transaction also total debit ,total credit and avilable balance so you can manage your buget.
</p>
<p>
profile:
you can change any details related to your profile also you can change password for change passoword old password is required.
Just in case you want to close the accountx to clear your transactions and start a new one
then you can quickly click on the Delete option and close your account. It is always possible to create or delete an account any time you wish to.
if you delete account your old data will not acsessible.
</p>

Live application link : [https://atul-accountx.herokuapp.com/](https://atul-accountx.herokuapp.com/)

## Project Strcuture:
Its a falsk based web application, I am using flask , flask-migration and postgresql as database ( heroku does not support sqlite).
you can see all dependencies [requirements.txt](./requirements.txt) file.

```sh
├── Procfile
├── README.md
├── accountx
│   ├── __init__.py 
│   ├── accounts.py
│   ├── auth.py 
│   ├── entry.py
│   ├── models.py
│   ├── static
│   │   ├── css
│   │   ├── images
│   │   ├── js
│   │   ├── plugins
│   │   └── theme
│   ├── templates
│   └── utils.py
├── migrations
│   ├── README
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── df4033a14dad_adding_phone.py
├── requirements.txt
└── run.py
```

## System Requirements

1. Postgresql database
2. windows / linux / mac with python3 installed

## Setup

1. initialize virtual environment and activate it

```
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```
 pip install -r requirements.txt
```

3. Setup database
following command will create database

first launch python console

```
from accountx import db

db.create_all()
```

## Run

```
export FLASK_APP=accountx
export FLASK_ENV=development

# then run

flask run
```