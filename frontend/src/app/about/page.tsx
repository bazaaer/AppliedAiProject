'use client';

// src/app/about/page.tsx
import React from "react";
import { Typography } from "@material-tailwind/react";
import Link from "next/link";

export default function About() {
  return (
    <div className="container flex flex-col mx-auto relative">
      <Link href="/" className="absolute top-4 left-0">
        <div className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition pl-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="w-6 h-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M15.75 19.5L8.25 12l7.5-7.5"
            />
          </svg>
          <span className="text-sm font-medium">Back</span>
        </div>
      </Link>

      <div className="flex !w-full py-20 mb-5 md:mb-20 flex-col justify-center !items-center bg-cover bg-center container max-w-6xl mx-auto rounded-2xl p-5 gap-4">
        <Typography
          className="text-2xl md:text-3xl text-center font-bold p-5 rounded-lg"
        >
          About us
        </Typography>
        <Typography
          className="px-100 text-center my-3 !text-base backdrop-blur-sm p-2 rounded-lg"
        >
          Lorem ipsum dolor, sit amet consectetur adipisicing elit. Ipsam
          ratione maiores nam, saepe porro fugiat quaerat explicabo pariatur
          nesciunt quam ullam veniam eum illo vel, aliquam dolorem impedit sint
          adipisci?
        </Typography>
      </div>
    </div>
  );
}
