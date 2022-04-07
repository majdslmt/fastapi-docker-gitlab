"""unit test"""
from datetime import datetime
from types import SimpleNamespace
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app, is_valid_uuid


def db_mock(data):
    """This function returns a database mocking object, that will be used
    instead of the actual db connection.
    """
    database = SimpleNamespace()
    database.cursor = CursorMock(data)
    return database


class CursorMock:
    """This class mocks a db cursor. It does not build upon unittest.mock but
    it is instead built from an empty class, patching manually all needed
    methods.
    """

    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __call__(self):
        return self

    @staticmethod
    def execute(*args):
        """This mocks cursor.execute. It returns args even though the return
        value of cursor.execute() is never used. This is to avoid the
        following linting error:

        W0613: Unused argument 'args' (unused-argument)
        """
        return args

    def fetchall(self):
        """This mocks cursor.fetchall.
        """
        return self.data


sale = [
    "0188146f-5360-408b-a7c5-3414077ceb59",
    "2022-01-25T13:52:34",
    "0188146f-5360-408b-a7c5-3414077ceb59"
]


all_stores = [
    ["75040436-56de-401b-8919-8d0063ac9dd7", "Djuristen"],
    ["75040436-56de-401b-8919-8d0063ac9dd7", "Djuristen"]
]


all_cities = [
    ["c62fd71a-4490-4ca8-88b2-b1f808c30368", "dd4cf820-f946-4f38-8492-ca5dfeed0d74", "Upplandsgatan 99", "12345",
     "Stockholm"],
    ["e16e4cbc-184c-4e0c-8951-9b851a2f566c", "75040436-56de-401b-8919-8d0063ac9dd7", "Skånegatan 420", "54321",
     "Falun"],
]


cities_data = {'data': [
    {'id': 'c62fd71a-4490-4ca8-88b2-b1f808c30368', 'store_id': 'dd4cf820-f946-4f38-8492-ca5dfeed0d74',
     'address': 'Upplandsgatan 99', 'zip': '12345', 'city': 'Stockholm'},
    {'id': 'e16e4cbc-184c-4e0c-8951-9b851a2f566c', 'store_id': '75040436-56de-401b-8919-8d0063ac9dd7',
     'address': 'Skånegatan 420', 'zip': '54321', 'city': 'Falun'}]}


sale_by_id_result = {'data': {'store': 'Den Stora Djurbutiken', 'timestamp': '2022-01-25 13:52:34',
                              'sale_id': '0188146f-5360-408b-a7c5-3414077ceb59',
                              'products': [{'name': 'Hundmat', 'qty': 3},
                                           {'name': 'Sömnpiller och energidryck för djur', 'qty': 12}]}}


def test_get_all_stores():
    """test."""
    app.db = db_mock(all_stores)
    client = TestClient(app)
    response = client.get("/stores")
    assert response.status_code == 200
    assert response.json() == {'data': [{'id': '75040436-56de-401b-8919-8d0063ac9dd7', 'name': 'Djuristen'},
                                        {'id': '75040436-56de-401b-8919-8d0063ac9dd7', 'name': 'Djuristen'}]}


def test_get_all_store_by_name():
    """test."""
    app.db = db_mock([all_stores[0]])
    client = TestClient(app)
    response = client.get("/stores/Den%20Lilla%20Djurbutiken")
    assert response.status_code == 200
    assert response.json() == {'data': [{'id': '75040436-56de-401b-8919-8d0063ac9dd7', 'name': 'Djuristen'}]}


def test_get_all_cities():
    """test."""
    app.db = db_mock(all_cities)
    client = TestClient(app)
    response = client.get("/cities")
    assert response.status_code == 200
    print(response.json())
    assert response.json() == cities_data


def test_get_city_by_name():
    """test."""
    app.db = db_mock([all_cities[0]])
    client = TestClient(app)
    response = client.get("/cities/Stockholm")
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {'data': [
        {'id': 'c62fd71a-4490-4ca8-88b2-b1f808c30368', 'store_id': 'dd4cf820-f946-4f38-8492-ca5dfeed0d74',
         'address': 'Upplandsgatan 99', 'zip': '12345', 'city': 'Stockholm'}]}


def test_get_sales_details():
    """test."""
    app.db = db_mock([
        (
            'Den Stora Djurbutiken',
            datetime(2022, 1, 25, 13, 52, 34),
            UUID('0188146f-5360-408b-a7c5-3414077ceb59'),
            'Hundmat',
            3
        ),
        (
            'Den Stora Djurbutiken',
            datetime(2022, 1, 25, 13, 52, 34),
            UUID('0188146f-5360-408b-a7c5-3414077ceb59'),
            'Sömnpiller och energidryck för djur',
            12
        )
    ])
    client = TestClient(app)
    response = client.get("/sales/0188146f-5360-408b-a7c5-3414077ceb59")
    assert response.status_code == 200
    assert response.json() == sale_by_id_result


def test_check_uuid_true():
    """test."""
    response = is_valid_uuid("75040436-56de-401b-8919-8d0063ac9dd7")
    assert response is True


def test_check_uuid_false():
    """test."""
    response = is_valid_uuid("test")
    assert response is False
