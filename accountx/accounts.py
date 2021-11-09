from flask import Blueprint, flash, redirect, render_template, request, url_for
from accountx import current_user, db
from accountx.models import Account
from sqlalchemy import delete


bp = Blueprint(
    "accounts", __name__, url_prefix="/accounts", template_folder="./templates/accounts"
)


@bp.before_request
def login_required():
    if current_user() is None:
        return redirect(url_for("auth.login"))


# Party handlers
@bp.route("/", methods=["GET", "POST"])
def index():
    accounts = current_user().accounts
    return render_template("index.html", accounts=accounts)


@bp.route("/new", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        if name is not None:
            account = Account(name, phone)
            account.user = current_user()
            db.session.add(account)
            try:
                db.session.commit()
                flash("added successfully", "success")
                return redirect(url_for("accounts.index"))
            except Exception:
                print(Exception)
                flash("Unable to save", "danger")
        else:
            flash("Name is required")
    return render_template("new.html")


@bp.route("/<account_id>/edit", methods=["GET", "POST"])
def edit(account_id):
    account = (
        Account.query.filter(Account.user_id == current_user().id)
        .filter(Account.id == account_id)
        .first()
    )

    if account is None:
        flash("Account id not found", "danger")
        return redirect(url_for("accounts.index"))

    if request.method == "POST":
        account.name = request.form.get("name")
        account.phone = request.form.get("phone")
        db.session.add(account)
        try:
            db.session.commit()
            flash("Updated successfully", "success")
            return redirect(url_for("accounts.index"))
        except:
            db.session.rollback()
            flash("Failed to updated", "danger")

    return render_template("edit.html", account=account)


@bp.post("/<account_id>/delete")
def delete(account_id):
    account = (
        Account.query.filter(Account.user_id == current_user().id)
        .filter(Account.id == account_id)
        .first()
    )

    if account is None:
        flash("Account not found", "danger")
        return redirect(url_for("accounts.index"))

    try:
        check = account.check_and_delete(db)
        if check is True:
            flash("Account deleted.", "success")
        if check is False:
            flash("Account not deleted", "danger")
    except Exception as e:
        print(e)
        flash("Unable to delete account", "danger")

    return redirect(url_for("accounts.index"))
