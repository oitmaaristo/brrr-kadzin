const API_BASE = '/api';

export interface SearchFilter {
  id: number;
  name: string;
  portals: string[];
  params: Record<string, string | number>;
  is_active: boolean;
  created_at: string;
}

export interface Listing {
  id: number;
  portal: string;
  external_id: string;
  url: string | null;
  title: string | null;
  price: number | null;
  year: number | null;
  mileage: number | null;
  fuel_type: string | null;
  transmission: string | null;
  body_type: string | null;
  location: string | null;
  image_url: string | null;
  first_seen_at: string;
  notified_at: string | null;
}

export interface Stats {
  total_listings: number;
  total_notified: number;
  active_filters: number;
  portal_counts: Record<string, number>;
  last_scrape: string | null;
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/stats`);
  return res.json();
}

export async function fetchFilters(): Promise<SearchFilter[]> {
  const res = await fetch(`${API_BASE}/filters`);
  return res.json();
}

export async function createFilter(data: {
  name: string;
  portals: string[];
  params: Record<string, string | number>;
}): Promise<SearchFilter> {
  const res = await fetch(`${API_BASE}/filters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteFilter(id: number): Promise<void> {
  await fetch(`${API_BASE}/filters/${id}`, { method: 'DELETE' });
}

export async function toggleFilter(id: number, isActive: boolean): Promise<SearchFilter> {
  const res = await fetch(`${API_BASE}/filters/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_active: isActive }),
  });
  return res.json();
}

export async function fetchListings(portal?: string, limit = 50): Promise<Listing[]> {
  const params = new URLSearchParams();
  if (portal) params.set('portal', portal);
  params.set('limit', String(limit));
  const res = await fetch(`${API_BASE}/listings?${params}`);
  return res.json();
}

export async function triggerCheck(listingId: number): Promise<unknown> {
  const res = await fetch(`${API_BASE}/listings/${listingId}/check`, { method: 'POST' });
  return res.json();
}
