import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9"
}

def get_product_data(url):
    # 🔥 segue redirects (link afiliado → produto real)
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10,
        allow_redirects=True
    )

    final_url = response.url  # URL REAL DO PRODUTO
    soup = BeautifulSoup(response.text, "html.parser")

    # 🔎 busca JSON-LD
    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            data = json.loads(script.string)

            if isinstance(data, dict) and data.get("@type") == "Product":
                title = data.get("name", "Produto não encontrado")

                offers = data.get("offers", {})
                price = offers.get("price")

                price = f"R$ {price}" if price else "Preço não encontrado"

                return {
                    "title": title,
                    "price": price,
                    "final_url": final_url
                }

        except Exception:
            continue

    return {
        "title": "Produto não encontrado",
        "price": "Preço não encontrado",
        "final_url": final_url
    }
