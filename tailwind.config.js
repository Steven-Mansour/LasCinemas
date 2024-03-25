/** @type {import('tailwindcss').Config} */
import resolveConfig from 'tailwindcss/resolveConfig'
import tailwindConfig from './tailwind.config.js'

const fullConfig = resolveConfig(tailwindConfig)
module.exports = {
  content: ["./templates/**/*.{html,js}",
    "./static/node_modules/tw-elements/dist/js/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        poppins: ['Poppins']
      },
      gridTemplateColumns: {
        // Simple 20 column grid
        '22': 'repeat(22, minmax(0, 1fr))',

        // Complex site-specific column configuration
        'footer': '200px minmax(900px, 1fr) 100px',
      }
    },
  },
  plugins: [require('@tailwindcss/forms'),
  require("tw-elements/dist/plugin.cjs"),
  require('tailwind-scrollbar'),
  ],
}

