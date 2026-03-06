import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { supabase } from "../services/supabase";
import s from "./shared.module.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleLogin(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      setError("Email ou senha inválidos.");
      setLoading(false);
      return;
    }

    navigate("/dashboard");
  }

  return (
    <div className={s.page}>
      <form className={s.card} onSubmit={handleLogin} noValidate>
        <div className={s.badge}>Área de acesso</div>

        <h1 className={s.heading}>
          Bem-vindo
          <br />
          <span className={s.accent}>de volta</span>
        </h1>
        <p className={s.sub}>// Entre com sua conta para continuar</p>

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
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        {error && <p className={s.error}>⚠ {error}</p>}

        <button className={s.btn} type="submit" disabled={loading}>
          {loading ? "Entrando..." : "Entrar →"}
        </button>

        {loading && (
          <div className={s.loadBar}>
            <div className={s.loadFill} />
          </div>
        )}

        <p className={s.footnote}>
          Não tem conta? <Link to="/register">Criar agora</Link>
        </p>

        <p className={s.stamp}>DIVULGA PRO · v2.0</p>
      </form>
    </div>
  );
}
