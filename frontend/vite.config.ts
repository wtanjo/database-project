import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  resolve: {
    alias: {
      // 设置 @ 指向 src 目录，方便后续导入
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      // 当请求以 /api 开头时，转发到 FastAPI
      // Docker 环境下通过 API_TARGET 环境变量指定，本地开发默认 127.0.0.1:8000
      '/api': {
        target: process.env.API_TARGET ?? 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})