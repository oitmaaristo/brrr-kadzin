'use client';

import { useEffect, useState } from 'react';
import type { SearchFilter } from '@/lib/api';

const PORTALS = ['auto24', 'autoportaal', 'veego', 'autodiiler'];
const FUEL_TYPES = ['bensiin', 'diisel', 'hübriid', 'elektri', 'gaas'];
const TRANSMISSIONS = ['manuaal', 'automaat'];
const BODY_TYPES = ['sedaan', 'universaal', 'luukpära', 'maastur', 'kupee', 'kabrio', 'kaubik'];
const DRIVE_TYPES = ['esisild', 'tagasild', 'nelik'];

export default function FiltersPage() {
  const [filters, setFilters] = useState<SearchFilter[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  // Form state
  const [name, setName] = useState('');
  const [selectedPortals, setSelectedPortals] = useState<string[]>(['auto24']);
  const [brand, setBrand] = useState('');
  const [model, setModel] = useState('');
  const [priceMin, setPriceMin] = useState('');
  const [priceMax, setPriceMax] = useState('');
  const [yearMin, setYearMin] = useState('');
  const [yearMax, setYearMax] = useState('');
  const [mileageMax, setMileageMax] = useState('');
  const [fuelType, setFuelType] = useState('');
  const [transmission, setTransmission] = useState('');
  const [bodyType, setBodyType] = useState('');
  const [driveType, setDriveType] = useState('');

  useEffect(() => {
    loadFilters();
  }, []);

  async function loadFilters() {
    try {
      const res = await fetch('/api/filters');
      const data = await res.json();
      setFilters(data);
    } catch {
      // API not available
    }
    setLoading(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const params: Record<string, string | number> = {};
    if (brand) params.brand = brand.toLowerCase();
    if (model) params.model = model;
    if (priceMin) params.price_min = parseInt(priceMin);
    if (priceMax) params.price_max = parseInt(priceMax);
    if (yearMin) params.year_min = parseInt(yearMin);
    if (yearMax) params.year_max = parseInt(yearMax);
    if (mileageMax) params.mileage_max = parseInt(mileageMax);
    if (fuelType) params.fuel_type = fuelType;
    if (transmission) params.transmission = transmission;
    if (bodyType) params.body_type = bodyType;
    if (driveType) params.drive_type = driveType;

    try {
      await fetch('/api/filters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name || `${brand || 'Koik'} ${model || ''}`.trim(),
          portals: selectedPortals,
          params,
        }),
      });
      resetForm();
      loadFilters();
    } catch {
      // Handle error
    }
  }

  async function handleDelete(id: number) {
    await fetch(`/api/filters/${id}`, { method: 'DELETE' });
    loadFilters();
  }

  async function handleToggle(id: number, isActive: boolean) {
    await fetch(`/api/filters/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: !isActive }),
    });
    loadFilters();
  }

  function resetForm() {
    setName('');
    setSelectedPortals(['auto24']);
    setBrand('');
    setModel('');
    setPriceMin('');
    setPriceMax('');
    setYearMin('');
    setYearMax('');
    setMileageMax('');
    setFuelType('');
    setTransmission('');
    setBodyType('');
    setDriveType('');
    setShowForm(false);
  }

  function togglePortal(portal: string) {
    setSelectedPortals(prev =>
      prev.includes(portal)
        ? prev.filter(p => p !== portal)
        : [...prev, portal]
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-teal border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl text-white mb-2">Filtrid</h1>
          <p className="text-gray-400">Halda oma otsingufiltreid</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-teal text-navy font-medium rounded-lg hover:bg-teal/90 transition-colors"
        >
          {showForm ? 'Tuhista' : 'Lisa filter'}
        </button>
      </div>

      {/* New filter form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-900/50 rounded-xl border border-gray-800 p-6 space-y-6">
          <h2 className="text-lg text-white">Uus filter</h2>

          {/* Name */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Filtri nimi</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="nt. BMW 3-seeria kuni 15k"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
            />
          </div>

          {/* Portals */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Portaalid</label>
            <div className="flex gap-2">
              {PORTALS.map(portal => (
                <button
                  key={portal}
                  type="button"
                  onClick={() => togglePortal(portal)}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    selectedPortals.includes(portal)
                      ? 'bg-teal text-navy font-medium'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {portal}
                </button>
              ))}
            </div>
          </div>

          {/* Brand & Model */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Mark</label>
              <input
                type="text"
                value={brand}
                onChange={e => setBrand(e.target.value)}
                placeholder="nt. BMW, Audi, Toyota"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Mudel</label>
              <input
                type="text"
                value={model}
                onChange={e => setModel(e.target.value)}
                placeholder="nt. 320d, A4, Corolla"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              />
            </div>
          </div>

          {/* Price range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Hind alates (EUR)</label>
              <input
                type="number"
                value={priceMin}
                onChange={e => setPriceMin(e.target.value)}
                placeholder="0"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Hind kuni (EUR)</label>
              <input
                type="number"
                value={priceMax}
                onChange={e => setPriceMax(e.target.value)}
                placeholder="50000"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              />
            </div>
          </div>

          {/* Year range */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Aasta alates</label>
              <input
                type="number"
                value={yearMin}
                onChange={e => setYearMin(e.target.value)}
                placeholder="2015"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Aasta kuni</label>
              <input
                type="number"
                value={yearMax}
                onChange={e => setYearMax(e.target.value)}
                placeholder="2026"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              />
            </div>
          </div>

          {/* Mileage */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Labisoit kuni (km)</label>
            <input
              type="number"
              value={mileageMax}
              onChange={e => setMileageMax(e.target.value)}
              placeholder="200000"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
            />
          </div>

          {/* Fuel, Transmission, Body, Drive */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Kutus</label>
              <select
                value={fuelType}
                onChange={e => setFuelType(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              >
                <option value="">Koik</option>
                {FUEL_TYPES.map(f => (
                  <option key={f} value={f}>{f}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Kaigukast</label>
              <select
                value={transmission}
                onChange={e => setTransmission(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              >
                <option value="">Koik</option>
                {TRANSMISSIONS.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Keretuup</label>
              <select
                value={bodyType}
                onChange={e => setBodyType(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              >
                <option value="">Koik</option>
                {BODY_TYPES.map(b => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Vedav sild</label>
              <select
                value={driveType}
                onChange={e => setDriveType(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:border-teal focus:outline-none"
              >
                <option value="">Koik</option>
                {DRIVE_TYPES.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              className="px-6 py-2 bg-teal text-navy font-medium rounded-lg hover:bg-teal/90 transition-colors"
            >
              Salvesta filter
            </button>
            <button
              type="button"
              onClick={resetForm}
              className="px-6 py-2 bg-gray-800 text-gray-300 rounded-lg hover:bg-gray-700 transition-colors"
            >
              Tuhista
            </button>
          </div>
        </form>
      )}

      {/* Existing filters */}
      <div className="space-y-3">
        {filters.length === 0 ? (
          <div className="bg-gray-900/50 rounded-xl border border-gray-800 p-8 text-center">
            <p className="text-gray-500">Filtreid pole veel. Kliki "Lisa filter" nuppu.</p>
          </div>
        ) : (
          filters.map(filter => (
            <div
              key={filter.id}
              className="bg-gray-900/50 rounded-xl border border-gray-800 p-4 flex items-center justify-between"
            >
              <div>
                <div className="flex items-center gap-3">
                  <span className={`w-2 h-2 rounded-full ${filter.is_active ? 'bg-teal' : 'bg-gray-600'}`} />
                  <span className="text-white font-medium">{filter.name}</span>
                </div>
                <div className="flex items-center gap-2 mt-2 ml-5">
                  {filter.portals.map(p => (
                    <span key={p} className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400">
                      {p}
                    </span>
                  ))}
                  {Object.entries(filter.params).map(([key, val]) => (
                    <span key={key} className="text-xs text-gray-500">
                      {key}: {val}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleToggle(filter.id, filter.is_active)}
                  className={`px-3 py-1 rounded text-xs ${
                    filter.is_active
                      ? 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                      : 'bg-teal/20 text-teal hover:bg-teal/30'
                  }`}
                >
                  {filter.is_active ? 'Peata' : 'Aktiveeri'}
                </button>
                <button
                  onClick={() => handleDelete(filter.id)}
                  className="px-3 py-1 rounded text-xs bg-red-500/10 text-red-400 hover:bg-red-500/20"
                >
                  Kustuta
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
