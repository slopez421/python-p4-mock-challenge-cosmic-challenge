#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)


@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = db.session.query(Scientist).all()
        return [scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in scientists], 200
    def post(self):
        name = request.get_json()['name']
        field_of_study = request.get_json()['field_of_study']

        try:
            scientist = Scientist(name=name, field_of_study=field_of_study)

            db.session.add(scientist)
            db.session.commit()
            
            return scientist.to_dict(), 201
        except:
            return {'errors': ['validation errors']}, 400


class ScientistById(Resource): 
    def get(self, id):
        scientist = db.session.query(Scientist).filter(Scientist.id ==id).first()
        if scientist:
            return scientist.to_dict(), 200
        return {'error': 'Scientist not found'}, 404
    def delete(self, id):
        scientist = db.session.query(Scientist).filter(Scientist.id ==id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return {}, 204
        return {'error': 'Scientist not found'}, 404
    def patch(self, id):
        scientist = db.session.query(Scientist).filter(Scientist.id == id).first()
        if scientist:
            try:
                for attr in request.get_json():
                    setattr(scientist, attr, request.get_json()[attr])
                db.session.add(scientist)
                db.session.commit()

                return scientist.to_dict(), 202
            except:
                return {'errors': ['validation errors']}, 400
            
        return {'error': 'Scientist not found'}, 404

class Planets(Resource):
    def get(self):
        planets = db.session.query(Planet).all()
        return [planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star')) for planet in planets], 200

class Missions(Resource):
    def post(self):
        name = request.get_json()['name']
        scientist_id = request.get_json()['scientist_id']
        planet_id = request.get_json()['planet_id']
        
        try:
            mission = Mission(name=name, scientist_id=scientist_id, planet_id=planet_id)
            db.session.add(mission)
            db.session.commit()

            return mission.to_dict(), 201
        except:
            return {'errors': ['validation errors']}, 400
            


api.add_resource(Missions, '/missions')
api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
