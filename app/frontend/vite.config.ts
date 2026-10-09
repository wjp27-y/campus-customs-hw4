import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Forward API calls and product images to the FastAPI backend (backend/main.py).
const API_URL = process.env.API_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": API_URL,
      "/images": API_URL,
    },
  },
});
