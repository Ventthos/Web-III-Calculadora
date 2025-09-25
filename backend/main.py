from datetime import datetime, timezone
from fastapi import FastAPI
from pymongo import MongoClient, ASCENDING, DESCENDING
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
        "date": datetime.now(tz=timezone.utc)

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
        "date": datetime.now(tz=timezone.utc)
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
        "date": datetime.now(tz=timezone.utc)
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
        "date": datetime.now(tz=timezone.utc)
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
def obtener_historial(operacion: str = None, fecha: datetime = None, ordenarPor: str = None, orden: str = None):
    if operacion != None and operacion not in ("suma", "resta", "multiplicacion", "division"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Operacion no soportada",
                "operacion": operacion
            }
        )
    if fecha != None and type(fecha) != datetime:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Fecha no valida",
                "fecha": fecha
            }
        )
    if ordenarPor != None and ordenarPor not in ("date", "resultado"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Ordenar por no soportado",
                "ordenarPor": ordenarPor
            }
        )
    
    if orden != None and orden not in ("asc", "desc"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Orden no soportado",
                "orden": orden
            }
        )
    
    filtro = {}
    if operacion:
        filtro["operacion"] = operacion
    if fecha:
        filtro["date"] = {
            "$gte": datetime(fecha.year, fecha.month, fecha.day),
            "$lt": datetime(fecha.year, fecha.month, fecha.day, 23, 59, 59)
        }

    orden_mongo = ASCENDING if orden == "asc" else DESCENDING
    sort = [(ordenarPor, orden_mongo)] if ordenarPor else None

    cursor = collection_historial.find(filtro)
    if sort:
        cursor = cursor.sort(sort)

    historial = []
    for doc in cursor:
        historial.append({
            "numeros": doc["numeros"],
            "resultado": doc["resultado"],
            "date": doc["date"].isoformat(),
            "operacion": doc["operacion"]
        })
    return {"historial": historial}

