from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
api = Api(app)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        return [hero.to_dict(rules=('-hero_powers',)) for hero in heroes], 200


class HeroByID(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if not hero:
            return {'error': 'Hero not found'}, 404
        return hero.to_dict(), 200


class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        return [power.to_dict(rules=('-hero_powers',)) for power in powers], 200


class PowerByID(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if not power:
            return {'error': 'Power not found'}, 404
        return power.to_dict(rules=('-hero_powers',)), 200

    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return {'error': 'Power not found'}, 404
        try:
            data = request.get_json()
            for attr in data:
                setattr(power, attr, data[attr])
            db.session.commit()
            return power.to_dict(rules=('-hero_powers',)), 200
        except Exception:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400


class HeroPowers(Resource):
    def post(self):
        try:
            data = request.get_json()
            hero_power = HeroPower(
                strength=data['strength'],
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            db.session.add(hero_power)
            db.session.commit()
            return hero_power.to_dict(), 200
        except Exception:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400


api.add_resource(Heroes, '/heroes')
api.add_resource(HeroByID, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowerByID, '/powers/<int:id>')
api.add_resource(HeroPowers, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
