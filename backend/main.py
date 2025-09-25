import datetime
from fastapi import FastAPI
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from models.SingleOperationBody import SingleOperationBody
from typing import List
from models.MultipleOperationBody import MultipleOperationBody

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a MongoDB
mongo_client = MongoClient("mongodb://admin_user:web3@mongo:27017")
database = mongo_client["practica1"]
collection_historial = database["historial"]

def checkAllElementsAreNumbers(array):
    if type(array) != list:
        return False
    if not all(isinstance(element, (int, float)) for element in array):
        return False
    return True

def checkAllNumbersArePositive(array):
    if checkAllElementsAreNumbers(array) == False:
        return False
    
    if not all(element >= 0 for element in array):
        return False
    return True

def returnNegativeNumberError(operacion: str, numeros: list):
    raise HTTPException(
        status_code=400,
        detail={
            "error": "No se permiten números negativos",
            "operacion": operacion,
            "numeros": numeros
        }
    )


@app.post("/calculadora/sum")
def sumar(body: SingleOperationBody):
    resultado = 0
    if not checkAllNumbersArePositive(body.numeros):
        return returnNegativeNumberError("suma", body.numeros)

    for element in body.numeros:
        resultado = resultado + element

    document = {
        "resultado": resultado,
        "numeros": body.numeros,
        "operacion": "suma",
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    collection_historial.insert_one(document)

    return {"numeros": body.numeros, "resultado": resultado, "operacion": "suma"}

@app.post("/calculadora/resta")
def restar(body: SingleOperationBody):  
    if not checkAllNumbersArePositive(body.numeros):
        return returnNegativeNumberError("resta", body.numeros)
    
    resultado = body.numeros[0]
    numerosASumar = body.numeros[1:]
    for element in numerosASumar:
        resultado = resultado - element

    document = {
        "resultado": resultado,
        "numeros": body.numeros,
        "operacion": "resta",
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    collection_historial.insert_one(document)

    return {"numeros": body.numeros, "resultado": resultado, "operacion": "resta"}

@app.post("/calculadora/mult")
def multiplicar(body: SingleOperationBody):
    resultado = 1
    if not checkAllNumbersArePositive(body.numeros):
        return returnNegativeNumberError("multiplicacion", body.numeros)

    for element in body.numeros:
        resultado = resultado * element

    document = {
        "resultado": resultado,
        "numeros": body.numeros,
        "operacion": "multiplicacion",
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    collection_historial.insert_one(document)

    return {"numeros": body.numeros, "resultado": resultado, "operacion": "multiplicacion"}


@app.post("/calculadora/div")
def dividir(body: SingleOperationBody):
    if not checkAllNumbersArePositive(body.numeros):
        return returnNegativeNumberError("division", body.numeros)

    resultado = body.numeros[0]
    numerosADividir = body.numeros[1:]

    if 0 in numerosADividir:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "No se puede dividir por cero",
                "operacion": "division",
                "numeros": body.numeros
            }
        )

    for element in numerosADividir:
        resultado = resultado / element

    document = {
        "resultado": resultado,
        "numeros": body.numeros,
        "operacion": "division",
        "date": datetime.datetime.now(tz=datetime.timezone.utc),
    }
    collection_historial.insert_one(document)

    return {"numeros": body.numeros, "resultado": resultado, "operacion": "division"}

@app.post("/calculadora/operacionMultiple")
def multiple_operacion(operations: MultipleOperationBody):
    responses = []
    for operation in operations.operaciones:
        singleOperation = SingleOperationBody(numeros=operation.numeros)
        try:
            if operation.operacion == "suma":
                responses.append(sumar(singleOperation))
            elif operation.operacion == "resta":
                responses.append(restar(singleOperation))
            elif operation.operacion == "multiplicacion":
                responses.append(multiplicar(singleOperation))
            elif operation.operacion == "division":
                responses.append(dividir(singleOperation))
            else:
                responses.append({
                    "error": "Operacion no soportada",
                    "operacion": operation.operacion,
                    "numeros": operation.numeros
                })
        except HTTPException as e:
            responses.append({
                "error": e.detail.get("error") if isinstance(e.detail, dict) else str(e.detail),
                "operacion": operation.operacion,
                "numeros": operation.numeros
            })
    return responses



@app.get("/calculadora/historial")
def obtener_historial():
    operaciones = collection_historial.find({})
    historial = []
    for operacion in operaciones:
        historial.append({
            "a": operacion["a"],
            "b": operacion["b"],
            "resultado": operacion["resultado"],
            "date": operacion["date"].isoformat(),
            "operacion": operacion["operacion"]
        })
    return {"historial": historial}

