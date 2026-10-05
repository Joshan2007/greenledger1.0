"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Leaf, 
  User, 
  Sliders, 
  Activity, 
  Zap
} from "lucide-react";

export const Navbar: React.FC = () => {
  const pathname = usePathname();

  const navLinks = [
    { href: "/dashboard", label: "Dashboard", icon: Activity },
    { href: "/optimize", label: "Optimize", icon: Zap },
    { href: "/impact", label: "Carbon Impact", icon: Leaf },
    { href: "/profile", label: "Profile", icon: User },
    { href: "/diagnostics", label: "ML Diagnostics", icon: Sliders },
  ];

  return (
    <>
      <header className="sticky top-0 z-50 w-full backdrop-blur-md bg-background/80 border-b border-surface-border transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          
          {/* Brand Logo */}
          <Link href="/" className="flex items-center gap-2 group">
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

        </div>
      </header>
    </>
  );
};
