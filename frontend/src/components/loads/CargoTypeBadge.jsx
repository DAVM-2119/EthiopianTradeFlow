import React from 'react';
import { Package, Box, Droplet, Container, Snowflake, AlertTriangle, Truck } from 'lucide-react';

export const CargoTypeBadge = ({ cargoType }) => {
  const cargoConfig = {
    GENERAL_CARGO: { label: 'General Cargo', icon: Package },
    DRY_BULK: { label: 'Dry Bulk', icon: Box },
    LIQUID_BULK: { label: 'Liquid Bulk', icon: Droplet },
    CONTAINERIZED: { label: 'Containerized', icon: Container },
    REFRIGERATED: { label: 'Refrigerated', icon: Snowflake },
    HAZARDOUS: { label: 'Hazardous', icon: AlertTriangle },
    HEAVY_MACHINERY: { label: 'Heavy Machinery', icon: Truck },
  };

  const config = cargoConfig[cargoType] || { label: cargoType || 'General Cargo', icon: Package };
  const Icon = config.icon;

  return (
    <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 text-[11px] font-medium text-slate-300 bg-slate-800/80 rounded-md border border-slate-700/60">
      <Icon className="w-3 h-3 text-cyan-400 shrink-0" />
      <span>{config.label}</span>
    </span>
  );
};
