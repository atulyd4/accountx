import os
from typing import Union
from distutils.log import debug
from flask import Flask, g, render_template, session
from flask.helpers import flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from sqlalchemy import func
from werkzeug.utils import redirect

from accountx.utils import gravatar_url

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

DATABASE_URL = os.environ["DB_URL"] or os.environ["DATABASE_URL"]

if DATABASE_URL is None:
    raise Exception("Database url is required.")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)

from accountx.models import Entry, TxnType, User


def current_user() -> Union[User, None]:
    if session.get("user_id") is not None:
        return User.query.get(session.get("user_id"))
    return None


from accountx import auth, accounts, entry


@app.before_first_request
@app.before_request
def setup():
    user = current_user()
    if user:
        app.jinja_env.globals.update(gravatar_url=gravatar_url(user.email))
        app.jinja_env.globals.update(current_user=user)


@app.get("/")
def index():
    if current_user() is None:
        return render_template("home.html")
    else:
        user = current_user()
        entries = (
            Entry.query.filter(Entry.user_id == user.id)
            .order_by(Entry.created_date.desc())
            .limit(5)
        )
        results = (
            Entry.query.with_entities(Entry.type, func.sum(Entry.amount).label("sum"))
            .filter(Entry.user_id == current_user().id)
            .group_by(Entry.type)
            .all()
        )

        resultSet = {"debit": 0.0, "credit": 0.0}

        for row in results:
            resultSet[row.type.name] = float(row["sum"])

        return render_template(
            "dashboard.html",
            entries=entries,
            user=user,
            total_credit=resultSet.get("credit"),
            total_debit=resultSet.get("debit"),
            balance=resultSet.get("credit") - resultSet.get("debit"),
        )


app.register_blueprint(auth.bp)
app.register_blueprint(accounts.bp)
app.register_blueprint(entry.bp)
