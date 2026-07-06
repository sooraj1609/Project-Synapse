/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        base: '#10172B',
        surface: '#1A2338',
        surfaceRaised: '#212C46',
        border: '#2B3654',
        textPrimary: '#E8ECF4',
        textMuted: '#8B93A7',
        ai: '#22D3EE',
        risk: {
          stable: '#2DD4BF',
          improving: '#60A5FA',
          warning: '#FBBF24',
          atrisk: '#FB923C',
          critical: '#F43F5E',
        },
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
