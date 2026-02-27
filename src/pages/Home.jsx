import { useState } from "react";
import ResultCard from "../components/ResultCard";
import styles from "./Home.module.css";
import { API_URL } from "../services/api";

import img from "../assets/Mobile.png";

function Home() {
  const [inputValue, setInputValue] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleBuscarProduto() {
    if (!inputValue.trim()) {
      setError("Cole o link do produto.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/mercadolivre`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: inputValue.trim(),
        }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const errorMessage =
          data?.detail || `Erro na requisição (${response.status})`;
        throw new Error(errorMessage);
      }

      setResult(data);
    } catch (err) {
      setError(err.message || "Erro ao buscar produto");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      <img src={img} alt="" className={styles.heroimage} />
      <h1 className={styles.title}>Divulga Promoções</h1>
      <input
        type="text"
        placeholder="Cole o link do Mercado Livre"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
      />

      <button onClick={handleBuscarProduto} disabled={loading}>
        {loading ? "Buscando produto..." : "🚀 Criar mensagem de venda"}
      </button>

      {loading && <p>Buscando dados no Mercado Livre..</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {result && <ResultCard data={result} />}
    </div>
  );
}

export default Home;
