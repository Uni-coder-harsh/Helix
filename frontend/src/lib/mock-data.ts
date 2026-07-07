export interface IssueUpdate {
  timestamp: string;
  status: string;
  note: string;
  author: string;
}

export interface Issue {
  id: string;
  title: string;
  description: string;
  category: string;
  status: "Submitted" | "Validated" | "Assigned" | "In_Progress" | "Completed";
  priority: "Critical" | "High" | "Medium" | "Low";
  citizenName: string;
  createdAt: string;
  updatedAt: string;
  constituency: string;
  location: { lat: number; lng: number };
  upvotes: number;
  updates: IssueUpdate[];
  aiDraftResponse?: string;
  assignedUnit?: string;
}

export const mockIssues: Issue[] = [
  {
    id: "ISS-1001",
    title: "Potable Water Pipeline Leakage",
    description: "Main supply pipeline leaking near Gate 3 of Sector 4 Central Park. Thousands of liters of water being wasted daily. Water pressure in nearby blocks has decreased.",
    category: "Water Supply & Sanitation",
    status: "In_Progress",
    priority: "High",
    citizenName: "Ramesh Kumar",
    createdAt: "2026-07-05T09:30:00Z",
    updatedAt: "2026-07-06T11:15:00Z",
    constituency: "East Bengaluru",
    location: { lat: 12.9716, lng: 77.6412 },
    upvotes: 84,
    assignedUnit: "Water Supply Maintenance Unit B",
    updates: [
      {
        timestamp: "2026-07-05T09:30:00Z",
        status: "Submitted",
        note: "Issue reported by citizen via web application with location pins.",
        author: "Ramesh Kumar (Citizen)"
      },
      {
        timestamp: "2026-07-05T14:20:00Z",
        status: "Validated",
        note: "AI analysis and image comparison validated water wastage. Geolocation matches municipal utility plan.",
        author: "AI Validator Service"
      },
      {
        timestamp: "2026-07-06T09:00:00Z",
        status: "Assigned",
        note: "Assigned to East District Municipal Engineering Team B.",
        author: "Workflow Coordinator"
      },
      {
        timestamp: "2026-07-06T11:15:00Z",
        status: "In_Progress",
        note: "Excavation and pipe replacement team dispatched. Expected repair duration is 6 hours.",
        author: "Officer Suresh Rao"
      }
    ],
    aiDraftResponse: "We have acknowledged the potable water pipeline leak at Sector 4 Central Park. Maintenance Unit B is currently on-site performing pipe sleeve replacement. Supply pressure will be restored shortly."
  },
  {
    id: "ISS-1002",
    title: "Water Logging at Metro Construction Junction",
    description: "Severe water logging under the Metro Pillar 142 junction after last night's rainfall. Traffic is gridlocked. No storm water drainage outlet is visible.",
    category: "Stormwater Drainage",
    status: "Submitted",
    priority: "Critical",
    citizenName: "Priya Murthy",
    createdAt: "2026-07-06T06:00:00Z",
    updatedAt: "2026-07-06T06:05:00Z",
    constituency: "Central Bengaluru",
    location: { lat: 12.9421, lng: 77.5910 },
    upvotes: 142,
    updates: [
      {
        timestamp: "2026-07-06T06:00:00Z",
        status: "Submitted",
        note: "Citizen reported via WhatsApp with photos and high upvote score.",
        author: "Priya Murthy (Citizen)"
      }
    ],
    aiDraftResponse: "Critical water logging flagged at Pillar 142 Metro Junction. The Decision Intelligence Service has suggested dispatching a high-capacity pump to drain the underpass, as traffic volume is 140% above normal capacity."
  },
  {
    id: "ISS-1003",
    title: "Streetlight Outages on Outer Ring Road",
    description: "A continuous stretch of 8 streetlights is non-functional, making the highway extremely dangerous for night commuters, especially two-wheelers.",
    category: "Public Lighting",
    status: "Validated",
    priority: "Medium",
    citizenName: "Anil Deshmukh",
    createdAt: "2026-07-04T18:45:00Z",
    updatedAt: "2026-07-05T08:00:00Z",
    constituency: "East Bengaluru",
    location: { lat: 12.9852, lng: 77.6724 },
    upvotes: 31,
    updates: [
      {
        timestamp: "2026-07-04T18:45:00Z",
        status: "Submitted",
        note: "Issue logged with street numbers.",
        author: "Anil Deshmukh (Citizen)"
      },
      {
        timestamp: "2026-07-05T08:00:00Z",
        status: "Validated",
        note: "Validated against utility grid status. confirmed blackout zone.",
        author: "AI Grid Monitor"
      }
    ],
    aiDraftResponse: "Outer Ring Road streetlight segment validated. Dispatch order suggested for Grid Replacement Contractor."
  },
  {
    id: "ISS-1004",
    title: "Uncollected Municipal Solid Waste",
    description: "Garbage sorting bins have not been cleared for 4 days. Strong odor and stray animals spreading waste onto pedestrian pathways.",
    category: "Solid Waste Management",
    status: "Completed",
    priority: "Medium",
    citizenName: "Preeti Sinha",
    createdAt: "2026-07-03T07:00:00Z",
    updatedAt: "2026-07-05T15:30:00Z",
    constituency: "South Bengaluru",
    location: { lat: 12.9112, lng: 77.5621 },
    upvotes: 18,
    assignedUnit: "Waste Clearance Unit 7",
    updates: [
      {
        timestamp: "2026-07-03T07:00:00Z",
        status: "Submitted",
        note: "Garbage overflow reported.",
        author: "Preeti Sinha (Citizen)"
      },
      {
        timestamp: "2026-07-03T11:00:00Z",
        status: "Validated",
        note: "Image validation confirms excessive pileup.",
        author: "AI Image Triage"
      },
      {
        timestamp: "2026-07-04T09:30:00Z",
        status: "Assigned",
        note: "Assigned to Waste Clearance Unit 7.",
        author: "System Dispatcher"
      },
      {
        timestamp: "2026-07-05T14:00:00Z",
        status: "In_Progress",
        note: "Compactor truck on route.",
        author: "Driver Rajesh"
      },
      {
        timestamp: "2026-07-05T15:30:00Z",
        status: "Completed",
        note: "Bins emptied and site disinfected. Geotagged verification photo uploaded.",
        author: "Waste Clearance Unit 7"
      }
    ],
    aiDraftResponse: "Waste accumulation cleared successfully. Geotagged photograph verified."
  }
];

export const mockAnalytics = {
  totalIssuesCount: 423,
  resolvedCount: 310,
  activeCount: 113,
  criticalCount: 12,
  averageResolutionDays: 2.4,
  issuesByCategory: [
    { name: "Water Supply", count: 120, pct: 28 },
    { name: "Roads & Traffic", count: 180, pct: 43 },
    { name: "Solid Waste", count: 73, pct: 17 },
    { name: "Lighting", count: 50, pct: 12 }
  ],
  trends: [
    { month: "Jan", reported: 80, resolved: 70 },
    { month: "Feb", reported: 95, resolved: 85 },
    { month: "Mar", reported: 110, resolved: 95 },
    { month: "Apr", reported: 140, resolved: 120 },
    { month: "May", reported: 175, resolved: 150 },
    { month: "Jun", reported: 220, resolved: 190 }
  ],
  efficiencyByWard: [
    { ward: "Ward 12 (Central)", avgDays: 1.8, count: 85 },
    { ward: "Ward 25 (East)", avgDays: 2.9, count: 130 },
    { ward: "Ward 45 (South)", avgDays: 2.1, count: 98 },
    { ward: "Ward 88 (North)", avgDays: 3.4, count: 110 }
  ]
};
