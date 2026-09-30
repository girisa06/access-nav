# INNOTHON26 — AccessiNav
## Accessible Transit App | 24-Hour Hackathon Build Plan

**Competition:** INNOTHON26 (INNOCOM) — "Inspire to Innovate"  
**Track:** Web & App Development with Cloud  
**Team:** Giri (Backend), Rajarajan (UI Design), Shubh (Frontend)  
**Problem:** Accessible transit routing for People with Disabilities

---

## PLATFORM SPECIFICATION ⭐

### Core Platform
- **Responsive Web App (React SPA)** — Deployed to Vercel
- **Progressive Web App (PWA)** — Installable from browser (iOS Safari + Android Chrome)
- **No native mobile build** — Web app only, BUT installable like a native app
- **No offline-first** — Online-first with graceful offline fallback (Phase 2)
- **Web Speech + TTS** — Deferred to Phase 1 (post-hackathon)

### Installation Flow (Judge Demo)
```
User opens link on phone
  ↓
Hamburger menu (≡) or browser prompt
  ↓
"Install app" button appears
  ↓
App installed on home screen
  ↓
Opens full-screen (looks like native app)
```

### Tech Stack
```
FRONTEND (Shubh → Vercel)
├── React 18 + Vite
├── Tailwind CSS + Shadcn/ui
├── Service Worker + PWA manifest (offline cache, installable)
├── Mapbox GL JS (routing + map tiles)
├── Supabase JS client (real-time subscriptions)
└── lucide-react, react-hook-form, Cloudinary

BACKEND (Giri → Railway)
├── FastAPI (core APIs + business logic)
├── GTFS-RT bindings (real-time transit data)
├── Route Service (step-free routing graph)
├── Alerts Service (real-time notifications)
└── SOS Handler (location + alert sharing)

DATA & INTEGRATIONS
├── PostgreSQL (Supabase) — routes, reports, users
├── Redis (Upstash) — live alerts cache, real-time subscriptions
├── GTFS-RT Feed — Chennai Metro + transit agencies (real-time)
├── Mapbox Directions API — routing
└── Cloudinary — photo uploads
```

---

## PRODUCT: AccessiNav

### 5 Screens (Mobile-Optimized, PWA-Ready)
1. **AuthChoice** — User / Volunteer / NGO selector
2. **Login/SignUp** — Universal email auth (all roles)
3. **Home** — Disability type selector (Wheelchair, Visual, Hearing, Cognitive)
4. **Search** — Start point → End point → Find routes
5. **Results/Map** — Accessible routes + live transit updates + community reports
6. **Report Form** — Submit accessibility report (photo + description)
7. **VolunteerDashboard** — Pending reports → Verify/Reject
8. **NgoDashboard** — Bulk verification + leaderboard

### Trust Hierarchy (3-Tier Badge System)
```
👤 User Report (gray badge)      → Community upvoted (≥3)
✅ Volunteer Verified (blue)     → Individual verified
✅ NGO Verified (green)          → Organization, highest trust
```

### Core Features
- **Real-time Transit Updates** — GTFS-RT integration (live vehicle positions, delays)
- **Accessible Routes Only** — Step-free, elevator, accessible stops
- **Community Verification** — Users report → Volunteers/NGOs verify → Badge awarded
- **Real-time Sync** — <150ms updates across all users (Supabase subscriptions)
- **SOS Button** — Fixed red button, triggers NGO alert with location
- **PWA Install** — Add to home screen from any browser
- **Offline Fallback** — Cached routes available if offline (Phase 2)

### Scope (Hackathon)
- **Primary disability:** Wheelchair / Mobility
- **Secondary UI:** Visual, Hearing, Cognitive (shown in UI, not fully functional)
- **Geography:** Chennai only
- **Users tested:** Regular user, Volunteer, NGO

---

## 5-PHASE 24-HOUR WORKFLOW

### Phase 1: Setup & Deployment (Hours 0–1)

**Giri (Backend):**
- [ ] Create Supabase project + enable real-time on all tables
- [ ] Create PostgreSQL tables (users, volunteers, ngos, reports, sos_alerts)
- [ ] Create FastAPI skeleton (main.py, auth endpoints, health check)
- [ ] Configure GTFS-RT feed parser (Chennai Metro)
- [ ] Deploy to Railway + test health endpoint
- [ ] Create `.env` template (Supabase URL, API key, Mapbox key, etc.)

