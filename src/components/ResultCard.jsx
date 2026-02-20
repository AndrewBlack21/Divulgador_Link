import styles from "./ResultCard.module.css";

export default function ResultCard({ data }) {
  const message = `🔥 OFERTA IMPERDÍVEL 🔥

📦 ${data.title}
💰 ${data.price}

👉 Compre aqui:
${data.affiliateLink}
`;

  function copyMessage() {
    navigator.clipboard.writeText(message);
    alert("Mensagem copiada!");
  }

  return (
    <div className={styles.result}>
      <p className={styles.title}>
        <strong>{data.title}</strong>
      </p>
      <p className={styles.price}>{data.price}</p>

      <textarea className={styles.message} value={message} readOnly />

      <button className={styles.copy} onClick={copyMessage}>
        Copiar mensagem
      </button>
    </div>
  );
}
