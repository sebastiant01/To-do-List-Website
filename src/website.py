from flask import render_template
from app_configuration import database, app


@app.route("/")
def homepage():
    return render_template("home.html")


if __name__ == "__main__":
    with app.app_context():
        database.create_all()

    app.run(debug=True)
