"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from datetime import datetime
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, FavoritePlanet, FavoriteCharacter
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
#from models import Person

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "estamosprobandotaken"  # Change this!
jwt = JWTManager(app)

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

@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email, password=password).first()
    if user is None:
        raise APIException('Bad username or password', status_code=401)

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)

@app.route('/people', methods=['GET'])
def get_person():
    people_query = Character.query.all()
    all_people = list(map(lambda x: x.serialize(), people_query))
    return jsonify(all_people), 200

@app.route('/people/<int:id>', methods=['GET'])
def get_character(id):
    character = Character.query.get(id)
    if character is None:
        raise APIException('Character not found', status_code=404)
    character = character.serialize()
    return jsonify(character), 200

@app.route('/people', methods=['POST'])
@jwt_required()
def add_people():
    character = Character.query.filter_by(name=request.json.get("name", None)).first()
    if character is not None:
        raise APIException('Character already exist', status_code=409)

    name = request.json.get("name", None)
    height = request.json.get("height", None)
    mass = request.json.get("mass", None)
    hair_color = request.json.get("hair_color", None)
    skin_color = request.json.get("skin_color", None)
    eye_color = request.json.get("eye_color", None)
    birth_year = request.json.get("birth_year", None)
    gender = request.json.get("gender", None)
    homeworld = request.json.get("homeworld", None)

    character = Character(name=name,
                    height=height,
                    mass=mass,
                    hair_color=hair_color,
                    skin_color=skin_color,
                    eye_color=eye_color,
                    birth_year=birth_year,
                    gender=gender,
                    homeworld=homeworld,
                    created=datetime.now(),
                    edited=datetime.now()
                    )
    db.session.add(character)
    db.session.commit()

    character = Character.query.filter_by(name=name).first()
    character = character.serialize()
    return jsonify(character), 201

@app.route('/people/<int:id>', methods=['PUT'])
@jwt_required()
def update_people(id):
    character = Character.query.get(id)

    if character is None:
        raise APIException('User not found', status_code=404)

    character.name = request.json.get("name", None)
    character.height = request.json.get("height", None)
    character.mass = request.json.get("mass", None)
    character.hair_color = request.json.get("hair_color", None)
    character.skin_color = request.json.get("skin_color", None)
    character.eye_color = request.json.get("eye_color", None)
    character.birth_year = request.json.get("birth_year", None)
    character.gender = request.json.get("gender", None)
    character.homeworld = request.json.get("homeworld", None)
    character.edited = datetime.now()

    db.session.commit()

    character = Character.query.get(id)
    character = character.serialize()
    return jsonify(character), 201

@app.route('/people/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_person(id):
    character = Character.query.get(id)
    if character is None:
        raise APIException('User not found', status_code=404)
    db.session.delete(character)
    db.session.commit()

    people_query = Character.query.all()
    all_people = list(map(lambda x: x.serialize(), people_query))
    return jsonify(all_people), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets_query = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets_query))
    return jsonify(all_planets), 200

@app.route('/planet/<int:id>', methods=['GET'])
def get_planet(id):
    planet = Planet.query.get(id)
    if planet is None:
        raise APIException('Planet not found', status_code=404)
    planet = planet.serialize()
    return jsonify(planet), 200

@app.route('/planets', methods=['POST'])
@jwt_required()
def add_planets():
    planet = Planet.query.filter_by(name=request.json.get("name", None)).first()
    if planet is not None:
        raise APIException('Planet already exist', status_code=409)

    name = request.json.get("name", None)
    rotation_period = request.json.get("rotation_period", None)
    orbital_period = request.json.get("orbital_period", None)
    diameter = request.json.get("diameter", None)
    climate = request.json.get("climate", None)
    gravity = request.json.get("gravity", None)
    terrain = request.json.get("terrain", None)
    surface_water = request.json.get("surface_water", None)
    population = request.json.get("population", None)
    url = request.json.get("url", None)

    planet = Planet(name=name,
                    rotation_period=rotation_period,
                    orbital_period=orbital_period,
                    diameter=diameter,
                    climate=climate,
                    gravity=gravity,
                    terrain=terrain,
                    surface_water=surface_water,
                    population=population,
                    url=url,
                    created=datetime.now(),
                    edited=datetime.now()
                    )
    db.session.add(planet)
    db.session.commit()

    planet = Planet.query.filter_by(name=name).first()
    planet = planet.serialize()
    return jsonify(planet), 201

