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
from models import db, User, Character, Planet, FavoritePlanet, FavoriteCharacter
#from models import Person

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

@app.route('/people', methods=['GET'])
def get_people():
    people_query = Character.query.all()
    all_people = list(map(lambda x: x.serialize(), people_query))
    return jsonify(all_people), 200

@app.route('/people/<int:id>', methods=['GET'])
def get_person(id):
    person = Character.query.get(id)
    person = person.serialize()
    return jsonify(person), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets_query = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets_query))
    return jsonify(all_planets), 200

@app.route('/planet/<int:id>', methods=['GET'])
def get_planet(id):
    planet = Planet.query.get(id)
    planet = planet.serialize()
    return jsonify(planet), 200

@app.route('/users', methods=['GET'])
def get_users():
    user_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), user_query))
    return jsonify(all_users)

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    user = user.serialize()
    return jsonify(user), 200

@app.route('/<username>/favorites', methods=['GET'])
def get_user_favorites(username):
    user = Character.query.filter_by(name=username).first()
    user_fav_characters = FavoriteCharacter.query.filter_by(user_id=user.id).all()
    user_fav_characters = list(map(lambda x: x.serialize(), user_fav_characters))
    user_fav_planets = FavoritePlanet.query.filter_by(user_id=user.id).all()
    user_fav_planets = list(map(lambda x: x.serialize(), user_fav_planets))
    user_fav = user_fav_characters + user_fav_planets
    return jsonify(user_fav)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    body = request.get_json()
    user = User.query.get(body['userid'])
    planet_exists = Planet.query.get(planet_id) is not None
    user_exists = user is not None
    if not planet_exists:
        raise APIException('Planet not found', status_code=404)
    if not user_exists:
        raise APIException('User not found', status_code=404)
    
    fav_exists = FavoritePlanet.query.filter_by(user_id=user.id, planet_id=planet_id).first() is not None
    if not fav_exists and planet_exists and user_exists:
        fav_planet = FavoritePlanet(planet_id=planet_id, user_id=user.id)
        db.session.add(fav_planet)
        db.session.commit()
        return get_user_favorites(user.name)
    else:
        return "Favorite already exist", 200

@app.route('/favorite/people/<int:character_id>', methods=['POST'])
def add_favorite_people(character_id):
    body = request.get_json()
    user = User.query.get(body['userid'])
    character_exists = Character.query.get(character_id) is not None
    user_exists = user is not None
    if not character_exists:
        raise APIException('Character not found', status_code=404)
    if not user_exists:
        raise APIException('User not found', status_code=404)
    
    fav_exists = FavoriteCharacter.query.filter_by(user_id=user.id, character_id=character_id).first() is not None
    if not fav_exists and character_exists and user_exists:
        fav_character = FavoriteCharacter(character_id=character_id, user_id=user.id)
        db.session.add(fav_character)
        db.session.commit()
        return get_user_favorites(user.name)
    else:
        return "Favorite already exist", 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    body = request.get_json()
    user = User.query.get(body['userid'])
    planet_exists = Planet.query.get(planet_id) is not None
    user_exists = user is not None
    if not planet_exists:
        raise APIException('Planet not found', status_code=404)
    if not user_exists:
        raise APIException('User not found', status_code=404)
    
    favorite = FavoritePlanet.query.filter_by(user_id=user.id, planet_id=planet_id).first()
    fav_exists = favorite is not None
    if fav_exists and planet_exists and user_exists:
        db.session.delete(favorite)
        db.session.commit()
        return get_user_favorites(user.name)
    else:
        raise APIException('Favorite not found', status_code=404)


@app.route('/favorite/people/<int:character_id>', methods=['DELETE'])
def delete_favorite_people(character_id):
    body = request.get_json()
    user = User.query.get(body['userid'])
    character_exists = Character.query.get(character_id) is not None
    user_exists = user is not None
    if not character_exists:
        raise APIException('Character not found', status_code=404)
    if not user_exists:
        raise APIException('User not found', status_code=404)
    
    favorite = FavoriteCharacter.query.filter_by(user_id=user.id, character_id=character_id).first()
    fav_exists = favorite is not None
    if fav_exists and character_exists and user_exists:
        db.session.delete(favorite)
        db.session.commit()
        return get_user_favorites(user.name)
    else:
        raise APIException('Favorite not found', status_code=404)



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
