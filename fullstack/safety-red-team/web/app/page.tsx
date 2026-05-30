import { StatusBar } from "@/components/StatusBar";
import { Hero } from "@/components/Hero";
import { Findings } from "@/components/Findings";

export default function Page() {
  return (
    <>
      <StatusBar />
      <main className="mx-auto max-w-[1180px] px-5 pb-24 space-y-16">
        <Hero />
        <Findings />
      </main>
    </>
  );
}
