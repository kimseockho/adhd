import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import fs from 'fs';

export default defineConfig({
plugins: [sveltekit()],
server: {
    https: {
    key: fs.readFileSync('ssl/key.pem'),
    cert: fs.readFileSync('ssl/cert.pem'),
    },
    host: '0.0.0.0'}
});
