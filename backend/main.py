from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import get_product_data

app = FastAPI()

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
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Mudança aqui: retorne o erro real para debug
        raise HTTPException(
            status_code=400,
            detail=f"Erro interno: {str(e)}",
        )