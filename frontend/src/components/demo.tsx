"use client";

import React from "react";
import { Typography, Button } from "@material-tailwind/react";
import CKEditorComponent from "@/components/CKEditorComponent";
import { useAuth } from "@/context/authContext";
import { useLogin } from "@/context/loginContext";
import Login from "./login";

function Demo() {
  const { isLoginOpen, openLogin, closeLogin } = useLogin();
  const { isLoggedIn } = useAuth();

  return (
    <header className="mt-5 bg-white p-8">
      <section className="grid h-auto gap-5 place-items-center pb-12">
        <Typography variant="h1" className="mb-2">
          Klopta
        </Typography>
        <Typography
          variant="lead"
          color="gray"
          className="max-w-3xl mb-1 text-center text-gray-500"
        >
          Enhance your writing by leaving the busywork to the AI.
        </Typography>
      </section>
      <div className="w-full lg:container lg:mx-auto">
        <div className="w-full rounded-lg object-cover bg-gray-100 p-3">
          {isLoggedIn ? (
            <CKEditorComponent />
          ) : (
            <div className="flex flex-col items-center justify-center h-96 bg-gray-200 rounded-lg">
              <Button
                color="blue"
                size="lg"
                className="mb-4"
                onClick={() => console.log("Try out for free clicked")}
              >
                Try out for free
              </Button>
              <Typography variant="small" color="gray" className="mb-4">
                or
              </Typography>
              <Button color="gray" size="lg" onClick={openLogin}>
                Log In
              </Button>
            </div>
          )}
        </div>
      </div>
      {isLoginOpen && <Login onClose={closeLogin} />}
    </header>
  );
}

export default Demo;
