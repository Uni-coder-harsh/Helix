"use client";

import React, { useState, useEffect, useRef } from "react";
import { fetchWithAuth } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import {
  MapPin,
  TrendingUp,
  AlertTriangle,
  Activity,
  Layers,
  Compass,
  Zap,
  Globe,
  Settings,
  Sparkles,
  ArrowRight,
  TrendingDown,
  Hammer,
  CheckCircle,
  Search,
  School,
  Building,
  TreePine,
  ShieldCheck,
  Navigation,
} from "lucide-react";

// MapLibre script and style loader helper
const loadMapLibreScript = (callback: () => void, onError: () => void) => {
  if (typeof window === "undefined") return;
  if ((window as any).maplibregl) {
    callback();
    return;
  }
  const existingScript = document.getElementById("maplibre-script");
  if (existingScript) {
    existingScript.addEventListener("load", callback);
    existingScript.addEventListener("error", onError);
    return;
  }

  // Load CSS
  const link = document.createElement("link");
  link.id = "maplibre-css";
  link.href = "https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css";
  link.rel = "stylesheet";
  document.head.appendChild(link);

  // Load JS
  const script = document.createElement("script");
  script.id = "maplibre-script";
  script.src = "https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js";
  script.async = true;
  script.defer = true;
  script.onload = () => {
    callback();
  };
  script.onerror = () => {
    onError();
  };
  document.head.appendChild(script);
};

