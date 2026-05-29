"use client";

import {
  ActionIcon,
  Alert,
  Badge,
  Box,
  Button,
  Card,
  Collapse,
  Container,
  Divider,
  Group,
  Loader,
  Paper,
  Progress,
  RingProgress,
  SegmentedControl,
  SimpleGrid,
  Skeleton,
  Stack,
  Tabs,
  Text,
  TextInput,
  ThemeIcon,
  Tooltip
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
  IconBell,
  IconChevronDown,
  IconClock,
  IconCopy,
  IconExternalLink,
  IconHistory,
  IconLink,
  IconSearch,
  IconShieldCheck,
  IconSparkles,
  IconTrendingDown,
  IconTrendingUp
} from "@tabler/icons-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { PriceRangeResult } from "@/lib/mock-price";
import { EnrichedPriceRangeResult, findPriceRangeFromApi } from "@/lib/price-api";
import { addSearchHistory, readSearchHistory, SearchHistoryItem } from "@/lib/search-history";

const popularItems = ["wireless mouse", "A4 file", "bluetooth speaker", "iPhone charger", "rice cooker", "gaming mouse"];
const storeFilters = ["All stores", "Daraz", "Singer", "SimplyTek", "Abans", "Redline"];
const categoryFilters = ["All categories", "Tech", "Office", "Home", "Mobile"];

function money(value: number) {
  return new Intl.NumberFormat("en-LK", { style: "currency", currency: "LKR", maximumFractionDigits: 0 }).format(value);
}

function PriceCard({ label, icon, result, tone }: { label: string; icon: React.ReactNode; result: NonNullable<PriceRangeResult["cheapest"]>; tone: "cheap" | "high" }) {
  const [open, setOpen] = useState(false);
  const accent = tone === "cheap" ? "#c8ff65" : "#ff6b35";

  return (
    <Card className="result-card" radius="32px" p="xl" withBorder>
      <Box className="result-card-bar" style={{ background: accent }} />
      <Group justify="space-between" align="flex-start" mb="xl">
        <Group gap="sm">
          <ThemeIcon size="lg" radius="xl" variant="light" color={tone === "cheap" ? "lime" : "orange"}>
            {icon}
          </ThemeIcon>
          <Box>
            <Text size="xs" fw={900} tt="uppercase" className="tracking-label">
              {label}
            </Text>
            <Text size="sm" c="dimmed">Best extreme match</Text>
          </Box>
        </Group>
        <RingProgress
          size={58}
          thickness={6}
          sections={[{ value: Math.round(result.confidence * 100), color: tone === "cheap" ? "lime" : "orange" }]}
          label={<Text ta="center" size="xs" fw={800}>{Math.round(result.confidence * 100)}%</Text>}
        />
      </Group>

      <Stack gap="xs">
        <Text size="28px" fw={950} lh={1} c="white">{result.siteName}</Text>
        <Text size="sm" c="dimmed" mih={44}>{result.title}</Text>
        <Text size="44px" fw={950} lh={1.05} c="white" mt="md">{money(result.price)}</Text>
      </Stack>

      <Group mt="xl" justify="space-between">
        <Button component="a" href={result.url} target="_blank" rel="noreferrer" color="lime" c="dark" fw={900} rightSection={<IconExternalLink size={16} />}>
          Visit site
        </Button>
        <Tooltip label="Show proof details">
          <ActionIcon size="lg" radius="xl" variant="subtle" color="gray" onClick={() => setOpen((value) => !value)}>
            <IconChevronDown className={open ? "rotate-180 transition" : "transition"} size={18} />
          </ActionIcon>
        </Tooltip>
      </Group>

      <Collapse in={open}>
        <Paper mt="lg" p="md" radius="xl" className="proof-panel">
          <Text size="xs" c="dimmed" tt="uppercase" fw={800}>Proof</Text>
          <Text size="sm" mt={6}>Source URL: {result.url}</Text>
          <Text size="sm" c="dimmed">{result.matchReason}. Last checked {result.lastChecked}.</Text>
          <Text size="sm" c="dimmed">Confidence is based on item-token overlap plus adapter metadata in the current MVP.</Text>
        </Paper>
      </Collapse>
    </Card>
  );
}