**Rajarajan (UI Design):**
- [ ] Create Figma design system (colors, typography, spacing)
- [ ] Design AuthChoice screen
- [ ] Design Home screen (disability selector)
- [ ] Create component specs (props, states, sizes)

**Shubh (Frontend):**
- [ ] Scaffold React + Vite + Tailwind + Shadcn/ui on Vercel
- [ ] Create `public/manifest.json` (PWA manifest with icons)
- [ ] Create `src/serviceWorker.js` (basic cache strategy)
- [ ] Add Service Worker registration to `src/main.jsx`
- [ ] Add PWA meta tags to `index.html`
- [ ] Create project structure (components, pages, lib, constants)
- [ ] Deploy skeleton to Vercel

**All:**
- [ ] Sync on API contracts (locked in below)
- [ ] Create 2 GitHub repos (frontend + backend)
- [ ] Get API keys: Mapbox, Supabase, Cloudinary, Redis
- [ ] Sync on design system + component structure

**✅ Hour 1 Checkpoint:** All three services deployed + API contracts locked

---

### Phase 2: Parallel Build (Hours 2–6) — NO WAITING

**Giri (Backend):**
- [ ] `POST /api/auth/register` → create user/volunteer/ngo
- [ ] `POST /api/auth/login` → return JWT + user_type
- [ ] `GET /api/routes?start&end&disability` → Query accessible routes (GTFS-RT)
- [ ] `GET /api/reports?lat&lon` → Fetch nearby accessibility reports
- [ ] `POST /api/reports` → Create new report
- [ ] `POST /api/reports/{id}/upvote` → Upvote report
- [ ] `POST /api/reports/{id}/verify` → Volunteer/NGO verify
- [ ] `GET /api/dashboard/pending-reports` → Volunteer dashboard
- [ ] `POST /api/sos` → Create SOS alert
- [ ] `GET /api/health` → Health check
- [ ] Deploy all endpoints to Railway
- [ ] Test with curl / Postman

**Rajarajan (UI Design):**
- [ ] Design all 5 screens in Figma
- [ ] Document component structure (RouteCard, ReportCard, SOSButton, etc.)
- [ ] Create button states (hover, active, disabled)
- [ ] Design verification badges (user, volunteer, ngo)
- [ ] Design VolunteerDashboard tabs (Pending, Verified, Leaderboard)

**Shubh (Frontend):**
- [ ] Create all components with mock data (NO waiting for Giri):
  - DisabilitySelector.jsx, RouteCard.jsx, ReportCard.jsx, SOSButton.jsx
  - VolunteerDashboard.jsx, NgoDashboard.jsx, ReportForm.jsx
  - Map component (Mapbox GL JS)
- [ ] Create all page components (AuthChoice, Login, SignUp, Home, Search, Results, etc.)
- [ ] Create `src/lib/constants.js` with MOCK_ROUTES, MOCK_REPORTS, MOCK_DISABILITIES
- [ ] Create `src/lib/api.js` (API calls + mock fallback)
- [ ] Wire all pages together with React Router
- [ ] Test navigation on mobile (responsive)
- [ ] Deploy to Vercel (with mock data)

**Mock Data Strategy:**
```javascript
// constants.js
export const MOCK_ROUTES = [
  { id: 1, mode: 'Metro', duration: '12 min', distance: '5.2 km', 
    accessible: true, steps: 0, stops: 3 },
  // ...
];

export const MOCK_REPORTS = [
  { id: 1, description: 'Lift broken', upvotes: 5, 
    report_source: 'user', verification_status: 'unverified' },
  // ...
];

// api.js
export const fetchRoutes = async (start, end, disability) => {
  try {
    return await fetch(`${API_URL}/routes?...`).then(r => r.json());
  } catch {
    return MOCK_ROUTES; // Fallback
  }
};
```

**✅ Hour 6 Checkpoint:** All APIs working + All components built (mock data) + Deployed

---

### Phase 3: Integration (Hours 6–14)

