"use client";

import React from "react";
import { UserMan, About } from "@/components";
import {
  Tabs,
  TabsHeader,
  TabsBody,
  Tab,
  TabPanel,
} from "@material-tailwind/react";

export function Body() {
  const labeldata = [
    { label: "About", value: "about", content: <About /> },
    { label: "Admin", value: "admin", content: <UserMan /> },
  ];

  return (
    <section className="grid h-auto gap-8 place-items-center p-8">
      <Tabs
        value="about"
        className="mx-auto max-w-7xl w-full mb-2"
      >
        <div className="w-full flex mb-1 flex-col items-center">
          <TabsHeader className="h-10 w-1/2 md:w-[50rem] border border-white/25 bg-opacity-90">
            {labeldata.map(({ label, value }) => (
              <Tab key={value} value={value}>
                {label}
              </Tab>
            ))}
          </TabsHeader>
          <TabsBody className="w-full container mx-auto pt-12 pb-16 text-center">
            {labeldata.map(({ value, content }) => (
              <TabPanel key={value} value={value}>
                {content}
              </TabPanel>
            ))}
          </TabsBody>
        </div>
      </Tabs>
    </section>
  );
}

export default Body;