function HistoryPanel({ history, onPick }: { history: SearchHistoryItem[]; onPick: (item: string) => void }) {
  if (history.length === 0) {
    return <Text size="sm" c="dimmed">No recent hunts yet. Search once and this panel stops looking unemployed.</Text>;
  }

  return (
    <Stack gap="sm">
      {history.map((entry) => (
        <Paper key={entry.id} p="md" radius="xl" className="mini-panel" onClick={() => onPick(entry.itemName)}>
          <Group justify="space-between" align="center">
            <Box>
              <Text fw={850} c="white">{entry.itemName}</Text>
              <Text size="xs" c="dimmed">{entry.cheapestSite} to {entry.mostExpensiveSite} • {entry.sourceCount} sources • {entry.checkedAt}</Text>
            </Box>
            <Box ta="right">
              <Text size="sm" fw={900} c="lime">{money(entry.cheapestPrice)}</Text>
              <Text size="xs" c="orange">{money(entry.mostExpensivePrice)}</Text>
            </Box>
          </Group>
        </Paper>
      ))}
    </Stack>
  );
}

export function PriceSearch() {
  const [item, setItem] = useState("wireless mouse");
  const [result, setResult] = useState<EnrichedPriceRangeResult | null>(null);
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [store, setStore] = useState("All stores");
  const [category, setCategory] = useState("All categories");

  useEffect(() => {
    setHistory(readSearchHistory());
  }, []);

  const summaryText = useMemo(() => {
    if (!result) return "";
    return `${result.itemName}\nCheapest: ${result.cheapest.siteName} ${money(result.cheapest.price)}\nMost expensive: ${result.mostExpensive.siteName} ${money(result.mostExpensive.price)}\nSpread: ${result.spreadPercent}%\nTrust: ${Math.round(result.trustScore * 100)}%`;
  }, [result]);

  async function onSubmit(event?: FormEvent) {
    event?.preventDefault();
    await runSearch(item);
  }

  async function writeClipboard(value: string, successTitle: string, successMessage: string) {
    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error("Clipboard API is unavailable on this browser.");
      }
      await navigator.clipboard.writeText(value);
      notifications.show({ title: successTitle, message: successMessage, color: "lime", icon: <IconCopy size={18} /> });
    } catch (error) {
      notifications.show({
        title: "Copy failed",
        message: error instanceof Error ? error.message : "Your browser blocked clipboard access.",
        color: "yellow",
        icon: <IconShieldCheck size={18} />
      });
    }
  }

  async function copySummary() {
    if (!summaryText) return;
    await writeClipboard(summaryText, "Copied", "Price summary copied.");
  }

  async function copyShareLink() {
    const url = new URL(window.location.href);
    url.searchParams.set("q", result?.itemName || item);
    await writeClipboard(url.toString(), "Share link copied", "Anyone can reopen this search query.");
  }

  async function runSearch(nextItem = item) {
    const cleanItem = nextItem.trim();
    if (!cleanItem) return;
    setLoading(true);
    setProgress(18);
    const timer = window.setInterval(() => {
      setProgress((value) => Math.min(value + 18, 92));
    }, 140);

    try {
      const next = await findPriceRangeFromApi(cleanItem);
      setProgress(100);
      setResult(next);
      setHistory(addSearchHistory(next));
      notifications.show({
        title: "Price range found",
        message: `Found cheapest and most expensive matches for ${cleanItem}.`,
        color: "lime",
        icon: <IconShieldCheck size={18} />
      });
    } catch (error) {
      notifications.show({
        title: "Search failed",
        message: error instanceof Error ? error.message : "Could not complete this search.",
        color: "red",
        icon: <IconShieldCheck size={18} />
      });
    } finally {
      window.clearInterval(timer);
      setLoading(false);
      window.setTimeout(() => setProgress(0), 420);
    }
  }

  function pickItem(nextItem: string) {
    setItem(nextItem);
    void runSearch(nextItem);
  }

  return (
    <Container size="lg" pb={96} pt={24}>
      <Paper className="search-shell" radius="32px" p="sm" shadow="xl" withBorder>
        <form onSubmit={onSubmit}>
          <Group gap="sm" align="stretch">
            <TextInput
              className="search-input"
              flex={1}
              size="xl"
              radius="24px"
              leftSection={<IconSearch size={22} />}
              value={item}
              onChange={(event) => setItem(event.currentTarget.value)}
              placeholder="Type anything. iPhone charger, rice cooker, A4 file..."
            />
            <Button type="submit" size="xl" radius="24px" color="lime" c="dark" fw={950} leftSection={loading ? <Loader size="sm" color="dark" /> : <IconSparkles size={22} />} disabled={loading}>
              Hunt price
            </Button>
          </Group>
        </form>
        {loading && <Progress value={progress} color="lime" radius="xl" size="sm" mt="sm" className="search-progress" />}
      </Paper>

      <Group mt="md" gap="sm">
        <Badge size="lg" radius="xl" variant="light" color="lime" leftSection={<IconShieldCheck size={14} />}>Shows extremes only</Badge>
        <Badge size="lg" radius="xl" variant="outline" color="gray">History and share links</Badge>
        <Badge size="lg" radius="xl" variant="outline" color="gray">Sri Lanka focused</Badge>
      </Group>

      <Tabs defaultValue="popular" variant="pills" radius="xl" mt="xl" classNames={{ panel: "phase-tabs-panel" }}>
        <Tabs.List>
          <Tabs.Tab value="popular" leftSection={<IconSparkles size={16} />}>Popular</Tabs.Tab>
          <Tabs.Tab value="filters" leftSection={<IconShieldCheck size={16} />}>Filters</Tabs.Tab>
          <Tabs.Tab value="history" leftSection={<IconHistory size={16} />}>History</Tabs.Tab>
          <Tabs.Tab value="alerts" leftSection={<IconBell size={16} />}>Alerts</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="popular" pt="md">
          <Group gap="sm">
            {popularItems.map((popular) => (
              <Button key={popular} radius="xl" variant="light" color="gray" onClick={() => pickItem(popular)}>{popular}</Button>
            ))}
          </Group>
        </Tabs.Panel>

        <Tabs.Panel value="filters" pt="md">
          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="md">
            <Paper p="md" radius="xl" className="mini-panel">
              <Text size="xs" tt="uppercase" fw={900} c="dimmed" mb="xs">Store filter placeholder</Text>
              <SegmentedControl fullWidth value={store} onChange={setStore} data={storeFilters} />
            </Paper>
            <Paper p="md" radius="xl" className="mini-panel">
              <Text size="xs" tt="uppercase" fw={900} c="dimmed" mb="xs">Category filter placeholder</Text>
              <SegmentedControl fullWidth value={category} onChange={setCategory} data={categoryFilters} />
            </Paper>
          </SimpleGrid>
        </Tabs.Panel>

        <Tabs.Panel value="history" pt="md">
          <HistoryPanel history={history} onPick={pickItem} />
        </Tabs.Panel>

        <Tabs.Panel value="alerts" pt="md">
          <Alert color="lime" radius="xl" icon={<IconBell size={18} />} className="mini-panel">
            Price alerts are staged for the production phase. The UI is ready for target price tracking once background jobs and user accounts land.
          </Alert>
        </Tabs.Panel>
      </Tabs>

      {loading && (
        <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg" mt={40}>
          <Skeleton height={330} radius="32px" />
          <Skeleton height={330} radius="32px" />
        </SimpleGrid>
      )}

      {result && !loading && (
        <Box mt={42} className="fade-in-up">
          <Group justify="space-between" align="end" mb="md">
            <Box>
              <Text size="xs" tt="uppercase" c="dimmed" fw={900} className="tracking-label">Results for</Text>
              <Text size="36px" fw={950} c="white" lh={1.1}>{result.itemName}</Text>
            </Box>
            <Group>
              <Badge size="xl" radius="xl" variant="light" color={result.status === "matched" ? "lime" : "yellow"}>{result.status === "matched" ? "Matched" : "Demo fallback"}</Badge>
              <Badge size="xl" radius="xl" variant="light" color="gray">{result.sourceCount} sources scanned</Badge>
              <Badge size="xl" radius="xl" variant="outline" color="gray" leftSection={<IconClock size={14} />}>{result.checkedAt}</Badge>
              <ActionIcon size="xl" radius="xl" variant="light" color="lime" onClick={copySummary} aria-label="Copy summary">
                <IconCopy size={20} />
              </ActionIcon>
              <ActionIcon size="xl" radius="xl" variant="light" color="gray" onClick={copyShareLink} aria-label="Copy share link">
                <IconLink size={20} />
              </ActionIcon>
            </Group>
          </Group>

          <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md" mb="lg">
            <Paper p="lg" radius="xl" className="mini-panel">
              <Text size="xs" tt="uppercase" c="dimmed" fw={900}>Trust score</Text>
              <Text size="32px" fw={950} c="lime">{Math.round(result.trustScore * 100)}%</Text>
              <Text size="xs" c="dimmed">Confidence plus source coverage minus warnings.</Text>
            </Paper>
            <Paper p="lg" radius="xl" className="mini-panel">
              <Text size="xs" tt="uppercase" c="dimmed" fw={900}>Price spread</Text>
              <Text size="32px" fw={950} c="orange">{result.spreadPercent}%</Text>
              <Text size="xs" c="dimmed">How much higher the expensive match is than the cheapest.</Text>
            </Paper>
            <Paper p="lg" radius="xl" className="mini-panel">
              <Text size="xs" tt="uppercase" c="dimmed" fw={900}>Candidates</Text>
              <Text size="32px" fw={950} c="white">{result.candidateCount}</Text>
              <Text size="xs" c="dimmed">Adapter candidates after dedupe and filtering.</Text>
            </Paper>
          </SimpleGrid>

          {result.warnings.length > 0 && (
            <Alert mb="lg" color="yellow" radius="xl" className="mini-panel">
              {result.warnings.join(" ")}
            </Alert>
          )}

          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
            <PriceCard label="Cheapest found" icon={<IconTrendingDown size={21} />} result={result.cheapest} tone="cheap" />
            <PriceCard label="Most expensive" icon={<IconTrendingUp size={21} />} result={result.mostExpensive} tone="high" />
          </SimpleGrid>

          {result.sources.length > 0 && (
            <Paper mt="lg" p="lg" radius="32px" className="mini-panel">
              <Group justify="space-between" mb="md">
                <Box>
                  <Text size="xs" tt="uppercase" c="dimmed" fw={900}>Source health</Text>
                  <Text fw={900} c="white">Live adapter readiness</Text>
                </Box>
                <Badge radius="xl" variant="light" color={result.apiMode === "api" ? "lime" : "gray"}>{result.apiMode === "api" ? "API" : "Demo"}</Badge>
              </Group>
              <Divider mb="md" opacity={0.18} />
              <SimpleGrid cols={{ base: 1, md: 2 }} spacing="sm">
                {result.sources.map((source) => (
                  <Group key={source.name} justify="space-between" className="source-row">
                    <Box>
                      <Text size="sm" fw={850} c="white">{source.siteName}</Text>
                      <Text size="xs" c="dimmed">{source.ok ? "Healthy" : source.error || "Failed"}</Text>
                    </Box>
                    <Badge radius="xl" color={source.ok ? "lime" : "red"}>{source.candidates} candidates</Badge>
                  </Group>
                ))}
              </SimpleGrid>
            </Paper>
          )}
        </Box>
      )}
    </Container>
  );
}
