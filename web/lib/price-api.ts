import { findPriceRange, PriceRangeResult } from "./mock-price";

export type SourceHealth = {
  name: string;
  siteName: string;
  ok: boolean;
  candidates: number;
  elapsedMs: number;
  error?: string | null;
};

export type EnrichedPriceRangeResult = PriceRangeResult & {
  candidateCount: number;
  warnings: string[];
  sources: SourceHealth[];
  trustScore: number;
  spreadPercent: number;
  apiMode: "mock" | "api";
};

type ApiExtreme = {
  site_name: string;
  price: string | number;
  url?: string | null;
  title: string;
  confidence: number;
  availability?: string | null;
  source_name?: string | null;
};

type ApiSourceHealth = {
  name: string;
  site_name: string;
  ok: boolean;
  candidates: number;
  elapsed_ms?: number;
  error?: string | null;
};

type ApiPriceRangeResponse = {
  result: {
    item_name: string;
    cheapest?: ApiExtreme | null;
    most_expensive?: ApiExtreme | null;
    source_count: number;
    candidate_count?: number;
    sources?: ApiSourceHealth[];
    warnings?: string[];
  };
};

function checkedAtLabel() {
  return new Intl.DateTimeFormat("en-LK", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "short"
  }).format(new Date());
}

function toNumber(value: string | number) {
  return typeof value === "number" ? value : Number(value);
}

function spreadPercent(cheapest: number, mostExpensive: number) {
  if (cheapest <= 0) return 0;
  return Math.round(((mostExpensive - cheapest) / cheapest) * 100);
}

function trustScore(confidence: number, candidateCount: number, warningCount: number) {
  const candidateBoost = Math.min(0.18, candidateCount * 0.025);
  const warningPenalty = Math.min(0.2, warningCount * 0.08);
  return Math.max(0.12, Math.min(0.99, confidence + candidateBoost - warningPenalty));
}

function mapExtreme(extreme: ApiExtreme) {
  return {
    siteName: extreme.site_name,
    price: toNumber(extreme.price),
    url: extreme.url || "#",
    title: extreme.title,
    confidence: extreme.confidence,
    lastChecked: checkedAtLabel(),
    matchReason: extreme.source_name ? `Matched through ${extreme.source_name}` : extreme.availability || "Adapter result"
  };
}

function enrichMockResult(result: PriceRangeResult, warnings: string[] = []): EnrichedPriceRangeResult {
  const candidateCount = result.sourceCount;
  return {
    ...result,
    candidateCount,
    warnings,
    sources: [
      { name: "demo-catalog", siteName: "Demo catalog", ok: true, candidates: candidateCount, elapsedMs: 0 }
    ],
    trustScore: trustScore(result.confidence, candidateCount, warnings.length),
    spreadPercent: spreadPercent(result.cheapest.price, result.mostExpensive.price),
    apiMode: "mock"
  };
}

export async function findPriceRangeFromApi(itemName: string): Promise<EnrichedPriceRangeResult> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!baseUrl) {
    return enrichMockResult(await findPriceRange(itemName));
  }

  try {
    const response = await fetch(`${baseUrl.replace(/\/$/, "")}/price-range`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_name: itemName, max_candidates: 20, live: process.env.NEXT_PUBLIC_ENABLE_LIVE_SCRAPING === "true" }),
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Price API failed with ${response.status}`);
    }

    const payload = (await response.json()) as ApiPriceRangeResponse;
    const result = payload.result;
    if (!result.cheapest || !result.most_expensive) {
      return enrichMockResult(await findPriceRange(itemName), result.warnings ?? ["API returned no matching price extremes."]);
    }

    const cheapest = mapExtreme(result.cheapest);
    const mostExpensive = mapExtreme(result.most_expensive);
    const warnings = result.warnings ?? [];
    const candidateCount = result.candidate_count ?? 0;
    const confidence = Math.min(0.98, (result.cheapest.confidence + result.most_expensive.confidence) / 2);

    return {
      itemName: result.item_name,
      cheapest,
      mostExpensive,
      sourceCount: result.source_count,
      checkedAt: checkedAtLabel(),
      confidence,
      status: candidateCount > 0 ? "matched" : "fallback",
      candidateCount,
      warnings,
      sources: (result.sources ?? []).map((source) => ({
        name: source.name,
        siteName: source.site_name,
        ok: source.ok,
        candidates: source.candidates,
        elapsedMs: source.elapsed_ms ?? 0,
        error: source.error
      })),
      trustScore: trustScore(confidence, candidateCount, warnings.length),
      spreadPercent: spreadPercent(cheapest.price, mostExpensive.price),
      apiMode: "api"
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown API failure";
    return enrichMockResult(await findPriceRange(itemName), [`Using demo fallback because the API is unreachable: ${message}`]);
  }
}
