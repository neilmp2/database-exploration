from app import app

import pytest


@pytest.fixture(scope='module')
def test_client():
    flask_app = app

    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client


@pytest.fixture(scope="session", autouse=True)
def pytest_sessionstart():
    import subprocess, time

    proc_redis = subprocess.Popen(['docker', 'run', '--rm', '-it', '-p', '6379:6379', 'redis'])
    proc_redis.wait()


def test_mp_overview_redis(test_client):
    import json

    r = test_client.delete("/date")

    r = test_client.put("/date", data="2020-11-05")
    assert(r.status_code == 200)

    r = test_client.put("/date", data="2020-11-12")
    assert(r.status_code == 200)

    r = test_client.get("/date")
    response_data = json.loads(r.data.decode('utf-8'))
    assert(r.status_code == 200)
    assert(response_data['version'] == 2)
    assert(response_data['value'] == "2020-11-12")

    r = test_client.get("/date/1")
    response_data = json.loads(r.data.decode('utf-8'))
    assert(r.status_code == 200)
    assert(response_data['version'] == 1)
    assert(response_data['value'] == "2020-11-05")

    r = test_client.get("/date/3")
    assert(r.status_code == 404)


def test_new_key_redis(test_client):
    import json

    r = test_client.delete("/newKey")

    r = test_client.get("/newKey")
    assert(r.status_code == 404)

    r = test_client.put("/newKey", data="Hi")
    assert(r.status_code == 200)

    r = test_client.get("/newKey")
    response_data = json.loads(r.data.decode('utf-8'))
    assert(r.status_code == 200)
    assert(response_data['version'] == 1)
    assert(response_data['value'] == "Hi")


def test_memory_redis(test_client):
    import json
    import random

    r = test_client.delete("/memory")

    for i in range(1, 100):
        data = "data" + str(i)
        r = test_client.put("/memory", data=data)
    
    randomOrder = list(range(1, 100))
    random.shuffle(randomOrder)
    for i in randomOrder:
        request_string = "/memory/" + str(i)
        value = "data" + str(i)
        r = test_client.get(request_string)
        response_data = json.loads(r.data.decode('utf-8'))
        assert(r.status_code == 200)
        assert(response_data['version'] == i)
        assert(response_data['value'] == value)


def test_delete_redis(test_client):
    import json

    r = test_client.delete("/newKey")

    r = test_client.put("/newKey", data="Hi")
    assert(r.status_code == 200)
    r = test_client.delete("/newKey")
    assert(r.status_code == 200)
    r = test_client.get("/newKey")
    assert(r.status_code == 404)
    r = test_client.put("/newKey", data="Hi")
    assert(r.status_code == 200)
    r = test_client.get("/newKey")
    response_data = json.loads(r.data.decode('utf-8'))
    assert(r.status_code == 200)
    assert(response_data['version'] == 1)
    assert(response_data['value'] == "Hi")
    