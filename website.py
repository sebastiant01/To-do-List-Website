from flask import Flask, render_template, redirect, url_for, request, session, flash
from database.tables import database, Users, Tasks
from datetime import timedelta

# We initialize all the setup we need for the application
app = Flask(__name__)
app.secret_key = "09042508"
app.permanent_session_lifetime = timedelta(days=1)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database.init_app(app=app)

#----------------------------------------------------------------------------------------------------------------------------
@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/user")
def user_account():
    if "username" in session:
        name = session["username"]

        return render_template("user.html", name=name)
    
    flash(message="You need to log in.", category="info")
    return redirect(url_for("login"))

@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    if "username" not in session:
        flash(message="You need to log in to view your tasks.", category="info")
        return redirect(url_for("login"))

    # We get the username of the user from the "session" dict, and search the user
    # in the database.
    username: str = session["username"]
    user: Users = Users.query.filter_by(name=username).first()

    if request.method == "POST":
        # This is to distinguish what action is performing at the moment, and which button
        # was clicked.
        action_button: str = request.form.get("action")
        task_id: str = request.form.get("task_id")
        task: Tasks = Tasks.query.filter_by(id=task_id, user_id=user.id).first()

        if action_button == "toggle_status":
            if task:
                task.status = not task.status
                database.session.commit()
                flash(message="Task status updated!", category="success")
            else:
                flash(message="Task not found", category="error")

        elif action_button == "delete":
            if task:
                database.session.delete(task)
                database.session.commit()
                flash(message="Task deleted!", category="success")
            else:
                flash(message="Task not found", category="error")
        return redirect(url_for("tasks"))

    # We go into the database and store all the user's tasks to display it.
    user_tasks = Tasks.query.filter_by(user_id=user.id).all()
    return render_template("tasks.html", tasks=user_tasks)

@app.route("/create_task", methods=["GET", "POST"])
def create_task():
    if "username" not in session:
        flash(message="You need to log in to create tasks.", category="info")
        return redirect(url_for("login"))

    if request.method == "POST":
        title: str = request.form.get("title")
        description: str = request.form.get("description")
        priority_level: str = request.form.get("priority_level")

        if not title or not description or not priority_level:
            flash(message="All the fields have to be filled.", category="info")
            return render_template("create_task.html")
        
        username = session["username"]
        user: Users = Users.query.filter_by(name=username).first()

        if not user:
            flash(message="User not found", category="info")
            return redirect(url_for("login"))
        
        new_task: Tasks = Tasks(title=title, description=description, priority_level=priority_level, user_id=user.id, status=False)
        database.session.add(new_task)
        database.session.commit()

        flash(message="Task created successfully!", category="info")
        return redirect(url_for("tasks"))

    return render_template("create_task.html")

# We capture the task id in tasks(), and then pass the value into this function.
@app.route("/modify_task/<task_id>", methods=["GET", "POST"])
def modify_task(task_id):
    if "username" not in session:
        flash(message="You need to log in to modify your tasks.", category="info")
        return redirect(url_for("login"))
    
    username: str = session["username"]
    user: Users = Users.query.filter_by(name=username).first()

    if not user:
        flash(message="User not found", category="info")
        return redirect(url_for("login"))

    # We search that specific task with the id we obtained from the parameter
    task: Tasks = Tasks.query.filter_by(id=task_id, user_id=user.id).first()
    if not task:
        flash(message="Task not found, or you don't have permission to modify it.", category="info")
        return redirect(url_for("tasks"))
    
    if request.method == "POST":
        # We request to get the user's input
        title: str = request.form.get("title")
        description: str = request.form.get("description")
        priority_level: str = request.form.get("priority_level")
        status: str = request.form.get("status")

        if not title or not description or not priority_level:
            flash(message="All the fields have to be filled.", category="info")
            return render_template("modify_task.html")

        # We access to each attribute of the task and modify it with the new values.
        task.title = title
        task.description = description
        task.priority_level = priority_level
        task.status = bool(int(status))
        
        database.session.commit()

        flash(message="Task modified correctly!", category="info")
        return redirect(url_for("tasks"))
    
    return render_template("modify_task.html", task=task)

@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        # We request to get the value of the variables
        username: str = request.form["username"]
        password: str = request.form["pw"]
        email: str = request.form["email"]
        telephone_number: str = request.form["telnum"]

        found_user = Users.query.filter_by(name=username, email=email).first()

        if found_user:
            flash(message="There already exists a user with the same username and/or e-mail. Try logging in.")
            return redirect(url_for("login"))

        user: Users = Users(username, password, email, telephone_number)

        database.session.add(user)
        database.session.commit()

        flash(message="Registration successful! Please log in.", category="info")
        return redirect(url_for("login"))

    return render_template("registration.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username: str = request.form["username"]
        password: str = request.form["pw"]

        found_user = Users.query.filter_by(name=username, password=password).first()

        if not found_user:
            flash(message="Username or password incorrect. Try again.")
            return render_template("login.html")

        session["username"] = username
        flash(message="Logged in successfully!", category="info")
        return redirect(url_for("user_account"))
    else:
        if "username" in session:
            flash(message="Already logged in.", category="info")
            return redirect(url_for("user_account"))
        
        return render_template("login.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        # Same as before, we need to distinguish which button was clicked.
        action_button: str = request.form.get("action")

        if action_button == "logout":
            session.pop("username", None)

            flash(message="Logged out successfully!", category="info")
            return redirect(url_for("login"))

        elif action_button == "delete":
            if "username" in session:
                username = session["username"]
                user: Users = Users.query.filter_by(name=username).first()

                session.pop("username", None)
                database.session.delete(user)
                database.session.commit()

                flash(message="User deleted!", category="info")
                return redirect(url_for("login"))
            else:
                flash(message="You need to log in.", category="info")
                return redirect(url_for("login"))

    return render_template("settings.html")

#----------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        database.create_all()

    app.run(debug=True)
