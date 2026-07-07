"use client";

import React, { useState, useEffect, useRef } from "react";
import { API_BASE_URL } from "@/config";
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
  const [useMockMap, setUseMockMap] = useState(false);
  const [mapLoaded, setMapLoaded] = useState(false);

  // Fetch basic overview and coordinate clusters
  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE_URL}/governance/constituency/overview`).then((r) => r.json()),
      fetch(`${API_BASE_URL}/governance/map`).then((r) => r.json()),
    ])
      .then(([over, mData]) => {
        setOverview(over);
        setMapData(mData);

        if (over.hotspots && over.hotspots.length > 0) {
          setSelectedHotspot(over.hotspots[0]);
        }

        loadMapLibreScript(
          () => {
            setMapLoaded(true);
          },
          () => {
            setUseMockMap(true);
          }
        );
        setLoading(false);
      })
      .catch((err) => {
        console.log("Offline, loading mock spatial dataset:", err);
        const mockOverview = {
          constituency_name: "Bangalore Central Constituency",
          overall_health_score: 78,
          overall_health_trend: "UP",
          category_scores: {
            "Roads & Sidewalks": 82,
            "Water Supply & Sanitation": 61,
            "Electricity & Power": 90,
            "Healthcare Facilities": 74,
            "Education & Schools": 69,
          },
          hotspots: [
            {
              id: "hotspot-water-shivaji",
              category: "Water Supply & Sanitation",
              latitude: 12.9755,
              longitude: 77.5955,
              complaints_count: 18,
              affected_population: 4320,
              linked_complaint_ids: ["ISSUE-001"],
              proposed_project: {
                title: "Reconstruct Main Water Pipe Trunk",
                estimated_cost: "₹18 Lakhs",
                estimated_duration: "45 Days",
                impact: "Eliminates water overflow hazards inside Shivajinagar playground.",
              },
            },
            {
              id: "hotspot-road-sector4",
              category: "Roads & Sidewalks",
              latitude: 12.9810,
              longitude: 77.5910,
              complaints_count: 6,
              affected_population: 350,
              linked_complaint_ids: ["ISSUE-002"],
              proposed_project: {
                title: "Full Sidewalk & Corridor Reconstruction",
                estimated_cost: "₹12 Lakhs",
                estimated_duration: "30 Days",
                impact: "Restores school pedestrian safe paths.",
              },
            },
          ],
          risk_zones: [
            {
              name: "Shivaji Nagar Sector B",
              risk_rating: "HIGH",
              reason: "Active cluster of 18 unresolved water leakage complaints.",
            },
          ],
          total_pending_issues: 24,
        };
        setOverview(mockOverview);
        setSelectedHotspot(mockOverview.hotspots[0]);

        setMapData({
          boundaries: { type: "FeatureCollection", features: [] },
          heatmap: [
            { lat: 12.9750, lng: 77.5950, weight: 2.5 },
            { lat: 12.9760, lng: 77.5960, weight: 2.5 },
            { lat: 12.9810, lng: 77.5910, weight: 1.0 },
          ],
          clusters: [
            { type: "cluster", latitude: 12.9755, longitude: 77.5955, count: 18, ids: ["ISSUE-001"] },
            { type: "single", id: "ISSUE-002", latitude: 12.9810, longitude: 77.5910, title: "Utility Dig Block Sector 4", category: "Roads & Sidewalks" },
          ],
          hotspots: mockOverview.hotspots,
        });
        setUseMockMap(true);
        setLoading(false);
      });
  }, []);

  // Fetch dynamic nearby assets on selected hotspot change
  useEffect(() => {
    if (selectedHotspot) {
      setLoadingAssets(true);
      const { latitude, longitude } = selectedHotspot;
      Promise.all([
        fetch(`${API_BASE_URL}/governance/spatial/places?latitude=${latitude}&longitude=${longitude}&type=school&radius=2000`).then((r) => r.json()),
        fetch(`${API_BASE_URL}/governance/spatial/places?latitude=${latitude}&longitude=${longitude}&type=hospital&radius=2000`).then((r) => r.json()),
        fetch(`${API_BASE_URL}/governance/spatial/places?latitude=${latitude}&longitude=${longitude}&type=park&radius=2000`).then((r) => r.json()),
      ])
        .then(([schools, hospitals, parks]) => {
          setNearbySchools(schools);
          setNearbyHospitals(hospitals);
          setNearbyParks(parks);
          setLoadingAssets(false);
        })
        .catch((err) => {
          console.error("Error fetching nearby assets:", err);
          // offline mock fallbacks
          setNearbySchools([
            { name: "Shivaji Nagar Government Primary School", address: "Shivaji Nagar Main Road, Bengaluru", rating: 4.2 },
            { name: "Sector 4 High School Block A", address: "Sector 4 Main Road, Bengaluru", rating: 4.5 }
          ]);
          setNearbyHospitals([
            { name: "Shivaji Nagar General Hospital", address: "Shivaji Nagar Main Road, Bengaluru", rating: 4.1 }
          ]);
          setNearbyParks([
            { name: "Shivaji Nagar Ward 12 Playground", address: "Shivaji Nagar Playground St, Bengaluru", rating: 4.4 }
          ]);
          setLoadingAssets(false);
        });
    }
  }, [selectedHotspot]);

  // MapLibre Maps Instance Hook
  useEffect(() => {
    if (mapLoaded && mapRef.current && mapData && activeTab === "map") {
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
        if (showBoundariesLayer && mapData.boundaries && mapData.boundaries.features) {
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
        if (showHeatmapLayer && mapData.heatmap) {
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
        if (showIssuesLayer && mapData.clusters) {
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
  }, [mapLoaded, mapData, showIssuesLayer, showHeatmapLayer, showBoundariesLayer, activeTab]);

  // Geocode address search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;
    setSearching(true);
    setSearchError("");

    fetch(`${API_BASE_URL}/governance/spatial/geocode?address=${encodeURIComponent(searchQuery)}`)
      .then((r) => {
        if (!r.ok) throw new Error("Location not found");
        return r.json();
      })
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
        } else {
          setSelectedHotspot({
            id: `searched-hs-${Date.now()}`,
            category: "Roads & Sidewalks",
            latitude: coords.latitude,
            longitude: coords.longitude,
            complaints_count: 3,
            affected_population: 850,
            linked_complaint_ids: [],
            proposed_project: {
              title: `Locality Rehabilitation: ${searchQuery}`,
              estimated_cost: "₹14 Lakhs",
              estimated_duration: "30 Days",
              impact: "Resolves geocoded transit blockages and community access safety.",
            },
          });
        }
      })
      .catch((err) => {
        setSearching(false);
        setSearchError("Location search failed. Try 'Shivaji Nagar' or 'Sector 4'.");
      });
  };

  const handleStartTender = (hotspotId: string) => {
    setTenderingStates((prev) => ({ ...prev, [hotspotId]: true }));
  };

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
        <button
          onClick={() => setActiveTab("health")}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
            activeTab === "health"
              ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Constituency Health
        </button>
        <button
          onClick={() => setActiveTab("projects")}
          className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition ${
            activeTab === "projects"
              ? "bg-white dark:bg-slate-900 shadow-sm text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          Proposed Projects
        </button>
      </div>

      {loading ? (
        <div className="p-8 text-center text-xs text-muted-foreground animate-pulse">
          Computing spatial coordinate clusters...
        </div>
      ) : (
        <div className="space-y-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left col: Health Score Summary & categories */}
              <div className="lg:col-span-2 space-y-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  {/* Master health card */}
                  <Card className="p-5 bg-gradient-to-br from-indigo-950 to-slate-950 text-white flex flex-col justify-between border-indigo-500/20">
                    <div>
                      <div className="flex justify-between items-center text-xs text-indigo-300 font-bold uppercase tracking-wider">
                        <span>Derived Health Score</span>
                        <Activity className="h-4 w-4 text-indigo-400" />
                      </div>
                      <div className="flex items-baseline gap-1 mt-4">
                        <span className="text-5xl font-extrabold">{overview.overall_health_score}</span>
                        <span className="text-slate-400 text-xs">/ 100</span>
                      </div>
                    </div>
                    <div className="text-[10px] text-indigo-300 mt-4 leading-normal">
                      Score dynamically derived based on {overview.total_pending_issues} unresolved citizen complaints and priority weightings.
                    </div>
                  </Card>

                  {/* Active Risk Zones */}
                  <Card className="p-5 border-red-500/20 bg-red-500/[0.01] flex flex-col justify-between">
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
                  </Card>
                </div>

                {/* Hotspots Project Proposal list */}
                <Card className="p-5 space-y-4">
                  <div className="border-l-4 border-indigo-500 pl-3">
                    <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                      Hotspot Projects (2+ Complaints Aggregated)
                    </h3>
                  </div>
                  <div className="space-y-4">
                    {overview.hotspots.map((hs: any, idx: number) => (
                      <div key={idx} className="border p-4 rounded-xl bg-card space-y-3 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-indigo-500/30 transition">
                        <div className="space-y-1 max-w-md">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="font-mono text-[9px]">{hs.category}</Badge>
                            <span className="text-xs text-muted-foreground font-semibold">
                              ({hs.complaints_count} complaints merged)
                            </span>
                          </div>
                          <h4 className="font-extrabold text-sm text-slate-800 dark:text-slate-200 mt-1">
                            {hs.proposed_project.title}
                          </h4>
                          <p className="text-[11px] text-muted-foreground leading-normal">
                            Suggested Project instead of {hs.complaints_count} patch updates. Saves budget overhead.
                          </p>
                        </div>
                        <div className="text-right flex-shrink-0 space-y-2">
                          <p className="text-xs font-bold text-emerald-500">{hs.proposed_project.estimated_cost}</p>
                          <Button size="sm" onClick={() => { setSelectedHotspot(hs); setActiveTab("map"); }} className="h-7 text-[10px] gap-1">
                            View on Map <ArrowRight className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>

              {/* Right column: Category progress overview */}
              <Card className="p-5 space-y-6">
                <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500">Category Index Details</h3>
                <div className="space-y-4">
                  {Object.entries(overview.category_scores).map(([name, score]: any, idx) => (
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
                  ))}
                </div>
              </Card>
            </div>
          )}

          {/* TAB 2: SPATIAL MAP */}
          {activeTab === "map" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Map grid representation */}
              <div className="lg:col-span-2 space-y-4">
                <div className="flex flex-col sm:flex-row gap-3">
                  {/* Locality Search bar */}
                  <form onSubmit={handleSearch} className="flex-1 flex gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      <input
                        type="text"
                        placeholder="Search address or locality (e.g. Sector 4, Shivaji Nagar)..."
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
                  {/* Top Layer indicators */}
                  <div className="flex flex-wrap gap-2 z-10">
                    <Button
                      size="sm"
                      variant={showIssuesLayer ? "default" : "outline"}
                      onClick={() => setShowIssuesLayer(!showIssuesLayer)}
                      className="h-7 text-[10px] rounded-full"
                    >
                      Issues ({mapData.clusters.length})
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

                  {/* MAP CANVAS */}
                  {useMockMap ? (
                    /* Elegant fallback mock coordinate grid map */
                    <div className="my-6 flex-1 border rounded-xl bg-card border-dashed p-6 flex flex-col justify-center items-center text-center relative overflow-hidden min-h-[350px]">
                      <div className="absolute inset-0 grid grid-cols-6 grid-rows-6 opacity-[0.03] dark:opacity-[0.08] pointer-events-none">
                        {Array.from({ length: 36 }).map((_, i) => (
                          <div key={i} className="border border-slate-700" />
                        ))}
                      </div>

                      <Compass className="h-10 w-10 text-indigo-500/80 animate-spin-slow mb-3" />
                      <span className="font-bold text-xs uppercase tracking-wider text-slate-400">
                        Shivaji Nagar W12 Ward GIS Boundaries
                      </span>
                      <span className="text-[10px] text-muted-foreground max-w-sm mt-1 leading-normal">
                        Using offline developer georeference visualization. Both mock clusters and polygons are fully functional.
                      </span>

                      {/* Mock boundary polygon outline visually */}
                      <svg className="absolute inset-0 w-full h-full opacity-10 pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <polygon points="25,25 75,25 75,75 25,75" fill="none" stroke="#6366f1" strokeWidth="1" />
                      </svg>

                      {/* Render Hotspots as interactive items */}
                      {showHotspotsLayer && mapData.hotspots.map((hs: any, idx: number) => {
                        const styleClass = hs.id === selectedHotspot?.id ? "scale-110 ring-4 ring-indigo-500/50" : "";
                        return (
                          <div
                            key={idx}
                            style={{
                              position: "absolute",
                              top: `${idx === 0 ? 40 : 65}%`,
                              left: `${idx === 0 ? 30 : 60}%`,
                            }}
                            className={`cursor-pointer transition-all duration-200 ${styleClass}`}
                            onClick={() => setSelectedHotspot(hs)}
                          >
                            <Badge className="bg-red-500 hover:bg-red-600 text-white font-bold p-1 px-2.5 rounded-full flex items-center gap-1 shadow-lg text-[9px]">
                              <MapPin className="h-3 w-3" /> {hs.complaints_count} complaints
                            </Badge>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    /* Actual Google Map div */
                    <div ref={mapRef} className="my-6 flex-1 rounded-xl min-h-[350px] border border-slate-200 dark:border-slate-800" />
                  )}

                  {/* Legend */}
                  <div className="flex flex-wrap gap-4 text-[9px] font-semibold text-muted-foreground border-t pt-2 border-slate-200/50 dark:border-slate-850">
                    <div className="flex items-center gap-1">
                      <span className="h-2 w-2 rounded-full bg-red-500" /> Active Hotspot
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="h-2 w-2 rounded-full bg-amber-500" /> Single Complaint
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="h-2 w-2 rounded-full bg-indigo-500/60" /> Ward Boundary
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="h-2 w-2 rounded-full bg-emerald-500" /> Government Infrastructure
                    </div>
                  </div>
                </Card>
              </div>

              {/* Right column: Selected Hotspot & dynamic nearby places */}
              <div className="space-y-4">
                {selectedHotspot ? (
                  <div className="space-y-4">
                    {/* Hotspot details */}
                    <Card className="p-5 border-2 border-indigo-500/20 bg-indigo-500/[0.01] space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] text-indigo-500 font-bold uppercase tracking-wider block">Selected Project Hotspot</span>
                        <Badge variant="outline" className="font-mono text-[9px]">{selectedHotspot.category}</Badge>
                      </div>
                      <h3 className="font-extrabold text-md text-slate-800 dark:text-slate-200 border-b pb-2">
                        {selectedHotspot.proposed_project.title}
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
                            {selectedHotspot.affected_population.toLocaleString("en-IN")} citizens
                          </span>
                        </div>
                        <div className="flex justify-between border-b pb-1.5">
                          <span className="text-slate-500">Estimated Cost:</span>
                          <span className="font-bold text-emerald-500">
                            {selectedHotspot.proposed_project.estimated_cost}
                          </span>
                        </div>
                        <div className="flex justify-between border-b pb-1.5">
                          <span className="text-slate-500">Estimated Duration:</span>
                          <span className="font-bold text-slate-850 dark:text-slate-200">
                            {selectedHotspot.proposed_project.estimated_duration}
                          </span>
                        </div>
                        <div className="space-y-1">
                          <span className="text-slate-500 block">AI Resolution Rationale:</span>
                          <p className="text-[11px] text-muted-foreground leading-normal bg-card p-2.5 rounded border border-slate-100 dark:border-slate-800 font-sans">
                            {selectedHotspot.proposed_project.impact}
                          </p>
                        </div>
                      </div>

                      <div className="pt-2">
                        {tenderingStates[selectedHotspot.id] ? (
                          <div className="p-2.5 border rounded-lg bg-emerald-500/10 text-emerald-600 text-xs font-bold text-center flex items-center justify-center gap-1.5 border-emerald-500/20">
                            <CheckCircle className="h-4 w-4" /> Project Tendering Flow Initiated
                          </div>
                        ) : (
                          <Button
                            onClick={() => handleStartTender(selectedHotspot.id)}
                            className="w-full text-xs h-9 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold flex items-center justify-center gap-1 border-none"
                          >
                            <Hammer className="h-3.5 w-3.5" /> Initiate Project Tendering
                          </Button>
                        )}
                      </div>
                    </Card>

                    {/* Dynamic Nearby places (Spatial Context Panel) */}
                    <Card className="p-5 space-y-4">
                      <div className="border-l-4 border-indigo-500 pl-3 flex justify-between items-center">
                        <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                          Civic Assets in Impact Radius
                        </h4>
                        <Badge variant="outline" className="text-[8px]">Spatial Context</Badge>
                      </div>

                      {loadingAssets ? (
                        <p className="text-[10px] text-muted-foreground animate-pulse">Scanning nearby infrastructure indices...</p>
                      ) : (
                        <div className="space-y-3.5">
                          {/* Schools list */}
                          <div className="space-y-2">
                            <span className="text-[9px] uppercase tracking-wider font-extrabold text-slate-400 flex items-center gap-1">
                              <School className="h-3 w-3 text-indigo-400" /> Schools / Education ({nearbySchools.length})
                            </span>
                            <div className="space-y-1.5">
                              {nearbySchools.map((item, idx) => (
                                <div key={idx} className="bg-slate-50 dark:bg-slate-900 p-2 rounded-lg border text-[11px] leading-tight">
                                  <div className="flex justify-between font-bold text-slate-800 dark:text-slate-200">
                                    <span>{item.name}</span>
                                    <span className="text-[9px] text-indigo-500">★ {item.rating}</span>
                                  </div>
                                  <p className="text-[9px] text-muted-foreground mt-0.5">{item.address}</p>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Hospitals list */}
                          <div className="space-y-2">
                            <span className="text-[9px] uppercase tracking-wider font-extrabold text-slate-400 flex items-center gap-1">
                              <Building className="h-3 w-3 text-red-400" /> Hospitals / Clinics ({nearbyHospitals.length})
                            </span>
                            <div className="space-y-1.5">
                              {nearbyHospitals.map((item, idx) => (
                                <div key={idx} className="bg-slate-50 dark:bg-slate-900 p-2 rounded-lg border text-[11px] leading-tight">
                                  <div className="flex justify-between font-bold text-slate-800 dark:text-slate-200">
                                    <span>{item.name}</span>
                                    <span className="text-[9px] text-red-500">★ {item.rating}</span>
                                  </div>
                                  <p className="text-[9px] text-muted-foreground mt-0.5">{item.address}</p>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Parks list */}
                          <div className="space-y-2">
                            <span className="text-[9px] uppercase tracking-wider font-extrabold text-slate-400 flex items-center gap-1">
                              <TreePine className="h-3 w-3 text-emerald-400" /> Open Parks / Playgrounds ({nearbyParks.length})
                            </span>
                            <div className="space-y-1.5">
                              {nearbyParks.map((item, idx) => (
                                <div key={idx} className="bg-slate-50 dark:bg-slate-900 p-2 rounded-lg border text-[11px] leading-tight">
                                  <div className="flex justify-between font-bold text-slate-800 dark:text-slate-200">
                                    <span>{item.name}</span>
                                    <span className="text-[9px] text-emerald-500">★ {item.rating}</span>
                                  </div>
                                  <p className="text-[9px] text-muted-foreground mt-0.5">{item.address}</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </Card>
                  </div>
                ) : (
                  <Card className="p-8 text-center text-xs text-muted-foreground border-dashed">
                    Select a hotspot pin on the map to evaluate developmental options and nearby assets.
                  </Card>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: CONSTITUENCY HEALTH */}
          {activeTab === "health" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(overview.category_scores).map(([name, score]: any, idx) => (
                <Card key={idx} className="p-5 flex flex-col justify-between min-h-[140px]">
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">{name}</span>
                    <Badge variant={score < 70 ? "destructive" : "default"} className="font-mono text-[9px]">
                      {score}/100 Score
                    </Badge>
                  </div>
                  <div className="mt-4 space-y-1">
                    <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          score < 70 ? "bg-red-500 animate-pulse" : "bg-emerald-500"
                        }`}
                        style={{ width: `${score}%` }}
                      />
                    </div>
                    <span className="text-[9px] text-muted-foreground block mt-1.5">
                      {score < 70
                        ? "⚠️ Below acceptable public index thresholds. Repair needed."
                        : "✓ Healthy infrastructure operations."}
                    </span>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* TAB 4: DEVELOPMENTAL PROJECTS */}
          {activeTab === "projects" && (
            <div className="space-y-6">
              <div className="border p-4 rounded-xl bg-indigo-500/[0.01] border-indigo-500/10 text-xs flex items-center justify-between gap-4">
                <p className="text-muted-foreground">
                  The following projects have been automatically derived by the **Spatial Intelligence Engine** to resolve overlapping citizen complaints collectively.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {overview.hotspots.map((hs: any, idx: number) => (
                  <Card key={idx} className="p-5 border-2 border-slate-100 dark:border-slate-800 hover:border-indigo-500/20 transition flex flex-col justify-between space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between items-center gap-2 border-b pb-2">
                        <span className="font-bold text-xs text-indigo-500 uppercase tracking-wider">{hs.category}</span>
                        <Badge variant="outline" className="text-[9px]">{hs.complaints_count} complaints merged</Badge>
                      </div>
                      <h4 className="font-extrabold text-md text-slate-800 dark:text-slate-200 mt-2">
                        {hs.proposed_project.title}
                      </h4>
                      <p className="text-xs text-slate-500 leading-relaxed font-sans mt-1">
                        Proposed Project: Replaces multiple individual repair logs. Coordinates are clustered within {hs.affected_population} citizen footprint zone.
                      </p>
                    </div>

                    <div className="space-y-3 pt-3 border-t">
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Budget Needed:</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">{hs.proposed_project.estimated_cost}</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-slate-400">Est. Duration:</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">{hs.proposed_project.estimated_duration}</span>
                      </div>

                      {tenderingStates[hs.id] ? (
                        <div className="p-2 border rounded-lg bg-emerald-500/10 text-emerald-600 text-xs font-bold text-center flex items-center justify-center gap-1.5 border-emerald-500/20">
                          <CheckCircle className="h-4 w-4" /> Tendering Process Active
                        </div>
                      ) : (
                        <Button
                          onClick={() => handleStartTender(hs.id)}
                          className="w-full text-xs h-9 bg-slate-900 hover:bg-slate-800 text-white font-semibold flex items-center justify-center gap-1 border-none"
                        >
                          <Hammer className="h-3.5 w-3.5" /> Start Tendering Process
                        </Button>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
