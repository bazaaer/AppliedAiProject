'use client';

import { Navbar, Footer } from "@/components";
import React from "react";

export default function About() {
  return (
    <div>
      {/* Navbar */}
      <Navbar />

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-center text-3xl font-bold mb-8">About Us</h1>

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
            <p className="mt-4 text-gray-700">
              Frontend Developer, API Communication Handyman
            </p>
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
            <p className="mt-4 text-gray-700">
              CKEditor Plugin Builder
            </p>
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
            <p className="mt-4 text-gray-700">
              LLM Engineer, AI Engineer
            </p>
          </div>

          {/* Column 4 */}
          <div className="text-center">
            <div className="w-32 h-32 mx-auto rounded-full overflow-hidden border border-gray-300">
              <img
                src="/avatars/Lander_Van_Der_Stighelen.jpg"  {/* Add the path for the new profile image */}
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
            <p className="mt-4 text-gray-700">
              DevOps Engineer, Docker Master
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
}

