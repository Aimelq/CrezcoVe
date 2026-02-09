import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
        },
    },
    server: {
        port: 3000,
        host: true,
        watch: {
            usePolling: true,
        },
        proxy: {
            '/api': {
                // El target DEBE ser el nombre del servicio en Docker
                target: 'http://backend:5000',
                changeOrigin: true,
            },
        },
    },
})
