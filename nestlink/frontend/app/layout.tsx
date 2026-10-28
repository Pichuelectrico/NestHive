import type { Metadata } from "next";
import { Fira_Code, Fira_Sans } from "next/font/google";
import { ToastProvider } from "@/hooks/useToast";
import { ToastStack } from "@/components/ToastStack";
import "./globals.css";

const firaSans = Fira_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-fira-sans",
  display: "swap",
});

const firaCode = Fira_Code({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-fira-code",
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
    <html lang="es" className={`${firaSans.variable} ${firaCode.variable}`}>
      <body className="font-sans antialiased">
        <ToastProvider>
          {children}
          <ToastStack />
        </ToastProvider>
      </body>
    </html>
  );
}
