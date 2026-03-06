import requests
from bs4 import BeautifulSoup
import json
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def _fetch(url, extra_headers=None):
    """Fetch URL and return (response, soup, final_url)."""
    h = {**HEADERS, **(extra_headers or {})}
    response = requests.get(url, headers=h, timeout=15, allow_redirects=True)
    soup = BeautifulSoup(response.text, "lxml")
    return response, soup, response.url


def _price_fmt(raw):
    """Normalise any price value to 'R$ X.XXX,XX' format."""
    if not raw:
        return "Preço não encontrado"
    s = str(raw).strip()
    # Already formatted (e.g. "R$ 199,90")
    if s.startswith("R$"):
        return s
    # Float like 1999.9
    try:
        val = float(s.replace(",", "."))
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return f"R$ {s}"


def _json_ld_product(soup):
    """Try standard JSON-LD Product schema (works on ML, Kabum, Casas Bahia, Americanas)."""
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            # Direct Product
            if isinstance(data, dict) and data.get("@type") == "Product":
                return data
            # Graph array
            if isinstance(data, dict) and "@graph" in data:
                for item in data["@graph"]:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        return item
            # Array at root
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        return item
        except Exception:
            continue
    return None


def _extract_from_json_ld(product_data):
    """Return (title, price_str) from a JSON-LD Product dict."""
    title = product_data.get("name", "").strip() or "Produto não encontrado"
    offers = product_data.get("offers") or {}
    # offers can be a list
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    price = offers.get("price") or offers.get("lowPrice")
    return title, _price_fmt(price)


# ─────────────────────────────────────────────
# MERCADO LIVRE
# ─────────────────────────────────────────────
def get_mercadolivre_data(url):
    _, soup, final_url = _fetch(url)

    # 1. JSON-LD
    ld = _json_ld_product(soup)
    if ld:
        title, price = _extract_from_json_ld(ld)
        if title != "Produto não encontrado":
            return {"title": title, "price": price, "final_url": final_url}

    # 2. Meta tags fallback
    title = (soup.find("meta", property="og:title") or {}).get("content", "")
    price_tag = soup.find("meta", itemprop="price") or soup.find("span", class_=re.compile(r"price|andes-money"))
    price = price_tag.get("content") if price_tag and price_tag.name == "meta" else (price_tag.get_text() if price_tag else "")

    return {
        "title": title or "Produto não encontrado",
        "price": _price_fmt(price) if price else "Preço não encontrado",
        "final_url": final_url,
    }


# ─────────────────────────────────────────────
# AMERICANAS / SUBMARINO / SHOPTIME  (B2W group)
# ─────────────────────────────────────────────
def get_americanas_data(url):
    _, soup, final_url = _fetch(url)

    # 1. JSON-LD
    ld = _json_ld_product(soup)
    if ld:
        title, price = _extract_from_json_ld(ld)
        if title != "Produto não encontrado":
            return {"title": title, "price": price, "final_url": final_url}

    # 2. __NEXT_DATA__ (Americanas uses Next.js)
    nd = soup.find("script", id="__NEXT_DATA__")
    if nd:
        try:
            data = json.loads(nd.string)
            props = data.get("props", {}).get("pageProps", {})
            # path: pageProps.product or pageProps.data.product
            product = props.get("product") or (props.get("data") or {}).get("product") or {}
            name = product.get("name") or product.get("title") or ""
            # price paths vary by version
            price_val = (
                product.get("price")
                or product.get("salesPrice")
                or (product.get("offers") or [{}])[0].get("price")
                or ""
            )
            if name:
                return {"title": name, "price": _price_fmt(price_val), "final_url": final_url}
        except Exception:
            pass

    # 3. Meta og tags
    title = (soup.find("meta", property="og:title") or {}).get("content", "")
    price_meta = soup.find("meta", property="product:price:amount") or soup.find("meta", itemprop="price")
    price = price_meta.get("content", "") if price_meta else ""

    return {
        "title": title or "Produto não encontrado",
        "price": _price_fmt(price) if price else "Preço não encontrado",
        "final_url": final_url,
    }


