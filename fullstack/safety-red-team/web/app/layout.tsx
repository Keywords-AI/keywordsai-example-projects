import type { Metadata } from "next";
import { Inter, Inter_Tight, JetBrains_Mono } from "next/font/google";
import "./globals.css";

// Bold Typography stack: Inter for body, Inter Tight for headlines, JetBrains Mono for metrics
const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const interTight = Inter_Tight({ subsets: ["latin"], variable: "--font-sans-tight", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: "Respan Red-Team · LLM Safety Scorecard",
  description:
    "An LLM safety red-teaming report. Every model call routed and judged through the Respan gateway.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${interTight.variable} ${mono.variable}`}>
      {/* suppressHydrationWarning: browser extensions (e.g. Grammarly) inject
          attributes on <body> after SSR, which would otherwise trip hydration. */}
      <body suppressHydrationWarning>
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
