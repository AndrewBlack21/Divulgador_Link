import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function ProtectedRoute({ children }) {
  const { user, plan, loading } = useAuth();

  if (loading) return <p>Carregando...</p>;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // usuário logado mas sem plano
  if (!plan && location.pathname !== "/choose-plan") {
    return <Navigate to="/choose-plan" replace />;
  }

  return children;
}
