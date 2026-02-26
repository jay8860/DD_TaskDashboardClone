/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Outfit', 'sans-serif'],
            },
            colors: {
                primary: {
                    light: '#6366f1', // Indigo 500
                    DEFAULT: '#3730a3', // Indigo 800
                    dark: '#1e1b4b', // Indigo 950
                },
                accent: {
                    violet: '#7c3aed',
                    blue: '#1d4ed8',
                    green: '#10b981',
                    orange: '#f59e0b',
                },
                dark: {
                    bg: '#000000',    // Pitch Black
                    card: '#0a0a0a',  // Extremely Dark Grey
                    border: '#1a1a1a',
                    text: '#f8fafc',  // Slate 50
                    muted: '#64748b', // Slate 500
                }
            },
            boxShadow: {
                'premium-sm': '0 2px 4px 0 rgba(0, 0, 0, 0.05)',
                'premium': '0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04)',
                'premium-lg': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
            },
            backdropBlur: {
                'premium': '12px',
            }
        },
    },
    plugins: [],
}
