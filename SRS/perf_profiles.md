Performance profiles and SLAs
============================

Baseline hardware profiles
- DEV: 4 vCPU, 8 GB RAM, local SSD
- PROD: 8 vCPU, 32 GB RAM, networked storage

Workload definitions
- Small run: 12 drivers × 20 laps
- Medium run: 20 drivers × 50 laps
- Large run: 30 drivers × 100 laps

SLAs (example)
- Latency SLA (DEV baseline): Medium run completes end-to-end < 120s
- Throughput SLA (PROD baseline): 1000 medium runs per 24h with a worker
  pool of size 10 and queue depth elasticity

Benchmarking
- Place benchmark scripts under `perf/` and run under controlled CI or
  nightly runners. Record environment and results in `perf/results/`.
