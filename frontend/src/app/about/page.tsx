'use client';

// src/app/about/page.tsx
import React from "react";
import { Typography } from "@material-tailwind/react";

export default function About() {
  return (
    <div className="container flex flex-col mx-auto">
      <div className="flex !w-full py-20 mb-5 md:mb-20 flex-col justify-center !items-center bg-cover bg-center container max-w-6xl mx-auto rounded-2xl p-5 gap-4">
        <Typography
          className="text-2xl md:text-3xl text-center font-bold p-5 rounded-lg"
        >
          About us
        </Typography>
        <Typography
          className="px-100 text-center my-3 !text-base backdrop-blur-sm p-2 rounded-lg"
        >
          Lorem ipsum dolor, sit amet consectetur adipisicing elit. Ipsam ratione maiores nam, saepe porro fugiat quaerat explicabo pariatur nesciunt quam ullam veniam eum illo vel, aliquam dolorem impedit sint adipisci?
        </Typography>
      </div>
    </div>
  );
}
