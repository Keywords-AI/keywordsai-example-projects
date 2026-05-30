import type { Metadata } from "next";
import { Public_Sans } from "next/font/google";
import "./globals.css";

// Bold Typography stack: Public Sans for all typography
const publicSans = Public_Sans({ subsets: ["latin"], variable: "--font-sans", display: "swap" });

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
