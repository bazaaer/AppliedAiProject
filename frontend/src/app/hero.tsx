"use client";

import Image from "next/image";
import { Typography } from "@material-tailwind/react";


function Hero() {
  return (
    <header className="mt-5 bg-white p-8">
      <section className="grid h-auto gap-8 place-items-center p-8">
        <Typography variant="h1" className="mb-2">
          about us
        </Typography>
        <Typography
          variant="lead"
          color="gray"
          className="max-w-3xl mb-1 text-center text-gray-500"
        >
          we are extremely cool
        </Typography>
      </section>
      <div className="w-full lg:container lg:mx-auto">
        <Image
          width={1024}
          height={400}
          src="/image/blog-background.png"
          alt="credit cards"
          className="h-96 w-full rounded-lg object-cover lg:h-[21rem]"
        />
      </div>
    </header>
  );
}
export default Hero;
