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
        scientist_list = [scientist.to_dict(rules = ("-missions",)) for scientist in Scientist.query.all()]
        return scientist_list, 200
    
    def post(self):
        data = request.get_json()
        try:
            new_scientist = Scientist(
                name = data["name"],
                field_of_study = data["field_of_study"]
            )
            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(rules = ("-missions",)), 201
        
        except ValueError as e:
            print(e.__str__())
            return {"errors": ["validation errors"]}, 400
        
    
api.add_resource(Scientists, "/scientists")

class ScientistsById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        if not scientist:
            return {"error": "scientist not found"}, 404
        return scientist.to_dict(), 200
    
    def patch(self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404

        try:
            data = request.get_json()
            for key in data:
                setattr(scientist, key, data[key])
            db.session.commit()
            return scientist.to_dict(rules = ("-missions",)), 202
        
        except ValueError as e:
            print(e.__str__())
            return {"errors": ["validation errors"]}, 400
        
        
    def delete(self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404

        db.session.delete(scientist)
        db.session.commit()

        return "", 204
    
api.add_resource(ScientistsById, "/scientists/<int:id>")

class Planets(Resource):
    def get(self):
        planet_list = [planet.to_dict(rules = ('-missions',)) for planet in Planet.query.all()]
        return planet_list, 200
    
api.add_resource(Planets, "/planets")

class Missions(Resource):
     def post(self):
        data = request.get_json()
        try:
            new_mission = Mission(
                scientist_id = data["scientist_id"],
                planet_id = data["planet_id"],
                name = data["name"]
            )
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(), 201
        
        except ValueError as e:
            print(e.__str__())
            return {"errors": ["validation errors"]}, 400
        
        
     
api.add_resource(Missions, "/missions")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
