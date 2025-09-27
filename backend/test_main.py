import mongomock
import pytest

from pymongo import MongoClient
from fastapi import FastAPI
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)

def create_fake_collection():
    fake_mongo_client = mongomock.MongoClient()
    database = fake_mongo_client.practica1
    collection = database.historial
    return collection

@pytest.fixture
def fake_collection(monkeypatch):
    collection = create_fake_collection()
    monkeypatch.setattr(main, "collection_historial", collection)
    return collection

def make_request(endpoint, numeros):
    body = {"numeros": numeros}
    response = client.post(f"/calculadora/{endpoint}", json=body)
    return response

def make_multiple_request(operations):
    body = {"operaciones": operations}
    response = client.post("/calculadora/operacionMultiple", json=body)
    return response

# Sumar
@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,10], 15),
        ([3,35], 38),
        ([5,7,3], 15),
        ([2,10,5,9,7], 33)
    ]
)
def test_sumar(fake_collection, numeros, resultado):
    response = make_request("sum", numeros)
    assert response.status_code == 200
    assert response.json() == {"numeros": numeros, "operacion": "suma", "resultado": resultado}
    assert fake_collection.find_one({"numeros": numeros, "operacion": "suma", "resultado": resultado}) is not None

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,-10], -5),
        ([-3,35], 32),
        ([5,-7,3], 1),
        ([-2,10,5,-9,-7], -3)
    ]
)
def test_sumar_negativo(fake_collection, numeros, resultado):
    response = make_request("sum", numeros)
    numerosNegativos = [n for n in numeros if n < 0]

    assert response.status_code == 400
    assert response.json() == { 
        "detail": {
            "error": "No se permiten números negativos",
            "operacion": "suma",
            "numerosNegativosEnviados": numerosNegativos
        }
    }
    assert fake_collection.find_one({"numeros": numeros, "operacion": "suma", "resultado": resultado}) is None

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,"-d10"], -5),
    ]
)
def test_sumar_invalidos(fake_collection, numeros, resultado):
    response = make_request("sum", numeros)
    assert response.status_code == 422
    assert response.json() == { 
        "detail": {
            "error": ["Error en body -> numeros -> 1: '-d10' no es válido."],
        }
    }
    assert fake_collection.find_one({"numeros": numeros, "operacion": "suma", "resultado": resultado}) is None

# Resta
@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,10], -5),
        ([3,35], -32),
        ([5,7,3], -5),
        ([2,10,5,9,7], -29),
        ([20,10,5], 5)
    ]
)
def test_restar(fake_collection, numeros, resultado):
    response = make_request("resta", numeros)
    assert response.status_code == 200
    assert response.json() == {"numeros": numeros, "operacion": "resta", "resultado": resultado}
    assert fake_collection.find_one({"numeros": numeros, "operacion": "resta", "resultado": resultado}) is not None

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,-10], -15),
        ([-3,35], -38),
        ([5,-7,3], 9),
        ([-2,10,5,-9,-7], -1)
    ]
)
def test_restar_negativo(fake_collection, numeros, resultado):
    response = make_request("resta", numeros)
    numerosNegativos = [n for n in numeros if n < 0]

    assert response.status_code == 400
    assert response.json() == { 
        "detail": {
            "error": "No se permiten números negativos",
            "operacion": "resta",
            "numerosNegativosEnviados": numerosNegativos
        }
    }
    assert fake_collection.find_one({"numeros": numeros, "operacion": "resta", "resultado": resultado}) is None

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,"-d10"], -5),
    ]
)
def test_restar_invalidos(fake_collection, numeros, resultado):
    response = make_request("resta", numeros)
    assert response.status_code == 422
    assert response.json() == { 
        "detail": {
            "error": ["Error en body -> numeros -> 1: '-d10' no es válido."],
        }
    }
    assert fake_collection.find_one({"numeros": numeros, "operacion": "resta", "resultado": resultado}) is None

