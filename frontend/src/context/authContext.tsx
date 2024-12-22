'use client';

import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';

interface AuthContextType {
  isLoggedIn: boolean;
  isDemoUser: boolean;
  apiKey: string | null;
  role: string | null;
  setApiKey: (apiKey: string | null) => void;
  setRole: (role: string | null) => void;
  demoLogin: () => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [isDemoUser, setIsDemoUser] = useState<boolean>(false);

  useEffect(() => {
    // Check for saved API key and role in localStorage (for logged-in users)
    const savedApiKey = localStorage.getItem('apiKey');
    const savedRole = localStorage.getItem('role');

    if (savedApiKey) {
      setApiKey(savedApiKey);
      setRole(savedRole);
      setIsLoggedIn(true);
    } else {
      // Check for demo session in sessionStorage
      const demoApiKey = sessionStorage.getItem('demoApiKey');
      const demoRole = sessionStorage.getItem('demoRole');
      if (demoApiKey) {
        setApiKey(demoApiKey);
        setRole(demoRole);
        setIsDemoUser(true);
      }
    }
  }, []);

  useEffect(() => {
    if (apiKey) {
      if (!isDemoUser) {
        localStorage.setItem('apiKey', apiKey);
      }
    } else {
      localStorage.removeItem('apiKey');
      sessionStorage.removeItem('demoApiKey');
    }

    if (role) {
      if (!isDemoUser) {
        localStorage.setItem('role', role);
      }
    } else {
      localStorage.removeItem('role');
      sessionStorage.removeItem('demoRole');
    }

    setIsLoggedIn(!!apiKey && !isDemoUser); // Logged-in state excludes demo users
  }, [apiKey, role, isDemoUser]);

  const logout = () => {
    setApiKey(null);
    setRole(null);
    setIsDemoUser(false);
    localStorage.removeItem('apiKey');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    sessionStorage.removeItem('demoApiKey');
    sessionStorage.removeItem('demoRole');
    setIsLoggedIn(false);
  };

  return (
    <AuthContext.Provider
      value={{ isLoggedIn, isDemoUser, apiKey, role, setApiKey, setRole, demoLogin, logout }}
    >
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
