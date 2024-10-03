/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  reactStrictMode: true,
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL,
    API_URL_DEV: process.env.NEXT_PUBLIC_API_URL_DEV,
  },
};

module.exports = nextConfig;
