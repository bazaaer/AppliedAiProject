import {
  Typography,
  IconButton
} from "@material-tailwind/react";

const CURRENT_YEAR = new Date().getFullYear();
const LINKS = [
  { name: "AP Hogeschool", href: "https://www.ap.be" },
  { name: "About Us", href: "/about" },
  { name: "Team", href: "/team" },
  { name: "Antwerpen", href: "https://www.antwerpen.be" },
];

export function Footer() {
  return (
    <footer className="pb-5 p-10 md:pt-10">
      <div className="container flex flex-col mx-auto">
        <div
          className="flex !w-full py-20 mb-5 md:mb-20 flex-col justify-center !items-center bg-cover bg-center container max-w-6xl mx-auto rounded-2xl p-5 gap-4"
          style={{ backgroundImage: 'url(/image/blog-background.png)' }}
        >
          <Typography
            className="text-2xl md:text-3xl text-center font-bold bg-gray-500 bg-opacity-10 backdrop-blur p-5 rounded-lg"
            color="white"
          >
            Questions? Message us!
          </Typography>
          <Typography
            color="white"
            className="px-100 text-center my-3 !text-base bg-gray-500 bg-opacity-10 backdrop-blur-sm p-2 rounded-lg"
          >
            You can always email us at john.doe@gmail.com
          </Typography>
        </div>

        <div className="flex flex-col md:flex-row items-center !justify-between">
          <Typography
            as="a"
            href="https://www.material-tailwind.com"
            target="_blank"
            variant="h6"
            className="text-gray-900 text-xs"
          >
            Material Tailwind
          </Typography>
          <ul className="flex justify-center my-4 md:my-0 w-max mx-auto items-center gap-4">
            {LINKS.map((link, index) => (
              <li key={index}>
                <Typography
                  as="a"
                  href={link.href}
                  variant="small"
                  color="white"
                  className="font-normal !text-gray-700 hover:!text-gray-900 transition-colors"
                >
                  {link.name}
                </Typography>
              </li>
            ))}
          </ul>
          <div className="flex w-fit justify-center gap-2">
            <IconButton size="sm" color="gray" variant="text">
              <a href="https://github.com/bazaaer/AppliedAiProject">
                <i className="fa-brands fa-github text-lg" />
              </a>
            </IconButton>
          </div>
        </div>
        <Typography
          color="blue-gray"
          className="text-center mt-12 font-normal !text-gray-700"
        >
          &copy; {CURRENT_YEAR} Made with{" "}
          <a href="https://www.material-tailwind.com" target="_blank">
            Material Tailwind
          </a>{" "}
        </Typography>
      </div>
    </footer>
  );
}

export default Footer;
