"use client";

import React, { useState, useEffect } from "react";
import { User, Flame, Calendar, TrendingDown } from "lucide-react";
import { Navbar } from "../../components/Navbar";
import { Footer } from "../../components/Footer";
import { fetchCreditState } from "../../lib/api";
import { UserCreditState } from "../../types";

export default function ProfilePage() {
  const [userState, setUserState] = useState<UserCreditState | null>(null);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    fetchCreditState().then(setUserState).catch(() => setLoadError(true));
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {loadError && <div className="rounded-xl border border-amber-500/40 bg-amber-950/30 px-4 py-3 text-xs font-mono text-amber-200">Progress data unavailable. Values are intentionally not estimated.</div>}

        <div className="p-8 rounded-3xl bg-gradient-to-br from-surface-card via-surface-card to-emerald-950/20 border border-emerald-500/40 relative overflow-hidden shadow-2xl">
          <div className="absolute top-0 right-0 w-80 h-80 bg-cyber-emerald/5 rounded-full blur-3xl pointer-events-none" />

          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-cyber-emerald to-cyber-cyan p-0.5 shadow-glow-green">
                <div className="w-full h-full bg-background rounded-[15px] flex items-center justify-center">
                  <User className="w-10 h-10 text-cyber-neon" />
                </div>
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-2xl font-black text-white tracking-tight">
                    Local Optimization Profile
                  </h2>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-950/80 border border-emerald-500/50 text-emerald-300">
                    Device learning
                  </span>
                </div>
                <div className="mt-1 flex items-center gap-3 text-xs font-mono">
                  <span className="text-cyber-neon font-bold">
                    Rank: {userState?.rank_title || "Eco Explorer"}
                  </span>
                  <span className="text-gray-400">.</span>
                  <span className="text-amber-400 font-bold flex items-center gap-1">
                    <Flame className="w-3.5 h-3.5" />
                    {userState?.current_streak_days ?? "Unavailable"}-Day Streak
                  </span>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-surface/80 border border-surface-border text-xs font-mono max-w-sm">
              <span className="text-gray-400 block text-[10px] uppercase tracking-widest">Verification model</span>
              <p className="mt-1 text-gray-300 leading-relaxed">
                Progress is based on local before/after telemetry and verified optimization outcomes.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 pt-6 border-t border-surface-border font-mono">
            <div>
              <span className="text-gray-400 text-[11px] block">Green Credits</span>
              <span className="text-2xl font-bold text-cyber-neon">
                {userState?.credit_balance ?? "Unavailable"} GC
              </span>
            </div>
            <div>
              <span className="text-gray-400 text-[11px] block">Total Optimizations</span>
              <span className="text-2xl font-bold text-white">
                {userState?.total_optimizations ?? "Unavailable"} Actions
              </span>
            </div>
            <div>
              <span className="text-gray-400 text-[11px] block">CO2 Prevented</span>
              <span className="text-2xl font-bold text-cyber-cyan">
                {userState?.lifetime_reduction_g_co2?.toFixed(1) ?? "Unavailable"} g
              </span>
            </div>
            <div>
              <span className="text-gray-400 text-[11px] block">Energy Saved</span>
              <span className="text-2xl font-bold text-emerald-400">
                {userState?.lifetime_energy_saved_kwh?.toFixed(3) ?? "Unavailable"} kWh
              </span>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <Calendar className="w-5 h-5 text-cyber-neon" />
            Verified Optimization History
          </h3>

          <div className="p-6 rounded-2xl bg-surface-card border border-surface-border overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-surface-border text-gray-400 uppercase tracking-wider text-[10px]">
                  <th className="pb-3">Timestamp</th>
                  <th className="pb-3">Action</th>
                  <th className="pb-3">Type</th>
                  <th className="pb-3 text-right">Credits</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border/50">
                {userState?.recent_transactions && userState.recent_transactions.length > 0 ? (
                  userState.recent_transactions.map((tx) => (
                    <tr key={tx.tx_id} className="hover:bg-surface-elevated/40 transition">
                      <td className="py-3 text-gray-400">{new Date(tx.timestamp).toLocaleString()}</td>
                      <td className="py-3 text-white font-semibold">{tx.description}</td>
                      <td className="py-3 text-emerald-400">{tx.type}</td>
                      <td className="py-3 text-right font-bold text-cyber-neon">
                        {tx.credits > 0 ? `+${tx.credits}` : tx.credits} GC
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} className="py-6 text-center text-gray-500">
                      No verified optimization transactions recorded yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-surface-card border border-surface-border flex items-start gap-3">
          <TrendingDown className="w-5 h-5 text-cyber-neon shrink-0 mt-0.5" />
          <p className="text-xs text-gray-400 leading-relaxed">
            Each successful optimization can be used as evidence for the local planner, improving future recommendations for this hardware profile.
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
