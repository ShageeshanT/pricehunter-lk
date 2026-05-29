export type PriceExtreme = {
  siteName: string;
  price: number;
  url: string;
  title: string;
  confidence: number;
  lastChecked: string;
  matchReason: string;
};

export type PriceRangeResult = {
  itemName: string;
  cheapest: PriceExtreme;
  mostExpensive: PriceExtreme;
  sourceCount: number;
  checkedAt: string;
  confidence: number;
  status: "matched" | "fallback";
};

const products = [
  { siteName: "Daraz LK", title: "Wireless mouse", price: 1450, url: "https://www.daraz.lk", keywords: ["wireless", "mouse"], source: "Marketplace listing" },
  { siteName: "SimplyTek", title: "Premium wireless mouse", price: 5850, url: "https://www.simplytek.lk", keywords: ["wireless", "mouse", "premium"], source: "Tech store listing" },
  { siteName: "Redline", title: "Gaming mouse", price: 7200, url: "https://redlinetech.lk", keywords: ["gaming", "mouse"], source: "Gaming store listing" },
  { siteName: "Daraz LK", title: "A4 file", price: 80, url: "https://www.daraz.lk", keywords: ["a4", "file"], source: "Marketplace listing" },
  { siteName: "OfficeMart", title: "Plastic A4 file", price: 140, url: "https://example.lk", keywords: ["a4", "file", "plastic"], source: "Office supply listing" },
  { siteName: "Singer", title: "Bluetooth speaker", price: 6490, url: "https://www.singer.lk", keywords: ["bluetooth", "speaker"], source: "Retail listing" },
  { siteName: "Abans", title: "Portable bluetooth speaker", price: 18990, url: "https://www.buyabans.com", keywords: ["bluetooth", "speaker", "portable"], source: "Retail listing" },
  { siteName: "Apple Asia", title: "USB C iPhone charger", price: 4900, url: "https://example.lk/charger", keywords: ["iphone", "charger", "usb", "c"], source: "Accessory listing" },
  { siteName: "Premium Mobile", title: "Original fast iPhone charger", price: 11900, url: "https://example.lk/premium-charger", keywords: ["iphone", "charger", "fast", "original"], source: "Accessory listing" },
  { siteName: "KitchenWorld", title: "1.8L rice cooker", price: 8650, url: "https://example.lk/rice-cooker", keywords: ["rice", "cooker"], source: "Home appliance listing" },
  { siteName: "Singer", title: "Premium fuzzy logic rice cooker", price: 32990, url: "https://www.singer.lk", keywords: ["rice", "cooker", "premium"], source: "Home appliance listing" }
];

function tokens(value: string) {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter(Boolean);
}

function score(itemName: string, keywords: string[]) {
  const query = tokens(itemName);
  const matches = query.filter((token) => keywords.includes(token)).length;
  return matches / Math.max(query.length, 1);
}

function nowLabel() {
  return new Intl.DateTimeFormat("en-LK", {
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "short"
  }).format(new Date());
}

function toExtreme(product: (typeof products)[number] & { confidence: number }, itemName: string): PriceExtreme {
  return {
    siteName: product.siteName,
    price: product.price,
    url: product.url,
    title: product.title,
    confidence: product.confidence,
    lastChecked: nowLabel(),
    matchReason: product.confidence >= 0.9 ? "Strong title match" : product.confidence >= 0.5 ? "Partial keyword match" : `Demo fallback for ${itemName}`
  };
}

export async function findPriceRange(itemName: string): Promise<PriceRangeResult> {
  await new Promise((resolve) => setTimeout(resolve, 720));
  const matches = products
    .map((product) => ({ ...product, confidence: score(itemName, product.keywords) }))
    .filter((product) => product.confidence > 0)
    .sort((a, b) => a.price - b.price);

  const fallback = [
    { siteName: "Shop A", title: `${itemName} economy listing`, price: 1250, url: "https://example.lk/a", confidence: 0.45, keywords: tokens(itemName), source: "Demo source" },
    { siteName: "Shop B", title: `${itemName} premium listing`, price: 4890, url: "https://example.lk/b", confidence: 0.42, keywords: tokens(itemName), source: "Demo source" }
  ];

  const finalMatches = matches.length >= 2 ? matches : fallback;
  const cheapest = finalMatches[0];
  const mostExpensive = finalMatches[finalMatches.length - 1];
  const confidence = Math.min(0.98, (cheapest.confidence + mostExpensive.confidence) / 2);

  return {
    itemName,
    cheapest: toExtreme(cheapest, itemName),
    mostExpensive: toExtreme(mostExpensive, itemName),
    sourceCount: finalMatches.length,
    checkedAt: nowLabel(),
    confidence,
    status: matches.length >= 2 ? "matched" : "fallback"
  };
}
