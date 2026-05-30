import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

// Match Respan's stack: Inter for everything, JetBrains Mono for metrics/ids.
const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: "Respan Red-Team · LLM Safety Scorecard",
  description:
    "An LLM safety red-teaming report. Every model call routed and judged through the Respan gateway.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable}`}>
      <body>
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  );
}
