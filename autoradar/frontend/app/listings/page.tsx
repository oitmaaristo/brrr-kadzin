'use client';

import { useEffect, useState } from 'react';
import type { Listing } from '@/lib/api';

const PORTALS = ['auto24', 'autoportaal', 'veego', 'autodiiler'];

export default function ListingsPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [portalFilter, setPortalFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadListings();
  }, [portalFilter]);

  async function loadListings() {
    setLoading(true);
    try {
      const params = new URLSearchParams({ limit: '100' });
      if (portalFilter) params.set('portal', portalFilter);
      const res = await fetch(`/api/listings?${params}`);
      const data = await res.json();
      setListings(data);
    } catch {
      // API not available
    }
    setLoading(false);
  }

  async function handleCheck(listingId: number) {
    try {
      await fetch(`/api/listings/${listingId}/check`, { method: 'POST' });
      alert('Taustauring tehtud!');
    } catch {
      alert('Taustauring ebaonnestus');
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl text-white mb-2">Kuulutused</h1>
        <p className="text-gray-400">Koik leitud kuulutused</p>
      </div>

      {/* Portal filter tabs */}
      <div className="flex gap-2">
        <button
          onClick={() => setPortalFilter('')}
          className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
            !portalFilter ? 'bg-teal text-navy font-medium' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
          }`}
        >
          Koik
        </button>
        {PORTALS.map(portal => (
          <button
            key={portal}
            onClick={() => setPortalFilter(portal)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
              portalFilter === portal ? 'bg-teal text-navy font-medium' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {portal}
          </button>
        ))}
      </div>

      {/* Listings table */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-teal border-t-transparent rounded-full animate-spin" />
        </div>
      ) : listings.length === 0 ? (
        <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-8 text-center">
          <p className="text-gray-500">Kuulutusi ei leitud.</p>
        </div>
      ) : (
        <div className="bg-gray-900/50 rounded-xl border border-gray-800 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800">
                <th className="text-left text-xs text-gray-400 font-medium px-4 py-3">Auto</th>
                <th className="text-left text-xs text-gray-400 font-medium px-4 py-3">Portaal</th>
                <th className="text-right text-xs text-gray-400 font-medium px-4 py-3">Hind</th>
                <th className="text-right text-xs text-gray-400 font-medium px-4 py-3">Aasta</th>
                <th className="text-right text-xs text-gray-400 font-medium px-4 py-3">Labisoit</th>
                <th className="text-left text-xs text-gray-400 font-medium px-4 py-3">Kutus</th>
                <th className="text-left text-xs text-gray-400 font-medium px-4 py-3">Kaigukast</th>
                <th className="text-center text-xs text-gray-400 font-medium px-4 py-3">Tegevused</th>
              </tr>
            </thead>
            <tbody>
              {listings.map(listing => (
                <tr key={listing.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      {listing.image_url && (
                        <img
                          src={listing.image_url}
                          alt=""
                          className="w-12 h-9 object-cover rounded"
                        />
                      )}
                      <span className="text-white text-sm">{listing.title ?? 'Tundmatu'}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400">
                      {listing.portal}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {listing.price ? (
                      <span className="text-teal font-heading">
                        {listing.price.toLocaleString('et-EE')} EUR
                      </span>
                    ) : (
                      <span className="text-gray-600">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-gray-300">
                    {listing.year ?? '-'}
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-gray-300">
                    {listing.mileage ? `${listing.mileage.toLocaleString('et-EE')} km` : '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-300">
                    {listing.fuel_type ?? '-'}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-300">
                    {listing.transmission ?? '-'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-2">
                      {listing.url && (
                        <a
                          href={listing.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs px-2 py-1 rounded bg-electric-blue/20 text-electric-blue hover:bg-electric-blue/30"
                        >
                          Vaata
                        </a>
                      )}
                      <button
                        onClick={() => handleCheck(listing.id)}
                        className="text-xs px-2 py-1 rounded bg-teal/10 text-teal hover:bg-teal/20"
                      >
                        Kontroll
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
