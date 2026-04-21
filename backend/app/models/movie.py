# Placeholder for SQLAlchemy Movie Model
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()

class MoviePlaceholder:
    def __init__(self, id, title, genres, synopsis, rating, poster_url):
        self.id = id
        self.title = title
        self.genres = genres
        self.synopsis = synopsis
        self.rating = rating
        self.poster_url = poster_url
        
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "genres": self.genres,
            "rating": self.rating
        }
