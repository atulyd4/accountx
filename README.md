# Accountx

#### Video Demo: https://youtu.be/o4yLRhvQves

#### Description:
Accountx is a smallscale book-keeping app , It will help you keep track of your daily transcations.
It will help you to organise your personal finance. it will give you easy overview of total money you have recieved or paid 
and how much money currently avilable.
along with top 10 recent transcations. it supports multiple accounts so you can create as much as required accounts.
you can download entries of any specific person or total entries in csv file.

Live application link : [https://atul-accountx.herokuapp.com/](https://atul-accountx.herokuapp.com/)

Features list : [https://atul-accountx.herokuapp.com/faq](https://atul-accountx.herokuapp.com/faq)

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