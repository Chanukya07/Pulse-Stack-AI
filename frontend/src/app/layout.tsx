import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

import { ChatPanel } from "@/components/agents/chat-panel";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PulseStack AI",
  description: "Autonomous AI-Powered Observability Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        {children}
        <ChatPanel />
      </body>
    </html>
  );
}
