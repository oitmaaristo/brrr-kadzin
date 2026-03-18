"use client";

import { usePathname } from "next/navigation";

const TABS = [
  { href: "/", label: "Dashboard" },
  { href: "/filters", label: "Filtrid" },
  { href: "/listings", label: "Kuulutused" },
];

export function NavBar() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-3 sm:top-4 z-40 mx-auto max-w-5xl px-4 sm:px-6 fade-up">
      <div className="glass rounded-2xl px-4 sm:px-5 py-3 flex items-center justify-between">
        <a href="/" className="font-heading font-bold text-lg sm:text-xl tracking-tight text-white shrink-0">
          auto<span className="text-accent">.</span>radar
        </a>

        <div className="flex items-center gap-0.5 sm:gap-1">
          {TABS.map((tab) => {
            const isActive = pathname === tab.href;
            return (
              <a
                key={tab.href}
                href={tab.href}
                className={`px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-medium rounded-xl transition-all duration-500 ease-smooth ${
                  isActive
                    ? "text-accent bg-accent/10"
                    : "text-zinc-500 hover:text-white"
                }`}
              >
                {tab.label}
              </a>
            );
          })}
        </div>

        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-40" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-accent" />
          </span>
          <span className="text-[11px] text-zinc-600 hidden sm:inline">Jalgib</span>
        </div>
      </div>
    </nav>
  );
}
