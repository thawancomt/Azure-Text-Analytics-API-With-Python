/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: "media",
  content: ["../{templates,static}/*.{html,js}"],
  theme: {
    extend: {
    },
  },
  plugins: [
    require('flowbite/plugin')
],
darkMode: 'media'
}
