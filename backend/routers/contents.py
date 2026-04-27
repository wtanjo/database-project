from fastapi import APIRouter
from db.mongo import contents_collection

router = APIRouter(prefix="/api/contents", tags=["contents"])

@router.get("")
async def list_contents():
    cursor = contents_collection.find({}).sort("_id", -1).limit(50)
    
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
    
    return results
