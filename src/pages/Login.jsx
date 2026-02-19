import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { supabase } from "../services/supabase";

// Styles
import styles from "./Login.module.css";
import img from "../assets/Mobile.png";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function handleLogin(e) {
    e.preventDefault();

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      console.error("Erro no login:", error.message);
      alert(error.message || "Email ou senha inválidos");
      return;
    }

    navigate("/dashboard");
  }

  return (
    <form className={styles.container} onSubmit={handleLogin}>
      <img src={img} alt="" className={styles.heroimage} />
      <h1 className={styles.title}>Login</h1>

      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <input
        type="password"
        placeholder="Senha"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button type="submit">Entrar</button>

      <p>
        Não tem conta? <Link to="/register">Criar agora</Link>
      </p>
    </form>
  );
}
