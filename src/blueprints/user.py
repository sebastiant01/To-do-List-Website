from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.tables import database, Users

user_bp = Blueprint("user", __name__, url_prefix="/user")

@user_bp.route("/")
def profile():
    if "username" in session:
        name = session["username"]
        return render_template("user/user.html", name=name)
    
    flash(message="You need to log in.", category="info")
    return redirect(url_for("auth.login"))

@user_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # Same as before, we need to distinguish which button was clicked.
        action_button = request.form.get("action")

        if action_button == "logout":
            return redirect(url_for("auth.logout"))

        elif action_button == "delete":
            if "username" in session:
                username = session["username"]
                user = Users.query.filter_by(name=username).first()

                if user:
                    session.pop("username", None)
                    database.session.delete(user)
                    database.session.commit()
                    flash(message="Account deleted!", category="info")
                else:
                    flash(message="User not found.", category="error")
                
                return redirect(url_for("auth.login"))
            else:
                flash(message="You need to log in.", category="info")
                return redirect(url_for("auth.login"))

    return render_template("user/settings.html")