# ─────────────────────────────────────────────
# SHOPEE
# ─────────────────────────────────────────────
def _shopee_api(url):
    """Tenta API pública da Shopee extraindo shopid/itemid da URL."""
    m = re.search(r"i\.(\d+)\.(\d+)", url)
    if not m:
        m2 = re.search(r"/product/(\d+)/(\d+)", url)
        if not m2:
            return None
        shop_id, item_id = m2.group(1), m2.group(2)
    else:
        shop_id, item_id = m.group(1), m.group(2)

    api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
    try:
        r = requests.get(
            api_url,
            headers={**HEADERS, "Referer": "https://shopee.com.br/", "x-api-source": "pc"},
            timeout=12,
        )
        d = r.json()
        # A API retorna {data: {item: {...}}} ou {data: {...}}
        item = ((d.get("data") or {}).get("item")) or (d.get("data")) or {}
        name = item.get("name") or item.get("title") or ""
        raw_price = item.get("price") or item.get("price_min") or 0
        if name and raw_price:
            return {
                "title": name,
                "price": _price_fmt(int(raw_price) / 100000),
                "final_url": f"https://shopee.com.br/produto-i.{shop_id}.{item_id}",
            }
    except Exception:
        pass
    return None


def get_shopee_data(url):
    final_url = url

    # 1. API pública (mais confiável)
    api_result = _shopee_api(url)
    if api_result:
        return api_result

    # 2. Página HTML com headers completos
    try:
        h = {
            **HEADERS,
            "Referer": "https://shopee.com.br/",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "cache-control": "max-age=0",
        }
        r = requests.get(url, headers=h, timeout=15, allow_redirects=True)
        final_url = r.url
        soup = BeautifulSoup(r.text, "lxml")

        title = (soup.find("meta", property="og:title") or {}).get("content", "")
        title = re.sub(r"\s*\|\s*Shopee.*$", "", title or "").strip()

        price = ""
        # meta product:price:amount
        for prop in ["product:price:amount", "og:price:amount"]:
            tag = soup.find("meta", property=prop)
            if tag and tag.get("content"):
                price = _price_fmt(tag["content"])
                break

        # og:description contém "R$ X,XX"
        if not price:
            desc = (soup.find("meta", property="og:description") or {}).get("content", "")
            m = re.search(r"R\$\s*[\d.,]+", desc or "")
            if m:
                price = m.group(0)

        # JSON embutido no HTML: "price":XXXXXXXXXX (valor * 100000)
        if not price:
            m2 = re.search(r'"price"\s*:\s*(\d{6,})', r.text)
            if m2:
                price = _price_fmt(int(m2.group(1)) / 100000)

        # JSON-LD
        ld = _json_ld_product(soup)
        if ld:
            t, p = _extract_from_json_ld(ld)
            if t != "Produto não encontrado":
                title = title or t
                price = price or p

        if title:
            return {"title": title, "price": price or "Preço não encontrado", "final_url": final_url}

    except Exception:
        pass

    return {"title": "Produto não encontrado", "price": "Preço não encontrado", "final_url": final_url}


# ─────────────────────────────────────────────
# KABUM
# ─────────────────────────────────────────────
def get_kabum_data(url):
    _, soup, final_url = _fetch(url)

    # 1. JSON-LD (Kabum has it)
    ld = _json_ld_product(soup)
    if ld:
        title, price = _extract_from_json_ld(ld)
        if title != "Produto não encontrado":
            return {"title": title, "price": price, "final_url": final_url}

    # 2. __NEXT_DATA__
    nd = soup.find("script", id="__NEXT_DATA__")
    if nd:
        try:
            data = json.loads(nd.string)
            pp = data.get("props", {}).get("pageProps", {})
            product = pp.get("data", {}).get("product", {}) or pp.get("product", {})
            name = product.get("ds_name") or product.get("name") or ""
            price_val = product.get("vl_preco") or product.get("vl_preco_desconto") or product.get("price") or ""
            if name:
                return {"title": name, "price": _price_fmt(price_val), "final_url": final_url}
        except Exception:
            pass

    # 3. Meta
    title = (soup.find("meta", property="og:title") or {}).get("content", "")
    price_meta = soup.find("span", class_=re.compile(r"priceCard|finalPrice|price", re.I))
    price = price_meta.get_text(strip=True) if price_meta else ""

    return {
        "title": title or "Produto não encontrado",
        "price": _price_fmt(price) if price else "Preço não encontrado",
        "final_url": final_url,
    }


