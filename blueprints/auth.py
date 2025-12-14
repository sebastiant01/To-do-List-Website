from flask import render_template, redirect, url_for, flash, session, request, Blueprint
from database.tables import database, Users

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["pw"]

        found_user = Users.query.filter_by(name=username, password=password).first()

        if not found_user:
            flash(message="Username or password incorrect. Try again.")
            return render_template("auth/login.html")

        session["username"] = username
        flash(message="Logged in successfully!", category="info")
        return redirect(url_for("user.profile"))
    else:
        if "username" in session:
            flash(message="Already logged in.", category="info")
            return redirect(url_for("user.profile"))
        
        return render_template("auth/login.html")

@auth_bp.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        # We request to get the value of the variables
        username = request.form["username"]
        password = request.form["pw"]
        email = request.form["email"]
        telephone_number = request.form["telnum"]

        if len(username) <= 7:
            flash(message="The username must be at least 8 characters.")
            return redirect(url_for("auth.registration"))

        has_letter = any(char.isalpha() for char in password)
        has_number = any(char.isdigit() for char in password)

        if not (has_letter and has_number):
            flash(message="The password must contain both letters and numbers.")
            return redirect(url_for("auth.registration"))

        if len(password) <= 7:
            flash(message="The password must be at least 8 characters.")
            return redirect(url_for("auth.registration"))

        found_user = Users.query.filter_by(name=username, email=email).first()

        if found_user:
            flash(message="There already exists a user with the same username and/or e-mail. Try logging in.")
            return redirect(url_for("auth.login"))

        user = Users(username, password, email, telephone_number)

        database.session.add(user)
        database.session.commit()

        flash(message="Registration successful! Please log in.", category="info")
        return redirect(url_for("auth.login"))

    return render_template("auth/registration.html")

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash(message="Logged out successfully!", category="info")
    return redirect(url_for("auth.login"))