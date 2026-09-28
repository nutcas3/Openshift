from fastapi import FastAPI

app = FastAPI(title="${{ values.name }}")


@app.get("/hello")
def hello() -> str:
    return "Hello from ${{ values.name }}"


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}
