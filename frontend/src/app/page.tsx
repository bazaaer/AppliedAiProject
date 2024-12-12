'use client';

// components
import { Navbar, Footer } from "@/components";
import React from "react";

// sections
import Demo from "./demo";
import Body from "./body";

// context
import { AuthProvider } from "@/context/authContext";

export default function Campaign() {
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
