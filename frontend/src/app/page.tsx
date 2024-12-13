'use client';

// components
import { Navbar, Footer } from "@/components";
import React from "react";

// sections
import Demo from "../components/demo";
import Body from "../components/body";

// context
import { AuthProvider } from "@/context/authContext";

export default function Page() {
  const bodyRef = React.useRef<HTMLDivElement | null>(null);

  return (
    <AuthProvider>
      <div>
        <Navbar bodyRef={bodyRef} />
        <Demo />
        <Body ref={bodyRef} />
        <Footer />
      </div>
    </AuthProvider>
  );
}
