module.exports = {
  purge: {
    content: [
      './src/**/*.{js,jsx,ts,tsx}',
      './public/index.html',
    ],
    options: {
      safelist: [],
    },
  },
  darkMode: 'class', // or 'media'
  theme: {
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [],
};

