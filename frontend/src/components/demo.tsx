"use client";

import { Typography } from "@material-tailwind/react";
import CKEditorComponent from "@/components/CKEditorComponent";
import { useEffect } from "react";
import { useAuth } from "@/context/authContext";

function Demo() {
  const { isLoggedIn, demoLogin } = useAuth();

  useEffect(() => {
    if (!isLoggedIn) {
      // Automatically login for demo when not logged in
      demoLogin();
    }
  }, [isLoggedIn, demoLogin]);

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
          <CKEditorComponent />
        </div>
      </div>
    </header>
  );
}

export default Demo;
