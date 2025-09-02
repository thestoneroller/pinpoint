from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/search")
def search(keyword: str):
    return {"keyword": keyword}
