import mongomock
import pytest

from pymongo import MongoClient
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import datetime

import main

client = TestClient(main.app)

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,10], True),
        ([3,35,"aaa"], False),
        ([5,"lll",3], False),
        ([2,10,"5",9,7], True)
    ]
)
def test_check_all_elements_are_numbers(numeros, resultado):
    main.check_all_elements_are_numbers(numeros) == resultado

@pytest.mark.parametrize(
    "numeros, resultado",
    [
        ([5,10], True),
        ([3,35,"aaa"], False),
        ([5,-9,3], False),
        ([2,10,"5",-9,7], False),
        ([5,34,6,7], True)
    ]
)
def test_check_all_numbers_are_positive(numeros, resultado):
    main.check_all_numbers_are_positive(numeros) == resultado

def test_format_validation_errors_sin_operacion():
    errors = [
        {"loc": ["query", "fecha"], "input": "invalid-date"}
    ]
    expected = {
        "error": ["Error en query -> fecha: 'invalid-date' no es válido."]
    }
    assert main.format_validation_errors(errors) == expected

def test_format_validation_errors_con_operacion():
    errors = [
        {"loc": ["body", "numeros", 0], "input": "abc"},
        {"loc": ["body", "operacion"], "input": "potencia"}
    ]
    expected = {
        "error": [
            "Error en body -> numeros -> 0: 'abc' no es válido.",
            "Error en body -> operacion: 'potencia' no es válido."
        ],
        "operacion": "suma"
    }
    assert main.format_validation_errors(errors, operacion="suma") == expected

@pytest.mark.parametrize(
    "numeros_negativos, operacion",
    [
        ([5,-10], "suma"),
        ([-3,35], "resta"),
        ([5,-7,3], "multiplicacion"),
        ([2,10,-5,9,7], "division")
    ]
)
def test_return_negative_number_error(numeros_negativos, operacion):
    with pytest.raises(HTTPException) as exc_info:
        main.return_negative_number_error(operacion, numeros_negativos)
    
    exc = exc_info.value
    assert exc.status_code == 400
    assert exc.detail == {
        "error": "No se permiten números negativos",
        "operacion": operacion,
        "numerosNegativosEnviados": numeros_negativos
    }

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
def format_expected_resultado(expected_data):
    historial = []
    for doc in expected_data:
        historial.append({
            "numeros": doc["numeros"],
            "resultado": doc["resultado"],
            "date": doc["date"].isoformat(),
            "operacion": doc["operacion"]
        })
    return historial


def llenar_coleccion():
    collection = create_fake_collection()
    collection.delete_many({})  
    docs = [
        {"numeros": [1, 2], "resultado": 3, "date": datetime(2025, 9, 26, 10, 0), "operacion": "suma"},
        {"numeros": [5, 5], "resultado": 10, "date": datetime(2025, 9, 26, 11, 0), "operacion": "suma"},
        {"numeros": [10, 3], "resultado": 7, "date": datetime(2025, 9, 26, 12, 0), "operacion": "resta"},
        {"numeros": [20, 4], "resultado": 5, "date": datetime(2025, 9, 26, 13, 0), "operacion": "division"},
        {"numeros": [2, 3], "resultado": 6, "date": datetime(2025, 9, 26, 14, 0), "operacion": "multiplicacion"},
        {"numeros": [2, 3], "resultado": 6, "date": datetime(2025, 9, 25, 14, 0), "operacion": "multiplicacion"},
    ]
    collection.insert_many(docs)
    return collection

def test_historial_completo(monkeypatch):
    collection = llenar_coleccion()
    monkeypatch.setattr(main, "collection_historial", collection)

    response = client.get("/calculadora/historial")
    assert response.status_code == 200

    expected_historial = [
        {"numeros": [1, 2], "resultado": 3, "date": "2025-09-26T10:00:00-06:00", "operacion": "suma"},
        {"numeros": [5, 5], "resultado": 10, "date": "2025-09-26T11:00:00-06:00", "operacion": "suma"},
        {"numeros": [10, 3], "resultado": 7, "date": "2025-09-26T12:00:00-06:00", "operacion": "resta"},
        {"numeros": [20, 4], "resultado": 5, "date": "2025-09-26T13:00:00-06:00", "operacion": "division"},
        {"numeros": [2, 3], "resultado": 6, "date": "2025-09-26T14:00:00-06:00", "operacion": "multiplicacion"},
        {"numeros": [2, 3], "resultado": 6, "date": "2025-09-25T14:00:00-06:00", "operacion": "multiplicacion"}
    ]

    assert response.json() == {"historial": expected_historial}

