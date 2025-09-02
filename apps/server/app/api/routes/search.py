from fastapi import APIRouter

router = APIRouter()


@router.post("/search")
def search(query: str):
    return {"query": query}