export default function SpatialMapPage() {
  const [activeTab, setActiveTab] = useState<"overview" | "map" | "health" | "projects">("overview");

  // Spatial Data states
  const [overview, setOverview] = useState<any>(null);
  const [mapData, setMapData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Map Filter layers
  const [showIssuesLayer, setShowIssuesLayer] = useState(true);
  const [showHeatmapLayer, setShowHeatmapLayer] = useState(true);
  const [showHotspotsLayer, setShowHotspotsLayer] = useState(true);
  const [showBoundariesLayer, setShowBoundariesLayer] = useState(true);

  // Selected Hotspot details
  const [selectedHotspot, setSelectedHotspot] = useState<any>(null);
  const [tenderingStates, setTenderingStates] = useState<Record<string, boolean>>({});

  // Dynamic nearby places assets
  const [nearbySchools, setNearbySchools] = useState<any[]>([]);
  const [nearbyHospitals, setNearbyHospitals] = useState<any[]>([]);
  const [nearbyParks, setNearbyParks] = useState<any[]>([]);
  const [loadingAssets, setLoadingAssets] = useState(false);

  // Search/Geocode states
  const [searchQuery, setSearchQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState("");

  // Map container references
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapError, setMapError] = useState(false);

  // Fetch basic overview and coordinate clusters
  useEffect(() => {
    Promise.all([
      fetchWithAuth("/governance/constituency/overview"),
      fetchWithAuth("/governance/map"),
    ])
      .then(([over, mData]) => {
        setOverview(over || null);
        setMapData(mData || { boundaries: { type: "FeatureCollection", features: [] }, heatmap: [], clusters: [], hotspots: [] });

        if (over?.hotspots && over.hotspots.length > 0) {
          setSelectedHotspot(over.hotspots[0]);
        }

        loadMapLibreScript(
          () => {
            setMapLoaded(true);
          },
          () => {
            setMapError(true);
          }
        );
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch map data:", err);
        setError("No data available");
        setLoading(false);
      });
  }, []);

  // Fetch dynamic nearby assets on selected hotspot change
  useEffect(() => {
    if (selectedHotspot) {
      setLoadingAssets(true);
      const { latitude, longitude } = selectedHotspot;
      Promise.all([
        fetchWithAuth(`/governance/spatial/places?latitude=${latitude}&longitude=${longitude}&type=school&radius=2000`).catch(() => []),
        fetchWithAuth(`/governance/spatial/places?latitude=${latitude}&longitude=${longitude}&type=hospital&radius=2000`).catch(() => []),
        fetchWithAuth(`/governance/spatial/places?latitude=${latitude}&longitude=${longitude}&type=park&radius=2000`).catch(() => []),
      ])
        .then(([schools, hospitals, parks]) => {
          setNearbySchools(Array.isArray(schools) ? schools : []);
          setNearbyHospitals(Array.isArray(hospitals) ? hospitals : []);
          setNearbyParks(Array.isArray(parks) ? parks : []);
          setLoadingAssets(false);
        })
        .catch((err) => {
          console.error("Error fetching nearby assets:", err);
          setNearbySchools([]);
          setNearbyHospitals([]);
          setNearbyParks([]);
          setLoadingAssets(false);
        });
    }
  }, [selectedHotspot]);

  // MapLibre Maps Instance Hook
  useEffect(() => {
    if (mapLoaded && !mapError && mapRef.current && mapData && activeTab === "map") {
      const center = [77.5955, 12.9755]; // [lng, lat]
      const map = new (window as any).maplibregl.Map({
        container: mapRef.current,
        style: {
          version: 8,
          sources: {
            "osm-tiles": {
              type: "raster",
              tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
              tileSize: 256,
              attribution: "© OpenStreetMap contributors",
            },
          },
          layers: [
            {
              id: "osm-layer",
              type: "raster",
              source: "osm-tiles",
              minzoom: 0,
              maxzoom: 19,
            },
          ],
        },
        center: center,
        zoom: 13.5,
      });
      mapInstanceRef.current = map;

      // Add navigation controls
      map.addControl(new (window as any).maplibregl.NavigationControl(), "top-right");

      map.on("load", () => {
        // Draw boundaries
        if (showBoundariesLayer && mapData.boundaries && mapData.boundaries.features && mapData.boundaries.features.length > 0) {
          map.addSource("boundaries-source", {
            type: "geojson",
            data: mapData.boundaries,
          });

          map.addLayer({
            id: "boundaries-layer",
            type: "fill",
            source: "boundaries-source",
            paint: {
              "fill-color": [
                "match",
                ["get", "level"],
                "ward", "#6366f1",
                "constituency", "#3b82f6",
                "#6366f1"
              ],
              "fill-opacity": 0.12,
            },
          });

          map.addLayer({
            id: "boundaries-outline",
            type: "line",
            source: "boundaries-source",
            paint: {
              "line-color": [
                "match",
                ["get", "level"],
                "ward", "#6366f1",
                "constituency", "#3b82f6",
                "#6366f1"
              ],
              "line-width": 2,
            },
          });
        }

        // Draw Heatmap
        if (showHeatmapLayer && mapData.heatmap && mapData.heatmap.length > 0) {
          const heatmapPoints = {
            type: "FeatureCollection",
            features: mapData.heatmap.map((pt: any) => ({
              type: "Feature",
              geometry: { type: "Point", coordinates: [pt.lng, pt.lat] },
              properties: { weight: pt.weight || 1.0 },
            })),
          };

          map.addSource("heatmap-source", {
            type: "geojson",
            data: heatmapPoints,
          });

          map.addLayer({
            id: "heatmap-layer",
            type: "heatmap",
            source: "heatmap-source",
            paint: {
              "heatmap-intensity": 1,
              "heatmap-color": [
                "interpolate",
                ["linear"],
                ["heatmap-density"],
                0, "rgba(99, 102, 241, 0)",
                0.2, "rgba(99, 102, 241, 0.2)",
                0.4, "rgba(34, 197, 94, 0.4)",
                0.6, "rgba(234, 179, 8, 0.6)",
                0.8, "rgba(239, 68, 68, 0.8)",
                1, "rgba(239, 68, 68, 1)"
              ],
              "heatmap-radius": 30,
              "heatmap-opacity": 0.7,
            },
          });
        }

        // Draw clustered markers
        if (showIssuesLayer && mapData.clusters && mapData.clusters.length > 0) {
          mapData.clusters.forEach((node: any) => {
            const isCluster = node.type === "cluster";
            const el = document.createElement("div");
            el.className = "flex items-center justify-center cursor-pointer transition-all hover:scale-110";

            el.style.width = isCluster ? "26px" : "16px";
            el.style.height = isCluster ? "26px" : "16px";
            el.style.borderRadius = "50%";
            el.style.backgroundColor = isCluster ? "#ef4444" : "#f59e0b";
            el.style.border = "2px solid #ffffff";
            el.style.boxShadow = "0 2px 4px rgba(0,0,0,0.3)";
            el.style.color = "#ffffff";
            el.style.fontSize = "10px";
            el.style.fontWeight = "bold";
            el.style.display = "flex";
            el.style.alignItems = "center";
            el.style.justifyContent = "center";

            if (isCluster) {
              el.innerText = String(node.count);
            }

            const popupContent = `
              <div style="color: #0f172a; font-family: system-ui, sans-serif; padding: 6px; width: 180px;">
                <h4 style="font-weight: 800; font-size: 13px; margin: 0 0 3px 0; color: #1e293b;">
                  ${isCluster ? `Cluster: ${node.count} Issues` : node.title}
                </h4>
                <p style="font-size: 10px; margin: 0 0 6px 0; color: #64748b;">
                  ${isCluster ? "Overlapping density zone" : node.category}
                </p>
                ${
                  isCluster
                    ? `<span style="font-size: 9px; font-weight: bold; color: #ef4444; background: #fee2e2; padding: 2px 6px; border-radius: 4px;">Active Hotspot</span>`
                    : `<a href="/issues/${node.id}" style="font-size: 11px; font-weight: 700; color: #6366f1; text-decoration: none; display: inline-block;">Open Decision Brief →</a>`
                }
              </div>
            `;

            const popup = new (window as any).maplibregl.Popup({ offset: 15 }).setHTML(popupContent);

            new (window as any).maplibregl.Marker(el)
              .setLngLat([node.longitude, node.latitude])
              .setPopup(popup)
              .addTo(map);

            el.addEventListener("click", () => {
              if (isCluster && node.ids && node.ids.length > 0) {
                const matched = overview?.hotspots?.find((h: any) => h.linked_complaint_ids.includes(node.ids[0]));
                if (matched) setSelectedHotspot(matched);
              } else if (node.id) {
                const matched = overview?.hotspots?.find((h: any) => h.linked_complaint_ids.includes(node.id));
                if (matched) setSelectedHotspot(matched);
              }
            });
          });
        }
      });

      return () => {
        map.remove();
      };
    }
  }, [mapLoaded, mapData, showIssuesLayer, showHeatmapLayer, showBoundariesLayer, activeTab, mapError, overview]);

  // Geocode address search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;
    setSearching(true);
    setSearchError("");

    fetchWithAuth(`/governance/spatial/geocode?address=${encodeURIComponent(searchQuery)}`)
      .then((coords) => {
        setSearching(false);
        if (mapInstanceRef.current) {
          mapInstanceRef.current.setCenter([coords.longitude, coords.latitude]);
          mapInstanceRef.current.setZoom(15);
        }

        // Locate or build a hotspot descriptor
        const matched = overview?.hotspots?.find(
          (h: any) =>
            Math.abs(h.latitude - coords.latitude) < 0.005 && Math.abs(h.longitude - coords.longitude) < 0.005
        );
        if (matched) {
          setSelectedHotspot(matched);
        }
      })
      .catch((err) => {
        setSearching(false);
        setSearchError("Location search failed.");
      });
  };

  const handleStartTender = (hotspotId: string) => {
    setTenderingStates((prev) => ({ ...prev, [hotspotId]: true }));
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-muted-foreground animate-pulse">Loading map data...</div>;
  }

  if (error || !overview) {
    return <div className="p-8 text-center text-sm font-semibold text-muted-foreground">No data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Geo-Intelligence Platform</h1>
          <p className="text-xs text-muted-foreground">
            Dynamic MapLibre GL OpenStreetMap integration displaying ward boundary polygons, complaint hotspots, heatmap density layers, and surrounding civic assets.
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg w-full max-w-lg">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
            activeTab === "overview"
              ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab("map")}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
            activeTab === "map"
              ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Live Spatial Map
        </button>
      </div>

      <div className="space-y-6">
        {/* TAB 1: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <Card className="p-5 bg-gradient-to-br from-indigo-950 to-slate-950 text-white flex flex-col justify-between border-indigo-500/20">
                  <div>
                    <div className="flex justify-between items-center text-xs text-indigo-300 font-bold uppercase tracking-wider">
                      <span>Derived Health Score</span>
                      <Activity className="h-4 w-4 text-indigo-400" />
                    </div>
                    <div className="flex items-baseline gap-1 mt-4">
                      <span className="text-5xl font-extrabold">{overview.overall_health_score ?? "--"}</span>
                      <span className="text-slate-400 text-xs">/ 100</span>
                    </div>
                  </div>
                  <div className="text-[10px] text-indigo-300 mt-4 leading-normal">
                    Score dynamically derived based on {overview.total_pending_issues || 0} unresolved citizen complaints and priority weightings.
                  </div>
                </Card>

                <Card className="p-5 border-red-500/20 bg-red-500/[0.01] flex flex-col justify-between">
                  {overview.risk_zones && overview.risk_zones.length > 0 ? (
                    <>
                      <div>
                        <span className="text-red-500 font-bold uppercase tracking-wider text-xs flex items-center gap-1">
                          <AlertTriangle className="h-4 w-4" /> Priority Risk Zones
                        </span>
                        <div className="mt-3">
                          <p className="font-bold text-sm text-slate-800 dark:text-slate-200">
                            {overview.risk_zones[0].name}
                          </p>
                          <p className="text-xs text-slate-500 mt-1 leading-normal">
                            {overview.risk_zones[0].reason}
                          </p>
                        </div>
                      </div>
                      <Badge variant="destructive" className="mt-4 justify-center w-full uppercase py-1">
                        {overview.risk_zones[0].risk_rating} Severity Rating
                      </Badge>
                    </>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-sm text-muted-foreground">
                      No active risk zones
                    </div>
                  )}
                </Card>
              </div>

              <Card className="p-5 space-y-4">
                <div className="border-l-4 border-indigo-500 pl-3">
                  <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                    Hotspot Projects
                  </h3>
                </div>
                <div className="space-y-4">
                  {overview.hotspots && overview.hotspots.length > 0 ? (
                    overview.hotspots.map((hs: any, idx: number) => (
                      <div key={idx} className="border p-4 rounded-xl bg-card space-y-3 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-indigo-500/30 transition">
                        <div className="space-y-1 max-w-md">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="font-mono text-[9px]">{hs.category}</Badge>
                            <span className="text-xs text-muted-foreground font-semibold">
                              ({hs.complaints_count} complaints merged)
                            </span>
                          </div>
                          <h4 className="font-extrabold text-sm text-slate-800 dark:text-slate-200 mt-1">
                            {hs.proposed_project?.title || "Unknown Project"}
                          </h4>
                          <p className="text-[11px] text-muted-foreground leading-normal">
                            {hs.proposed_project?.impact || "No description available"}
                          </p>
                        </div>
                        <div className="text-right flex-shrink-0 space-y-2">
                          <p className="text-xs font-bold text-emerald-500">{hs.proposed_project?.estimated_cost || "--"}</p>
                          <Button size="sm" onClick={() => { setSelectedHotspot(hs); setActiveTab("map"); }} className="h-7 text-[10px] gap-1">
                            View on Map <ArrowRight className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-muted-foreground text-center py-4">No data available</div>
                  )}
                </div>
              </Card>
            </div>

            <Card className="p-5 space-y-6">
              <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500">Category Index Details</h3>
              <div className="space-y-4">
                {overview.category_scores && Object.keys(overview.category_scores).length > 0 ? (
                  Object.entries(overview.category_scores).map(([name, score]: any, idx) => (
                    <div key={idx} className="space-y-1.5">
                      <div className="flex justify-between text-xs font-bold">
                        <span className="text-slate-700 dark:text-slate-300 truncate">{name}</span>
                        <span className={score < 70 ? "text-red-500 font-mono" : "text-emerald-500 font-mono"}>
                          {score}/100
                        </span>
                      </div>
                      <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            score < 70 ? "bg-red-500" : "bg-emerald-500"
                          }`}
                          style={{ width: `${score}%` }}
                        />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-sm text-muted-foreground text-center py-4">No category data available</div>
                )}
              </div>
            </Card>
          </div>
        )}

        {/* TAB 2: SPATIAL MAP */}
        {activeTab === "map" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div className="flex flex-col sm:flex-row gap-3">
                <form onSubmit={handleSearch} className="flex-1 flex gap-2">
                  <div className="relative flex-1">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <input
                      type="text"
                      placeholder="Search address or locality..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg pl-9 pr-4 py-2 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                    />
                  </div>
                  <Button type="submit" disabled={searching} className="text-xs h-9 py-0">
                    {searching ? "Searching..." : "Search"}
                  </Button>
                </form>
              </div>

              {searchError && <p className="text-[11px] text-red-500 font-bold">{searchError}</p>}

              <Card className="p-4 bg-slate-50 dark:bg-slate-950/30 border rounded-xl relative min-h-[480px] flex flex-col justify-between overflow-hidden">
                <div className="flex flex-wrap gap-2 z-10">
                  <Button
                    size="sm"
                    variant={showIssuesLayer ? "default" : "outline"}
                    onClick={() => setShowIssuesLayer(!showIssuesLayer)}
                    className="h-7 text-[10px] rounded-full"
                  >
                    Issues ({mapData?.clusters?.length || 0})
                  </Button>
                  <Button
                    size="sm"
                    variant={showHeatmapLayer ? "default" : "outline"}
                    onClick={() => setShowHeatmapLayer(!showHeatmapLayer)}
                    className="h-7 text-[10px] rounded-full"
                  >
                    Heatmap Density
                  </Button>
                  <Button
                    size="sm"
                    variant={showHotspotsLayer ? "default" : "outline"}
                    onClick={() => setShowHotspotsLayer(!showHotspotsLayer)}
                    className="h-7 text-[10px] rounded-full"
                  >
                    Proposed Projects
                  </Button>
                  <Button
                    size="sm"
                    variant={showBoundariesLayer ? "default" : "outline"}
                    onClick={() => setShowBoundariesLayer(!showBoundariesLayer)}
                    className="h-7 text-[10px] rounded-full"
                  >
                    Ward Boundaries
                  </Button>
                </div>

                {mapError ? (
                  <div className="my-6 flex-1 border rounded-xl bg-card border-dashed p-6 flex flex-col justify-center items-center text-center">
                    Map could not be loaded.
                  </div>
                ) : (
                  <div ref={mapRef} className="my-6 flex-1 rounded-xl min-h-[350px] border border-slate-200 dark:border-slate-800 bg-slate-100" />
                )}
              </Card>
            </div>

            <div className="space-y-4">
              {selectedHotspot ? (
                <div className="space-y-4">
                  <Card className="p-5 border-2 border-indigo-500/20 bg-indigo-500/[0.01] space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] text-indigo-500 font-bold uppercase tracking-wider block">Selected Project Hotspot</span>
                      <Badge variant="outline" className="font-mono text-[9px]">{selectedHotspot.category}</Badge>
                    </div>
                    <h3 className="font-extrabold text-md text-slate-800 dark:text-slate-200 border-b pb-2">
                      {selectedHotspot.proposed_project?.title || "Unnamed Project"}
                    </h3>

                    <div className="space-y-3 text-xs">
                      <div className="flex justify-between border-b pb-1.5">
                        <span className="text-slate-500">Merged Complaints:</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">
                          {selectedHotspot.complaints_count} active tickets
                        </span>
                      </div>
                      <div className="flex justify-between border-b pb-1.5">
                        <span className="text-slate-500">Affected Footprint:</span>
                        <span className="font-bold text-indigo-600">
                          {selectedHotspot.affected_population?.toLocaleString("en-IN") || "--"} citizens
                        </span>
                      </div>
                      <div className="flex justify-between border-b pb-1.5">
                        <span className="text-slate-500">Estimated Cost:</span>
                        <span className="font-bold text-emerald-500">
                          {selectedHotspot.proposed_project?.estimated_cost || "--"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Duration:</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">
                          {selectedHotspot.proposed_project?.estimated_duration || "--"}
                        </span>
                      </div>
                    </div>
                  </Card>
                </div>
              ) : (
                <div className="p-8 text-center text-sm font-semibold text-muted-foreground border rounded-xl">
                  Select a hotspot on the map to view details.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
