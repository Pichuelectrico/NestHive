/**
 * Configuración de Next.js.
 *
 * - Modo Docker/live (por defecto): output "standalone", sin basePath.
 * - Build estático para GitHub Pages: activar con env NESTLINK_PAGES=1 y
 *   NESTLINK_BASE_PATH (ej. "/NestLink"); Next usa basePath + assetPrefix y
 *   genera la salida en frontend/out/ bajo ese subpath.
 */
/** @type {import('next').NextConfig} */
const isPages = process.env.NESTLINK_PAGES === "1";
const basePath = (process.env.NESTLINK_BASE_PATH ?? "").trim();

const nextConfig = {
  reactStrictMode: true,
  output: isPages ? "export" : "standalone",
  ...(isPages && basePath
    ? { basePath, assetPrefix: basePath, trailingSlash: true }
    : {}),
};

export default nextConfig;
