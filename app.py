from flask_cors import CORS
from flask import Flask, json, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow.fields import Email
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from joblib import load
import warnings
from array import array

from werkzeug.wrappers import response
warnings.filterwarnings('ignore')

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY'] = 'super-secret'

CORS(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)

pipeline = load("lepto.joblib")


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped')


@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(planet_name='Mercury', planet_type='Class D',
                     home_star='Sol', mass=3.258e23, radius=1516, distance=35.98e6)

    venus = Planet(planet_name='Venus', planet_type='Class K',
                   home_star='Sol', mass=4.258e23, radius=1313, distance=37.98e6)

    db.session.add(mercury)
    db.session.add(venus)

    test_user = User(
        first_name='Ricky',
        last_name='Rivaldo',
        email='test@test.com',
        password='P@ssword'
    )

    db.session.add(test_user)
    db.session.commit()
    print('Database Seeded!')


@app.route("/")
def hello_world():
    return "<p>Ini API TESTING v2</p>"


@app.route("/test")
def test():
    return jsonify(message="test2")


@app.route("/rf", methods=['POST'])
def rf():
    # lalala
    # opsi1 = request.form['opsi1']
    # opsi2 = request.form['opsi2']
    # opsi3 = request.form['opsi3']
    # opsi4 = request.form['opsi4']
    # opsi5 = request.form['opsi5']
    # opsi6 = request.form['opsi6']
    # opsi7 = request.form['opsi7']
    # opsi8 = request.form['opsi8']
    # opsi9 = request.form['opsi9']
    # opsi10 = request.form['opsi10']
    datas = json.loads(request.data)

    testingX = [[datas['opsi1'], datas['opsi2'], datas['opsi3'], datas['opsi4'], datas['opsi5'],
                 datas['opsi6'], datas['opsi7'], datas['opsi8'], datas['opsi9'], datas['opsi10']]]
    # testingX = [[1, 1, 1, 0, 1, 1, 0, 0, 0, 0]]
    prediksi = pipeline.predict(testingX)
    hasil = str(prediksi)
    # hasil_prediksi = json.loads(str(prediksi))
    # return jsonify(message="prediksi= "+str(prediksi))
    return jsonify(hasil[1])
    # return testingX['data']
    # return datas


@app.route("/parameters")
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message="Sorry " + name + ", masih kecil"), 401
    else:
        return jsonify(message=name + " dah tua boleh masuk")


@app.route("/parameters2/<string:name>/<int:age>")
def parameters2(name: str, age: int):
    if age < 18:
        return jsonify(message="Sorry " + name + ", masih kecil"), 401
    else:
        return jsonify(message=name + " dah tua boleh masuk")


@app.route("/planets", methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='Email sudah terpakai'), 409
    else:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        user = User(first_name=first_name, last_name=last_name,
                    email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='Berhasil Register'), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login Berhasil", access_token=access_token)
    else:
        return jsonify(message="Email/passwword salah"), 401


@app.route('/planet_details/<int:planet_id>', methods=["GET"])
def planet_details(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message="Gadak planetnya"), 404


@app.route('/add_planet', methods=['POST'])
@jwt_required()  # hilangkan kalo ga perlu login loginan
def add_planet():
    planet_name = request.form['planet_name']
    test = Planet.query.filter_by(planet_name=planet_name).first()
    if test:
        return jsonify("Udah ada planet ini"), 409
    else:
        planet_type = request.form['planet_type']
        home_star = request.form['home_star']
        mass = float(request.form['mass'])
        radius = float(request.form['radius'])
        distance = float(request.form['distance'])

        new_planet = Planet(planet_name=planet_name,
                            planet_type=planet_type,
                            mass=mass,
                            home_star=home_star,
                            radius=radius,
                            distance=distance)

        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message="Planet Masuk"), 201


@app.route('/update_planet', methods=['PUT'])
def update_planet():
    planet_id = int(request.form['planet_id'])
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        planet.planet_name = request.form['planet_name']
        planet.planet_type = request.form['planet_type']
        planet.mass = float(request.form['mass'])
        planet.home_star = request.form['home_star']
        planet.radius = float(request.form['radius'])
        planet.distance = float(request.form['distance'])

        db.session.commit()
        return jsonify(message="Planet Terupdate"), 202
    else:
        return jsonify(message="Planet Gadak"), 404


@app.route('/delete_planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id: int):
    planet = Planet.query.filter_by(planet_id=planet_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message="Terhapus"), 202
    else:
        return jsonify(message="Gadak planet itu"), 404


# database model


class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class Planet(db.Model):
    __tablename__ = "planets"
    planet_id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('planet_id', 'planet_name', 'planet_type',
                  'home_star', 'mass', 'radius', 'distance')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)
