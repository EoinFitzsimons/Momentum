# Executive Summary

Momentum is a multi-discipline motorsport management simulation developed as a final-year Computer Science project. The purpose of this report is to describe the system design, implementation, and evaluation of a playable engine that supports multiple racing disciplines and a career-focused management layer.

The system models drivers (50+ attributes), teams (tiered budgets), staff (40+ attributes), and tracks (175 circuits) and uses an AI agent-based live-racing engine to generate race outcomes. Races run as real-time simulations where each driver acts as an autonomous agent making per-tick decisions (target ~30 ticks per second). The backend is Python-based and uses SQLite for persistence; a FastAPI layer provides optional headless/API access. Supporting libraries include NumPy/SciPy for numerical work, Faker for procedural name/asset generation, and PyTorch-ready hooks for future ML models.

Key results and conclusions:

- The realtime agent engine produces observable, watchable races with emergent behaviours, suitable for GUI display and interactive demos.
- The data model and API persist race results and standings; simulations are non-deterministic by design and are not seeded for exact replay. When reproducibility is required the system records run parameters and optional full telemetry for inspection, not by exposing RNG seeds.

# 1.0 Introduction

## 1.1 Background

Motorsport management simulation is a niche genre with limited multi-discipline offerings. This project was started to build a modern, extensible platform that supports multiple racing categories, deep driver/team management, and visible, agent-driven race dynamics rather than instant batch results. The realtime agentic approach improves player engagement by showing decisions and interactions as they happen.

## 1.2 Aims

The project aims to:

- Deliver a multi-discipline simulation that supports Single Seater, Touring, Rally/Stage, Urban/Street, Drag/Acceleration, Sprint/Rallycross, and Endurance.
- Provide a rich data model (drivers, teams, staff, tracks) to support career progression and management features.
- Implement an AI agent-based live-racing engine as the primary simulation path.
- Expose a REST API for integration and build a path to scale background workloads.

## 1.3 Technology

Primary technologies used:

- Python (backend and GUI glue)
- PyQt6 for the desktop GUI launcher and race visualization
- FastAPI + uvicorn for optional headless/API mode
- SQLite for persistent storage (momentum.db)
- NumPy and SciPy for numerical and probabilistic modelling
- PyTorch (optional) for future ML decision models
- Faker for procedural name and content generation

These technologies are used to keep the system portable, easy to run locally, and straightforward to migrate to heavier infrastructure if required.

## 1.4 Structure

This document is organised as follows:

- Executive Summary: short overview, results and recommendations.
- Introduction: project background, aims, technologies and structure.
- Requirements: functional and data requirements for core gameplay and career features.
- Design & Architecture: system components, data model and simulation engine details.
- Implementation: key modules, code structure and integration points.
- Testing & Evaluation: performance testing, validation and limitations.
- Conclusions & Further Development: lessons learned and recommended next steps.