**Giri (Backend):**
- [ ] Implement Supabase real-time subscriptions (reports, sos_alerts)
- [ ] Add Redis caching for routes (GTFS-RT updates every 30s)
- [ ] Implement verification badge logic (user → volunteer/ngo → verified_by_type)
- [ ] Add error handling + response middleware
- [ ] Test real-time sync (two devices, submit report on one → appears on both)

**Shubh (Frontend):**
- [ ] Replace mock API calls with real endpoints (api.js)
- [ ] Wire Supabase real-time listeners (on reports, sos_alerts)
- [ ] Test two phones side-by-side (real-time verification)
- [ ] Add loading states + error handling
- [ ] Implement toast notifications (success, error)
- [ ] Test PWA installation on real phone (add to home screen)
- [ ] Test offline fallback (disable network → cached routes still load)

**Rajarajan:**
- [ ] Review component specs against Shubh's implementation
- [ ] Minor design tweaks (colors, spacing, icon sizes)

**Testing:**
- [ ] End-to-end: User login → Search route → See live updates → Submit report
- [ ] Volunteer flow: Login as volunteer → Dashboard → Verify report → Badge appears on user's phone (real-time)
- [ ] NGO flow: Same as volunteer, but different badge color
- [ ] SOS: Submit SOS → Alert triggered → Shown to NGOs
- [ ] PWA: Install app on phone → Open from home screen → All features work

**✅ Hour 12 Checkpoint:** Fully integrated + real-time sync working + PWA installable

---

### Phase 4: Polish & Performance (Hours 14–18)

**Shubh (Frontend):**
- [ ] Mobile testing on real device:
  - Touch targets ≥48px
  - No zoom required
  - Fonts ≥16px
  - Tap all buttons, scroll, submit forms
- [ ] Performance optimization:
  - Lighthouse audit → target >80
  - Image compression (<50KB each)
  - Code splitting (React.lazy for pages)
  - Remove console logs
- [ ] Accessibility audit (WCAG AA):
  - Focus indicators visible
  - Color contrast 4.5:1 (text on background)
  - All form labels associated
  - Screen reader tested
- [ ] PWA refinement:
  - Update manifest.json with correct app name/icons
  - Service Worker caching strategy (stale-while-revalidate)
  - Test install on iPhone (Safari) + Android (Chrome)
- [ ] Error handling:
  - API failures → show error toast + retry button
  - Network offline → show "Offline mode" banner
  - Form validation → inline error messages

**Giri (Backend):**
- [ ] Load testing (simulate 100+ concurrent users)
- [ ] Database query optimization
- [ ] Error handling + logging
- [ ] CORS configuration (allow Vercel domain)

**Rajarajan:**
- [ ] Final design review
- [ ] Dark mode toggle (optional, if time permits)

**✅ Hour 18 Checkpoint:** Polished + performant + PWA tested + accessibility pass

---

### Phase 5: Demo Prep & Submission (Hours 18–24)

**Hours 18–19: Backup Demo Video**
- [ ] Screen record 5-min demo (start-to-finish user flow)
- [ ] Show: Login → Search → Results with real-time updates → Verify as volunteer → Badge appears → SOS
- [ ] Upload to Google Drive (link in README)
- [ ] Test video plays on laptop before submission

**Hours 19–21: Practice Pitch (3 min)**
- [ ] **Giri:** Problem statement + team intro (0:00–0:30)
- [ ] **Shubh:** Live demo on phone (0:30–1:30)
  - Open Vercel link → Install app → Show home screen icon
  - Search route → See real-time transit updates (GTFS-RT)
  - Submit report → Real-time verification → Badge appears
  - SOS demo
- [ ] **Rajarajan:** Design + accessibility (1:30–2:00)
- [ ] **Giri:** Close + key takeaway (2:00–2:50)
- [ ] Practice twice with timer

**Hours 21–22: Prepare Submission Files**
- [ ] Update README.md:
  - Problem statement
  - Tech stack
  - Features implemented
  - How to run locally (if needed)
  - Links: Vercel (live), GitHub (frontend + backend), Figma design
