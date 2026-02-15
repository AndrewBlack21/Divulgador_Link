import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import styles from "./Dashboard.module.css";
import img from "../assets/Mobile.png";

export default function Dashboard() {
  const { user, plan } = useAuth();
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      <img src={img} alt="" className={styles.heroimage} />
      <h1 className={styles.title}>Dashboard</h1>

      <p className={styles.subtitle}>Usuario: {user?.email}</p>
      <p className={styles.subtitle}>Plano: {plan?.toUpperCase()}</p>

      {plan === "free" && (
        <>
          <p className={styles.subtitle}>
            Voce pode gerar ate 10 links por dia.
          </p>

          <button onClick={() => navigate("/home")}>Gerar Link</button>

          <button onClick={() => navigate("/choose-plan")}>
            Fazer upgrade pra Pro
          </button>
        </>
      )}

      {plan === "pro" && (
        <>
          <p>Links ilimitados</p>

          <button onClick={() => navigate("/home")}>
            Gerar Link Ilimitado
          </button>

          <button onClick={() => navigate("/choose-plan")}>
            Gerenciar Plano
          </button>
        </>
      )}
    </div>
  );
}
