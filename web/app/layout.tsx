import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";
import "./globals.css";
import { ColorSchemeScript, MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PriceHunter LK",
  description: "Find the cheapest and most expensive prices across Sri Lankan stores."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <ColorSchemeScript defaultColorScheme="dark" />
      </head>
      <body className={inter.className}>
        <MantineProvider
          defaultColorScheme="dark"
          theme={{
            primaryColor: "lime",
            defaultRadius: "xl",
            fontFamily: inter.style.fontFamily,
            colors: {
              lime: ["#f8ffe9", "#ecffd0", "#d8ffa1", "#c8ff65", "#b3f542", "#9cdd2c", "#79ad1e", "#5b8319", "#405d13", "#293d0b"]
            }
          }}
        >
          <Notifications position="top-right" />
          {children}
        </MantineProvider>
      </body>
    </html>
  );
}
