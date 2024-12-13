'use client';

// src/app/about/page.tsx
import React from "react";
import { Typography } from "@material-tailwind/react";
import Link from "next/link";

export default function Team() {
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
            <Typography className="text-2xl md:text-3xl text-center font-bold p-5 rounded-lg">
              Our Team
            </Typography>
            <div className="px-100 text-center my-3 !text-base backdrop-blur-sm p-2 rounded-lg">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8"> {/* Updated grid to have 4 columns */}
                {/* Column 1 */}
                <div className="text-center">
                  <div className="w-32 h-32 mx-auto rounded-full overflow-hidden border border-gray-300">
                    <img
                      src="/avatars/Grim_Van_Daele.jpg"
                      alt="G. Van Daele"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <a
                    href="https://linkedin.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-4 text-gray-600 hover:text-gray-900"
                  >
                    <img
                      src="/logos/logo-linkedin.svg"
                      alt="LinkedIn"
                      className="w-6 h-6 inline"
                    />
                  </a>
                  <Typography className="mt-4 text-gray-700">
                    Frontend Developer, API Communication Handyman
                  </Typography>
                </div>
    
                {/* Column 2 */}
                <div className="text-center">
                  <div className="w-32 h-32 mx-auto rounded-full overflow-hidden border border-gray-300">
                    <img
                      src="/avatars/Jarn_Vaerewijck.jpg"
                      alt="J. Vaerewijck"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <a
                    href="https://linkedin.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-4 text-gray-600 hover:text-gray-900"
                  >
                    <img
                      src="/logos/logo-linkedin.svg"
                      alt="LinkedIn"
                      className="w-6 h-6 inline"
                    />
                  </a>
                  <Typography className="mt-4 text-gray-700">
                    CKEditor Plugin Builder
                  </Typography>
                </div>
    
                {/* Column 3 */}
                <div className="text-center">
                  <div className="w-32 h-32 mx-auto rounded-full overflow-hidden border border-gray-300">
                    <img
                      src="/avatars/Jurrean_De_Nys.jpg"
                      alt="J. De Nys"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <a
                    href="https://linkedin.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-4 text-gray-600 hover:text-gray-900"
                  >
                    <img
                      src="/logos/logo-linkedin.svg"
                      alt="LinkedIn"
                      className="w-6 h-6 inline"
                    />
                  </a>
                  <Typography className="mt-4 text-gray-700">
                    LLM Engineer, AI Engineer
                  </Typography>
                </div>
    
                {/* Column 4 */}
                <div className="text-center">
                  <div className="w-32 h-32 mx-auto rounded-full overflow-hidden border border-gray-300">
                    <img
                      src="/avatars/Lander_Van_Der_Stighelen.jpg" // Ensure this image exists or is correct
                      alt="L. Van Der Stighelen"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <a
                    href="https://linkedin.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-4 text-gray-600 hover:text-gray-900"
                  >
                    <img
                      src="/logos/logo-linkedin.svg"
                      alt="LinkedIn"
                      className="w-6 h-6 inline"
                    />
                  </a>
                  <Typography className="mt-4 text-gray-700">
                    DevOps Engineer, Docker Master
                  </Typography>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
}
