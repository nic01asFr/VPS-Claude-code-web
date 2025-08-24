module.exports = {
  lintOnSave: false,
  publicPath: '/',
  productionSourceMap: false,
  devServer: {
    proxy: {
      '/api': {
        target: 'https://claude-api.colaig.fr',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'https://claude-api.colaig.fr',
        changeOrigin: true,
        ws: true
      }
    }
  }
} 