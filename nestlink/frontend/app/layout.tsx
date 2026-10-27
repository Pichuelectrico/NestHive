import type { Metadata } from "next";
import { JetBrains_Mono, Outfit } from "next/font/google";
import { ToastProvider } from "@/hooks/useToast";
import { ToastStack } from "@/components/ToastStack";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "NestHive — Centro de Operaciones",
  description: "Orquestación intralogística AMR — Nestlé InnoLabs",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className={`${outfit.variable} ${jetbrains.variable}`}>
      <body className="font-sans antialiased">
        <ToastProvider>
          {children}
          <ToastStack />
        </ToastProvider>
      </body>
    </html>
  );
}
