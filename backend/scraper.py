import re
import requests

MELI_API_BASE_URL = "https://api.mercadolibre.com"


def _extract_item_id(url: str) -> str | None:
    """Extrai o ID do item (ex.: MLB21263763) a partir de uma URL do Mercado Livre."""
    if not url:
        return None

    # Procura por MLB seguido de 8 a 12 dígitos
    match = re.search(r"MLB-?(\d{8,12})", url.upper())
    if match:
        return f"MLB{match.group(1)}"

    return None


def _format_price(price: float | int | None, currency: str | None) -> str:
    if price is None:
        return "Preço não encontrado"

    currency_symbol = "R$" if currency == "BRL" else (currency or "")
    return f"{currency_symbol} {price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def get_product_data(url: str) -> dict:
    item_id = _extract_item_id(url)

    if not item_id:
        raise ValueError("Não foi possível identificar o código do produto na URL enviada.")

    response = requests.get(f"{MELI_API_BASE_URL}/items/{item_id}", timeout=10)
    response.raise_for_status()

    data = response.json()

    title = data.get("title", "Produto não encontrado")
    price = _format_price(data.get("price"), data.get("currency_id"))
    permalink = data.get("permalink") or url

    return {
        "title": title,
        "price": price,
        "final_url": permalink,
    }