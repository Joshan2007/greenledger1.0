"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Leaf, 
  User, 
  Sliders, 
  Activity, 
  Zap,
  Globe,
  Sun,
  Flame,
  Check,
  X,
  ChevronDown
} from "lucide-react";
import { fetchGridIntelligence, switchGridZone } from "../lib/api";
import { GridState } from "../types";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const [gridState, setGridState] = useState<GridState | null>(null);
  const [isGridModalOpen, setIsGridModalOpen] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);

  useEffect(() => {
    const loadGrid = async () => {
      const data = await fetchGridIntelligence();
      if (data) setGridState(data);
    };
    loadGrid();
    const interval = setInterval(loadGrid, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectZone = async (zoneKey: string) => {
    setIsSwitching(true);
    const updated = await switchGridZone(zoneKey);
    if (updated) setGridState(updated);
    setIsSwitching(false);
    setIsGridModalOpen(false);
  };

  const navLinks = [
    { href: "/dashboard", label: "Dashboard", icon: Activity },
    { href: "/optimize", label: "Optimize", icon: Zap },
    { href: "/impact", label: "Carbon Impact", icon: Leaf },
    { href: "/profile", label: "Profile", icon: User },
    { href: "/diagnostics", label: "ML Diagnostics", icon: Sliders },
  ];

  const getStatusBadge = (status?: string) => {
    if (status === "clean") {
      return { dot: "bg-emerald-400", border: "border-emerald-500/40", text: "text-emerald-300", bg: "bg-emerald-950/60" };
    }
    if (status === "dirty_peak") {
      return { dot: "bg-rose-400 animate-pulse", border: "border-rose-500/40", text: "text-rose-300", bg: "bg-rose-950/60" };
    }
    return { dot: "bg-amber-400", border: "border-amber-500/40", text: "text-amber-300", bg: "bg-amber-950/60" };
  };

  const badgeStyle = getStatusBadge(gridState?.status);

  return (
    <>
      <header className="sticky top-0 z-50 w-full backdrop-blur-md bg-background/80 border-b border-surface-border transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-2 group shrink-0">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyber-emerald to-cyber-cyan flex items-center justify-center p-0.5 shadow-glow-green">
              <div className="w-full h-full bg-background rounded-[7px] flex items-center justify-center">
                <Leaf className="w-5 h-5 text-cyber-neon transition-transform group-hover:scale-110" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-emerald-200 to-cyber-neon bg-clip-text text-transparent">
                GreenLedger
              </span>
              <span className="text-[9px] uppercase tracking-widest text-emerald-400 font-mono -mt-1">
                AI Carbon Protocol
              </span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                    isActive
                      ? "bg-surface-elevated text-cyber-neon border border-cyber-emerald/40 shadow-glow-green"
                      : "text-gray-400 hover:text-white hover:bg-surface-card"
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? "text-cyber-neon" : "text-gray-400"}`} />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Novelty 2: Real-Time Grid Carbon Intelligence Pill */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsGridModalOpen(true)}
              className={`px-3 py-1.5 rounded-xl border ${badgeStyle.border} ${badgeStyle.bg} flex items-center gap-2 transition hover:scale-105 shadow-sm text-xs font-mono`}
              title="Click to view real-time grid carbon intelligence & shift workloads"
            >
              <span className={`w-2 h-2 rounded-full ${badgeStyle.dot}`} />
              <div className="flex items-center gap-1.5">
                <span className="text-white font-semibold">
                  {gridState ? gridState.zone : "Grid Sync"}
                </span>
                <span className="text-gray-400 hidden sm:inline">·</span>
                <span className={`${badgeStyle.text} font-bold hidden sm:inline`}>
                  {gridState ? `${gridState.intensity_g_per_kwh} g/kWh` : "Checking"}
                </span>
                {gridState && gridState.carbon_multiplier > 1.0 && (
                  <span className="px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-300 text-[10px] font-bold border border-rose-500/30">
                    {gridState.carbon_multiplier}x
                  </span>
                )}
              </div>
              <ChevronDown className="w-3 h-3 text-gray-400" />
            </button>
          </div>

        </div>
      </header>

      {/* Grid Carbon Intelligence Modal */}
      {isGridModalOpen && gridState && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-lg p-6 rounded-2xl bg-surface-card border border-surface-border shadow-2xl relative space-y-5">
            
            {/* Close Button */}
            <button
              onClick={() => setIsGridModalOpen(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-surface-elevated transition"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Modal Header */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-950/80 border border-emerald-500/40 flex items-center justify-center text-cyber-neon">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">
                  Dynamic Carbon Grid Intelligence
                </h3>
                <span className="text-[11px] font-mono text-emerald-400">
                  Novelty 2: Temporal Grid Workload Shifting
                </span>
              </div>
            </div>

            {/* Current Grid Metrics */}
            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-surface/70 border border-surface-border">
                <span className="text-gray-400 text-[10px]">Real-Time Marginal Carbon:</span>
                <div className="text-lg font-bold text-cyber-neon mt-0.5">
                  {gridState.intensity_g_per_kwh} <span className="text-xs text-gray-400">g CO₂/kWh</span>
                </div>
                <span className="text-[10px] text-gray-500">
                  ({gridState.intensity_kg_per_kwh} kg CO₂e/kWh)
                </span>
              </div>

              <div className="p-3 rounded-xl bg-surface/70 border border-surface-border">
                <span className="text-gray-400 text-[10px]">Renewable Generation:</span>
                <div className="text-lg font-bold text-emerald-400 mt-0.5">
                  ~{gridState.renewable_percentage}%
                </div>
                <span className="text-[10px] text-gray-500">Wind & Solar Mix</span>
              </div>

              <div className="p-3 rounded-xl bg-surface/70 border border-surface-border">
                <span className="text-gray-400 text-[10px]">Clean Solar Window:</span>
                <div className="text-xs font-bold text-amber-300 mt-1 flex items-center gap-1">
                  <Sun className="w-3.5 h-3.5 text-amber-400" />
                  <span>{gridState.clean_window_text}</span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-surface/70 border border-surface-border">
                <span className="text-gray-400 text-[10px]">Credit Incentive Multiplier:</span>
                <div className="text-base font-bold text-rose-300 mt-0.5 flex items-center gap-1">
                  <Flame className="w-3.5 h-3.5 text-rose-400" />
                  <span>{gridState.carbon_multiplier}x Active</span>
                </div>
              </div>
            </div>

            {/* Recommendation Callout */}
            <div className="p-3.5 rounded-xl bg-surface/90 border border-surface-border text-xs text-gray-300 leading-relaxed font-mono">
              <strong className="text-white block mb-1">
                {gridState.status_label} ({gridState.zone_name})
              </strong>
              {gridState.recommendation}
            </div>

            {/* Regional Zone Switcher */}
            <div className="space-y-2">
              <span className="text-[11px] font-mono text-gray-400 uppercase tracking-wider block">
                Simulate / Select Regional Electricity Grid:
              </span>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                {[
                  { id: "IN-SR", label: "India (Southern Grid - SR)" },
                  { id: "IN-NATIONAL", label: "India (National Grid)" },
                  { id: "US-CAISO", label: "USA (California CAISO)" },
                  { id: "US-NATIONAL", label: "USA (EPA eGRID Avg)" },
                  { id: "GB-NATIONAL", label: "United Kingdom (Live ESO)" },
                  { id: "EU-GERMANY", label: "Germany (Agora Grid)" },
                  { id: "NORDIC", label: "Nordic Clean Energy" }
                ].map((z) => (
                  <button
                    key={z.id}
                    onClick={() => handleSelectZone(z.id)}
                    disabled={isSwitching}
                    className={`p-2 rounded-lg text-left transition text-[11px] flex items-center justify-between border ${
                      gridState.zone === z.id
                        ? "bg-emerald-950/80 border-emerald-500/60 text-emerald-300 font-bold"
                        : "bg-surface/50 border-surface-border text-gray-400 hover:text-white hover:bg-surface-elevated"
                    }`}
                  >
                    <span className="truncate">{z.label}</span>
                    {gridState.zone === z.id && <Check className="w-3.5 h-3.5 text-cyber-neon shrink-0" />}
                  </button>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}
    </>
  );
};
