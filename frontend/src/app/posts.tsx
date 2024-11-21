"use client";

import React from "react";
import {
  Typography,
  Tabs,
  TabsHeader,
  Tab,
  Button,
  Input
} from "@material-tailwind/react";

export function Posts() {
  return (
    <section className="grid h-auto gap-8 place-items-center p-8">
      <Tabs value="trends" className="mx-auto max-w-7xl w-full mb-2">
        <div className="w-full flex mb-1 flex-col items-center">
          <TabsHeader className="h-10 w-1/2 md:w-[50rem] border border-white/25 bg-opacity-90">
            <Tab value="about">about</Tab>
            <Tab value="admin">admin</Tab>
          </TabsHeader>
        </div>
      </Tabs>
      <div className="w-w-full container mx-auto pt-12 pb-24 text-center">
        <Typography
          color="blue-gray"
          className="mx-auto w-full text-[30px] lg:text-[48px] font-bold leading-[45px] lg:leading-[60px] lg:max-w-2xl"
        >
          Klopta
        </Typography>
        <Typography
          variant="lead"
          className="mx-auto mt-8 mb-4 w-full px-8 !text-gray-700 lg:w-10/12 lg:px-12 xl:w-8/12 xl:px-20"
        >
          enhance your writing by leaving the busywork to the AI.
        </Typography>
        <div className="grid place-items-start justify-center gap-2">
          <div className="mt-8 flex flex-col items-center justify-center gap-4 md:flex-row">
            <div className="w-80">
              {/* @ts-ignore */}
              <Input label="john@pork.com" />
            </div>
            <Button size="md" className="lg:w-max shrink-0" fullWidth color="gray">
              create key
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Posts;