# ─────────────────────────────────────────────
# CASAS BAHIA / PONTO / EXTRA  (Via Varejo group)
# ─────────────────────────────────────────────
def get_casasbahia_data(url):
    _, soup, final_url = _fetch(url)

    # 1. JSON-LD (mais confiável quando presente)
    ld = _json_ld_product(soup)
    if ld:
        title, price = _extract_from_json_ld(ld)
        if title != "Produto não encontrado":
            return {"title": title, "price": price, "final_url": final_url}

    # 2. __NEXT_DATA__ — vários caminhos possíveis na estrutura
    nd = soup.find("script", id="__NEXT_DATA__")
    if nd:
        try:
            data = json.loads(nd.string)
            pp = data.get("props", {}).get("pageProps", {})

            # caminho 1: pageProps.product
            # caminho 2: pageProps.initialData.product
            # caminho 3: pageProps.data.product
            product = (
                pp.get("product")
                or (pp.get("initialData") or {}).get("product")
                or (pp.get("data") or {}).get("product")
                or {}
            )

            name = product.get("name") or product.get("title") or product.get("description", "")[:80]

            # preço: tentar vários campos
            price_val = (
                (product.get("prices") or {}).get("price")
                or (product.get("prices") or {}).get("bestPrice")
                or (product.get("prices") or {}).get("offerPrice")
                or product.get("price")
                or product.get("offerPrice")
                or product.get("salePrice")
                or ""
            )

            if name:
                return {"title": name, "price": _price_fmt(price_val), "final_url": final_url}

        except Exception:
            pass

    # 3. Procura JSON inline com "productName" ou "offerPrice"
    for sc in soup.find_all("script"):
        text = sc.string or ""
        if "productName" in text or "offerPrice" in text:
            try:
                m_name  = re.search(r'"productName"\s*:\s*"([^"]+)"', text)
                m_price = re.search(r'"(?:offerPrice|bestPrice|price)"\s*:\s*([\d.]+)', text)
                if m_name:
                    name  = m_name.group(1)
                    price = _price_fmt(m_price.group(1)) if m_price else "Preço não encontrado"
                    return {"title": name, "price": price, "final_url": final_url}
            except Exception:
                pass

    # 4. Meta tags og / microdata
    title = (soup.find("meta", property="og:title") or {}).get("content", "")
    price_meta = (
        soup.find("meta", itemprop="price")
        or soup.find("meta", property="product:price:amount")
    )
    price = price_meta.get("content", "") if price_meta else ""

    # 5. Span com data-testid ou class com "price"
    if not price:
        for attr in [{"data-testid": re.compile(r"price", re.I)},
                     {"class": re.compile(r"price|preco|valor", re.I)}]:
            span = soup.find("span", attr)
            if span:
                price = span.get_text(strip=True)
                break

    return {
        "title": title or "Produto não encontrado",
        "price": _price_fmt(price) if price else "Preço não encontrado",
        "final_url": final_url,
    }


# ─────────────────────────────────────────────
# OLX
# ─────────────────────────────────────────────
def get_olx_data(url):
    _, soup, final_url = _fetch(url)

    # 1. __NEXT_DATA__ — OLX usa Next.js, dados completos aqui
    nd = soup.find("script", id="__NEXT_DATA__")
    if nd:
        try:
            data = json.loads(nd.string)
            pp = data.get("props", {}).get("pageProps", {})

            # OLX pode ter a estrutura em vários caminhos
            ad = (
                pp.get("ad")
                or pp.get("adData")
                or (pp.get("pageProps") or {}).get("ad")
                or {}
            )

            # fallback: busca recursiva pela chave "subject"
            if not ad.get("subject"):
                ad = _find_key_recursive(data, "ad") or {}

            name = ad.get("subject") or ad.get("title") or ""

            # preço: OLX armazena em cents (price.value) ou direto
            price_obj = ad.get("price") or {}
            if isinstance(price_obj, dict):
                price_val = price_obj.get("value") or price_obj.get("amount") or 0
            else:
                price_val = price_obj or 0

            if not price_val:
                price_val = ad.get("priceValue") or ad.get("priceAmount") or 0

            if name:
                price_str = _price_fmt(int(price_val)) if price_val else "Preço não encontrado"
                return {"title": name, "price": price_str, "final_url": final_url}

        except Exception:
            pass

    # 2. JSON-LD
    ld = _json_ld_product(soup)
    if ld:
        title, price = _extract_from_json_ld(ld)
        if title != "Produto não encontrado":
            return {"title": title, "price": price, "final_url": final_url}

    # 3. og:title + regex no HTML
    title = (soup.find("meta", property="og:title") or {}).get("content", "")

    # OLX coloca o preço na og:description: "R$ 1.500"
    desc = (soup.find("meta", property="og:description") or {}).get("content", "")
    price = ""
    m = re.search(r"R\$\s*[\d.,]+", desc or "")
    if m:
        price = m.group(0)

    # Inline script com "subject" e "value"
    if not price or not title:
        for sc in soup.find_all("script"):
            text = sc.string or ""
            if '"subject"' in text or '"advert"' in text:
                try:
                    if not title:
                        ms = re.search(r'"subject"\s*:\s*"([^"]+)"', text)
                        if ms:
                            title = ms.group(1)
                    if not price:
                        mp = re.search(r'"value"\s*:\s*(\d+)', text)
                        if mp:
                            price = _price_fmt(int(mp.group(1)))
                    if title and price:
                        break
                except Exception:
                    pass

    return {
        "title": title or "Produto não encontrado",
        "price": price or "Preço não encontrado",
        "final_url": final_url,
    }


