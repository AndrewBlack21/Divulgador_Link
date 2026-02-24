import json
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


NOT_FOUND = "Produto não encontrado"
NOT_FOUND_PRICE = "Preço não encontrado"


def _format_price(value):
    if value is None or value == "":
        return NOT_FOUND_PRICE

    if isinstance(value, str):
        cleaned = value.strip().replace("R$", "").replace(".", "").replace(",", ".")
    else:
        cleaned = str(value)

    try:
        number = Decimal(cleaned)
        return f"R$ {number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (InvalidOperation, ValueError):
        value_str = str(value).strip()
        if value_str.lower().startswith("r$"):
            return value_str
        return f"R$ {value_str}"


def _fetch_page(url):
    response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
    response.raise_for_status()
    return response


def _fetch_json(url, *, headers=None):
    response = requests.get(
        url,
        headers=headers or HEADERS,
        timeout=15,
        allow_redirects=True,
    )
    response.raise_for_status()
    return response.json()


def _extract_from_json_ld(soup):
    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        raw_json = script.string or script.get_text(strip=True)
        if not raw_json:
            continue

        try:
            payload = json.loads(raw_json)
        except Exception:
            continue

        entries = payload if isinstance(payload, list) else [payload]

        for entry in entries:
            if not isinstance(entry, dict):
                continue

            if entry.get("@type") != "Product":
                continue

            title = entry.get("name") or NOT_FOUND
            offers = entry.get("offers") or {}


    price_meta = (
        soup.find("meta", property="product:price:amount")
        or soup.find("meta", property="og:price:amount")
        or soup.find("meta", attrs={"itemprop": "price"})
    )

    if price_meta:
        price = price_meta.get("content")

    return title, _format_price(price) if price else None


def _extract_shopee_embedded_json(soup):
    # Shopee costuma expor dados do produto em scripts de estado inicial.
    possible_scripts = soup.find_all("script")

    title = None
    price = None

    patterns = [
        r'"name"\s*:\s*"([^\"]{6,200})"',
        r'"item_name"\s*:\s*"([^\"]{6,200})"',
    ]

    price_patterns = [
        r'"price"\s*:\s*"?(\d+(?:[\.,]\d+)?)"?',
        r'"price_min"\s*:\s*"?(\d+(?:[\.,]\d+)?)"?',
        r'"price_max"\s*:\s*"?(\d+(?:[\.,]\d+)?)"?',
    ]

    invalid_title_tokens = {
        "shopee__domain",
        "shopee__",
        "default_title",
        "meta_title",
        "shopee brasil",
    }

    for script in possible_scripts:
        content = script.string or script.get_text() or ""
        if "shopee" not in content.lower() and "price" not in content.lower():
            continue

        if title is None:
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    candidate_title = match.group(1).replace("\\u0026", "&").strip()
                    lowered_candidate = candidate_title.lower()
                    if any(token in lowered_candidate for token in invalid_title_tokens):
                        continue
                    if len(candidate_title) < 10:
                        continue
                    title = candidate_title
                    break

        if price is None:
            for pattern in price_patterns:
                match = re.search(pattern, content)
                if match:
                    raw_value = match.group(1)
                    try:
                        numeric = Decimal(raw_value.replace(",", "."))
                        # Alguns payloads da Shopee trazem 47.00 como 4700000.
                        if "." not in raw_value and "," not in raw_value and numeric >= 100000:
                            numeric = numeric / 100000
                        price = _format_price(numeric)
                    except Exception:
                        price = _format_price(raw_value)
                    break

        if title and price:
            break

    return title, price


def _extract_shopee_ids(url):
    parsed_url = urlparse(url)
    path = parsed_url.path

    # URLs mais comuns: /...-i.<shopid>.<itemid> ou /product/<shopid>/<itemid>
    match = re.search(r"-i\.(\d+)\.(\d+)", path)
    if match:
        return match.group(1), match.group(2)

    match = re.search(r"/product/(\d+)/(\d+)", path)
    if match:
        return match.group(1), match.group(2)

    return None, None


def _fetch_shopee_product_from_api(url):
    shop_id, item_id = _extract_shopee_ids(url)
    if not shop_id or not item_id:
        return None, None

    api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"

    api_headers = {
        **HEADERS,
        "Referer": url,
        "X-Requested-With": "XMLHttpRequest",
    }

    payload = _fetch_json(api_url, headers=api_headers)
    item = (payload or {}).get("data") or {}

    title = item.get("name")
    price_value = item.get("price_min") or item.get("price")
    if price_value is not None:
        price_value = Decimal(price_value) / 100000

    return title, _format_price(price_value) if price_value is not None else None


def get_product_data(url):
    response = _fetch_page(url)
    final_url = response.url
    soup = BeautifulSoup(response.text, "html.parser")

    title, price = _extract_from_json_ld(soup)

    if not title or price == NOT_FOUND_PRICE:
        meta_title, meta_price = _extract_from_meta(soup)
        title = title or meta_title
        price = price if price and price != NOT_FOUND_PRICE else meta_price

    return {
        "title": title or NOT_FOUND,
        "price": price or NOT_FOUND_PRICE,
        "final_url": final_url,
    }


def get_shopee_product_data(url):
    final_url = url

    try:
        title, price = _fetch_shopee_product_from_api(url)
    except Exception:
        title, price = None, None

    if title and price and price != NOT_FOUND_PRICE:
        return {
            "title": title,
            "price": price,
            "final_url": final_url,
        }

    response = _fetch_page(url)
    final_url = response.url
    soup = BeautifulSoup(response.text, "html.parser")

    if not title or not price or price == NOT_FOUND_PRICE:
        ld_title, ld_price = _extract_from_json_ld(soup)
        title = title or ld_title
        price = price if price and price != NOT_FOUND_PRICE else ld_price

    if not title or not price or price == NOT_FOUND_PRICE:
        meta_title, meta_price = _extract_from_meta(soup)
        title = title or meta_title
        price = price if price and price != NOT_FOUND_PRICE else meta_price

    if not title or not price or price == NOT_FOUND_PRICE:
        script_title, script_price = _extract_shopee_embedded_json(soup)
        title = title or script_title
        price = price if price and price != NOT_FOUND_PRICE else script_price

    return {
        "title": title or NOT_FOUND,
        "price": price or NOT_FOUND_PRICE,
        "final_url": final_url,
    }