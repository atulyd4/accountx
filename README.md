# Accountx

#### Video Demo: https://youtu.be/o4yLRhvQves

#### Description:
Accountx is a smallscale book-keeping app , It will help you keep track of your daily transcations.
It will help you to organise your personal finance. it will give you easy overview of total money you have recieved or paid 
and how much money currently avilable. you can see latest 5 recent transcations on dashboard page. 
if you have gravatar account then your profile image automtically update.After creating account when you login first time then you can choose your currency symbol and time zone.
Accountx supports multiple accounts so you can create as much as required accounts by default three accounts(self,bank,cash) are created when you signup.
you can download transctions of any specific person or total transactions in csv file.
Live application link : [https://atul-accountx.herokuapp.com/](https://atul-accountx.herokuapp.com/)
 Project Strcuture:
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