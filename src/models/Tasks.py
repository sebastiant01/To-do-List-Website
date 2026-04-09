from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class Tasks(database.Model):
    id: int = database.Column(database.Integer, primary_key=True)
    title: str = database.Column(database.String(50))
    description: str = database.Column(database.String(150))
    priority_level: str = database.Column(database.String(30))
    status: bool = database.Column(database.Boolean, default=False)

    user_id: str = database.Column(
        database.Integer, database.ForeignKey("users.id"), nullable=False
    )

    def __init__(self, title, description, priority_level, user_id, status=False):
        self.title = title
        self.description = description
        self.priority_level = priority_level
        self.user_id = user_id
        self.status = status
