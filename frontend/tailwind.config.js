/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#fcfbf9',
        surface: '#ffffff',
        'surface-subtle': '#f7f6f2',
        charcoal: {
          900: '#151816',
          800: '#1f2421',
          700: '#2d3330',
          600: '#404743',
          500: '#5c635f',
          400: '#7d8580',
          300: '#a3aba6',
        },
        olive: {
          50: '#f4f6f4',
          100: '#e5eae5',
          200: '#cbd6cc',
          500: '#5a7258',
          600: '#485e46',
          700: '#394b37',
          800: '#2c3b2b',
        },
        ochre: {
          50: '#fbf8f0',
          100: '#f6eedb',
          200: '#ebd9b4',
          500: '#b8860b',
          600: '#9e7409',
          700: '#7a5a07',
        },
        border: {
          DEFAULT: '#e6e3dc',
          subtle: '#efece6',
          strong: '#d4cfc5',
        },
        tag: {
          clean: '#2e7d32',
          tampered: '#b91c1c',
          warning: '#c27803',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}
