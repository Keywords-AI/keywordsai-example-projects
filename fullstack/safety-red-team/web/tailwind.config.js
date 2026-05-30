/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        muted: 'var(--muted)',
        'muted-foreground': 'var(--muted-foreground)',
        accent: 'var(--accent)',
        'accent-foreground': 'var(--accent-foreground)',
        border: 'var(--border)',
        input: 'var(--input)',
        ring: 'var(--ring)',
      },
      fontFamily: {
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        'sans-tight': ['var(--font-sans-tight)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      fontSize: {
        xs: '0.75rem',
        sm: '0.875rem',
        base: '1rem',
        lg: '1.125rem',
        xl: '1.25rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
        '4xl': '2.5rem',
        '5xl': ['3.5rem', { lineHeight: '1.1' }],
        '6xl': ['4.5rem', { lineHeight: '1.1' }],
        '7xl': ['6rem', { lineHeight: '1.1' }],
        '8xl': ['8rem', { lineHeight: '1.1' }],
        '9xl': ['10rem', { lineHeight: '1' }],
      },
      letterSpacing: {
        tightest: '-0.06em',
        tighter: '-0.04em',
        tight: '-0.02em',
        normal: '-0.01em',
        wide: '0.05em',
        wider: '0.1em',
        widest: '0.2em',
      },
      lineHeight: {
        none: '1',
        tight: '1.1',
        snug: '1.25',
        normal: '1.6',
        relaxed: '1.75',
      },
      borderRadius: {
        none: '0px',
      },
      animation: {
        'reveal': 'reveal 500ms cubic-bezier(0.25, 0, 0, 1) both',
        'underline': 'underline 150ms cubic-bezier(0.25, 0, 0, 1)',
      },
      keyframes: {
        reveal: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        underline: {
          'from': { transform: 'scaleX(0)' },
          'to': { transform: 'scaleX(1)' },
        },
      },
      transitionDuration: {
        micro: '150ms',
        standard: '200ms',
        slow: '500ms',
      },
    },
  },
  corePlugins: {
    borderRadius: false,
  },
};