def test_historial_completo(monkeypatch):
    collection = llenar_coleccion()
    monkeypatch.setattr(main, "collection_historial", collection)

    response = client.get("/calculadora/historial")
    assert response.status_code == 200

    expected_historial = [
        {"numeros": [1, 2], "resultado": 3, "date": "2025-09-26T10:00:00-06:00", "operacion": "suma"},
        {"numeros": [5, 5], "resultado": 10, "date": "2025-09-26T11:00:00-06:00", "operacion": "suma"},
        {"numeros": [10, 3], "resultado": 7, "date": "2025-09-26T12:00:00-06:00", "operacion": "resta"},
        {"numeros": [20, 4], "resultado": 5, "date": "2025-09-26T13:00:00-06:00", "operacion": "division"},
        {"numeros": [2, 3], "resultado": 6, "date": "2025-09-26T14:00:00-06:00", "operacion": "multiplicacion"},
        {"numeros": [2, 3], "resultado": 6, "date": "2025-09-25T14:00:00-06:00", "operacion": "multiplicacion"}
    ]

    assert response.json() == {"historial": expected_historial}


@pytest.mark.parametrize(
    "ruta, expected_historial",
    [
        (
            "/calculadora/historial?operacion=suma",
            [
                {"numeros": [1, 2], "resultado": 3, "date": "2025-09-26T10:00:00-06:00", "operacion": "suma"},
                {"numeros": [5, 5], "resultado": 10, "date": "2025-09-26T11:00:00-06:00", "operacion": "suma"},
            ]
        ),
        (
            "/calculadora/historial?operacion=resta",
            [
                {"numeros": [10, 3], "resultado": 7, "date": "2025-09-26T12:00:00-06:00", "operacion": "resta"}
            ]
        ),
        (
            "/calculadora/historial?operacion=multiplicacion",
            [
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-26T14:00:00-06:00", "operacion": "multiplicacion"},
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-25T14:00:00-06:00", "operacion": "multiplicacion"}
            ]
        ),
        (
            "/calculadora/historial?operacion=division",
            [
                {"numeros": [20, 4], "resultado": 5, "date": "2025-09-26T13:00:00-06:00", "operacion": "division"}
            ]
        ),
        (
            "/calculadora/historial?ordenarPor=resultado&orden=asc",
            [
                {"numeros": [1, 2], "resultado": 3, "date": "2025-09-26T10:00:00-06:00", "operacion": "suma"},
                {"numeros": [20, 4], "resultado": 5, "date": "2025-09-26T13:00:00-06:00", "operacion": "division"},
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-26T14:00:00-06:00", "operacion": "multiplicacion"},
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-25T14:00:00-06:00", "operacion": "multiplicacion"},
                {"numeros": [10, 3], "resultado": 7, "date": "2025-09-26T12:00:00-06:00", "operacion": "resta"},   
                {"numeros": [5, 5], "resultado": 10, "date": "2025-09-26T11:00:00-06:00", "operacion": "suma"},
            ]
        ),
        (
            "/calculadora/historial?ordenarPor=resultado&orden=desc",
            [
                {"numeros": [5, 5], "resultado": 10, "date": "2025-09-26T11:00:00-06:00", "operacion": "suma"},
                {"numeros": [10, 3], "resultado": 7, "date": "2025-09-26T12:00:00-06:00", "operacion": "resta"},
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-26T14:00:00-06:00", "operacion": "multiplicacion"},
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-25T14:00:00-06:00", "operacion": "multiplicacion"},
                {"numeros": [20, 4], "resultado": 5, "date": "2025-09-26T13:00:00-06:00", "operacion": "division"},
                {"numeros": [1, 2], "resultado": 3, "date": "2025-09-26T10:00:00-06:00", "operacion": "suma"},
            ]
        ),
        (
            "/calculadora/historial?ordenarPor=date&orden=asc",
            [
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-25T14:00:00-06:00", "operacion": "multiplicacion"},
                {"numeros": [1, 2], "resultado": 3, "date": "2025-09-26T10:00:00-06:00", "operacion": "suma"},
                {"numeros": [5, 5], "resultado": 10, "date": "2025-09-26T11:00:00-06:00", "operacion": "suma"},
                {"numeros": [10, 3], "resultado": 7, "date": "2025-09-26T12:00:00-06:00", "operacion": "resta"},
                {"numeros": [20, 4], "resultado": 5, "date": "2025-09-26T13:00:00-06:00", "operacion": "division"},
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-26T14:00:00-06:00", "operacion": "multiplicacion"},
            ]
        ),
        (
            "/calculadora/historial?ordenarPor=date&orden=desc",
            [
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-26T14:00:00-06:00", "operacion": "multiplicacion"},
                {"numeros": [20, 4], "resultado": 5, "date": "2025-09-26T13:00:00-06:00", "operacion": "division"},
                {"numeros": [10, 3], "resultado": 7, "date": "2025-09-26T12:00:00-06:00", "operacion": "resta"},
                {"numeros": [5, 5], "resultado": 10, "date": "2025-09-26T11:00:00-06:00", "operacion": "suma"},
                {"numeros": [1, 2], "resultado": 3, "date": "2025-09-26T10:00:00-06:00", "operacion": "suma"},
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-25T14:00:00-06:00", "operacion": "multiplicacion"}
            ]
        ),
        (
            "/calculadora/historial?fecha=2025-09-25",
            [
                {"numeros": [2, 3], "resultado": 6, "date": "2025-09-25T14:00:00-06:00", "operacion": "multiplicacion"}
            ]
        ),
        (
            "/calculadora/historial?operacion=suma&ordenarPor=resultado&orden=desc",
            [
                {"numeros": [5, 5], "resultado": 10, "date": "2025-09-26T11:00:00-06:00", "operacion": "suma"},
                {"numeros": [1, 2], "resultado": 3, "date": "2025-09-26T10:00:00-06:00", "operacion": "suma"},
            ]
        ),
        (
            "/calculadora/historial?operacion=suma&ordenarPor=date&orden=asc",
            [
                {"numeros": [1, 2], "resultado": 3, "date": "2025-09-26T10:00:00-06:00", "operacion": "suma"},
                {"numeros": [5, 5], "resultado": 10, "date": "2025-09-26T11:00:00-06:00", "operacion": "suma"},
            ]
        ),
    ]
)
def test_historial_filtro(monkeypatch, ruta, expected_historial):
    collection = llenar_coleccion()
    monkeypatch.setattr(main, "collection_historial", collection)
    client = TestClient(main.app)

    response = client.get(ruta)
    assert response.status_code == 200
    assert response.json() == {"historial": expected_historial}

