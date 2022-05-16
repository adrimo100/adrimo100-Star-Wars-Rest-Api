from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

planet_favourites = db.Table('planet_favourites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('planet_id', db.Integer, db.ForeignKey('planet.id'), primary_key=True)
)

people_favourites = db.Table('people_favourites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True),
    db.Column('people_id', db.Integer, db.ForeignKey('people.id'), nullable=False, primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    planet_favourites = db.relationship('Planet', secondary=planet_favourites, lazy='subquery')
    people_favourites = db.relationship('People', secondary=people_favourites, lazy='subquery')
    
    def __repr__(self):
        return self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }


class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    climate = db.Column(db.String(10), nullable=False)
    terrain = db.Column(db.String(10), nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    gravity = db.Column(db.Integer, nullable=False)
    orbital_period = db.Column(db.Integer, nullable=False)
    population = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return self.name
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "diameter": self.diameter,
            "gravity": self.gravity,
            "orbital_period": self.orbital_period,
            "population": self.population
        }


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    birthyear = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(6), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=False)
    homeplanet = db.relationship('Planet', lazy='subquery', backref='habitants')

    def __repr__(self):
        return self.name
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birthyear": self.birthyear,
            "gender": self.gender,
            "height": self.height,
            "homeplanet": self.homeplanet.name
        }