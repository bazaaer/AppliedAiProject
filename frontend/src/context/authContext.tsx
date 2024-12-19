'use client';

import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';

interface AuthContextType {
  isLoggedIn: boolean;
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

  const demoLogin = async () => {
    // Set username and password for demo login
    const username = 'temp';
    const password = 'temp';
  
    try {
      const response = await fetch("https://klopta.vinnievirtuoso.online/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });
  
      console.log("Response status:", response.status); // For debugging
  
      if (response.ok) {
        // Parse the response if login is successful
        const data = await response.json();
        const demoApiKey = data.token;
  
        // Store the API key and role in sessionStorage for the demo session
        sessionStorage.setItem('apiKey', demoApiKey);
  
        // Update the state to reflect the demo login
        setApiKey(demoApiKey);
  
        console.log("Demo login successful:", data);
      } else {
        console.log("Error response:", response);
        try {
          const errorData = await response.json();
          console.log("Error data:", errorData); // For debugging
          // Handle error and maybe set an error message state
        } catch (parseError) {
          console.log("Error parsing response:", parseError); // For debugging
        }
      }
    } catch (error) {
      console.log("Unexpected error:", error);
      // Handle unexpected error
    }
  };

  const logout = () => {
    setApiKey(null);
    setRole(null);
    localStorage.removeItem('apiKey');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
    setIsLoggedIn(false); // Set isLoggedIn to false upon logout
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, apiKey, role, setApiKey, setRole, logout, demoLogin }}>
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
