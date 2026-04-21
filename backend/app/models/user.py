# Placeholder for SQLAlchemy User Model
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

class UserPlaceholder:
    def __init__(self, id, name, email, password_hash):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.preferences = []
        self.watch_history = []
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }
