import { useState } from "react";
import ResultCard from "../components/ResultCard";
import styles from "./Home.module.css";
import { API_URL } from "../services/api";

const img = "/src/assets/Mobile.png";

function Home() {
  const [inputValue, setInputValue] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleBuscarProduto() {
    if (!inputValue) return alert("Cole o link do produto");

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/mercadolivre`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: inputValue,
        }),
      });

      if (!response.ok) {
        throw new Error("Erro na requisição");
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      alert("Erro ao buscar produto");
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
