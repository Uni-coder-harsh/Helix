import React from "react";
import { MapPlaceholder } from "@/components/map-placeholder";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Compass, ShieldAlert, Cpu } from "lucide-react";

export default function MapPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Geo-Spatial Telemetry Console</h1>
        <p className="text-xs text-muted-foreground">Geographic mapping overlay of municipal issues, ward boundaries, and field coordinate vectors.</p>
      </div>

      <MapPlaceholder />

      {/* Auxiliary Map Telemetry Feed */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-4 space-y-2">
          <div className="flex items-center space-x-2">
            <Compass className="h-4.5 w-4.5 text-indigo-500" />
            <h4 className="font-bold text-xs">Coordinate Projection Layer</h4>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Wired to WGS-84 GIS mapping standards. Geotags matched with municipal easement layouts to detect public vs private utilities.
          </p>
        </Card>
        <Card className="p-4 space-y-2">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="h-4.5 w-4.5 text-red-500" />
            <h4 className="font-bold text-xs">Hotspot Density Indicators</h4>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Sector-4 Central Park reports highest water wasting density index. Alerting ward engineer for direct preventative checks.
          </p>
        </Card>
        <Card className="p-4 space-y-2">
          <div className="flex items-center space-x-2">
            <Cpu className="h-4.5 w-4.5 text-emerald-500 animate-pulse" />
            <h4 className="font-bold text-xs">Connected Fleet GPS</h4>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Currently tracking 4 municipal service vans and 2 heavy excavation compressors active on Sector 4.
          </p>
        </Card>
      </div>
    </div>
  );
}
