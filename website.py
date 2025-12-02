from flask import Flask, render_template, redirect, url_for, request, session, flash

app = Flask(__name__)
app.secret_key = "rollheiser"

@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/user")
def userAccount():
    if "username" in session:
        name = session["username"]

        return render_template("user.html", name=name)
    
    flash(message="You need to log in.", category="info")
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username: str = request.form["usname"]
        session["username"] = username

        flash(message="Logged in succesfully!", category="info")
        return redirect(url_for("userAccount"))
    else:
        if "username" in session:
            flash(message="Already logged in.", category="info")
            return redirect(url_for("userAccount"))
        
        return render_template("login.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        session.pop("username", None)

        flash(message="Logged out succesfully!", category="info")
        return redirect(url_for("login"))

    return render_template("settings.html")


if __name__ == "__main__":
    app.run(debug=True)