def _find_key_recursive(obj, key, depth=0):
    """Busca recursiva por uma chave em um dict/list aninhado."""
    if depth > 6:
        return None
    if isinstance(obj, dict):
        if key in obj and isinstance(obj[key], dict):
            return obj[key]
        for v in obj.values():
            result = _find_key_recursive(v, key, depth + 1)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _find_key_recursive(item, key, depth + 1)
            if result:
                return result
    return None


# ─────────────────────────────────────────────
# MAGAZINE LUIZA (bonus)
# ─────────────────────────────────────────────
def get_magalu_data(url):
    _, soup, final_url = _fetch(url)

    # 1. JSON-LD
    ld = _json_ld_product(soup)
    if ld:
        title, price = _extract_from_json_ld(ld)
        if title != "Produto não encontrado":
            return {"title": title, "price": price, "final_url": final_url}

    # 2. __NEXT_DATA__
    nd = soup.find("script", id="__NEXT_DATA__")
    if nd:
        try:
            data = json.loads(nd.string)
            pp = data.get("props", {}).get("pageProps", {})
            product = pp.get("data", {}) or {}
            name = product.get("title") or product.get("name") or ""
            price_val = (
                product.get("price")
                or product.get("bestPrice")
                or product.get("priceV2", {}).get("price")
                or ""
            )
            if name:
                return {"title": name, "price": _price_fmt(price_val), "final_url": final_url}
        except Exception:
            pass

    title = (soup.find("meta", property="og:title") or {}).get("content", "")
    price_meta = soup.find("meta", itemprop="price") or soup.find("meta", property="product:price:amount")
    price = price_meta.get("content", "") if price_meta else ""

    return {
        "title": title or "Produto não encontrado",
        "price": _price_fmt(price) if price else "Preço não encontrado",
        "final_url": final_url,
    }


# ─────────────────────────────────────────────
# ROUTER — detect site from URL and call right scraper
# ─────────────────────────────────────────────
def get_product_data(url):
    u = url.lower()

    if "mercadolivre.com" in u or "mercadolibre.com" in u or "mlb" in u:
        return get_mercadolivre_data(url)

    if "americanas.com" in u or "submarino.com" in u or "shoptime.com" in u:
        return get_americanas_data(url)

    if "shopee.com" in u:
        return get_shopee_data(url)

    if "kabum.com" in u:
        return get_kabum_data(url)

    if "casasbahia.com" in u or "pontofrio.com" in u or "extra.com" in u or "ponto.com" in u:
        return get_casasbahia_data(url)

    if "olx.com" in u:
        return get_olx_data(url)

    if "magazineluiza.com" in u or "magalu.com" in u:
        return get_magalu_data(url)

    # Generic fallback: try JSON-LD then og:title
    return _generic_fallback(url)


def _generic_fallback(url):
    _, soup, final_url = _fetch(url)
    ld = _json_ld_product(soup)
    if ld:
        title, price = _extract_from_json_ld(ld)
        return {"title": title, "price": price, "final_url": final_url}

    title = (soup.find("meta", property="og:title") or {}).get("content", "Produto não encontrado")
    price_meta = soup.find("meta", itemprop="price") or soup.find("meta", property="product:price:amount")
    price = _price_fmt(price_meta.get("content", "")) if price_meta else "Preço não encontrado"
    return {"title": title, "price": price, "final_url": final_url}