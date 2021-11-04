import json
from operator import mul
from sqlalchemy import or_
from sqlalchemy.orm import contains_eager, aliased
from werkzeug.datastructures import Accept
from wtforms import Form, StringField, validators, SelectField, TextAreaField
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from accountx import current_user, db
from accountx.models import Account, Entry, EntrySchema
from sqlalchemy.exc import SQLAlchemyError
from IPython import embed


bp = Blueprint(
    "entry", __name__, url_prefix="/entries", template_folder="./templates/entry"
)


@bp.before_request
def login_required():
    if current_user() is None:
        return redirect(url_for("auth.login"))


class EntryForm(Form):
    type = SelectField(
        "Type",
        choices=[("debit", "Paid  [debit]"), ("credit", "Received [credit]")],
    )
    amount = StringField("Amount")
    from_account = SelectField(
        "From",
        choices=[],
    )
    to_account = SelectField(
        "To",
        choices=[],
    )

    description = TextAreaField(
        "description", [validators.optional(), validators.length(max=200)]
    )


# Party handlers
@bp.get("/")
def index():
    return render_template("entry/index.html", entries=[])


@bp.get("/entries-json")
def index_json():
    user_id = current_user().id
    query = Entry.query
    query = query.filter(Entry.user_id == user_id)

    # search filter
    search = request.args.get("search[value]")
    if search:
        a1 = aliased(Account)
        a2 = aliased(Account)

        query = query.join(a1, Entry.from_account)
        query = query.join(a2, Entry.to_account)

        print(query)
        query = query.filter(
            db.or_(
                Entry.description.ilike(f"%{search}%"),
                Entry.amount.ilike(f"%{search}%"),
                a1.name.ilike(f"%{search}%"),
                a2.name.ilike(f"%{search}%"),
            )
        )

    print(request.args)
    if request.args.get("account_id") is not None:
        print("inside account id block")
        account_id = request.args.get("account_id")
        query = query.filter(
            or_(Entry.from_account_id == account_id, Entry.to_account_id == account_id)
        )
    total_filtered = query.count()
    # pagination
    start = request.args.get("start", type=int)
    length = request.args.get("length", type=int)
    query = query.offset(start).limit(length)

    print(query)
    entries = query.all()

    entry_schema = EntrySchema(many=True)
    result = entry_schema.dump(entries)
    return jsonify(
        {
            "data": result,
            "recordsTotal": total_filtered,
            "recordsTotal": Entry.query.count(),
        }
    )


# Party handlers
@bp.route("/new", methods=["GET", "POST"])
def create():
    accounts = current_user().accounts
    form = EntryForm(request.form)
    form.from_account.choices = [
        (account.id, account.name.capitalize()) for account in accounts
    ]
    form.to_account.choices = [
        (account.id, account.name.capitalize()) for account in accounts
    ]

    if request.method == "POST":
        entry = Entry()
        user = current_user()
        f_account = (
            Account.query.filter(Account.user_id == user.id)
            .filter(Account.id == request.form.get("from_account"))
            .first()
        )
        t_account = (
            Account.query.filter(Account.user_id == user.id)
            .filter(Account.id == request.form.get("to_account"))
            .first()
        )
        if not f_account:
            f = Account(request.form.get("from_account"))
            f.user_id = user.id
            db.session.add(f)
            db.session.commit()
            entry.from_account_id = f.id
        else:
            entry.from_account_id = f_account.id

        if not t_account:
            t = Account(request.form.get("to_account"))
            t.user_id = user.id
            db.session.add(t)
            db.session.commit()
            entry.to_account_id = t.id
        else:
            entry.to_account_id = t_account.id

        entry.to_account_id = form.to_account.data
        entry.amount = form.amount.data
        entry.type = form.type.data
        entry.description = form.description.data
        entry.user = user
        db.session.add(entry)
        try:
            db.session.commit()
            flash("Entry added.", "success")
            return redirect(url_for("entry.index"))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Unable to save", "danger")
            error = str(e.__dict__["orig"])
            print(error)
    return render_template("entry/new.html", form=form)


@bp.get("/<id>")
def details(id):
    entry = (
        Entry.query.filter(Entry.user == current_user()).filter(Entry.id == id).first()
    )
    if entry:
        return render_template("entry/details.html", entry=entry)
    else:
        flash("Entry not found", "danger")
        return redirect(url_for("entry.index"))


# @bp.get("/<name>")
# def show_all(name):
#     latest_entry = (
#         Entry.query.filter(Entry.user == current_user())
#         .filter(Entry.to_account == name)
#         .order_by(Entry.created_date.desc())
#     )
#     if latest_entry:
#         return render_template("entry/all_details.html", latest_entry=latest_entry)
#     else:
#         flash("Entry not found", "danger")
#         return redirect(url_for("entry.index"))
