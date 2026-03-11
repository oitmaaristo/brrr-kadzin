'use client';

import { useEffect, useState } from 'react';
import type { Listing, Stats } from '@/lib/api';

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentListings, setRecentListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [statsRes, listingsRes] = await Promise.all([
          fetch('/api/stats').then(r => r.json()),
          fetch('/api/listings?limit=10').then(r => r.json()),
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

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-teal border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">Kasutatud autode kuulutuste monitor</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard label="Kuulutusi kokku" value={stats?.total_listings ?? 0} />
        <StatCard label="Teavitusi saadetud" value={stats?.total_notified ?? 0} />
        <StatCard label="Aktiivseid filtreid" value={stats?.active_filters ?? 0} />
        <StatCard
          label="Viimane kontroll"
          value={stats?.last_scrape ? formatTime(stats.last_scrape) : 'Pole veel'}
          isText
        />
      </div>

      {/* Portal breakdown */}
      {stats?.portal_counts && Object.keys(stats.portal_counts).length > 0 && (
        <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-6">
          <h2 className="text-lg text-white mb-4">Portaalide kaupa</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.portal_counts).map(([portal, count]) => (
              <div key={portal} className="text-center">
                <div className="text-2xl font-heading text-white">{count}</div>
                <div className="text-sm text-gray-400">{portal}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent listings */}
      <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg text-white">Viimased kuulutused</h2>
          <a href="/listings" className="text-teal text-sm hover:underline">
            Vaata koiki
          </a>
        </div>

        {recentListings.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            Kuulutusi pole veel leitud. Lisa filtreid, et alustada otsimist.
          </p>
        ) : (
          <div className="space-y-3">
            {recentListings.map(listing => (
              <ListingRow key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  isText,
}: {
  label: string;
  value: number | string;
  isText?: boolean;
}) {
  return (
    <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-4">
      <div className="text-sm text-gray-400 mb-1">{label}</div>
      <div className={`font-heading text-white ${isText ? 'text-sm' : 'text-2xl'}`}>
        {typeof value === 'number' ? value.toLocaleString('et-EE') : value}
      </div>
    </div>
  );
}

function ListingRow({ listing }: { listing: Listing }) {
  const portalColors: Record<string, string> = {
    auto24: 'bg-blue-500/20 text-blue-400',
    autoportaal: 'bg-green-500/20 text-green-400',
    veego: 'bg-purple-500/20 text-purple-400',
    autodiiler: 'bg-orange-500/20 text-orange-400',
  };

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/30 hover:bg-gray-800/60 transition-colors">
      <div className="flex items-center gap-4">
        {listing.image_url && (
          <img
            src={listing.image_url}
            alt={listing.title ?? ''}
            className="w-16 h-12 object-cover rounded"
          />
        )}
        <div>
          <div className="text-white text-sm font-medium">{listing.title ?? 'Tundmatu auto'}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className={`text-xs px-2 py-0.5 rounded ${portalColors[listing.portal] ?? 'bg-gray-700 text-gray-300'}`}>
              {listing.portal}
            </span>
            {listing.year && <span className="text-xs text-gray-400">{listing.year}</span>}
            {listing.mileage && (
              <span className="text-xs text-gray-400">
                {listing.mileage.toLocaleString('et-EE')} km
              </span>
            )}
          </div>
        </div>
      </div>
      <div className="text-right">
        {listing.price && (
          <div className="text-teal font-heading text-lg">
            {listing.price.toLocaleString('et-EE')} EUR
          </div>
        )}
        {listing.url && (
          <a
            href={listing.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-electric-blue hover:underline"
          >
            Vaata kuulutust
          </a>
        )}
      </div>
    </div>
  );
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString('et-EE', { hour: '2-digit', minute: '2-digit' });
}