@app.route('/planet/<int:id>', methods=['PUT'])
@jwt_required()
def update_planet(id):
    planet = Planet.query.get(id)

    if planet is None:
        raise APIException('Planet not found', status_code=404)

    planet.name = request.json.get("name", None)
    planet.rotation_period = request.json.get("rotation_period", None)
    planet.orbital_period = request.json.get("orbital_period", None)
    planet.diameter = request.json.get("diameter", None)
    planet.climate = request.json.get("climate", None)
    planet.gravity = request.json.get("gravity", None)
    planet.terrain = request.json.get("terrain", None)
    planet.surface_water = request.json.get("surface_water", None)
    planet.population = request.json.get("population", None)
    planet.url = request.json.get("url", None)
    planet.edited = datetime.now()

    db.session.commit()

    planet = Planet.query.get(id)
    planet = planet.serialize()
    return jsonify(planet), 201

@app.route('/planet/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_planet(id):
    planet = Planet.query.get(id)
    if planet is None:
        raise APIException('Planet not found', status_code=404)
    db.session.delete(planet)
    db.session.commit()

    planets_query = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets_query))
    return jsonify(all_planets), 200

@app.route('/users', methods=['GET'])
def get_users():
    user_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), user_query))
    return jsonify(all_users)

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user is None:
        raise APIException('User not found', status_code=404)
    user = user.serialize()
    return jsonify(user), 200

@app.route('/users', methods=['POST'])
@jwt_required()
def add_user():
    user = User.query.filter_by(email=request.json.get("email", None)).first()
    if user is not None:
        raise APIException('User already exist', status_code=409)

    name = request.json.get("name", None)
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User(name=name,
                email=email,
                password=password
                )
    db.session.add(user)
    db.session.commit()

    user = User.query.filter_by(email=email).first()
    user = user.serialize()
    return jsonify(user), 201

@app.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = User.query.get(id)

    if user is None:
        raise APIException('User not found', status_code=404)

    user.name = request.json.get("name", None)
    user.email = request.json.get("email", None)

    db.session.commit()

    user = User.query.get(id)
    user = user.serialize()
    return jsonify(user), 201

@app.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get(id)
    if user is None:
        raise APIException('User not found', status_code=404)
    db.session.delete(user)
    db.session.commit()

    users_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users_query))
    return jsonify(all_users), 200

@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def get_user_favorites():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
    user_fav_characters = FavoriteCharacter.query.filter_by(user_id=user.id).all()
    user_fav_characters = list(map(lambda x: x.serialize(), user_fav_characters))
    user_fav_planets = FavoritePlanet.query.filter_by(user_id=user.id).all()
    user_fav_planets = list(map(lambda x: x.serialize(), user_fav_planets))
    user_fav = user_fav_characters + user_fav_planets
    return jsonify(user_fav)

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
@jwt_required()
def add_favorite_planet(planet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
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
        return get_user_favorites()
    else:
        raise APIException('Favorite already exist', status_code=409)

@app.route('/favorite/people/<int:character_id>', methods=['POST'])
@jwt_required()
def add_favorite_people(character_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
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
        return get_user_favorites()
    else:
        raise APIException('Favorite already exist', status_code=409)

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_planet(planet_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
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
        return get_user_favorites()
    else:
        raise APIException('Favorite not found', status_code=404)

@app.route('/favorite/people/<int:character_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_people(character_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()
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
        return get_user_favorites()
    else:
        raise APIException('Favorite not found', status_code=404)

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
