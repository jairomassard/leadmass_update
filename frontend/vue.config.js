const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // Configuración de proxy para dev local
        changeOrigin: true,
      },
    },
  },
  publicPath: '/',
});

