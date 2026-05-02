import { fileURLToPath, URL } from "node:url";

import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";

import Components from "unplugin-vue-components/vite";
import { PrimeVueResolver } from "@primevue/auto-import-resolver";

export default defineConfig(({ mode }) => {
  let config = {
    css: {
      devSourcemap: false, // 关闭 CSS source map
    },
    plugins: [
      vue(),
      Components({
        resolvers: [PrimeVueResolver()],
      }),
    ],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
        "#": fileURLToPath(new URL("./src/utils", import.meta.url)),
      },
    },
    build: {
      minify: "rolldown",
      cssMinify: true,
      sourcemap: false,
      reportCompressedSize: false,
      chunkSizeWarningLimit: 2000,
    },
    esbuild: {
      drop: ["console", "debugger"],
    },
  };
  if (mode === "debug") {
    const env = loadEnv(mode, process.cwd(), "dev_");
    if (!env.dev_backend) {
      throw new Error("请在 .env 文件中设置 dev_backend 环境变量");
    }
    config["server"] = {
      proxy: {
        "/api": {
          target: env.dev_backend,
          changeOrigin: true,
        },
        "/image": {
          target: env.dev_backend,
          changeOrigin: true,
        },
      },
    };
  }
  return config;
});