- [ ] Create `.pptx` slide deck:
  - Slide 1: Problem + accessibility crisis (stat)
  - Slide 2: Solution overview
  - Slide 3: Key features (real-time, verification, PWA)
  - Slide 4: Tech architecture (frontend/backend/data)
  - Slide 5: Demo walkthrough (screenshots)
  - Slide 6: Roadmap (5 phases to profitability)
  - Slide 7: Thank you + call to action
- [ ] Create submission folder with all links

**Hours 22–23: Submit to Portal**
- [ ] Upload .pptx + README to hackathon portal
- [ ] Submit links: Vercel, GitHub repos, Figma, demo video
- [ ] Confirm submission received

**Hours 23–24: Live Demo Rehearsal**
- [ ] Set up demo phone (charge fully, test WiFi)
- [ ] Verify app loads from Vercel link
- [ ] Test PWA installation
- [ ] Final run-through of pitch
- [ ] If live demo crashes → Play backup video

**✅ Hour 24 Checkpoint:** Submitted + rehearsed + ready for live demo

---

## API CONTRACTS (Locked In — Do Not Change)

```javascript
// Authentication
POST /api/auth/register
  Request:  { email, password, user_type, name?, organization_name? }
  Response: { user_id, email, user_type, token }

POST /api/auth/login
  Request:  { email, password }
  Response: { user_id, email, user_type, token }

// Routes (with GTFS-RT real-time)
GET /api/routes?start=lat,lon&end=lat,lon&disability=wheelchair
  Response: { 
    routes: [
      { 
        id, mode, duration, distance, accessible, steps, stops,
        realtime_updates: { delay_min, vehicle_position, next_arrival }
      }
    ]
  }

// Reports & Verification
GET /api/reports?lat=13.05&lon=80.25&radius=5
  Response: {
    reports: [
      { 
        id, description, photo_url, latitude, longitude,
        upvotes, report_source, verification_status,
        verified_by_name, verified_by_type (badge info)
      }
    ]
  }

POST /api/reports
  Request:  { description, photo_url, latitude, longitude, user_id }
  Response: { id, created_at }

POST /api/reports/{id}/upvote
  Response: { upvotes: N }

POST /api/reports/{id}/verify
  Request:  { verifier_id, verification_status } (verify or reject)
  Response: { verified_by_type } (volunteer or ngo)

// Volunteer Dashboard
GET /api/dashboard/pending-reports?verifier_id=UUID
  Response: { reports: [...], count: N }

// SOS
POST /api/sos
  Request:  { latitude, longitude, user_id }
  Response: { alert_id, status }

// Health
GET /api/health
  Response: { status: "ok" }
```

---

## DATABASE SCHEMA

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  user_type VARCHAR(20) NOT NULL,  -- 'user', 'volunteer', 'ngo'
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE volunteers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  verification_level VARCHAR(20) DEFAULT 'bronze',
  total_verified INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ngos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  organization_name TEXT NOT NULL,
  website TEXT,
  verification_level VARCHAR(20) DEFAULT 'gold',
  total_verified INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reported_by UUID REFERENCES users(id),
  report_source VARCHAR(20),   -- 'user', 'volunteer', 'ngo'
  description TEXT NOT NULL,
  photo_url TEXT,
  latitude FLOAT,
  longitude FLOAT,
  upvotes INT DEFAULT 0,
  verified_by UUID,
  verified_by_type VARCHAR(20),  -- 'volunteer', 'ngo'
  verification_status VARCHAR(20) DEFAULT 'unverified',  -- 'unverified', 'verified', 'false'
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sos_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  latitude FLOAT,
  longitude FLOAT,
  status VARCHAR(20) DEFAULT 'active',  -- 'active', 'resolved'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enable Realtime on all tables (Supabase)
