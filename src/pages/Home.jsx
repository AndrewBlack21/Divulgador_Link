import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import ResultCard from "../components/ResultCard";
import styles from "./Home.module.css";
import { API_URL } from "../services/api";

import img from "../assets/Mobile.png";

function Home() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialMarketplace =
    searchParams.get("market") === "shopee" ? "shopee" : "mercadolivre";

  const [marketplace, setMarketplace] = useState(initialMarketplace);
  const [inputValue, setInputValue] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleMarketplaceChange(nextMarketplace) {
    setMarketplace(nextMarketplace);
    setResult(null);
    setError("");
    setInputValue("");
    setSearchParams({ market: nextMarketplace });
  }

  async function handleBuscarProduto() {
    if (!inputValue) return alert("Cole o link do produto");

    setLoading(true);
    setError("");

    try {
      const requestPayload = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: inputValue,
        }),
      };

      const response = await fetch(`${API_URL}/${marketplace}`, requestPayload);

      if (marketplace === "shopee" && response.status === 404) {
        throw new Error("Shopee endpoint indisponível");
      }

      if (!response.ok) {
        throw new Error(`Erro na requisição (${response.status})`);
      }

      const data = await response.json();

      const shopeeWithoutData =
        marketplace === "shopee" &&
        data?.title === "Produto não encontrado" &&
        data?.price === "Preço não encontrado";

      if (shopeeWithoutData) {
        throw new Error("Shopee sem dados do produto");
      }

      setResult(data);
    } catch (err) {
      setResult(null);

      if (
        err instanceof Error &&
        err.message === "Shopee endpoint indisponível"
      ) {
        setError(
          "A busca da Shopee ainda não está ativa no servidor. Faça o deploy do backend com o endpoint /shopee.",
        );
        return;
      }

      if (
        err instanceof Error &&
        err.message === "Shopee sem dados do produto"
      ) {
        setError(
          "Não consegui extrair título e preço desse link da Shopee. Tente um link de produto direto ou outro anúncio.",
        );
        return;
      }

      setError(
        "Erro ao buscar produto. Verifique se o link e tente novamente.",
      );
    } finally {
      setLoading(false);
    }
  }

  const marketplaceLabel =
    marketplace === "mercadolivre" ? "Mercado Livre" : "Shopee";

  return (
    <div className={styles.container}>
      <img src={img} alt="" className={styles.heroimage} />
      <h1 className={styles.title}>Divulga Promoções</h1>

      <div className={styles.marketSwitcher}>
        <button
          type="button"
          className={`${styles.marketButton} ${
            marketplace === "mercadolivre" ? styles.activeMarket : ""
          }`}
          onClick={() => handleMarketplaceChange("mercadolivre")}
        >
          Mercado Livre
        </button>
        <button
          type="button"
          className={`${styles.marketButton} ${
            marketplace === "shopee" ? styles.activeMarket : ""
          }`}
          onClick={() => handleMarketplaceChange("shopee")}
        >
          Shopee
        </button>
      </div>

      <input
        type="text"
        placeholder={`Cole o link da ${marketplaceLabel}`}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
      />

      <button onClick={handleBuscarProduto} disabled={loading}>
        {loading ? "Buscando produto..." : "🚀 Criar mensagem de venda"}
      </button>

      {loading && <p>Buscando dados na {marketplaceLabel}...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {result && <ResultCard data={result} />}
    </div>
  );
}

export default Home;
