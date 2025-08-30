/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,svelte}",
  ],
  theme: {
    extend: {
      colors: {
        // Cyberpunk CRAWLED Color Palette
        cyber: {
          black: '#0a0a0a',
          dark: '#1a1a1a',
          gray: '#2a2a2a',
          'light-gray': '#3a3a3a',
        },
        neon: {
          cyan: '#00ffff',
          pink: '#ff0080',
          lime: '#39ff14',
          blue: '#0080ff',
          green: '#00ff41',
          red: '#ff073a',
          purple: '#bf00ff',
          orange: '#ff8c00',
        },
        // Compatibility colors
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe', 
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#00ffff', // Neon cyan
          600: '#0080ff', // Electric blue
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        }
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', 'monospace'],
        'cyber': ['Orbitron', 'Share Tech Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.8s ease-out',
        'slide-up': 'slideUp 0.6s ease-out', 
        'scale-in': 'scaleIn 0.4s ease-out',
        'pulse-glow': 'pulseGlow 2s infinite',
        'float': 'float 3s ease-in-out infinite',
        'cyber-pulse': 'cyberPulse 2s ease-in-out infinite alternate',
        'glitch': 'glitch 0.3s infinite',
        'matrix-rain': 'matrixRain 20s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(-10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        cyberPulse: {
          '0%': { boxShadow: '0 0 5px #00ffff' },
          '100%': { boxShadow: '0 0 20px #00ffff, 0 0 30px #00ffff' },
        },
        glitch: {
          '0%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' }, 
          '80%': { transform: 'translate(2px, -2px)' },
          '100%': { transform: 'translate(0)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
      boxShadow: {
        'cyber': '0 8px 32px rgba(0, 255, 255, 0.1)',
        'cyber-glow': '0 0 20px rgba(0, 255, 255, 0.4)',
        'cyber-pink': '0 0 20px rgba(255, 0, 128, 0.4)',
        'cyber-lime': '0 0 20px rgba(57, 255, 20, 0.4)',
        'neon-cyan': '0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 40px #00ffff',
        'neon-pink': '0 0 10px #ff0080, 0 0 20px #ff0080, 0 0 40px #ff0080',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}