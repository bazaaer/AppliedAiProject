import {
    Typography
} from "@material-tailwind/react";

export function About() {
    return (
        <div>
            <Typography
                color="blue-gray"
                className="mx-auto w-full text-[30px] lg:text-[48px] font-bold leading-[45px] lg:leading-[60px] lg:max-w-2xl"
            >
                About
            </Typography>
            <Typography
                variant="lead"
                className="mx-auto mt-8 mb-4 w-full px-8 !text-gray-700 lg:w-10/12 lg:px-12 xl:w-8/12 xl:px-20"
            >
                we are extremely cool
            </Typography>
        </div>
    )
}