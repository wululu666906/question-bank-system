import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api/dify': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api\/dify/, ''),
        // 增加代理超时时间 (单位: 毫秒)，防止长时间思考导致连接断开
        timeout: 300000,
        proxyTimeout: 300000,
      },
    },
  },
})
