module.exports = {
  transpileDependencies: [
    "vuetify"
  ],
  devServer: {
    proxy: {
      '^/api': {
        target: 'http://192.168.30.100:8000',
        ws: true,
        changeOrigin: true
      }
    }
  }
}
