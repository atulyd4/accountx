from flask import Blueprint, flash, redirect, render_template, request, url_for
from accountx import current_user, db
from accountx.models import Account


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
        if name is not None:
            account = Account(name)
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
