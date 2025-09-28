from datetime import datetime, timezone
from fastapi import FastAPI, Request
from pymongo import MongoClient, ASCENDING, DESCENDING
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from models.SingleOperationBody import SingleOperationBody
from typing import List
from models.MultipleOperationBody import MultipleOperationBody
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_validation_errors(errors, operacion: str = None):
    errores = []
    for err in errors:
        loc_type = err["loc"][0]
        loc_rest = " -> ".join([str(l) for l in err["loc"][1:]])
        input_value = err.get("input", "")
        if loc_rest:
            errores.append(f"Error en {loc_type} -> {loc_rest}: '{input_value}' no es válido.")
        else:
            errores.append(f"Error en {loc_type}: '{input_value}' no es válido.")
    
    respuesta = {"error": errores}
    if operacion:
        respuesta["operacion"] = operacion
    return respuesta

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": format_validation_errors(exc.errors())}
    )

# Conexión a MongoDB
mongo_client = MongoClient("mongodb://admin_user:web3@mongo:27017")
database = mongo_client["practica1"]
collection_historial = database["historial"]

def check_all_elements_are_numbers(array):
    if type(array) != list:
        return False
    if not all(isinstance(element, (int, float)) for element in array):
        return False
    return True

def check_all_numbers_are_positive(array):
    if check_all_elements_are_numbers(array) == False:
        return False
    
    if not all(element >= 0 for element in array):
        return False
    return True

def return_negative_number_error(operacion: str, numeros: list):
    raise HTTPException(
        status_code=400,
        detail={
            "error": "No se permiten números negativos",
            "operacion": operacion,
            "numerosNegativosEnviados": numeros
        }
    )

def save_in_db(operacion: str, numeros: list, resultado: float):
    document = {
        "resultado": resultado,
        "numeros": numeros,
        "operacion": operacion,
        "date": datetime.now(tz=timezone.utc)
    }
    collection_historial.insert_one(document)

@app.post("/calculadora/sum")
def sumar(body: SingleOperationBody):
    resultado = 0
    if not check_all_numbers_are_positive(body.numeros):
        negativeNumbers = [element for element in body.numeros if element < 0]
        return return_negative_number_error("suma", negativeNumbers)

    for element in body.numeros:
        resultado = resultado + element

    save_in_db("suma", body.numeros, resultado)

    return {"numeros": body.numeros, "resultado": resultado, "operacion": "suma"}

@app.post("/calculadora/resta")
def restar(body: SingleOperationBody):  
    if not check_all_numbers_are_positive(body.numeros):
        negativeNumbers = [element for element in body.numeros if element < 0]
        return return_negative_number_error("resta", negativeNumbers)
    
    resultado = body.numeros[0]
    numerosASumar = body.numeros[1:]
    for element in numerosASumar:
        resultado = resultado - element

    save_in_db("resta", body.numeros, resultado)

    return {"numeros": body.numeros, "resultado": resultado, "operacion": "resta"}

@app.post("/calculadora/mult")
def multiplicar(body: SingleOperationBody):
    resultado = 1
    if not check_all_numbers_are_positive(body.numeros):
        negativeNumbers = [element for element in body.numeros if element < 0]
        return return_negative_number_error("multiplicacion", negativeNumbers)

    for element in body.numeros:
        resultado = resultado * element

    save_in_db("multiplicacion", body.numeros, resultado)

    return {"numeros": body.numeros, "resultado": resultado, "operacion": "multiplicacion"}


@app.post("/calculadora/div")
def dividir(body: SingleOperationBody):
    if not check_all_numbers_are_positive(body.numeros):
        negativeNumbers = [element for element in body.numeros if element < 0]
        return return_negative_number_error("division", negativeNumbers)

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

    save_in_db("division", body.numeros, resultado)

    return {"numeros": body.numeros, "resultado": resultado, "operacion": "division"}

@app.post("/calculadora/operacionMultiple")
def multiple_operacion(operations: MultipleOperationBody):
    responses = []
    has_error = False

    for operation in operations.operaciones:
        try:
    
            singleOperation = SingleOperationBody(numeros=operation.numeros)

            if operation.operacion == "suma":
                responses.append(sumar(singleOperation))
            elif operation.operacion == "resta":
                responses.append(restar(singleOperation))
            elif operation.operacion == "multiplicacion":
                responses.append(multiplicar(singleOperation))
            elif operation.operacion == "division":
                responses.append(dividir(singleOperation))
            else:
                has_error = True
                responses.append({
                    "error": "Operacion no soportada",
                    "operacion": operation.operacion,
                    "numeros": operation.numeros
                })

        except ValidationError as e:
            has_error = True
            responses.append(format_validation_errors(e.errors(), operation.operacion))
        except HTTPException as e:
            has_error = True
            responses.append(e.detail)

    status_code = 206 if has_error else 200
    return JSONResponse(content=responses, status_code=status_code)



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


