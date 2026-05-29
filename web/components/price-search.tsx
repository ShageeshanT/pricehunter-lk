"use client";

import {
  ActionIcon,
  Badge,
  Box,
  Button,
  Card,
  Collapse,
  Container,
  Group,
  Loader,
  Paper,
  Progress,
  RingProgress,
  SimpleGrid,
  Skeleton,
  Stack,
  Text,
  TextInput,
  ThemeIcon,
  Tooltip
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconChevronDown, IconClock, IconCopy, IconExternalLink, IconSearch, IconShieldCheck, IconSparkles, IconTrendingDown, IconTrendingUp } from "@tabler/icons-react";
import { FormEvent, useState } from "react";
import { findPriceRange, PriceRangeResult } from "@/lib/mock-price";

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
          <Text size="sm" c="dimmed">Confidence is based on item-token overlap in the current MVP. Real adapters will add stronger validation.</Text>
        </Paper>
      </Collapse>
    </Card>
  );
}

export function PriceSearch() {
  const [item, setItem] = useState("wireless mouse");
  const [result, setResult] = useState<PriceRangeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!item.trim()) return;
    setLoading(true);
    setProgress(18);
    const timer = window.setInterval(() => {
      setProgress((value) => Math.min(value + 18, 92));
    }, 140);
    const next = await findPriceRange(item.trim());
    window.clearInterval(timer);
    setProgress(100);
    setResult(next);
    setLoading(false);
    window.setTimeout(() => setProgress(0), 420);
    notifications.show({
      title: "Price range found",
      message: `Found cheapest and most expensive matches for ${item.trim()}.`,
      color: "lime",
      icon: <IconShieldCheck size={18} />
    });
  }

  async function copySummary() {
    if (!result) return;
    const text = `${result.itemName}\nCheapest: ${result.cheapest.siteName} ${money(result.cheapest.price)}\nMost expensive: ${result.mostExpensive.siteName} ${money(result.mostExpensive.price)}`;
    await navigator.clipboard.writeText(text);
    notifications.show({ title: "Copied", message: "Price summary copied.", color: "lime", icon: <IconCopy size={18} /> });
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
        <Badge size="lg" radius="xl" variant="outline" color="gray">Smooth Mantine UI</Badge>
        <Badge size="lg" radius="xl" variant="outline" color="gray">Sri Lanka focused</Badge>
      </Group>

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
              <ActionIcon size="xl" radius="xl" variant="light" color="lime" onClick={copySummary}>
                <IconCopy size={20} />
              </ActionIcon>
            </Group>
          </Group>
          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
            <PriceCard label="Cheapest found" icon={<IconTrendingDown size={21} />} result={result.cheapest} tone="cheap" />
            <PriceCard label="Most expensive" icon={<IconTrendingUp size={21} />} result={result.mostExpensive} tone="high" />
          </SimpleGrid>
        </Box>
      )}
    </Container>
  );
}
