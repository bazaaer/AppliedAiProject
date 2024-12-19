'use client';

import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';

interface AuthContextType {
  isLoggedIn: boolean;
  apiKey: string | null;
  role: string | null;
  setApiKey: (apiKey: string | null) => void;
  setRole: (role: string | null) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

  useEffect(() => {
    const savedApiKey = localStorage.getItem('apiKey');
    const savedRole = localStorage.getItem('role');
    if (savedApiKey) {
      setApiKey(savedApiKey);
    }
    if (savedRole) {
      setRole(savedRole);
    }
    setIsLoggedIn(!!savedApiKey);
  }, []);

  useEffect(() => {
    if (apiKey) {
      localStorage.setItem('apiKey', apiKey);
    } else {
      localStorage.removeItem('apiKey');
    }
    if (role) {
      localStorage.setItem('role', role);
    } else {
      localStorage.removeItem('role');
    }
    setIsLoggedIn(!!apiKey);
  }, [apiKey, role]);

  const logout = () => {
    setApiKey(null);
    setRole(null);
    localStorage.removeItem('apiKey');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    setIsLoggedIn(false); // Set isLoggedIn to false upon logout
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, apiKey, role, setApiKey, setRole, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook to access the AuthContext values
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
