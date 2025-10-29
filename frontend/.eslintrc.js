module.exports = {
    root: true,
    env: {
      browser: true,
      node: true
    },
    extends: [
      'plugin:vue/essential',
      'eslint:recommended'
    ],
    globals: {
      fbq: 'readonly' // Declara fbq como una variable global de solo lectura
    },
    rules: {}
  };