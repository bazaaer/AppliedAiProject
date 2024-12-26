import React, { createContext, useContext, useState, useEffect } from "react";
import Cookies from "js-cookie";

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

  // Load token and role from cookies
  useEffect(() => {
    const savedApiKey = Cookies.get("apiKey");
    const savedRole = Cookies.get("role");

    if (savedApiKey) {
      setApiKey(savedApiKey);
      setRole(savedRole);
      setIsLoggedIn(true);
    }
  }, []);

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
      if (data.role === "temp") {
        // cookies for "temp" expire at end of session
        Cookies.set("apiKey", data.token, { secure: true, sameSite: "Strict" });
        Cookies.set("role", data.role, { secure: true, sameSite: "Strict" });
      } else {
        Cookies.set("apiKey", data.token, { secure: true, sameSite: "Strict", expires: 7 });
        Cookies.set("role", data.role, { secure: true, sameSite: "Strict", expires: 7 });
      }

      setApiKey(data.token);
      setRole(data.role);
      setIsLoggedIn(true);
      localStorage.setItem("username", username);
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  };

  const logout = () => {
    Cookies.remove("apiKey");
    Cookies.remove("role");
    localStorage.removeItem("username");
    setApiKey(null);
    setRole(null);
    setIsLoggedIn(false);
  };

  return (
    <AuthContext.Provider
      value={{
        isLoggedIn,
        role,
        apiKey,
        setApiKey,
        setRole,
        loginAs,
        logout,
      }}
    >
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
