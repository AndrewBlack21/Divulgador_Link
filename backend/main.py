from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import get_product_data
import os, sys

print("CWD:", os.getcwd())
print("SYS.PATH:", sys.path)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductRequest(BaseModel):
    url: str


def _build_response(url: str) -> dict:
    """Shared logic: scrape → return standard payload."""
    product = get_product_data(url)
    print(product)

    if product["title"] == "Produto não encontrado":
        raise HTTPException(status_code=422, detail="Produto não encontrado. Verifique o link.")

    return {
        "title": product["title"],
        "price": product["price"],
        "affiliateLink": product["final_url"],
    }


# ── single universal endpoint (used by the frontend) ──────────────────────
@app.post("/scrape")
def scrape_any(data: ProductRequest):
    """Auto-detects the store from the URL."""
    try:
        return _build_response(data.url)
    except HTTPException:
        raise
    except Exception as e:
        print("scrape error:", e)
        raise HTTPException(status_code=400, detail="Erro ao buscar produto.")


# ── kept for backwards-compatibility ──────────────────────────────────────
@app.post("/mercadolivre")
def mercadolivre(data: ProductRequest):
    try:
        return _build_response(data.url)
    except HTTPException:
        raise
    except Exception as e:
        print("mercadolivre error:", e)
        raise HTTPException(status_code=400, detail="Erro ao buscar produto.")


# ── per-store endpoints (optional, all delegate to auto-detect) ────────────
@app.post("/americanas")
def americanas(data: ProductRequest):
    try:
        return _build_response(data.url)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao buscar produto.")


@app.post("/shopee")
def shopee(data: ProductRequest):
    try:
        return _build_response(data.url)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao buscar produto.")


@app.post("/kabum")
def kabum(data: ProductRequest):
    try:
        return _build_response(data.url)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao buscar produto.")


@app.post("/casasbahia")
def casasbahia(data: ProductRequest):
    try:
        return _build_response(data.url)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao buscar produto.")


@app.post("/olx")
def olx(data: ProductRequest):
    try:
        return _build_response(data.url)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao buscar produto.")


@app.post("/magalu")
def magalu(data: ProductRequest):
    try:
        return _build_response(data.url)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Erro ao buscar produto.")