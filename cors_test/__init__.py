from flask import Flask, jsonify, request, abort
from .models import setup_db, Plant
from flask_cors import CORS


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authroization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    
    @app.route('/plants')
    def get_plants():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        plants = Plant.query.all()
        formatted_plants = [plant.format() for plant in plants]

        return jsonify({
            'success' : True,
            'plants' : formatted_plants,
            'total_plants' : len(formatted_plants)
        })
    @app.route('/plants/<int:plant_id>')
    def get_specific_plant(plant_id):
        plant = Plant.query.filter(Plant.id == plant_id).one_or_none()

        if plant is None:
            abort(404)

        else:
            return jsonify({
                'success' : True,
                'plant' : plant.format()
            })
    return app


