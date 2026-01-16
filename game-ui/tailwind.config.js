/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'midnight': '#0f172a',
                'gold': '#fbbf24',
                'deep-purple': '#581c87',
            },
            fontFamily: {
                premium: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