@pytest.mark.parametrize(
    "ruta, codigo, expected_detail",
    [
        (
            "/calculadora/historial?operacion=potencia",
            400,
            {"error": "Operacion no soportada", "operacion": "potencia"}
        ),
        (
            "/calculadora/historial?fecha=invalid-date",
            422,
            {"error": ["Error en query -> fecha: 'invalid-date' no es válido."]}
        ),
        (
            "/calculadora/historial?ordenarPor=nombre&orden=asc",
            400,
            {"error": "Ordenar por no soportado", "ordenarPor": "nombre"}
        ),
        (
            "/calculadora/historial?ordenarPor=resultado&orden=up",
            400,
            {"error": "Orden no soportado", "orden": "up"}
        ),
        (
            "/calculadora/historial?operacion=raiz&ordenarPor=fecha&orden=sideways",
            400,
            {"error": "Operacion no soportada", "operacion": "raiz"}
        ),
    ]
)
def test_historial_errores(monkeypatch, ruta, codigo, expected_detail):
    collection = llenar_coleccion()  
    monkeypatch.setattr(main, "collection_historial", collection)

    response = client.get(ruta)
    assert response.status_code == codigo
    assert "detail" in response.json()
    assert response.json()["detail"] == expected_detail


@pytest.mark.parametrize(
    "operacion, numeros, resultado",
    [
        ("suma", [1, 2], 3),
        ("resta", [5, 3,1], 1),
        ("multiplicacion", [2, 3,2,2], 24),
        ("division", [10, 2], 5)
    ]
)
def test_save_in_db(fake_collection, operacion, numeros, resultado):
    main.save_in_db(operacion, numeros, resultado)
    doc = fake_collection.find_one({"operacion": operacion})
    assert doc["operacion"] == operacion
    assert doc["numeros"] == numeros
    assert doc["resultado"] == resultado
    assert type(doc["date"]) == datetime