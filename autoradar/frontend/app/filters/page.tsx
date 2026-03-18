"use client";

import { useEffect, useState } from "react";
import type { SearchFilter } from "@/lib/api";

const PORTALS = ["auto24", "autoportaal", "veego", "autodiiler"];
const FUEL_TYPES = ["bensiin", "diisel", "hubriid", "elektri", "gaas"];
const TRANSMISSIONS = ["manuaal", "automaat"];
const BODY_TYPES = [
  "sedaan",
  "universaal",
  "luukpara",
  "maastur",
  "kupee",
  "kabrio",
  "kaubik",
];
const DRIVE_TYPES = ["esisild", "tagasild", "nelik"];

export default function FiltersPage() {
  const [filters, setFilters] = useState<SearchFilter[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  const [name, setName] = useState("");
  const [selectedPortals, setSelectedPortals] = useState<string[]>(["auto24"]);
  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [yearMin, setYearMin] = useState("");
  const [yearMax, setYearMax] = useState("");
  const [mileageMax, setMileageMax] = useState("");
  const [fuelType, setFuelType] = useState("");
  const [transmission, setTransmission] = useState("");
  const [bodyType, setBodyType] = useState("");
  const [driveType, setDriveType] = useState("");
  const [excludeKeywords, setExcludeKeywords] = useState("");

  useEffect(() => {
    loadFilters();
  }, []);

  async function loadFilters() {
    try {
      const res = await fetch("/api/filters");
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
    if (excludeKeywords) params.exclude_keywords = excludeKeywords;

    try {
      await fetch("/api/filters", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name || `${brand || "Koik"} ${model || ""}`.trim(),
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
    await fetch(`/api/filters/${id}`, { method: "DELETE" });
    loadFilters();
  }

  async function handleToggle(id: number, isActive: boolean) {
    await fetch(`/api/filters/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_active: !isActive }),
    });
    loadFilters();
  }

  function resetForm() {
    setName("");
    setSelectedPortals(["auto24"]);
    setBrand("");
    setModel("");
    setPriceMin("");
    setPriceMax("");
    setYearMin("");
    setYearMax("");
    setMileageMax("");
    setFuelType("");
    setTransmission("");
    setBodyType("");
    setDriveType("");
    setExcludeKeywords("");
    setShowForm(false);
  }

  function togglePortal(portal: string) {
    setSelectedPortals((prev) =>
      prev.includes(portal)
        ? prev.filter((p) => p !== portal)
        : [...prev, portal]
    );
  }

  const inputClass =
    "w-full bg-surface-700 border border-white/[0.06] rounded-xl px-3 py-2.5 text-white text-sm focus:border-accent/50 focus:outline-none focus:ring-1 focus:ring-accent/20 transition-all duration-300 placeholder:text-zinc-600";

  const selectClass =
    "w-full bg-surface-700 border border-white/[0.06] rounded-xl px-3 py-2.5 text-white text-sm focus:border-accent/50 focus:outline-none focus:ring-1 focus:ring-accent/20 transition-all duration-300";

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 fade-up">
        <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 sm:space-y-10">
      <div className="flex items-center justify-end fade-up">
        <button
          onClick={() => setShowForm(!showForm)}
          className={`px-5 py-2.5 font-heading font-semibold text-sm rounded-xl transition-all duration-500 ease-smooth active:scale-[0.98] ${
            showForm
              ? "bg-white/[0.03] text-zinc-400 border border-white/[0.06]"
              : "bg-accent text-surface-900 hover:shadow-[0_4px_16px_rgba(0,200,150,0.2)]"
          }`}
        >
          {showForm ? "Tuhista" : "Lisa filter"}
        </button>
      </div>

      {/* New filter form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="doppel fade-up">
          <div className="doppel-inner p-5 sm:p-8 space-y-6">
            <h2 className="text-lg font-heading font-bold text-white tracking-tight">
              Uus filter
            </h2>

            {/* Name */}
            <div>
              <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                Filtri nimi
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="nt. BMW 3-seeria kuni 15k"
                className={inputClass}
              />
            </div>

            {/* Portals */}
            <div>
              <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                Portaalid
              </label>
              <div className="flex gap-2 flex-wrap">
                {PORTALS.map((portal) => (
                  <button
                    key={portal}
                    type="button"
                    onClick={() => togglePortal(portal)}
                    className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-500 ease-smooth active:scale-[0.98] ${
                      selectedPortals.includes(portal)
                        ? "bg-accent text-surface-900"
                        : "bg-white/[0.03] text-zinc-500 hover:bg-white/[0.06] border border-white/[0.06]"
                    }`}
                  >
                    {portal}
                  </button>
                ))}
              </div>
            </div>

            {/* Brand & Model */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Mark
                </label>
                <input
                  type="text"
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  placeholder="nt. BMW, Audi, Toyota"
                  className={inputClass}
                />
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Mudel
                </label>
                <input
                  type="text"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  placeholder="nt. 320d, A4, Corolla"
                  className={inputClass}
                />
              </div>
            </div>

            {/* Price range */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Hind alates (EUR)
                </label>
                <input
                  type="number"
                  value={priceMin}
                  onChange={(e) => setPriceMin(e.target.value)}
                  placeholder="0"
                  className={inputClass}
                />
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Hind kuni (EUR)
                </label>
                <input
                  type="number"
                  value={priceMax}
                  onChange={(e) => setPriceMax(e.target.value)}
                  placeholder="50000"
                  className={inputClass}
                />
              </div>
            </div>

            {/* Year range */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Aasta alates
                </label>
                <input
                  type="number"
                  value={yearMin}
                  onChange={(e) => setYearMin(e.target.value)}
                  placeholder="2015"
                  className={inputClass}
                />
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Aasta kuni
                </label>
                <input
                  type="number"
                  value={yearMax}
                  onChange={(e) => setYearMax(e.target.value)}
                  placeholder="2026"
                  className={inputClass}
                />
              </div>
            </div>

            {/* Mileage */}
            <div>
              <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                Labisoit kuni (km)
              </label>
              <input
                type="number"
                value={mileageMax}
                onChange={(e) => setMileageMax(e.target.value)}
                placeholder="200000"
                className={inputClass}
              />
            </div>

            {/* Exclude keywords */}
            <div>
              <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                Valista sonad
              </label>
              <input
                type="text"
                value={excludeKeywords}
                onChange={(e) => setExcludeKeywords(e.target.value)}
                placeholder="nt. paat, haagis, tsikkel, mootorratas"
                className={inputClass}
              />
              <p className="text-[11px] text-zinc-600 mt-1.5">
                Kuulutused, mille pealkirjas on need sonad, jaetakse vahele
              </p>
            </div>

            {/* Fuel, Transmission, Body, Drive */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Kutus
                </label>
                <select
                  value={fuelType}
                  onChange={(e) => setFuelType(e.target.value)}
                  className={selectClass}
                >
                  <option value="">Koik</option>
                  {FUEL_TYPES.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Kaigukast
                </label>
                <select
                  value={transmission}
                  onChange={(e) => setTransmission(e.target.value)}
                  className={selectClass}
                >
                  <option value="">Koik</option>
                  {TRANSMISSIONS.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Keretyyp
                </label>
                <select
                  value={bodyType}
                  onChange={(e) => setBodyType(e.target.value)}
                  className={selectClass}
                >
                  <option value="">Koik</option>
                  {BODY_TYPES.map((b) => (
                    <option key={b} value={b}>
                      {b}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-[10px] uppercase tracking-[0.15em] text-zinc-500 font-medium mb-2">
                  Vedav sild
                </label>
                <select
                  value={driveType}
                  onChange={(e) => setDriveType(e.target.value)}
                  className={selectClass}
                >
                  <option value="">Koik</option>
                  {DRIVE_TYPES.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                className="px-6 py-2.5 bg-accent text-surface-900 font-heading font-semibold text-sm rounded-xl hover:shadow-[0_4px_16px_rgba(0,200,150,0.2)] transition-all duration-500 ease-smooth active:scale-[0.98]"
              >
                Salvesta filter
              </button>
              <button
                type="button"
                onClick={resetForm}
                className="px-6 py-2.5 bg-white/[0.03] text-zinc-400 rounded-xl hover:bg-white/[0.06] border border-white/[0.06] transition-all duration-500 ease-smooth active:scale-[0.98]"
              >
                Tuhista
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Existing filters */}
      <div className="space-y-3">
        {filters.length === 0 ? (
          <div className="doppel fade-up">
            <div className="doppel-inner p-8 sm:p-12 text-center">
              <p className="text-zinc-600 text-sm">
                Filtreid pole veel. Kliki &quot;Lisa filter&quot; nuppu.
              </p>
            </div>
          </div>
        ) : (
          filters.map((filter, i) => (
            <div
              key={filter.id}
              className="doppel card-hover fade-up"
              style={{ animationDelay: `${Math.min(i * 0.06, 0.3)}s` }}
            >
              <div className="doppel-inner p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-3 sm:gap-4">
                  <span className="mt-1.5 shrink-0">
                    {filter.is_active ? (
                      <span className="relative flex h-2.5 w-2.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-30" />
                        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-accent" />
                      </span>
                    ) : (
                      <span className="w-2.5 h-2.5 rounded-full bg-zinc-700 block" />
                    )}
                  </span>
                  <div>
                    <span className="text-white font-heading font-semibold tracking-tight">
                      {filter.name}
                    </span>
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      {filter.portals.map((p) => (
                        <span
                          key={p}
                          className="text-[10px] px-2 py-0.5 rounded-lg bg-white/[0.03] text-zinc-500 border border-white/[0.06]"
                        >
                          {p}
                        </span>
                      ))}
                      {Object.entries(filter.params).map(([key, val]) => {
                        const labels: Record<string, string> = {
                          brand: "Mark",
                          model: "Mudel",
                          price_min: "Hind alates",
                          price_max: "Hind kuni",
                          year_min: "Aasta alates",
                          year_max: "Aasta kuni",
                          mileage_max: "Km kuni",
                          fuel_type: "Kutus",
                          transmission: "Kaigukast",
                          body_type: "Kere",
                          drive_type: "Vedav sild",
                          exclude_keywords: "Valistatud",
                        };
                        return (
                          <span
                            key={key}
                            className="text-[11px] text-zinc-600"
                          >
                            {labels[key] || key}: {val}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-6 sm:ml-0">
                  <button
                    onClick={() => handleToggle(filter.id, filter.is_active)}
                    className={`px-3 py-1.5 rounded-xl text-xs transition-all duration-500 ease-smooth active:scale-[0.98] ${
                      filter.is_active
                        ? "bg-white/[0.03] text-zinc-500 hover:bg-white/[0.06] border border-white/[0.06]"
                        : "bg-accent/10 text-accent hover:bg-accent/20 border border-accent/10"
                    }`}
                  >
                    {filter.is_active ? "Peata" : "Aktiveeri"}
                  </button>
                  <button
                    onClick={() => handleDelete(filter.id)}
                    className="px-3 py-1.5 rounded-xl text-xs bg-red-500/[0.06] text-red-400/60 hover:bg-red-500/[0.12] border border-red-500/[0.08] transition-all duration-500 ease-smooth active:scale-[0.98]"
                  >
                    Kustuta
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
