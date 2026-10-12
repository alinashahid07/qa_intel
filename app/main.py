from fastapi import FastAPI

app = FastAPI(title="QA Intel Platform")


@app.get("/health")
def health():
    return {"status": "ok"}