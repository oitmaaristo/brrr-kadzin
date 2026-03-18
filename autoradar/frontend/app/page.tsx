"use client";

import { useEffect, useState } from "react";
import type { Listing, Stats } from "@/lib/api";
import { ListingCard, type PriceHistory } from "./components/listing-card";

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentListings, setRecentListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [priceHistory, setPriceHistory] = useState<PriceHistory[]>([]);

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, listingsRes] = await Promise.all([
          fetch("/api/stats").then((r) => r.json()),
          fetch("/api/listings?limit=10").then((r) => r.json()),
        ]);
        setStats(statsRes);
        setRecentListings(listingsRes);
      } catch {
        // API not available yet
      }
      setLoading(false);
    }
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  async function toggleExpand(listingId: number) {
    if (expandedId === listingId) {
      setExpandedId(null);
      setPriceHistory([]);
      return;
    }
    setExpandedId(listingId);
    try {
      const res = await fetch(`/api/listings/${listingId}/price-history`);
      if (res.ok) {
        setPriceHistory(await res.json());
      }
    } catch {
      setPriceHistory([]);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 fade-up">
        <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 sm:space-y-12">
      {/* Stats — Asymmetric Bento Grid (desktop) */}
      <section className="hidden sm:block fade-up fade-up-d1">
        <div className="grid grid-cols-12 gap-3">
          {/* Big stat */}
          <div className="col-span-5 row-span-2 doppel">
            <div className="doppel-inner h-full p-8 flex flex-col justify-between">
              <span className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-medium">
                Kuulutusi kokku
              </span>
              <div>
                <span className="text-6xl font-heading font-extrabold text-white tracking-tight nums">
                  {(stats?.total_listings ?? 0).toLocaleString("et-EE")}
                </span>
              </div>
            </div>
          </div>

          {/* Small stats */}
          <div className="col-span-4 doppel">
            <div className="doppel-inner p-6">
              <span className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-medium">
                Teavitusi saadetud
              </span>
              <div className="text-3xl font-heading font-bold text-white mt-3 tracking-tight nums">
                {(stats?.total_notified ?? 0).toLocaleString("et-EE")}
              </div>
            </div>
          </div>

          <div className="col-span-3 doppel">
            <div className="doppel-inner p-6">
              <span className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-medium">
                Aktiivseid filtreid
              </span>
              <div className="text-3xl font-heading font-bold text-white mt-3 tracking-tight">
                {stats?.active_filters ?? 0}
              </div>
            </div>
          </div>

          {/* Portal breakdown */}
          <div className="col-span-7 doppel">
            <div className="doppel-inner p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-medium">
                  Portaalid
                </span>
                {stats?.last_scrape && (
                  <span className="text-[10px] text-zinc-600 font-mono">
                    Viimane kontroll: {formatTime(stats.last_scrape)}
                  </span>
                )}
              </div>
              {stats?.portal_counts &&
                Object.keys(stats.portal_counts).length > 0 && (
                  <div className="grid grid-cols-4 gap-4">
                    {Object.entries(stats.portal_counts).map(([portal, count]) => (
                      <div key={portal}>
                        <div className="text-2xl font-heading font-bold text-white tracking-tight nums">
                          {count}
                        </div>
                        <div className="text-xs text-zinc-600 mt-0.5">{portal}</div>
                      </div>
                    ))}
                  </div>
                )}
            </div>
          </div>
        </div>
      </section>

      {/* Mobile: compact summary */}
      <section className="sm:hidden fade-up fade-up-d1">
        <div className="doppel">
          <div className="doppel-inner p-4 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="text-zinc-500">
                Filtreid:{" "}
                <span className="text-white font-medium">
                  {stats?.active_filters ?? 0}
                </span>
              </span>
              <span className="text-zinc-500">
                Kontroll:{" "}
                <span className="text-white font-medium font-mono">
                  {stats?.last_scrape ? formatTime(stats.last_scrape) : "\u2013"}
                </span>
              </span>
            </div>
            {stats?.portal_counts &&
              Object.keys(stats.portal_counts).length > 0 && (
                <div className="grid grid-cols-4 gap-2 pt-2 border-t border-white/[0.06]">
                  {Object.entries(stats.portal_counts).map(([portal, count]) => (
                    <div key={portal} className="text-center">
                      <div className="text-lg font-heading font-bold text-white nums">
                        {count}
                      </div>
                      <div className="text-[10px] text-zinc-600">{portal}</div>
                    </div>
                  ))}
                </div>
              )}
          </div>
        </div>
      </section>

      {/* Recent listings */}
      <section className="fade-up fade-up-d2">
        <div className="flex items-end justify-between mb-4 sm:mb-6">
          <h2 className="text-lg sm:text-2xl font-heading font-bold text-white tracking-tight">
            Viimased kuulutused
          </h2>
          <a
            href="/listings"
            className="text-accent text-xs sm:text-sm hover:underline underline-offset-4"
          >
            Vaata koiki
          </a>
        </div>

        {recentListings.length === 0 ? (
          <div className="doppel">
            <div className="doppel-inner p-8 sm:p-12 text-center">
              <p className="text-zinc-600 text-sm">
                Kuulutusi pole veel leitud. Lisa filtreid, et alustada otsimist.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {recentListings.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                isExpanded={expandedId === listing.id}
                priceHistory={expandedId === listing.id ? priceHistory : []}
                onToggle={() => toggleExpand(listing.id)}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString("et-EE", { hour: "2-digit", minute: "2-digit" });
}
