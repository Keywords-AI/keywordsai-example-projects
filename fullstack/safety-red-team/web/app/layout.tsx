import type { Metadata } from "next";
import { Public_Sans } from "next/font/google";
import "./globals.css";

// Public Sans carries all typography; the theme reads it via --font-public-sans.
const publicSans = Public_Sans({
  subsets: ["latin"],
  variable: "--font-public-sans",
  display: "swap",
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Respan Red-Team · LLM Safety Scorecard",
  description:
    "An LLM safety red-teaming report. Every model call routed and judged through the Respan gateway.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${publicSans.variable}`}>
      {/* suppressHydrationWarning: browser extensions (e.g. Grammarly) inject
          attributes on <body> after SSR, which would otherwise trip hydration. */}
      <body suppressHydrationWarning>
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
