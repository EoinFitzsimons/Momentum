"""Archived: Playability test from legacy suite"""
from simulation import app
from fastapi.testclient import TestClient
import json

client = TestClient(app)

print("\n" + "="*80)
print("🎮 MOMENTUM MOTORSPORT - BACKEND PLAYABILITY ASSESSMENT")
print("="*80)

# Test 1: API Basics
print("\n1. ✅ API Server Status:")
resp = client.get("/")
print(f"   Status: {resp.status_code}")
endpoints = resp.json()["endpoints"]
print(f"   Available endpoints: {len(endpoints)}")

# Test 2: Database
print("\n2. ✅ Database Status:")
resp = client.get("/stats")
stats_data = resp.json().get("database_stats", {})
print(f"   Teams: {stats_data.get('teams', 0):,}")
print(f"   Drivers: {stats_data.get('drivers', 0):,}")
print(f"   Tracks: {stats_data.get('tracks', 0):,}")

print("\n" + "="*80)
print("📊 PLAYABILITY ASSESSMENT SUMMARY")
print("="*80)