# Multiplicacion
@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,10], 50),
        ([3,35], 105),
        ([5,7,3], 105),
        ([2,10,5,9,7], 6300),
        ([20,10,5], 1000),
        ([2.5,2,2], 10)
    ]
)
def test_multiplicar(fake_collection, numeros, resultado):
    response = make_request("mult", numeros)
    assert response.status_code == 200
    assert response.json() == {"numeros": numeros, "operacion": "multiplicacion", "resultado": resultado}
    assert fake_collection.find_one({"numeros": numeros, "operacion": "multiplicacion", "resultado": resultado}) is not None

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,-10], -50),
        ([-3,35], -105),
        ([5,-7,3], -105),
        ([-2,10,5,-9,-7], -6300),
        ([2.5,-2,2], -10)
    ]
)
def test_multiplicar_negativo(fake_collection, numeros, resultado):
    response = make_request("mult", numeros)
    numerosNegativos = [n for n in numeros if n < 0]

    assert response.status_code == 400
    assert response.json() == { 
        "detail": {
            "error": "No se permiten números negativos",
            "operacion": "multiplicacion",
            "numerosNegativosEnviados": numerosNegativos
        }
    }
    assert fake_collection.find_one({"numeros": numeros, "operacion": "multiplicacion", "resultado": resultado}) is None

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,"-mg10"], -5),
    ]
)
def test_multiplicar_invalidos(fake_collection, numeros, resultado):
    response = make_request("mult", numeros)
    assert response.status_code == 422
    assert response.json() == { 
        "detail": {
            "error": ["Error en body -> numeros -> 1: '-mg10' no es válido."],
        }
    }
    assert fake_collection.find_one({"numeros": numeros, "operacion": "multiplicacion", "resultado": resultado}) is None

# Division
@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,10], 0.5),
        ([10,5], 2),
        ([30,10,3], 1),
        ([1000,10,10,10,0.5], 2),
        ([20,10,5], 0.4),
        ([2.5,2,2], 0.625)
    ]
)
def test_dividir(fake_collection, numeros, resultado):
    response = make_request("div", numeros)
    assert response.status_code == 200
    assert response.json() == {"numeros": numeros, "operacion": "division", "resultado": resultado}
    assert fake_collection.find_one({"numeros": numeros, "operacion": "division", "resultado": resultado}) is not None

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,-10], -0.5),
        ([-10,5], -2),
        ([30,-10,3], -1),
        ([1000,10,10,-10,0.5], -2),
        ([-20,10,5], -0.4),
        ([2.5,-2,2], -0.625)
    ]
)
def test_dividir_negativo(fake_collection, numeros, resultado):
    response = make_request("div", numeros)
    numerosNegativos = [n for n in numeros if n < 0]

    assert response.status_code == 400
    assert response.json() == { 
        "detail": {
            "error": "No se permiten números negativos",
            "operacion": "division",
            "numerosNegativosEnviados": numerosNegativos
        }
    }
    assert fake_collection.find_one({"numeros": numeros, "operacion": "division", "resultado": resultado}) is None

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,"-mg10"], -5),
    ]
)
def test_dividir_invalidos(fake_collection, numeros, resultado):
    response = make_request("div", numeros)
    assert response.status_code == 422
    assert response.json() == { 
        "detail": {
            "error": ["Error en body -> numeros -> 1: '-mg10' no es válido."],
        }
    }
    assert fake_collection.find_one({"numeros": numeros, "operacion": "division", "resultado": resultado}) is None

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,0], 0),
        ([8,0], 0),
        ([30,0,3], 0),
        ([800,10,0,10,0.5], 0),
        ([20,10,0], 0),
        ([2.5,0,2], 0)
    ]
)
def test_dividir_entre_cero(fake_collection, numeros, resultado):
    response = make_request("div", numeros)
    assert response.status_code == 403
    assert response.json() == {
        "detail": {
            "error": "No se puede dividir por cero",
            "operacion": "division",
            "numeros": numeros
        }
    }
    assert fake_collection.find_one({"numeros": numeros, "operacion": "division", "resultado": resultado}) is None


