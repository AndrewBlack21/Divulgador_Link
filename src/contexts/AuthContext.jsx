import { createContext, useContext, useEffect, useState } from "react";
import { supabase } from "../services/supabase";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadUser() {
    try {
      const { data, error: authError } = await supabase.auth.getUser();

      if (authError) {
        console.error("Erro ao buscar usuário:", authError.message);
        setUser(null);
        setPlan(null);
        setLoading(false);
        return;
      }

      const currentUser = data?.user ?? null;
      setUser(currentUser);

      if (currentUser) {
        const { data: profile, error: profileError } = await supabase
          .from("profiles")
          .select("plan")
          .eq("id", currentUser.id)
          .single();

        if (profileError) {
          console.error("Erro ao buscar perfil:", profileError.message);
          setPlan(null);
        } else {
          setPlan(profile?.plan ?? null);
        }
      }
    } catch (err) {
      console.error("Erro inesperado no AuthContext:", err);
      setUser(null);
      setPlan(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUser();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      loadUser();
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ user, plan, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
