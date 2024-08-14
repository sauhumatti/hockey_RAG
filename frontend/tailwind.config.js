/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'hockey-blue': '#4a90e2',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}

