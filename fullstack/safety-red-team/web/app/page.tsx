import { StatusBar } from "@/components/StatusBar";
import { Hero } from "@/components/Hero";
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
      <main className="mx-auto max-w-[1180px] px-5 pb-10 space-y-16">
        <Hero />
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
