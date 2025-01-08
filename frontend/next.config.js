/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Enables static export
  trailingSlash: true, // Adds a trailing slash for better compatibility with static hosting
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
    unoptimized: true, // Disables image optimization for static export
  },
  typescript: {
    ignoreBuildErrors: true, // Ignores TypeScript errors during the build process
  },
};

module.exports = nextConfig;
