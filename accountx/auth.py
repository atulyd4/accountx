import functools
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import flask
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import Form, StringField, PasswordField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from accountx import db, current_user, app
from accountx.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="./templates/auth")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if current_user() is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


class RegistrationForm(Form):
    name = StringField(
        "Name", [validators.DataRequired(), validators.Length(min=2, max=25)]
    )
    email = StringField(
        "Email Address", [validators.DataRequired(), validators.Length(min=6, max=35)]
    )
    password = PasswordField(
        "New Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat Password")


def validate_current_password(_, field):
    """custom validator to validate current users password"""
    user = current_user()
    valid = check_password_hash(user.password_hash, field.data)
    if not valid:
        raise validators.ValidationError("Current password is invalid")


class ChangePasswordForm(Form):
    current_password = StringField(
        "Current Password", [validators.DataRequired(), validate_current_password]
    )
    password = PasswordField(
        "New Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat Password")


# registration and login
@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if email and password:
            user = User.query.filter(User.email == email).first()
            if user is not None and check_password_hash(user.password_hash, password):
                flash("Logged in", "success")
                session["user_id"] = user.id
                return redirect(url_for("index"))
            else:
                flash("Wrong email or password", "danger")
                return redirect(url_for("auth.login"))
        else:
            # flash and redirect back to login
            flash("Wrong email or password", "danger")
            return redirect(url_for("auth.login"))
    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("index"))

    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        user = User(form.name.data, form.email.data)
        user.password_hash = generate_password_hash(str(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        user.name = request.form.get("name") or user.name
        user.currency_symbol = request.form.get("currency_symbol")
        user.timezone = request.form.get("timezone")
        db.session.add(user)
        db.session.commit()
        flash("Updated successfully.", "success")
    return render_template("profile.html", user=user)


@bp.post("/finish")
@login_required
def finish():
    user = User.query.get(session["user_id"])
    user.currency_symbol = request.form.get("currency_symbol")
    user.timezone = request.form.get("timezone")
    db.session.add(user)
    user.onboarded = True
    db.session.commit()
    flash("Successfully saved.", "success")
    return redirect(url_for("index"))


@bp.route("/profile/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == "POST" and form.validate():
        user = current_user()
        user.password_hash = generate_password_hash(str(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash("Password updated.", "success")
    return render_template("change-password.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    # remove the username from the session if it's there
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("index"))


@bp.post("/delete")
@login_required
def delete():
    """Delete profile"""
    user = current_user()
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash("Account deleted.", "success")
    return redirect(url_for("index"))
