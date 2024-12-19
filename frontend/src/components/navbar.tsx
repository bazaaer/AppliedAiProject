import React, { useState, useEffect } from "react";
import { Navbar as MTNavbar, Collapse, Button, IconButton, Typography } from "@material-tailwind/react";
import { UserCircleIcon, CommandLineIcon, XMarkIcon, Bars3Icon } from "@heroicons/react/24/solid";
import Login from "./login";
import { useAuth } from "@/context/authContext";

const NAV_MENU = [
  {
    name: "Docs",
    icon: CommandLineIcon,
    href: "https://klopta.vinnievirtuoso.online/api/docs/index.html",
  },
];

interface NavItemProps {
  children: React.ReactNode;
  href?: string;
}

interface NavbarProps {
  bodyRef: React.RefObject<HTMLDivElement>;
}

function NavItem({ children, href }: NavItemProps) {
  return (
    <li>
      <Typography
        as="a"
        href={href || "#"}
        target={href ? "_blank" : "_self"}
        variant="paragraph"
        color="gray"
        className="flex items-center gap-2 font-medium text-gray-900"
      >
        {children}
      </Typography>
    </li>
  );
}

export function Navbar({ bodyRef }: NavbarProps) {
  const [open, setOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [username, setUsername] = useState<string | null>("Try-Out Mode");

  const { isLoggedIn, logout } = useAuth();

  const handleOpen = () => setOpen((cur) => !cur);

  const handleOpenLogin = () => setIsLoginOpen(true);

  const handleCloseLogin = () => setIsLoginOpen(false);

  const handleLogout = () => {
    logout();
    setUsername("Try-Out Mode");
  };

  const handleLogoClick = () => {
    bodyRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    const savedUsername = localStorage.getItem("username");
    setUsername(savedUsername || "Try-Out Mode");
  }, [isLoggedIn]);

  React.useEffect(() => {
    window.addEventListener(
      "resize",
      () => window.innerWidth >= 960 && setOpen(false)
    );
  }, []);

  return (
    <>
      <MTNavbar shadow={false} fullWidth className="border-0 sticky top-0 z-[1001]">
        <div className="container mx-auto flex items-center justify-between">
          <Typography
            as="a"
            onClick={handleLogoClick}
            color="blue-gray"
            className="text-lg font-bold text-[#fd5f22] cursor-pointer"
          >
            Klopta
          </Typography>
          <ul className="ml-10 hidden items-center gap-8 lg:flex ml-auto mr-auto">
            <NavItem>
              <UserCircleIcon className="h-5 w-5" />
              {username}
            </NavItem>
            {NAV_MENU.map(({ name, icon: Icon, href }) => (
              <NavItem key={name} href={href}>
                <Icon className="h-5 w-5" />
                {name}
              </NavItem>
            ))}
          </ul>
          <div className="hidden items-center gap-2 lg:flex">
            <Button color="gray" onClick={isLoggedIn ? handleLogout : handleOpenLogin}>
              {isLoggedIn ? "Log Out" : "Log In"}
            </Button>
          </div>
          <IconButton
            variant="text"
            color="gray"
            onClick={handleOpen}
            className="ml-auto inline-block lg:hidden"
          >
            {open ? (
              <XMarkIcon strokeWidth={2} className="h-6 w-6" />
            ) : (
              <Bars3Icon strokeWidth={2} className="h-6 w-6" />
            )}
          </IconButton>
        </div>
        <Collapse open={open}>
          <div className="container mx-auto mt-3 border-t border-gray-200 px-2 pt-4">
            <ul className="flex flex-col gap-4">
              <NavItem>
                <UserCircleIcon className="h-5 w-5" />
                {username}
              </NavItem>
              {NAV_MENU.map(({ name, icon: Icon }) => (
                <NavItem key={name}>
                  <Icon className="h-5 w-5" />
                  {name}
                </NavItem>
              ))}
            </ul>
            <div className="mt-6 mb-4 flex items-center gap-2">
              <Button color="gray" onClick={isLoggedIn ? handleLogout : handleOpenLogin}>
                {isLoggedIn ? "Log Out" : "Log In"}
              </Button>
            </div>
          </div>
        </Collapse>
      </MTNavbar>
      {isLoginOpen && <Login onClose={handleCloseLogin} />}
    </>
  );
}

export default Navbar;
