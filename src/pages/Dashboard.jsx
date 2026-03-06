import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import s from "./shared.module.css";
import ds from "./Dashboard.module.css";

export default function Dashboard() {
  const { user, plan } = useAuth();
  const navigate = useNavigate();

  const isFree = plan === "free";
  const isPro = plan === "pro";

  return (
    <div className={s.page}>
      <div className={s.card}>
        <div className={s.badge}>{isPro ? "⚡ Plano PRO" : "Plano FREE"}</div>

        <h1 className={s.heading}>
          Seu
          <br />
          <span className={s.accent}>Dashboard</span>
        </h1>
        <p className={s.sub}>// Painel de controle da sua conta</p>

        <div className={s.divider} />

        {/* User info */}
        <div className={ds.infoBox}>
          <div className={ds.infoRow}>
            <span className={ds.infoKey}>Usuário</span>
            <span className={ds.infoVal}>{user?.email}</span>
          </div>
          <div className={ds.infoRow}>
            <span className={ds.infoKey}>Plano</span>
            <span className={`${ds.infoVal} ${isPro ? ds.pro : ds.free}`}>
              {plan?.toUpperCase()}
            </span>
          </div>
          {isFree && (
            <div className={ds.infoRow}>
              <span className={ds.infoKey}>Limite</span>
              <span className={ds.infoVal}>10 links / dia</span>
            </div>
          )}
          {isPro && (
            <div className={ds.infoRow}>
              <span className={ds.infoKey}>Limite</span>
              <span className={ds.infoVal}>Ilimitado ✓</span>
            </div>
          )}
        </div>

        <div className={ds.actions}>
          <button className={s.btn} onClick={() => navigate("/home")}>
            🚀 {isPro ? "Gerar Link Ilimitado" : "Gerar Link"}
          </button>

          {isFree && (
            <button
              className={s.btnGhost}
              onClick={() => navigate("/choose-plan")}
            >
              ⚡ Fazer upgrade para PRO
            </button>
          )}

          {isPro && (
            <button
              className={s.btnGhost}
              onClick={() => navigate("/choose-plan")}
            >
              Gerenciar plano
            </button>
          )}
        </div>

        <p className={s.stamp}>DIVULGA PRO · v2.0</p>
      </div>
    </div>
  );
}
