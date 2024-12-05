'use client';

import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';

// Define types for the AuthContext
interface AuthContextType {
  token: string | null;
  role: string | null;
  setToken: (token: string | null) => void;
  setRole: (role: string | null) => void;
}

// Create AuthContext
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider to wrap the app and provide context values
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);

  // Effect to load token from localStorage if available
  useEffect(() => {
    const savedToken = localStorage.getItem('api_key');
    const savedRole = localStorage.getItem('role');
    if (savedToken) {
      setToken(savedToken);
    }
    if (savedRole) {
      setRole(savedRole);
    }
  }, []);

  // Save token and role in localStorage whenever they change
  useEffect(() => {
    if (token) {
      localStorage.setItem('api_key', token);
    } else {
      localStorage.removeItem('api_key');
    }
    if (role) {
      localStorage.setItem('role', role);
    } else {
      localStorage.removeItem('role');
    }
  }, [token, role]);

  return (
    <AuthContext.Provider value={{ token, role, setToken, setRole }}>
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
