from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///telemetry.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Measurement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), nullable=False)
    measurement_type = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(32), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'measurement_type': self.measurement_type,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat()
        }


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/time')
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.route('/measurements', methods=['POST'])
def create_measurement():
    data = request.get_json()
    measurement = Measurement(
        device_id=data['device_id'],
        measurement_type=data['measurement_type'],
        value=data['value'],
        unit=data['unit']
    )
    db.session.add(measurement)
    db.session.commit()
    return jsonify(measurement.to_dict()), 201


@app.route('/measurements', methods=['GET'])
def get_measurements():
    measurements = Measurement.query.all()
    return jsonify([m.to_dict() for m in measurements])


@app.route('/measurements/<int:id>', methods=['GET'])
def get_measurement(id):
    measurement = db.session.get(Measurement, id)
    if measurement is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(measurement.to_dict())


@app.route('/measurements/<int:id>', methods=['PUT'])
def update_measurement(id):
    measurement = db.session.get(Measurement, id)
    if measurement is None:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json()
    measurement.device_id = data.get('device_id', measurement.device_id)
    measurement.measurement_type = data.get('measurement_type', measurement.measurement_type)
    measurement.value = data.get('value', measurement.value)
    measurement.unit = data.get('unit', measurement.unit)
    db.session.commit()
    return jsonify(measurement.to_dict())


@app.route('/measurements/<int:id>', methods=['DELETE'])
def delete_measurement(id):
    measurement = db.session.get(Measurement, id)
    if measurement is None:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(measurement)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    #app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True)
