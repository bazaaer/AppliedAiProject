import React, { createContext, useContext, useState } from "react";

interface AuthContextType {
  isLoggedIn: boolean;
  role: string | null;
  apiKey: string | null;
  setApiKey: (key: string) => void;
  setRole: (role: string) => void;
  loginAs: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [role, setRole] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState<string | null>(null);

  const loginAs = async (username: string, password: string): Promise<void> => {
    try {
      const response = await fetch("https://klopta.vinnievirtuoso.online/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Login failed");
      }

      const data = await response.json();
      setApiKey(data.token);
      setRole(data.role);
      localStorage.setItem("username", username);
      setIsLoggedIn(true);
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  };

  const logout = () => {
    setIsLoggedIn(false);
    setApiKey(null);
    setRole(null);
    localStorage.removeItem("username");
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, role, apiKey, setApiKey, setRole, loginAs, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
