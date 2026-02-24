from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import get_product_data, get_shopee_product_data
import os
import sys

print("CWD:", os.getcwd())
print("SYS.PATH:", sys.path)

app = FastAPI()

# Libera o front
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductRequest(BaseModel):
    url: str


@app.post("/mercadolivre")
def mercadolivre(data: ProductRequest):
    try:
        product = get_product_data(data.url)

        return {
            "title": product["title"],
            "price": product["price"],
            "affiliateLink": product["final_url"],
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao buscar produto") from e


@app.post("/shopee")
def shopee(data: ProductRequest):
    try:
        product = get_shopee_product_data(data.url)

        return {
            "title": product["title"],
            "price": product["price"],
            "affiliateLink": product["final_url"],
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail="Erro ao buscar produto") from e