import { Badge, Box, Card, Group, SimpleGrid, Stack, Text, ThemeIcon } from "@mantine/core";
import { IconBolt, IconDeviceMobile, IconGauge, IconShieldCheck } from "@tabler/icons-react";

const features = [
  {
    title: "Instant extremes",
    text: "The interface is tuned around one answer pair: cheapest and most expensive.",
    icon: IconBolt
  },
  {
    title: "Smooth feedback",
    text: "Skeleton cards, toasts, hover lift, focus rings, and animated reveal states are wired in.",
    icon: IconGauge
  },
  {
    title: "Trust cues",
    text: "Confidence, source count, checked time, and proof panels make the mock MVP feel honest.",
    icon: IconShieldCheck
  },
  {
    title: "Mobile first",
    text: "The search form, result grid, and buttons collapse cleanly for phones.",
    icon: IconDeviceMobile
  }
];

export function PhaseOneShowcase() {
  return (
    <Box className="phase-strip" mx="auto" maw={1180} px={{ base: 16, sm: 24 }} pb={96}>
      <Group justify="space-between" mb="xl" align="end">
        <Stack gap={4}>
          <Badge color="lime" variant="light" radius="xl">Phase 1 complete</Badge>
          <Text size="38px" fw={950} lh={1.05} c="white">Premium MVP shell</Text>
        </Stack>
        <Text maw={420} c="dimmed" size="sm">
          This phase makes PriceHunter LK feel like a real product before the search adapters get upgraded in Phase 2.
        </Text>
      </Group>

      <SimpleGrid cols={{ base: 1, sm: 2, lg: 4 }} spacing="md">
        {features.map((feature) => (
          <Card key={feature.title} className="phase-card" radius="28px" p="lg" withBorder>
            <ThemeIcon size="xl" radius="xl" color="lime" variant="light" mb="lg">
              <feature.icon size={22} />
            </ThemeIcon>
            <Text fw={900} size="lg" c="white">{feature.title}</Text>
            <Text mt="xs" size="sm" c="dimmed" lh={1.65}>{feature.text}</Text>
          </Card>
        ))}
      </SimpleGrid>
    </Box>
  );
}
