import { ArrowUpRight, Gauge, Globe2, Zap } from "lucide-react";
import { PriceSearch } from "@/components/price-search";
import { PhaseOneShowcase } from "@/components/phase-one-showcase";

export default function Home() {
  return (
    <main className="price-grid min-h-screen overflow-hidden bg-ink">
      <div className="pointer-events-none fixed left-1/2 top-0 h-[32rem] w-[32rem] -translate-x-1/2 rounded-full bg-limeglow/10 blur-3xl" />
      <div className="pointer-events-none fixed right-0 top-24 h-[24rem] w-[24rem] rounded-full bg-ember/10 blur-3xl" />

      <nav className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-limeglow font-black text-ink shadow-glow">PH</div>
          <div>
            <p className="text-lg font-black tracking-tight text-white">PriceHunter LK</p>
            <p className="text-xs text-slate-500">Find the price extremes</p>
          </div>
        </div>
        <a href="https://github.com/ShageeshanT/pricehunter-lk" target="_blank" rel="noreferrer" className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-white/10 sm:inline-flex">
          GitHub <ArrowUpRight className="h-4 w-4" />
        </a>
      </nav>

      <section className="relative z-10 mx-auto max-w-6xl px-4 pb-10 pt-12 text-center sm:px-6 lg:px-8">
        <div className="mx-auto mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.06] px-4 py-2 text-sm font-semibold text-slate-300 backdrop-blur-xl">
          <Zap className="h-4 w-4 text-limeglow" /> Type item. Get cheapest and highest. Done.
        </div>
        <h1 className="mx-auto max-w-5xl text-5xl font-black tracking-[-0.05em] text-white sm:text-7xl lg:text-8xl">
          Find the cheapest and most expensive price in seconds.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-400">
          PriceHunter LK scans configured ecommerce-style sources and returns the only two answers people actually want: where it is cheapest, and where it is painfully overpriced.
        </p>
        <div className="mt-8 grid gap-3 sm:grid-cols-3">
          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 text-left backdrop-blur-xl">
            <Globe2 className="mb-4 h-6 w-6 text-limeglow" />
            <p className="font-bold text-white">Multi-site search</p>
            <p className="mt-1 text-sm text-slate-500">Built for Sri Lankan stores and ecommerce sources.</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 text-left backdrop-blur-xl">
            <Gauge className="mb-4 h-6 w-6 text-limeglow" />
            <p className="font-bold text-white">No clutter</p>
            <p className="mt-1 text-sm text-slate-500">Only min and max price. The rest can stay in spreadsheet jail.</p>
          </div>
          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 text-left backdrop-blur-xl">
            <Zap className="mb-4 h-6 w-6 text-limeglow" />
            <p className="font-bold text-white">Agent-ready</p>
            <p className="mt-1 text-sm text-slate-500">Backend API is already shaped for real search adapters.</p>
          </div>
        </div>
      </section>

      <PriceSearch />
      <PhaseOneShowcase />
    </main>
  );
}
