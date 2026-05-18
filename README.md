# Blackcoffer Insights Dashboard

A full-stack data visualization dashboard built with **FastAPI** (Python backend) + **MongoDB Atlas** (database) + **HTML / Chart.js** (frontend).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Backend | Python, FastAPI |
| Database | MongoDB Atlas |
| Hosting (API) | Render.com |

---

## Project Structure

```
blackcoffer-dashboard/
├── main.py            ← FastAPI backend (all API routes)
├── requirements.txt   ← Python dependencies
└── index.html         ← Frontend dashboard (fetches from API)
```

---

## Features

- **7 Interactive Charts**
  - Average Intensity by Sector (horizontal bar)
  - PESTLE Distribution (donut chart)
  - Intensity / Likelihood / Relevance by End Year (multi-line trend)
  - Records by Region (horizontal bar)
  - Top Topics — Intensity vs Likelihood (bubble chart)
  - Intensity vs Likelihood (scatter plot)
  - Top Countries by Record Count (horizontal bar)

- **7 Sidebar Filters** — End Year, Sector, Topic, Region, PEST, Country, Source
- **Live KPI Cards** — Avg Intensity, Likelihood, Relevance, Total Records
- **Data Table** — Top 50 records by intensity with color-coded badges
- All charts and KPIs update instantly when filters change

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/api/data` | All records (supports all filters) |
| GET | `/api/filters` | Unique values for all filter dropdowns |
| GET | `/api/stats` | KPI aggregates (avg intensity, likelihood, relevance) |
| GET | `/api/charts/sector` | Avg intensity grouped by sector |
| GET | `/api/charts/pestle` | Count grouped by PESTLE category |
| GET | `/api/charts/year` | Avg metrics grouped by end year |
| GET | `/api/charts/region` | Count grouped by region |
| GET | `/api/charts/topics` | Top topics for bubble chart |
| GET | `/api/charts/country` | Top 15 countries by count |

All endpoints support query filters: `end_year`, `sector`, `topic`, `region`, `pestle`, `country`, `source`

**Example:** `https://your-api.onrender.com/api/data?sector=Energy&region=Asia`

---

## Setup & Deployment

### Step 1 — MongoDB Atlas

1. Create a free account at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Create a free **M0 cluster**
3. Create a database named `blackcoffer` and collection named `insights`
4. Import `jsondata.json` via the Atlas UI (Insert Document)
5. Go to **Network Access** → Add IP → **Allow Access from Anywhere** (`0.0.0.0/0`)
6. Go to **Connect** → **Drivers** → copy your connection string:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/
   ```

---

### Step 2 — GitHub

1. Create a new repository on [github.com](https://github.com)
2. Upload these files by dragging and dropping:
   - `main.py`
   - `requirements.txt`
   - `index.html`
3. Commit changes

---

### Step 3 — Deploy API on Render

1. Create a free account at [render.com](https://render.com) (sign up with GitHub)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Fill in the settings:

| Field | Value |
|---|---|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port 10000` |

5. Add an **Environment Variable**:

| Key | Value |
|---|---|
| `MONGO_URI` | `mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/` |

6. Click **Deploy**
7. Render gives you a live URL: `https://blackcoffer-dashboard.onrender.com`

---

### Step 4 — Connect Frontend to API

Open `index.html` and find this line near the top of the `<script>` tag:

```javascript
const API = "http://localhost:8000";
```

Change it to your Render URL:

```javascript
const API = "https://blackcoffer-dashboard.onrender.com";
```

Save and re-upload `index.html` to GitHub.

Now open `index.html` in any browser — it will call your live API and render all charts.

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `MONGO_URI` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster0.xyz.mongodb.net/` |

---

## Dataset

- **Source:** Blackcoffer assignment JSON dataset
- **Records:** 1000 insight documents
- **Fields:** `intensity`, `likelihood`, `relevance`, `sector`, `topic`, `region`, `country`, `pestle`, `source`, `end_year`, `start_year`, `title`, `insight`, `url`
