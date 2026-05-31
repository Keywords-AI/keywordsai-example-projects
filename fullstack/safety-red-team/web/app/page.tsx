import { StatusBar } from "@/components/StatusBar";
import { Hero } from "@/components/Hero";
import { Method } from "@/components/Method";
import { Findings } from "@/components/Findings";
import { Leaderboard } from "@/components/Leaderboard";
import { ThreatMatrix } from "@/components/ThreatMatrix";
import { AttackVectors } from "@/components/AttackVectors";
import { TraceLog } from "@/components/TraceLog";
import { Footer } from "@/components/Footer";

export default function Page() {
  return (
    <>
      <StatusBar />
      <main className="mx-auto max-w-5xl px-6 sm:px-12 lg:px-16 pb-12 space-y-0">
        <Hero />
        <Method />
        <Findings />
        <Leaderboard />
        <ThreatMatrix />
        <AttackVectors />
        <TraceLog />
      </main>
      <Footer />
    </>
  );
}
