from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import Optional
import os

app = FastAPI(title="Blackcoffer Insights API")

# Allow the frontend HTML file (opened from disk) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MongoDB connection ──────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["blackcoffer"]
collection = db["insights"]


# ── Helper ──────────────────────────────────────────────────────────────────
def build_query(
    end_year: Optional[int],
    sector: Optional[str],
    topic: Optional[str],
    region: Optional[str],
    pestle: Optional[str],
    country: Optional[str],
    source: Optional[str],
    swot: Optional[str],
):
    q = {}
    if end_year:
        q["end_year"] = end_year
    if sector:
        q["sector"] = sector
    if topic:
        q["topic"] = topic
    if region:
        q["region"] = {"$regex": region, "$options": "i"}
    if pestle:
        q["pestle"] = pestle
    if country:
        q["country"] = country
    if source:
        q["source"] = source
    if swot:
        q["swot"] = swot
    return q


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Blackcoffer Insights API is running", "docs": "/docs"}


@app.get("/api/data")
def get_data(
    end_year: Optional[int] = Query(None),
    sector: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    pestle: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    swot: Optional[str] = Query(None),
    limit: int = Query(1000, le=5000),
):
    """Return filtered insight records."""
    q = build_query(end_year, sector, topic, region, pestle, country, source, swot)
    docs = list(collection.find(q, {"_id": 0}).limit(limit))
    return {"count": len(docs), "data": docs}


@app.get("/api/filters")
def get_filters():
    """Return all unique values for every filter dropdown."""
    def distinct(field):
        return sorted([v for v in collection.distinct(field) if v])

    return {
        "end_years": sorted([v for v in collection.distinct("end_year") if v]),
        "sectors":   distinct("sector"),
        "topics":    distinct("topic"),
        "regions":   distinct("region"),
        "pestles":   distinct("pestle"),
        "countries": distinct("country"),
        "sources":   distinct("source"),
        "swots":     distinct("swot"),
    }


@app.get("/api/stats")
def get_stats(
    end_year: Optional[int] = Query(None),
    sector: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    pestle: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    swot: Optional[str] = Query(None),
):
    """Aggregated statistics for KPI cards."""
    q = build_query(end_year, sector, topic, region, pestle, country, source, swot)

    pipeline = [
        {"$match": q},
        {"$group": {
            "_id": None,
            "count":          {"$sum": 1},
            "avg_intensity":  {"$avg": "$intensity"},
            "avg_likelihood": {"$avg": "$likelihood"},
            "avg_relevance":  {"$avg": "$relevance"},
        }}
    ]
    result = list(collection.aggregate(pipeline))
    if not result:
        return {"count": 0, "avg_intensity": 0, "avg_likelihood": 0, "avg_relevance": 0}

    r = result[0]
    return {
        "count":          r["count"],
        "avg_intensity":  round(r["avg_intensity"] or 0, 1),
        "avg_likelihood": round(r["avg_likelihood"] or 0, 1),
        "avg_relevance":  round(r["avg_relevance"] or 0, 1),
    }


@app.get("/api/charts/sector")
def chart_sector(
    end_year: Optional[int] = Query(None),
    sector: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    pestle: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    """Average intensity grouped by sector."""
    q = build_query(end_year, sector, topic, region, pestle, country, source, None)
    pipeline = [
        {"$match": {**q, "sector": {"$ne": ""}}},
        {"$group": {"_id": "$sector", "avg_intensity": {"$avg": "$intensity"}, "count": {"$sum": 1}}},
        {"$sort": {"avg_intensity": -1}},
        {"$limit": 15},
    ]
    return list(collection.aggregate(pipeline))


@app.get("/api/charts/pestle")
def chart_pestle(
    end_year: Optional[int] = Query(None),
    sector: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    pestle: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    """Record count grouped by PESTLE category."""
    q = build_query(end_year, sector, topic, region, pestle, country, source, None)
    pipeline = [
        {"$match": {**q, "pestle": {"$ne": ""}}},
        {"$group": {"_id": "$pestle", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return list(collection.aggregate(pipeline))


@app.get("/api/charts/year")
def chart_year(
    sector: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    pestle: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    """Average intensity, likelihood, relevance grouped by end year."""
    q = build_query(None, sector, topic, region, pestle, country, source, None)
    pipeline = [
        {"$match": {**q, "end_year": {"$ne": None, "$lte": 2060}}},
        {"$group": {
            "_id": "$end_year",
            "avg_intensity":  {"$avg": "$intensity"},
            "avg_likelihood": {"$avg": "$likelihood"},
            "avg_relevance":  {"$avg": "$relevance"},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]
    return list(collection.aggregate(pipeline))


@app.get("/api/charts/region")
def chart_region(
    end_year: Optional[int] = Query(None),
    sector: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    pestle: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    """Record count grouped by region."""
    q = build_query(end_year, sector, topic, None, pestle, country, source, None)
    pipeline = [
        {"$match": {**q, "region": {"$ne": ""}}},
        {"$group": {"_id": "$region", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return list(collection.aggregate(pipeline))


@app.get("/api/charts/country")
def chart_country(
    end_year: Optional[int] = Query(None),
    sector: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    pestle: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    """Top 15 countries by record count."""
    q = build_query(end_year, sector, topic, region, pestle, None, source, None)
    pipeline = [
        {"$match": {**q, "country": {"$ne": ""}}},
        {"$group": {"_id": "$country", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15},
    ]
    return list(collection.aggregate(pipeline))


@app.get("/api/charts/topics")
def chart_topics(
    end_year: Optional[int] = Query(None),
    sector: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    pestle: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
):
    """Top topics with avg intensity, likelihood, and count — for bubble chart."""
    q = build_query(end_year, sector, None, region, pestle, country, source, None)
    pipeline = [
        {"$match": {**q, "topic": {"$ne": ""}}},
        {"$group": {
            "_id": "$topic",
            "avg_intensity":  {"$avg": "$intensity"},
            "avg_likelihood": {"$avg": "$likelihood"},
            "count": {"$sum": 1},
        }},
        {"$sort": {"count": -1}},
        {"$limit": 15},
    ]
    return list(collection.aggregate(pipeline))