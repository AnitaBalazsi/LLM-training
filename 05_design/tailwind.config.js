/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#030213',
        'accent': '#D4183D',
        'muted': '#717182',
        'card': '#FFFFFF',
        'border': 'rgba(0, 0, 0, 0.1)',
        'input': '#F3F3F5'
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif']
      },
      boxShadow: {
        'card': '0px 10px 15px 0px rgba(0, 0, 0, 0.1), 0px 4px 6px 0px rgba(0, 0, 0, 0.1)'
      },
      borderRadius: {
        'lg': '12.75px',
        'md': '8.75px',
        'sm': '6.75px'
      }
    },
  },
  plugins: [],
}
