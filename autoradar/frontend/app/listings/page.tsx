"use client";

import { useEffect, useState } from "react";
import type { Listing } from "@/lib/api";
import { ListingCard, type PriceHistory } from "../components/listing-card";

const PORTALS = ["auto24", "autoportaal", "veego", "autodiiler"];

export default function ListingsPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [portalFilter, setPortalFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [priceHistory, setPriceHistory] = useState<PriceHistory[]>([]);

  useEffect(() => {
    loadListings();
  }, [portalFilter]);

  async function loadListings() {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: "100" });
      if (portalFilter) params.set("portal", portalFilter);
      const res = await fetch(`/api/listings?${params}`);
      const data = await res.json();
      setListings(data);
    } catch {
      // API not available
    }
    setLoading(false);
  }

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

  return (
    <div className="space-y-6">
      {/* Portal filter tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1 fade-up">
        <button
          onClick={() => setPortalFilter("")}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-500 ease-smooth whitespace-nowrap active:scale-[0.98] ${
            !portalFilter
              ? "bg-accent text-surface-900"
              : "bg-white/[0.03] text-zinc-500 hover:bg-white/[0.06] border border-white/[0.06]"
          }`}
        >
          Koik
        </button>
        {PORTALS.map((portal) => (
          <button
            key={portal}
            onClick={() => setPortalFilter(portal)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-500 ease-smooth whitespace-nowrap active:scale-[0.98] ${
              portalFilter === portal
                ? "bg-accent text-surface-900"
                : "bg-white/[0.03] text-zinc-500 hover:bg-white/[0.06] border border-white/[0.06]"
            }`}
          >
            {portal}
          </button>
        ))}
      </div>

      {/* Listings */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
        </div>
      ) : listings.length === 0 ? (
        <div className="doppel fade-up">
          <div className="doppel-inner p-8 sm:p-12 text-center">
            <p className="text-zinc-600">Kuulutusi ei leitud.</p>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {listings.map((listing, i) => (
            <div
              key={listing.id}
              className="fade-up"
              style={{ animationDelay: `${Math.min(i * 0.04, 0.4)}s` }}
            >
              <ListingCard
                listing={listing}
                isExpanded={expandedId === listing.id}
                priceHistory={expandedId === listing.id ? priceHistory : []}
                onToggle={() => toggleExpand(listing.id)}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
