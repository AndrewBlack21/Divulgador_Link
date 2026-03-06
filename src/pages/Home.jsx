import { useState } from "react";
import s from "./shared.module.css";
import hs from "./Home.module.css";
import { API_URL } from "../services/api";

const SITES = [
  {
    id: "mercadolivre",
    label: "Mercado Livre",
    emoji: "🛒",
    placeholder: "Cole o link do Mercado Livre",
  },
  {
    id: "americanas",
    label: "Americanas",
    emoji: "🏪",
    placeholder: "Cole o link da Americanas",
  },
  {
    id: "shopee",
    label: "Shopee",
    emoji: "🛍️",
    placeholder: "Cole o link da Shopee",
  },
  {
    id: "kabum",
    label: "Kabum",
    emoji: "💻",
    placeholder: "Cole o link do Kabum",
  },
  {
    id: "casasbahia",
    label: "Casas Bahia",
    emoji: "🏠",
    placeholder: "Cole o link Casas Bahia",
  },
  { id: "olx", label: "OLX", emoji: "📦", placeholder: "Cole o link do OLX" },
];

function buildMessage(data) {
  return `🔥 OFERTA IMPERDÍVEL 🔥\n\n📦 ${data.title}\n💰 ${data.price}\n\n👉 Compre aqui:\n${data.affiliateLink}`;
}

export default function Home() {
  const [site, setSite] = useState(SITES[0]);
  const [inputValue, setInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  async function handleBuscar() {
    if (!inputValue.trim()) {
      setError("Cole o link do produto.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: inputValue.trim() }),
      });
      const data = await response.json().catch(() => null);
      if (!response.ok)
        throw new Error(data?.detail || `Erro ${response.status}`);
      setResult(data);
    } catch (err) {
      setError(err.message || "Erro ao buscar produto.");
    } finally {
      setLoading(false);
    }
  }

  function handleCopy() {
    navigator.clipboard.writeText(buildMessage(result));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function changeSite(s) {
    setSite(s);
    setResult(null);
    setError("");
    setInput("");
  }

  return (
    <div className={s.page}>
      <div className={`${s.card} ${hs.wideCard}`}>
        <div className={s.badge}>Gerador de promoções</div>

        <h1 className={s.heading}>
          Divulga
          <br />
          <span className={s.accent}>Promoções</span>
        </h1>
        <p className={s.sub}>// Cole o link → copie a mensagem pronta</p>

        <div className={s.divider} />

        {/* site selector */}
        <p className={s.label}>Selecionar loja</p>
        <div className={hs.siteGrid}>
          {SITES.map((st) => (
            <button
              key={st.id}
              className={`${hs.siteBtn} ${site.id === st.id ? hs.siteBtnOn : ""}`}
              onClick={() => changeSite(st)}
            >
              <span className={hs.siteEmoji}>{st.emoji}</span>
              {st.label}
            </button>
          ))}
        </div>

        {/* input */}
        <div className={s.inputWrap}>
          <span className={s.inputIcon}>🔗</span>
          <input
            className={s.input}
            type="text"
            placeholder={site.placeholder}
            value={inputValue}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleBuscar()}
          />
        </div>

        <button
          className={s.btn}
          onClick={handleBuscar}
          disabled={loading || !inputValue.trim()}
        >
          {loading ? "Buscando produto..." : "🚀 Criar mensagem de venda"}
        </button>

        {loading && (
          <div className={s.loadBar}>
            <div className={s.loadFill} />
          </div>
        )}
        {error && <p className={s.error}>⚠ {error}</p>}

        {/* result */}
        {result && (
          <div className={hs.result}>
            <p className={hs.resultTitle}>{result.title}</p>
            <p className={hs.resultPrice}>{result.price}</p>

            <div className={hs.messageBox}>
              <pre className={hs.messageText}>{buildMessage(result)}</pre>
            </div>

            <button
              className={copied ? hs.copiedBtn : hs.copyBtn}
              onClick={handleCopy}
            >
              {copied ? "✓ Copiado!" : "Copiar mensagem"}
            </button>
          </div>
        )}

        <p className={s.stamp}>DIVULGA PRO · v2.0</p>
      </div>
    </div>
  );
}
