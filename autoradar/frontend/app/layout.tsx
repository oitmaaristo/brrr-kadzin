import type { Metadata } from "next";
import "./globals.css";
import { NavBar } from "./navbar";

export const metadata: Metadata = {
  title: "Autoradar",
  description: "Kasutatud autode kuulutuste monitor",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="et">
      <body className="grain min-h-screen overflow-x-hidden">
        {/* Ambient glow orbs */}
        <div className="glow-orb w-96 h-96 bg-emerald-500/5 -top-48 -right-48" />
        <div className="glow-orb w-80 h-80 bg-cyan-500/[0.04] bottom-0 left-0" />

        <NavBar />
        <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 sm:py-12 relative z-10">
          {children}
        </main>
      </body>
    </html>
  );
}