# Operaciones multiples
@pytest.mark.parametrize(
    "operations_input, resultados_esperados",
    [
        (
            [
                {"operacion": "suma", "numeros": [5,10,9]},
                {"operacion": "resta", "numeros": [20,5]},
                {"operacion": "multiplicacion", "numeros": [2,3]},
                {"operacion": "division", "numeros": [10,2]}
            ],
            [24, 15, 6, 5]
        ),
        (
            [
                {"operacion": "suma", "numeros": [1,2]},
                {"operacion": "multiplicacion", "numeros": [3,4]},
            ],
            [3, 12]
        ),
    ]
)
def test_operaciones_multiples(fake_collection, operations_input, resultados_esperados):
    expected = []
    for op, resultado in zip(operations_input, resultados_esperados):
        expected.append({
            "numeros": op["numeros"],
            "operacion": op["operacion"],
            "resultado": resultado
        })

    response = make_multiple_request(operations_input)
    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize(
    "operations_input",
    [
        [
            {"operacion": "suma", "numeros": [5,-10]},
            {"operacion": "resta", "numeros": [-5,3]}
        ],
        [
            {"operacion": "multiplicacion", "numeros": [2,-3]},
            {"operacion": "division", "numeros": [-10,2]}
        ]
    ]
)
def test_operaciones_negativas_multiples(fake_collection, operations_input):
    expected = []
    for op in operations_input:
        numeros_negativos = [n for n in op["numeros"] if n < 0]
        expected.append({
            "error": "No se permiten números negativos",
            "operacion": op["operacion"],
            "numerosNegativosEnviados": numeros_negativos
        })

    response = make_multiple_request(operations_input)
    assert response.status_code == 206
    assert response.json() == expected


@pytest.mark.parametrize(
    "operations_input,expected",
    [
        (
            [
                {"operacion": "suma", "numeros": [5, 5]},  
                {"operacion": "resta", "numeros": [10, "0d"]}  
            ],
            [
                {"operacion": "suma", "numeros": [5, 5], "resultado": 10},
                {"error": ["Error en numeros -> 1: '0d' no es válido."], "operacion": "resta"}
            ]
        )
    ]
)
def test_operaciones_invalidas_multiples(fake_collection, operations_input, expected):
    response = make_multiple_request(operations_input)
    assert response.status_code == 206

    assert response.json() == expected



@pytest.mark.parametrize(
    "operations, expected",
    [
        (
            [{"operacion": "potencia", "numeros": [2,3]}, {"operacion": "multiplicacion", "numeros": [2,3]}],
            [{"error": "Operacion no soportada", "operacion": "potencia", "numeros": [2,3]}, {"numeros":[2,3],"resultado":6,"operacion":"multiplicacion"}]
        ),
        (
            [{"operacion": "mod", "numeros": [10,3]}],
            [{"error": "Operacion no soportada", "operacion": "mod", "numeros": [10,3]}]
        )
    ]
)
def test_operaciones_no_soportadas_multiples(fake_collection, operations, expected):
    response = make_multiple_request(operations)
    assert response.status_code == 206
    assert response.json() == expected


@pytest.mark.parametrize(
    "operations, expected",
    [
        (
            [{"operacion": "division", "numeros": [8,4]}, {"operacion": "division", "numeros": [10,0]}, {"operacion": "division", "numeros": [10,2]}],
            [{"numeros":[8,4],"resultado":2,"operacion":"division"}, {"error": "No se puede dividir por cero", "operacion": "division", "numeros": [10,0]}, {"numeros":[10,2],"resultado":5,"operacion":"division"}]
        ),
        (
            [{"operacion": "division", "numeros": [0,0]}],
            [{"error": "No se puede dividir por cero", "operacion": "division", "numeros": [0,0]}]
        )
    ]
)
def test_operaciones_division_por_cero_multiples(fake_collection, operations, expected):
    response = make_multiple_request(operations)
    assert response.status_code == 206
    assert response.json() == expected


# --> Del historial
colection = create_fake_collection()

lista_sumas = [
    [3],
    [1, 2],
    [4, 5, 6],
    [7, 8, 9, 10],
    [2, 3, 5, 7, 11],
    [10, 20, 30, 40, 50, 60],
    [5, 10, 15, 20, 25, 30, 35],
    [1, 2, 3, 4, 5, 6, 7, 8],
    [9, 8, 7, 6, 5, 4, 3, 2, 1],
    [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
]
