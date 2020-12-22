# demoapp frontend

## Project setup

```
npm install
```

### and hot-reload for development

```
npm run serve
```

For the devlopment to avoid cors issue when connection the backend API,
add or edit `vue.config.js` file with `devServer proxy` setting.

```
module.exports = {
  devServer: {
    proxy: {
      '^/api': {
        target: 'http://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  }
}
```

Replace `http://localhost:8000` with whatever your API endpoint.

### Compiles and minifies for production
```
npm run build
```

### Run your unit tests
```
npm run test:unit
```
