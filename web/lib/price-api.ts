import { findPriceRange, PriceRangeResult } from "./mock-price";

type ApiExtreme = {
  site_name: string;
  price: string | number;
  url?: string | null;
  title: string;
  confidence: number;
  availability?: string | null;
  source_name?: string | null;
};

type ApiPriceRangeResponse = {
  result: {
    item_name: string;
    cheapest?: ApiExtreme | null;
    most_expensive?: ApiExtreme | null;
    source_count: number;
    candidate_count?: number;
    warnings?: string[];
  };
};

function toNumber(value: string | number) {
  return typeof value === "number" ? value : Number(value);
}

function mapExtreme(extreme: ApiExtreme) {
  return {
    siteName: extreme.site_name,
    price: toNumber(extreme.price),
    url: extreme.url || "#",
    title: extreme.title,
    confidence: extreme.confidence,
    lastChecked: new Intl.DateTimeFormat("en-LK", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "short" }).format(new Date()),
    matchReason: extreme.source_name ? `Matched through ${extreme.source_name}` : extreme.availability || "Adapter result"
  };
}

export async function findPriceRangeFromApi(itemName: string): Promise<PriceRangeResult> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!baseUrl) {
    return findPriceRange(itemName);
  }

  const response = await fetch(`${baseUrl.replace(/\/$/, "")}/price-range`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ item_name: itemName, max_candidates: 20 }),
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Price API failed with ${response.status}`);
  }

  const payload = (await response.json()) as ApiPriceRangeResponse;
  const result = payload.result;
  if (!result.cheapest || !result.most_expensive) {
    return findPriceRange(itemName);
  }

  return {
    itemName: result.item_name,
    cheapest: mapExtreme(result.cheapest),
    mostExpensive: mapExtreme(result.most_expensive),
    sourceCount: result.source_count,
    checkedAt: new Intl.DateTimeFormat("en-LK", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "short" }).format(new Date()),
    confidence: Math.min(0.98, (result.cheapest.confidence + result.most_expensive.confidence) / 2),
    status: result.candidate_count && result.candidate_count > 0 ? "matched" : "fallback"
  };
}
