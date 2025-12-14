from flask import Flask, render_template
from database.tables import database
import os
from datetime import timedelta

from blueprints.auth import auth_bp
from blueprints.tasks import tasks_bp
from blueprints.user import user_bp

# We initialize all the setup we need for the application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-only-for-testing')
app.permanent_session_lifetime = timedelta(days=1)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database.init_app(app=app)

app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(user_bp)

#-----------------------------------------------------------------------------------------------------------------------
@app.route("/")
def homepage():
    return render_template("home.html")

#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        database.create_all()

    app.run(debug=True)
