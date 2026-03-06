import { supabase } from "../services/supabase";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import s from "./shared.module.css";
import cp from "./ChoosePlan.module.css";

export default function ChoosePlan() {
  const { user } = useAuth();
  const navigate = useNavigate();

  async function selectPlan(plan) {
    await supabase.from("profiles").upsert({ id: user.id, plan });
    navigate("/home");
  }

  return (
    <div className={s.page}>
      <div className={s.card}>
        <div className={s.badge}>Planos</div>

        <h1 className={s.heading}>
          Escolha seu
          <br />
          <span className={s.accent}>plano</span>
        </h1>
        <p className={s.sub}>// Comece grátis ou vá para o PRO</p>

        <div className={s.divider} />

        <div className={cp.plans}>
          {/* FREE */}
          <div className={cp.planCard}>
            <div className={cp.planHeader}>
              <span className={cp.planName}>FREE</span>
              <span className={cp.planPrice}>
                R$ 0<small>/mês</small>
              </span>
            </div>
            <ul className={cp.planFeatures}>
              <li>✓ 10 links por dia</li>
              <li>✓ Mercado Livre</li>
              <li>✓ Mensagem pronta para copiar</li>
              <li className={cp.disabled}>✗ Lojas extras</li>
              <li className={cp.disabled}>✗ Links ilimitados</li>
            </ul>
            <button className={s.btnGhost} onClick={() => selectPlan("free")}>
              Começar grátis
            </button>
          </div>

          {/* PRO */}
          <div className={`${cp.planCard} ${cp.planCardPro}`}>
            <div className={cp.proTag}>⚡ Popular</div>
            <div className={cp.planHeader}>
              <span className={cp.planName}>PRO</span>
              <span className={`${cp.planPrice} ${cp.proPriceColor}`}>
                R$ 19<small>/mês</small>
              </span>
            </div>
            <ul className={cp.planFeatures}>
              <li>✓ Links ilimitados</li>
              <li>✓ Todas as lojas</li>
              <li>✓ Mensagem personalizada</li>
              <li>✓ Suporte prioritário</li>
              <li>✓ Novidades antecipadas</li>
            </ul>
            <button className={s.btn} onClick={() => selectPlan("pro")}>
              Assinar PRO →
            </button>
          </div>
        </div>

        <p className={s.stamp}>DIVULGA PRO · v2.0</p>
      </div>
    </div>
  );
}
