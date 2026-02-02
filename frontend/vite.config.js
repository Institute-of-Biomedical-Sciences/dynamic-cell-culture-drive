import tailwind from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import {fileURLToPath, URL} from "node:url";
import {defineConfig} from "vite";

export default defineConfig({
  plugins : [
    vue(),
    tailwind({
      base : "./src/index.css",
    }),
  ],
  resolve : {alias : {"@" : fileURLToPath(new URL("./src", import.meta.url))}},
  server : {
    port : 5173,
    proxy : {
      "/api" : {
        target : "http://localhost:8000",
        changeOrigin : true,
        rewrite : (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
