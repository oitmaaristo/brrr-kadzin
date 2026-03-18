"use client";

import type { Listing } from "@/lib/api";

const portalColors: Record<string, string> = {
  auto24: "bg-blue-500/10 text-blue-400/80 border-blue-500/10",
  autoportaal: "bg-green-500/10 text-green-400/80 border-green-500/10",
  veego: "bg-purple-500/10 text-purple-400/80 border-purple-500/10",
  autodiiler: "bg-orange-500/10 text-orange-400/80 border-orange-500/10",
};

export interface PriceHistory {
  id: number;
  old_price: number | null;
  new_price: number | null;
  changed_at: string;
}

export function ListingCard({
  listing,
  isExpanded,
  priceHistory,
  onToggle,
}: {
  listing: Listing;
  isExpanded: boolean;
  priceHistory: PriceHistory[];
  onToggle: () => void;
}) {
  return (
    <div className="doppel card-hover">
      <div className="doppel-inner overflow-hidden">
        {/* Compact row */}
        <button
          onClick={onToggle}
          className="w-full flex items-center gap-3 sm:gap-4 p-3 sm:p-4 hover:bg-white/[0.02] transition-colors duration-500 ease-smooth text-left"
        >
          {/* Image */}
          <div className="w-16 h-12 sm:w-28 sm:h-20 bg-surface-700 rounded-xl overflow-hidden shrink-0 border border-white/[0.04]">
            {listing.image_url ? (
              <img
                src={listing.image_url}
                alt=""
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-zinc-700 text-[10px]">
                Pilt puudub
              </div>
            )}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 sm:gap-3">
              <div className="min-w-0">
                <h3 className="text-white font-heading font-semibold text-xs sm:text-[15px] tracking-tight line-clamp-2 sm:line-clamp-1">
                  {listing.title ?? "Tundmatu auto"}
                </h3>
                <div className="flex items-center gap-1.5 sm:gap-2 mt-1 sm:mt-1.5 flex-wrap">
                  <span
                    className={`px-1.5 sm:px-2 py-0.5 rounded-lg text-[9px] sm:text-[10px] font-medium border ${
                      portalColors[listing.portal] ?? "bg-zinc-500/10 text-zinc-400 border-zinc-500/10"
                    }`}
                  >
                    {listing.portal}
                  </span>
                  <span className="text-[10px] sm:text-[11px] text-zinc-600">
                    {[
                      listing.year,
                      listing.mileage
                        ? `${listing.mileage.toLocaleString("et-EE")} km`
                        : null,
                      listing.fuel_type,
                      listing.transmission,
                    ]
                      .filter(Boolean)
                      .join(" \u00B7 ")}
                  </span>
                </div>
              </div>

              {/* Price */}
              <div className="text-right shrink-0">
                {listing.price ? (
                  <span className="text-base sm:text-xl font-heading font-bold text-accent tracking-tight nums">
                    {listing.price.toLocaleString("et-EE")} &euro;
                  </span>
                ) : (
                  <span className="text-zinc-700 text-xs">-</span>
                )}
              </div>
            </div>
          </div>
        </button>

        {/* Expanded detail view */}
        {isExpanded && (
          <div className="border-t border-white/[0.06] p-3 sm:p-5 space-y-3 sm:space-y-4">
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-5">
              {listing.image_url && (
                <div className="w-full sm:w-48 h-32 sm:h-36 bg-surface-700 rounded-xl overflow-hidden shrink-0 border border-white/[0.04]">
                  <img
                    src={listing.image_url}
                    alt={listing.title ?? ""}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                </div>
              )}

              <div className="flex-1 grid grid-cols-2 gap-x-4 gap-y-2 text-xs sm:text-sm">
                <DetailRow label="Portaal" value={listing.portal} />
                <DetailRow label="Aasta" value={listing.year?.toString()} />
                <DetailRow
                  label="Labisoit"
                  value={
                    listing.mileage
                      ? `${listing.mileage.toLocaleString("et-EE")} km`
                      : undefined
                  }
                />
                <DetailRow label="Kutus" value={listing.fuel_type} />
                <DetailRow label="Kaigukast" value={listing.transmission} />
                <DetailRow label="Keretyyp" value={listing.body_type} />
                <DetailRow label="Asukoht" value={listing.location} />
                <DetailRow
                  label="Leitud"
                  value={new Date(listing.first_seen_at).toLocaleDateString("et-EE")}
                />
              </div>
            </div>

            {/* Price history */}
            {priceHistory.length > 0 && (
              <div className="doppel">
                <div className="doppel-inner p-3 sm:p-4">
                  <h4 className="text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                    Hinna ajalugu
                  </h4>
                  <div className="space-y-1.5">
                    {priceHistory.map((ph) => {
                      const diff = (ph.new_price ?? 0) - (ph.old_price ?? 0);
                      const isDown = diff < 0;
                      return (
                        <div
                          key={ph.id}
                          className="flex flex-col sm:flex-row sm:items-center justify-between text-xs sm:text-sm gap-1"
                        >
                          <span className="text-zinc-500 font-mono text-xs">
                            {new Date(ph.changed_at).toLocaleDateString("et-EE")}
                          </span>
                          <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                            <span className="text-zinc-600 line-through nums">
                              {ph.old_price?.toLocaleString("et-EE")} &euro;
                            </span>
                            <span className="text-zinc-600">&rarr;</span>
                            <span className="text-white nums">
                              {ph.new_price?.toLocaleString("et-EE")} &euro;
                            </span>
                            <span
                              className={`nums font-medium ${
                                isDown ? "text-emerald-400" : "text-red-400"
                              }`}
                            >
                              ({isDown ? "" : "+"}
                              {diff.toLocaleString("et-EE")} &euro;)
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div className="flex flex-wrap gap-2">
              {listing.url && (
                <a
                  href={listing.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 rounded-xl text-xs sm:text-sm bg-accent/10 text-accent hover:bg-accent/20 border border-accent/10 transition-all duration-500 ease-smooth active:scale-[0.98]"
                >
                  Vaata kuulutust
                </a>
              )}
              <a
                href="https://eteenindus.mnt.ee/public/soidukTaustakontroll.jsf"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 rounded-xl text-xs sm:text-sm bg-white/[0.03] text-zinc-400 hover:bg-white/[0.06] border border-white/[0.06] transition-all duration-500 ease-smooth active:scale-[0.98]"
              >
                Transpordiamet
              </a>
              <a
                href="https://vs.lkf.ee"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 rounded-xl text-xs sm:text-sm bg-white/[0.03] text-zinc-400 hover:bg-white/[0.06] border border-white/[0.06] transition-all duration-500 ease-smooth active:scale-[0.98]"
              >
                LKF
              </a>
              <a
                href="https://www.vininfo.ee"
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 rounded-xl text-xs sm:text-sm bg-white/[0.03] text-zinc-400 hover:bg-white/[0.06] border border-white/[0.06] transition-all duration-500 ease-smooth active:scale-[0.98]"
              >
                Vininfo
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value?: string | null }) {
  if (!value) return null;
  return (
    <div>
      <span className="text-zinc-600">{label}: </span>
      <span className="text-zinc-300">{value}</span>
    </div>
  );
}
