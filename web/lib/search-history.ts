import { EnrichedPriceRangeResult } from "./price-api";

export type SearchHistoryItem = {
  id: string;
  itemName: string;
  checkedAt: string;
  cheapestSite: string;
  cheapestPrice: number;
  mostExpensiveSite: string;
  mostExpensivePrice: number;
  trustScore: number;
  spreadPercent: number;
  sourceCount: number;
};

const STORAGE_KEY = "pricehunter.lk.searchHistory.v1";

export function toHistoryItem(result: EnrichedPriceRangeResult): SearchHistoryItem {
  return {
    id: `${result.itemName}-${Date.now()}`,
    itemName: result.itemName,
    checkedAt: result.checkedAt,
    cheapestSite: result.cheapest.siteName,
    cheapestPrice: result.cheapest.price,
    mostExpensiveSite: result.mostExpensive.siteName,
    mostExpensivePrice: result.mostExpensive.price,
    trustScore: result.trustScore,
    spreadPercent: result.spreadPercent,
    sourceCount: result.sourceCount
  };
}

export function readSearchHistory(): SearchHistoryItem[] {
  if (typeof window === "undefined") return [];
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];

  try {
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item) => typeof item?.itemName === "string").slice(0, 8) as SearchHistoryItem[];
  } catch {
    return [];
  }
}

export function saveSearchHistory(items: SearchHistoryItem[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items.slice(0, 8)));
}

export function addSearchHistory(result: EnrichedPriceRangeResult) {
  const nextItem = toHistoryItem(result);
  const existing = readSearchHistory().filter((item) => item.itemName.toLowerCase() !== result.itemName.toLowerCase());
  const next = [nextItem, ...existing].slice(0, 8);
  saveSearchHistory(next);
  return next;
}
