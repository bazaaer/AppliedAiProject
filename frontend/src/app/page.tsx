'use client';

// components
import { Navbar, Footer } from "@/components";

// sections
import Demo from "./demo";
import Body from "./body";

// context
import { AuthProvider } from "@/context/authContext";

export default function Campaign() {
  return (
    <AuthProvider>
      <div>
        <Navbar />
        <Demo />
        <Body />
        <Footer />
      </div>
    </AuthProvider>
  );
}
