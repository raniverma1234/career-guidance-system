import { createContext, useContext, useEffect, useState } from "react";
import api, { TOKEN_KEY } from "./api";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // we only need to wait if a saved token has to be checked
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem(TOKEN_KEY)));

  // on page load: if a token is saved, fetch the student's profile
  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) {
      return;
    }
    api
      .get("/profile/me")
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    // the backend login expects form data with the fields "username" and "password"
    const body = new URLSearchParams();
    body.append("username", email.trim());
    body.append("password", password);
    const res = await api.post("/auth/login", body);
    localStorage.setItem(TOKEN_KEY, res.data.access_token);
    const me = await api.get("/profile/me");
    setUser(me.data);
    return me.data;
  }

  async function register({ name, email, password, age }) {
    await api.post("/auth/register", {
      name: name.trim(),
      email: email.trim(),
      password,
      age: age ? Number(age) : null,
    });
    return login(email, password);
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }

  function updateUser(newUser) {
    setUser(newUser);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}