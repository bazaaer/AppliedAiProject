'use client';

import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';

// Define types for the AuthContext
interface AuthContextType {
  isLoggedIn: boolean;
  apiKey: string | null;
  role: string | null;
  setApiKey: (apiKey: string | null) => void;
  setRole: (role: string | null) => void;
  logout: () => void; // New logout method
}

// Create AuthContext
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider to wrap the app and provide context values
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false); // Track login state

  // Effect to load apiKey from localStorage if available
  useEffect(() => {
    const savedApiKey = localStorage.getItem('apiKey');
    const savedRole = localStorage.getItem('role');
    if (savedApiKey) {
      setApiKey(savedApiKey);
    }
    if (savedRole) {
      setRole(savedRole);
    }
    // Set isLoggedIn based on the presence of apiKey
    setIsLoggedIn(!!savedApiKey);
  }, []);

  // Save apiKey and role in localStorage whenever they change
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
    // Update isLoggedIn based on apiKey
    setIsLoggedIn(!!apiKey);
  }, [apiKey, role]);

  // Logout method to clear apiKey and role
  const logout = () => {
    setApiKey(null);
    setRole(null);
    localStorage.removeItem('apiKey');
    localStorage.removeItem('role');
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