ALTER PUBLICATION supabase_realtime ADD TABLE users, volunteers, ngos, reports, sos_alerts;
```

---

## PWA SETUP CHECKLIST

### Phase 1 (Hours 0–1): Shubh Must Create

**`public/manifest.json`**
```json
{
  "name": "AccessiNav - Accessible Transit",
  "short_name": "AccessiNav",
  "description": "Real-time accessible transit routes for people with disabilities",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1e40af",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icon-maskable.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
```

**`public/serviceWorker.js`** (basic cache strategy)
```javascript
const CACHE_NAME = 'accessinav-v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/icon-192.png',
  '/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Network-first for API calls, cache-first for assets
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const cacheCopy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, cacheCopy));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
  } else {
    event.respondWith(
      caches.match(event.request).then(response => response || fetch(event.request))
    );
  }
});
```

**`src/main.jsx`** (register service worker)
```javascript
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/serviceWorker.js')
      .then(reg => console.log('SW registered'))
      .catch(err => console.log('SW registration failed'));
  });
}

// Detect when PWA is installable
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  // Show "Install" button in UI if desired
});
```

**`index.html` head additions**
```html
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#1e40af">
<meta name="description" content="Real-time accessible transit routes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="AccessiNav">
<link rel="apple-touch-icon" href="/icon-192.png">
<link rel="icon" type="image/png" href="/icon-192.png">
```

### Phase 4 (Hours 14–18): Test PWA

**Android Chrome:**
- [ ] Open Vercel link on phone
- [ ] Tap hamburger menu (≡)
- [ ] Tap **"Install app"** (appears after 30s on site)
- [ ] Tap "Install"
- [ ] App appears on home screen
- [ ] Tap icon → Opens full-screen (no browser UI)
- [ ] Test all features work
- [ ] Disable WiFi → Cached routes still load

**iOS Safari:**
- [ ] Open Vercel link on iPhone
- [ ] Tap Share (↗)
- [ ] Tap **"Add to Home Screen"**
- [ ] Tap "Add"
- [ ] App appears on home screen
- [ ] Tap icon → Opens full-screen
- [ ] Test all features work

---

## COMPONENT STRUCTURE

```
src/
  components/
    DisabilitySelector.jsx      props: { selected, onChange }
    RouteCard.jsx               props: { route, onSelect }
    ReportCard.jsx              props: { report, onUpvote, onVerify }
    VolunteerDashboard.jsx      props: { volunteerId }
    NgoDashboard.jsx            props: { ngoId }
    SOSButton.jsx               props: { userId }
    Map.jsx                     props: { routes, reports, center }
    Header.jsx                  props: { userType, onLogout }
    LoadingSpinner.jsx
    ErrorToast.jsx
  
  pages/
    AuthChoice.jsx              (User/Volunteer/NGO choice)
    Login.jsx / SignUp.jsx      (unified auth)
    Home.jsx                    (disability selector)
    Search.jsx                  (start → end)
    Results.jsx                 (show routes + real-time updates)
    Map.jsx                     (interactive map)
    ReportForm.jsx              (new report submission)
    VolunteerDashboard.jsx      (pending reports)
    NgoDashboard.jsx            (bulk verification)
  
  lib/
    api.js                      (real API calls + mock fallback)
    constants.js                (MOCK_ROUTES, MOCK_REPORTS, DISABILITIES)
    auth.js                     (JWT storage/retrieval)
    supabaseClient.js           (Supabase client setup + real-time listeners)
  
  App.jsx                       (React Router setup)
  main.jsx                      (Service Worker registration)
```

---

## PHASE CHECKPOINTS

| **Hour** | **Giri (Backend)** | **Rajarajan (Design)** | **Shubh (Frontend)** | **Risk** |
|----------|-------------------|------------------------|----------------------|----------|
| **1** | ✅ Supabase + FastAPI deployed | ✅ Design system ready | ✅ React + PWA on Vercel | Deploy fails |
| **6** | ✅ All 5 endpoints working | ✅ All 5 screens designed | ✅ All components built (mock) | API mismatch |
| **12** | ✅ Real-time + verify logic | ✅ Specs documented | ✅ Fully wired to API | CORS errors |
| **18** | ✅ Polished + tested | ✅ Final tweaks | ✅ Mobile tested + PWA installable | Crashes |
| **24** | ✅ Live + stable | ✅ Deck ready | ✅ Demo smooth | WiFi issues |

---

## 3-MINUTE DEMO SCRIPT

```
0:00 - "I'm a wheelchair user in Chennai. Maps don't show accessible routes. AccessiNav does."

0:20 - [Open phone]
       "Watch how it works."
       Tap Vercel link → App loads

