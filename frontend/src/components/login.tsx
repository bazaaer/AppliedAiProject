'use client';

import React, { useState } from "react";
import { Typography, Button } from "@material-tailwind/react";
import { useAuth } from "@/context/authContext";  // Import the context to update the token

interface LoginProps {
  onClose: () => void;
  onLoginSuccess: () => void;
}

const Login: React.FC<LoginProps> = ({ onClose, onLoginSuccess }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  
  const { setToken, setRole } = useAuth();  // Access context methods to set token and role

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setErrorMessage("Both fields are required.");
      return;
    }

    try {
      const response = await fetch("https://klopta.vinnievirtuoso.online/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      // Debugging: Log the response status
      console.log("Response status:", response.status);

      if (response.ok) {
        const data = await response.json();
        console.log("Login success:", data);  // Log the successful response

        // Store the API key (token) and role in the context
        setToken(data.api_key);  // Store the api_key as token
        setRole(data.role);      // Store the role (if necessary)

        // Close the login popup and notify the app about successful login
        onClose();
      } else {
        // If the response is not OK, we handle the error here
        console.log("Error response:", response);
        try {
          const errorData = await response.json();
          console.log("Error data:", errorData);
          setErrorMessage(errorData.message || "Login failed. Please try again.");
        } catch (parseError) {
          console.log("Error parsing response:", parseError);
          setErrorMessage("Login failed. An unknown error occurred.");
        }
      }
    } catch (error) {
      // Catch any unexpected errors
      console.log("Unexpected error:", error);
      setErrorMessage("An unexpected error occurred. Please try again.");
    }
  };

  return (
    <section className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-[2000]">
      <div className="relative w-full max-w-md bg-white rounded-lg shadow dark:border dark:bg-gray-800 dark:border-gray-700">
        <div className="p-6 space-y-4 sm:p-8">
          <button
            onClick={onClose}
            className="absolute top-2 right-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
          >
            ✕
          </button>
          <Typography
            variant="h5"
            color="blue-gray"
            className="text-lg font-bold text-gray-900 dark:text-white"
          >
            Log In
          </Typography>
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="username"
                className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
              >
                Username
              </label>
              <input
                type="text"
                name="username"
                id="username"
                className="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                placeholder="emelia_erickson24"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div>
              <label
                htmlFor="password"
                className="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
              >
                Password
              </label>
              <input
                type="password"
                name="password"
                id="password"
                placeholder="••••••••"
                className="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {errorMessage && (
              <Typography color="red" className="text-sm">
                {errorMessage}
              </Typography>
            )}
            <Button
              type="submit"
              color="blue"
              className="w-full text-center text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800"
            >
              Log in
            </Button>
          </form>
        </div>
      </div>
    </section>
  );
};

export default Login;
