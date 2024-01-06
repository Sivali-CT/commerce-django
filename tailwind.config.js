/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./auctions/templates/auctions/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [require('@tailwindcss/aspect-ratio')],
}

