from flask import render_template, redirect, url_for, flash, session, request, Blueprint
from database.tables import database, Tasks, Users

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("/", methods=["GET", "POST"])
def list_tasks():
    if "username" not in session:
        flash(message="You need to log in to view your tasks.", category="info")
        return redirect(url_for("auth.login"))

    # We get the username of the user from the "session" dict, and search the user
    # in the database.
    username = session["username"]
    user = Users.query.filter_by(name=username).first()

    if not user:
        flash(message="User not found.", category="danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        # This is to distinguish what action is performing at the moment, and which button
        # was clicked.
        action_button = request.form.get("action")
        task_id = request.form.get("task_id")
        task = Tasks.query.filter_by(id=task_id, user_id=user.id).first()

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
        
        return redirect(url_for("tasks.list_tasks"))
    
    # We go into the database and store all the user's tasks to display it.
    user_tasks = Tasks.query.filter_by(user_id=user.id).all()
    return render_template("tasks/tasks.html", tasks=user_tasks)

@tasks_bp.route("/create", methods=["GET", "POST"])
def create_task():
    if "username" not in session:
        flash(message="You need to log in to create tasks.", category="info")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        priority_level = request.form.get("priority_level")

        if not title or not description or not priority_level:
            flash(message="All the fields have to be filled.", category="info")
            return render_template("tasks/create_task.html")
        
        username = session["username"]
        user = Users.query.filter_by(name=username).first()

        if not user:
            flash(message="User not found", category="info")
            return redirect(url_for("auth.login"))
        
        new_task = Tasks(
            title=title, 
            description=description, 
            priority_level=priority_level, 
            user_id=user.id, 
            status=False
        )
        database.session.add(new_task)
        database.session.commit()

        flash(message="Task created successfully!", category="info")
        return redirect(url_for("tasks.list_tasks"))

    return render_template("tasks/create_task.html")

@tasks_bp.route("/<int:task_id>/edit", methods=["GET", "POST"])
def modify_task(task_id):
    if "username" not in session:
        flash(message="You need to log in to modify your tasks.", category="info")
        return redirect(url_for("auth.login"))
    
    username = session["username"]
    user = Users.query.filter_by(name=username).first()

    if not user:
        flash(message="User not found", category="info")
        return redirect(url_for("auth.login"))

    # We search that specific task with the id we obtained from the parameter
    task = Tasks.query.filter_by(id=task_id, user_id=user.id).first()
    
    if not task:
        flash(message="Task not found, or you don't have permission to modify it.", category="info")
        return redirect(url_for("tasks.list_tasks"))
    
    if request.method == "POST":
        # We request to get the user's input
        title = request.form.get("title")
        description = request.form.get("description")
        priority_level = request.form.get("priority_level")
        status = request.form.get("status")

        if not title or not description or not priority_level:
            flash(message="All the fields have to be filled.", category="info")
            return render_template("tasks/modify_task.html", task=task)

        # We access to each attribute of the task and modify it with the new values.
        task.title = title
        task.description = description
        task.priority_level = priority_level
        task.status = bool(int(status))
        
        database.session.commit()

        flash(message="Task modified correctly!", category="info")
        return redirect(url_for("tasks.list_tasks"))
    
    return render_template("tasks/modify_task.html", task=task)