0:25 - [Tap hamburger menu]
       "See this? Any browser. Any phone."
       Tap "Install app"
       App appears on home screen
       "It's now on my home screen like a native app."

0:35 - [Tap app icon, opens full-screen]
       "Now it looks like a real mobile app."
       Select "Wheelchair" disability

0:50 - Search: "St Thomas Mount" → "Central Station"
       "Let me search for an accessible route."
       
1:00 - [Results appear]
       "Only wheelchair-accessible routes. See the real-time updates?
        That's live transit data from Chennai Metro (GTFS-RT)."
       Scroll to show 3 routes
       
1:20 - [Show reports with badges]
       "This is our community verification system.
        👤 User report, ✅ Verified by Priya (volunteer), ✅ Verified by NGO"
       
1:40 - [Switch to second phone with Volunteer login]
       "Let me verify a report as a volunteer."
       Open VolunteerDashboard
       Tap "Verify" on a report
       
1:50 - [Switch back to first phone]
       "Watch... report now shows 'Verified by Volunteer' badge. Real-time."
       [Badge appeared on first phone]
       
2:00 - [SOS Demo]
       "In an emergency, users hit the SOS button.
        Location shared with nearest NGO in seconds."
       Tap red SOS button
       
2:20 - "35 million people rely on transit in India.
        AccessiNav is built for them.
        Real-time routes. Community trust. One tap to install.
        Built by 3 students. Built in 24 hours."

