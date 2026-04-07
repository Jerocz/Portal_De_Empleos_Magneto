from fastapi import FastAPI

app = FastAPI(title="Portal de Empleos API")

@app.get("/")
def root():
    return {"message": "API funcionando correctamente"}