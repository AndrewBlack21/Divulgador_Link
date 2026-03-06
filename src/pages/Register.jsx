import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { supabase } from "../services/supabase";
import s from "./shared.module.css";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleRegister(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { error } = await supabase.auth.signUp({ email, password });

    if (error) {
      setError("Erro ao cadastrar. Tente novamente.");
      setLoading(false);
      return;
    }

    navigate("/dashboard");
  }

  return (
    <div className={s.page}>
      <form className={s.card} onSubmit={handleRegister} noValidate>
        <div className={s.badge}>Cadastro</div>

        <h1 className={s.heading}>
          Crie sua
          <br />
          <span className={s.accent}>conta grátis</span>
        </h1>
        <p className={s.sub}>// Comece a divulgar promoções agora</p>

        <div className={s.divider} />

        <p className={s.label}>Email</p>
        <div className={s.inputWrap}>
          <span className={s.inputIcon}>✉</span>
          <input
            className={s.input}
            type="email"
            placeholder="seu@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <p className={s.label}>Senha</p>
        <div className={s.inputWrap}>
          <span className={s.inputIcon}>🔒</span>
          <input
            className={s.input}
            type="password"
            placeholder="Mínimo 6 caracteres"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {error && <p className={s.error}>⚠ {error}</p>}

        <button className={s.btn} type="submit" disabled={loading}>
          {loading ? "Criando conta..." : "Cadastrar →"}
        </button>

        {loading && (
          <div className={s.loadBar}>
            <div className={s.loadFill} />
          </div>
        )}

        <p className={s.footnote}>
          Já tem conta? <Link to="/login">Entrar</Link>
        </p>

        <p className={s.stamp}>DIVULGA PRO · v2.0</p>
      </form>
    </div>
  );
}
