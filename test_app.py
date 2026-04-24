import pytest
from app import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        with app.test_client() as client:
            yield client
        db.drop_all()


def test_hello_world(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hello, World!' in response.data


def test_get_time(client):
    response = client.get('/time')
    assert response.status_code == 200
    assert len(response.data) > 0


def test_create_measurement(client):
    response = client.post('/measurements', json={
        'device_id': 'sensor-01',
        'measurement_type': 'temperature',
        'value': 22.5,
        'unit': 'Celsius'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['device_id'] == 'sensor-01'
    assert data['value'] == 22.5
    assert 'id' in data
    assert 'timestamp' in data


def test_get_all_measurements(client):
    client.post('/measurements', json={
        'device_id': 'sensor-01',
        'measurement_type': 'humidity',
        'value': 65.0,
        'unit': '%'
    })
    client.post('/measurements', json={
        'device_id': 'sensor-02',
        'measurement_type': 'humidity',
        'value': 70.0,
        'unit': '%'
    })
    response = client.get('/measurements')
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_single_measurement(client):
    post_response = client.post('/measurements', json={
        'device_id': 'sensor-02',
        'measurement_type': 'pressure',
        'value': 1013.25,
        'unit': 'hPa'
    })
    measurement_id = post_response.get_json()['id']
    response = client.get(f'/measurements/{measurement_id}')
    assert response.status_code == 200
    assert response.get_json()['value'] == 1013.25


def test_get_measurement_not_found(client):
    response = client.get('/measurements/999')
    assert response.status_code == 404


def test_update_measurement(client):
    post_response = client.post('/measurements', json={
        'device_id': 'sensor-01',
        'measurement_type': 'temperature',
        'value': 20.0,
        'unit': 'Celsius'
    })
    measurement_id = post_response.get_json()['id']
    response = client.put(f'/measurements/{measurement_id}', json={'value': 25.0})
    assert response.status_code == 200
    assert response.get_json()['value'] == 25.0


def test_delete_measurement(client):
    post_response = client.post('/measurements', json={
        'device_id': 'sensor-01',
        'measurement_type': 'temperature',
        'value': 20.0,
        'unit': 'Celsius'
    })
    measurement_id = post_response.get_json()['id']
    assert client.delete(f'/measurements/{measurement_id}').status_code == 204
    assert client.get(f'/measurements/{measurement_id}').status_code == 404
