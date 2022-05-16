"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# People endpoints
@app.route('/people')
def get_people():
    "Returns the list of people"
    people = [people.serialize() for people in People.query.all()]

    return jsonify(people), 200

@app.route('/people/<int:person_id>')
def get_person(person_id):
    "Returns person with id = person_id"
    person = People.query.get(person_id).serialize()
    
    return jsonify(person), 200

# Planet endpoints
@app.route('/planets')
def get_planets():
    "Returns the list of planets"
    planets = [planet.serialize() for planet in Planet.query.all()]

    return jsonify(planets), 200

@app.route('/planets/<int:planet_id>')
def get_planet(planet_id):
    "Returns planet with id = planet_id"
    planet = Planet.query.get(planet_id).serialize()

    return jsonify(planet), 200

# User endpoints
@app.route('/users', methods=['GET'])
def get_users():
    "Returns the list of users"
    users = [user.serialize() for user in User.query.all()]

    return jsonify(users), 200

@app.route('/users/<int:user_id>/favourites')
def get_favourites(user_id):
    "Returns favorites of user with id='user_id'"
    user = User.query.get(user_id)
    favourites = [
            favourite.serialize()
            for favourite
            in user.planet_favourites + user.people_favourites
        ]

    return jsonify(favourites), 200


@app.route('/users/<int:user_id>/favourites', methods=['POST'])
def add_favourite(user_id):
    """
    Adds favourite to user with 'user_id'
    Assumes a request body of shape: 
    {
        "type": "planet" | "people",
        "id": Int
    }
    """
    user = User.query.get(user_id)
    if user == None:
        return jsonify({"error": "User not found"}), 404
    
    favouriteType = request.json["type"]
    id = request.json["id"]

    if favouriteType == "planet":
        planet = Planet.query.get(id)
        if planet == None:
            return jsonify({ "error": "Planet not found" }), 404

        user.planet_favourites.append(planet)
        db.session.commit()
        return jsonify(f"Added {planet} to {user} favourites"), 200
    
    if favouriteType == "people":
        person = People.query.get(id)
        if person == None:
            return jsonify({ "error": "Person not found" }), 404
            
        user.people_favourites.append(person)
        db.session.commit()
        return jsonify(f"Added {person} to {user} favourites"), 200
            
    return jsonify({ "error": "Invalid favourite type. Must be 'planet' or 'people'" }), 400


@app.route('/users/<int:user_id>/favourites/people/<int:person_id>', methods=['DELETE'])
def delete_person_favourite(user_id, person_id):
    "Deletes favorite person with id = person_id from user with id = user_id"
    user = User.query.get(user_id)
    if user == None:
        return jsonify({"error": "User not found"}), 404

    person = People.query.get(person_id)
    if person == None:
        return jsonify({"error": "Person not found"}), 404

    try:
        user.people_favourites.remove(person) 
        db.session.commit()
        return jsonify({ "message": f"Removed {person} from {user}'s favourites"})
    except ValueError:
        return jsonify({ "error": f"{person} not in {user}'s favourites"})
    

@app.route('/users/<int:user_id>/favourites/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet_favourite(user_id, planet_id):
    "Deletes favorite person with id = planet_id from user with id = user_id"
    user = User.query.get(user_id)
    if user == None:
        return jsonify({"error": "User not found"}), 404
    

    planet = Planet.query.get(planet_id)
    if planet == None:
        return jsonify({"error": "Planet not found"}), 404

    try:
        user.planet_favourites.remove(planet) 
        db.session.commit()
        return jsonify({ "message": f"Removed {planet} from {user}'s favourites"})
    except ValueError:
        return jsonify({ "error": f"{planet} not in {user}'s favourites"})
    
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
