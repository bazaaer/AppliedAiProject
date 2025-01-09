'use client';

import React from "react";
import dynamic from "next/dynamic";

// Dynamically import components to ensure SSR safety
const Navbar = dynamic(() => import("@/components").then((mod) => mod.Navbar), { ssr: false });
const Footer = dynamic(() => import("@/components").then((mod) => mod.Footer), { ssr: false });
const Demo = dynamic(() => import("../components/demo"), { ssr: false });
const Body = dynamic(() => import("../components/body"), { ssr: false });

// context
import { AuthProvider } from "@/context/authContext";
import { LoginProvider } from "@/context/loginContext";

export default function Page() {
  return (
    <AuthProvider>
      <LoginProvider>
        <div>
          <Navbar />
          <Demo />
          <Body />
          <Footer />
        </div>
      </LoginProvider>
    </AuthProvider>
  );
}
