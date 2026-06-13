from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import uuid4, UUID
from datetime import datetime

app = FastAPI()

class Advertisement(BaseModel):
    id: Optional[UUID] = Field(default_factory=uuid4)
    title: str
    description: str
    price: float
    author: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

ads_db = {}

@app.post("/advertisement")
def create_ad(ad: Advertisement):
    ad.id = uuid4()
    ad.created_at = datetime.utcnow()

    if not ad.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if ad.price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")
    if not ad.author.strip():
        raise HTTPException(status_code=400, detail="Author cannot be empty")
    ads_db[ad.id] = ad
    return ad

@app.patch("/advertisement/{advertisement_id}")
def update_ad(advertisement_id: UUID, ad_update: Advertisement):
    if advertisement_id not in ads_db:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    stored_ad = ads_db[advertisement_id]
    update_data = ad_update.dict(exclude_unset=True)

    if 'title' in update_data and not update_data['title'].strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if 'price' in update_data and update_data['price'] < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")
    if 'author' in update_data and not update_data['author'].strip():
        raise HTTPException(status_code=400, detail="Author cannot be empty")
    
    for key, value in update_data.items():
        setattr(stored_ad, key, value)
    ads_db[advertisement_id] = stored_ad
    return stored_ad

@app.delete("/advertisement/{advertisement_id}")
def delete_ad(advertisement_id: UUID):
    if advertisement_id not in ads_db:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    del ads_db[advertisement_id]
    return {"detail": "Deleted"}

@app.get("/advertisement/{advertisement_id}")
def get_ad(advertisement_id: UUID):
    if advertisement_id not in ads_db:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ads_db[advertisement_id]

@app.get("/advertisement")
def search_ads(
    title: Optional[str] = None,
    description: Optional[str] = None,
    author: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None
):
    results = list(ads_db.values())

    if title:
        results = [ad for ad in results if title.lower() in ad.title.lower()]

    if description:
        results = [ad for ad in results if description.lower() in ad.description.lower()]

    if author:
        results = [ad for ad in results if author.lower() in ad.author.lower()]

    if min_price is not None:
        results = [ad for ad in results if ad.price >= min_price]

    if max_price is not None:
        results = [ad for ad in results if ad.price <= max_price]

    if created_after:
        results = [ad for ad in results if ad.created_at >= created_after]

    if created_before:
        results = [ad for ad in results if ad.created_at <= created_before]

    return results