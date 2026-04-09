from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


class Users(database.Model):
    id: int = database.Column(database.Integer, primary_key=True)
    name: str = database.Column(database.String(80))
    password: str = database.Column(database.String(20))
    email: str = database.Column(database.String(50))
    telephone: str = database.Column(database.String(15))

    tasks = database.relationship(
        "Tasks", backref="owner", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(self, name, password, email, telephone):
        self.name = name
        self.password = password
        self.email = email
        self.telephone = telephone
