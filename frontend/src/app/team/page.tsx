'use client';

// src/app/about/page.tsx
import React from 'react';
import { Typography } from '@material-tailwind/react';
import Link from 'next/link';

// Define an array of team members with their details
const teamMembers = [
  {
    name: 'Grim Van Daele',
    role: 'Frontend Developer, API Communication Handyman',
    image: '/avatars/Grim_Van_Daele.jpg',
    linkedin: 'https://linkedin.com/in/grim-van-daele-7a6711309/',
  },
  {
    name: 'Jarn Vaerewijck',
    role: 'CKEditor Plugin Builder',
    image: '/avatars/Jarn_Vaerewijck.png',
    linkedin: 'https://linkedin.com/in/jarn-vaerewijck-52b625255/',
  },
  {
    name: 'Jurrean De Nys',
    role: 'LLM Engineer, AI Engineer',
    image: '/avatars/Jurrean_De_Nys.png',
    linkedin: 'https://linkedin.com/in/jurreandenys/',
  },
  {
    name: 'Lander Van Der Stighelen',
    role: 'DevOps Engineer, Docker Master',
    image: '/avatars/Lander_Van_Der_Stighelen.jpg',
    linkedin: 'https://linkedin.com/in/landervds/',
  },
];

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
        <Typography as="h1" variant="h3" className="text-2xl md:text-3xl text-center font-bold p-5 rounded-lg">
          Our Team
        </Typography>
        <div className="px-100 text-center my-3 !text-base backdrop-blur-sm p-2 rounded-lg">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {teamMembers.map((member, index) => (
              <div key={index} className="text-center">
                <div className="w-32 h-32 mx-auto rounded-full overflow-hidden border border-gray-300">
                  <img
                    src={member.image}
                    alt={member.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <a
                  href={member.linkedin}
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
                <Typography as="h3" variant='h5' className="mt-4 text-gray-800">{member.name}</Typography>
                <Typography as="p" className="mt-4 text-gray-700">{member.role}</Typography>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