2:50 - [Thank you slide]
```

**Backup:** If live demo fails, play 5-min pre-recorded video (Hour 19).

---

## GitHub STRATEGY

### Two Separate Repos

**Frontend:** `innothon26-frontend`
- Owner: Shubh
- Auto-deploy to Vercel on push to main
- Branches: `shubh/phase2-components`, `shubh/phase3-integration`, `shubh/phase4-polish`
- Merge to main at hours 6, 12, 18

**Backend:** `innothon26-backend`
- Owner: Giri
- Auto-deploy to Railway on push to main
- Branches: `giri/phase2-apis`, `giri/phase3-realtime`, `giri/phase4-polish`
- Merge to main at hours 6, 12, 18

**Design:** Figma only (Rajarajan, no GitHub needed)

### Merge Schedule
```
Hour 6:  Both merge Phase 2 → All components + APIs working
Hour 12: Both merge Phase 3 → Full integration + real-time
Hour 18: Both merge Phase 4 → Polished + tested
```

**No commits of:**
- `.env` files (use Railway/Vercel secrets)
- `node_modules/` or `venv/`
- `.DS_Store`, `dist/`, `__pycache__/`

---

## DELIVERY FILES (Hour 22 Submission)

```
📦 INNOTHON26-Submission/
├── 📄 README.md                    (problem, features, tech stack)
├── 📊 AccessiNav.pptx             (7 slides)
├── 🎬 demo-video.mp4              (5 min backup demo, Google Drive link)
├── 🔗 Links.txt
│   ├── Live App: https://innothon26-frontend.vercel.app
│   ├── Frontend Repo: https://github.com/shubh/innothon26-frontend
│   ├── Backend Repo: https://github.com/giri/innothon26-backend
│   ├── Figma Design: https://figma.com/...
│   └── Demo Video: https://drive.google.com/...
```

---

## TESTING CHECKLIST (Hour 14–18)

### Functionality
- [ ] All 5 screens render correctly
- [ ] Login/SignUp works (all 3 user types)
- [ ] Search route works (real data from GTFS-RT)
- [ ] Real-time transit updates appear
- [ ] Report submission works
- [ ] Upvote works (number increments)
- [ ] Verification works (badge appears on other user's phone)
- [ ] Volunteer dashboard loads pending reports
- [ ] SOS button sends alert

### Mobile (Real Device)
- [ ] Responsive (no horizontal scroll)
- [ ] Touch targets ≥48px (all buttons tappable)
- [ ] Fonts ≥16px (readable without zoom)
- [ ] Images load (no broken images)
- [ ] Tap all buttons, forms, links
- [ ] Scroll works smoothly

### PWA
- [ ] Install button appears (hamburger menu or browser prompt)
- [ ] App installs to home screen
- [ ] App opens full-screen (no browser UI)
- [ ] All features work from installed app
- [ ] Icons display correctly
- [ ] Offline fallback works (disable WiFi → cached routes load)

### Performance
- [ ] Lighthouse >80
- [ ] Images <50KB each
- [ ] Page load <3s
- [ ] No console errors/warnings

### Accessibility
- [ ] Focus indicators visible (Tab through page)
- [ ] Color contrast 4.5:1 (WAVE checker)
- [ ] Form labels associated (screen reader test)
- [ ] All icons have alt text
- [ ] Keyboard navigation works (no mouse needed)

### Real-Time Sync
- [ ] Open app on two phones
- [ ] Submit report on Phone 1
- [ ] Report appears on Phone 2 <150ms (refresh if needed)
- [ ] Verify report on Phone 2
- [ ] Badge appears on Phone 1 (real-time)
- [ ] SOS alert appears on NGO dashboard (real-time)

---

## PRODUCT ROADMAP (Post-Hackathon)

**Phase 0 (Now - Hour 24):** MVP hackathon
- ✅ Wheelchair focus
- ✅ 3 user types
- ✅ Chennai only
- ✅ GTFS-RT real-time
- ✅ PWA installable

**Phase 1 (1–3 months):** Polish
- [ ] Web Speech + TTS integration
- [ ] Offline mode (Service Worker caching)
- [ ] 1000 active users
- [ ] iOS/Android app store
- [ ] NGO partnerships (3–5 NGOs)

**Phase 2 (3–6 months):** Expand Accessibility
- [ ] All 4 disabilities (Wheelchair, Visual, Hearing, Cognitive)
- [ ] NGO admin tools (bulk verification, dashboard)
- [ ] Gamification (leaderboards, achievements)
- [ ] 5000 users

**Phase 3 (6–12 months):** Multi-City
- [ ] 10 cities (Delhi, Mumbai, Bangalore, Hyderabad, etc.)
- [ ] Multi-language (Hindi, Tamil, Telugu, Kannada)
- [ ] Municipality integrations
- [ ] 50,000 users

**Phase 4 (12+ months):** Scale & Profit
- [ ] 30 cities
- [ ] 500K users
- [ ] Revenue: $165K/mo (B2B NGO subscriptions + B2C premium features)
- [ ] Profit: ~$65K/mo

**Phase 5 (2+ years):** Southeast Asia
- [ ] Bangkok, Jakarta, Manila, Ho Chi Minh City
- [ ] Regional partnerships
- [ ] 5M+ users

---

## KEY TAKEAWAYS

✅ **Responsive Web App** → Mobile-optimized, works on all phones
✅ **PWA Installable** → Add to home screen from any browser (judge's wow factor)
✅ **Real-Time Updates** → GTFS-RT + Supabase subscriptions (<150ms sync)
✅ **Community Trust** → 3-tier verification badges (user → volunteer → NGO)
✅ **Offline Ready** → Service Worker caching for graceful degradation
✅ **Accessibility First** → WCAG AA, focus indicators, high contrast
✅ **No Native App** → Web-only = faster to build, same UX
✅ **Web Speech Deferred** → Phase 1, not in 24-hour scope
✅ **Two-Tier GitHub** → Frontend + Backend repos, auto-deploy to Vercel + Railway
✅ **Demo Magic** → Install app live in 30s → Full-screen demo → Judge sees native-like app

---

## QUICK REFERENCE: HOUR-BY-HOUR

```
Hour 0  → Start
Hour 1  ✅ Setup complete (all 3 deployed)
Hour 2-6 → Parallel build (no waiting)
Hour 6  ✅ All APIs + components done (with mock data)
Hour 6-12 → Integration (wire real API)
Hour 12 ✅ Fully integrated + real-time working
Hour 12-18 → Polish + testing
Hour 18 ✅ Mobile tested + PWA installable
Hour 18-20 → Demo video (backup)
Hour 20-22 → .pptx + README
Hour 22-23 → Submit to portal
Hour 23-24 → Live demo + celebration 🎉
```

---

**Last Updated:** 30 September 2026 | **Team:** Giri, Rajarajan, Shubh | **Event:** INNOTHON26
