import { supabase } from "../services/supabase";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

// Styles
import styles from "./ChoosePlan.module.css";
import img from "../assets/Mobile.png";

export default function ChoosePlan() {
  const { user } = useAuth();
  const navigate = useNavigate();

  async function selectPlan(plan) {
    const { error } = await supabase.from("profiles").upsert({
      id: user.id,
      plan,
    });

    if (error) {
      console.error("Erro ao salvar plano:", error.message);
      alert("Erro ao salvar plano. Tente novamente.");
      return;
    }

    navigate("/home");
  }

  return (
    <div className={styles.container}>
      <img src={img} alt="" className={styles.heroimage} />
      <h2>Escolha seu plano</h2>
      <button onClick={() => selectPlan("free")}>Plano FREE</button>
      <button onClick={() => selectPlan("pro")}>Plano PRO</button>
    </div>
  );
}
