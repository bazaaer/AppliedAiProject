'use client';

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
        <h1 className="text-2xl md:text-3xl text-center font-bold p-5 rounded-lg">
          Over Klopta
        </h1>
        <div className="about-us bg-gray-50 text-gray-800 p-8">
          <section className="intro mb-8">
            <p className="mb-4 text-center">
              <strong className="font-semibold">Klopta</strong> is een
              innovatieve applicatie die speciaal is ontwikkeld voor de
              redacteurs van Stad Antwerpen. Het doel van Klopta is om het
              proces van contentcreatie te vereenvoudigen, versnellen en
              verbeteren. Door gebruik te maken van geavanceerde
              AI-technologie, helpt de tool redacteurs om teksten te
              analyseren, verbeteren en herschrijven, terwijl de huisstijl en
              consistentie altijd gewaarborgd blijven.
            </p>
            <p className="mb-4 text-center">
              Een belangrijke kracht van Klopta is de integratie van{" "}
              <strong className="font-semibold">Checket</strong>, een slimme
              assistent die redacteurs ondersteunt bij het optimaliseren van
              teksten. Of het nu gaat om het scoren van teksten op basis van de
              huisstijl, het herschrijven van zinnen of het selecteren van
              alternatieve suggesties, Klopta maakt het eenvoudig en
              intuïtief. Met deze tool kunnen redacteurs hoogwaardige,
              toegankelijke en begrijpelijke content creëren voor diverse
              doelgroepen, zonder in te boeten op snelheid of kwaliteit.
            </p>
          </section>

          <section className="mission">
            <h2 className="font-bold mb-4 text-center text-2xl">
              Onze Missie
            </h2>
            <p className="mb-4 text-center">
              Bij Stad Antwerpen geloven we in de kracht van efficiënte en
              toegankelijke communicatie. Klopta is ontwikkeld om redacteurs
              te ondersteunen bij het vertalen van complexe en technische
              teksten naar content die iedereen begrijpt. De applicatie is
              ontworpen met oog voor gebruiksgemak en sluit naadloos aan bij de
              bestaande workflows van redacteurs. Zo kunnen zij zich richten op
              wat echt belangrijk is: het maken van impactvolle en relevante
              content.
            </p>
            <p className="mb-4 text-center">
              Met Klopta willen we de redacteurs van Stad Antwerpen niet alleen
              tijd besparen, maar hen ook een krachtige tool bieden om
              consistentie en kwaliteit te waarborgen. Klopta is meer dan een
              hulpmiddel – het is een partner in de dagelijkse uitdagingen van
              contentcreatie.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
