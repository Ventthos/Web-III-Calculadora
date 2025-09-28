import random
import main


def fill_collection(monkeypatch, collection_historial,client, n=20):
    if  collection_historial.count_documents({}) > 0:
        collection_historial.delete_many({})
    operaciones = ["sum", "resta", "mult", "div"]

    monkeypatch.setattr(main, "collection_historial", collection_historial)

    for _ in range(n):
        numeros = [random.randint(1, 100) for _ in range(random.randint(1, 10))]
        operacion = random.choice(operaciones)
        payload = {"numeros": numeros}
        response = client.post(f"/calculadora/{operacion}", json=payload)