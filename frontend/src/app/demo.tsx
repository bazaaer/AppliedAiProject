"use client";

import { Typography } from "@material-tailwind/react";
import CKEditorComponent from "@/components/CKEditorComponent";


function Demo() {
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
          enhance your writing by leaving the busywork to the AI.
        </Typography>
      </section>
      <div className="w-full lg:container lg:mx-auto">
        <div
          className="h-96 w-full rounded-lg object-cover lg:h-[21rem] bg-gray-100"
        >
          <CKEditorComponent />
        </div>
      </div>
    </header>
  );
}
export default Demo;
