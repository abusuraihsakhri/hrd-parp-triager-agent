# HRD PARP Triager Agent

> **Domain:** Medical Oncology & Cancer Staging Systems
> **Reference Guidelines & Standards:** `AJCC Cancer Staging Manual & NCCN Clinical Practice Guidelines`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**HRD PARP Triager Agent** is an advanced analytical and computational platform implementing Homologous Recombination Deficiency & PARP Inhibitor Response evaluation. It integrates BRCA1/2 germline/somatic status with genomic scar indices (LOH, TAI, LST) to predict synthetic lethality and PARP inhibitor benefit.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`BRCAMutationClassifierAgent`**: Specialized Sub-Agent 1 for BRCA mutation classification.
- **`GenomicScarCalculatorAgent`**: Specialized Sub-Agent 2 for genomic scar index calculation.
- **`PARPResponsePredictorAgent`**: Specialized Sub-Agent 3 for PARP inhibitor response prediction.

### 🤖 Multi-Agent Architecture

The system uses a **supervisor orchestrator** pattern:
- **`SystemSupervisor`** — coordinates multiple specialized workers.
- **`InvariantQCWorker`** — primary mathematical & protocol boundary auditor.
- **`SafetyEscalationWorker`** — safety boundary, toxicity & emergency interlock worker.
- **`ProtocolConformanceWorker`** — spec conformance, anomaly triage & discordance checker.

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py audit --task-id <value> --target <value> --primary <value> --secondary <value>
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Specifies input measurement or parameter value.
- `--target`: Specifies input measurement or parameter value.
- `--primary`: Primary metric value (float).
- `--secondary`: Secondary metric value (float).
- `--critical`: Trigger emergency/critical flag.
- `--status`: Status/phenotype descriptor.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `case_id` | Parameter / observation metric | Required |
| `patient_synthetic_id` | Parameter / observation metric | Required |
| `metric_primary` | Parameter / observation metric | Required |
| `metric_secondary` | Parameter / observation metric | Required |
| `is_stat` | Parameter / observation metric | Required |
| `status_flag` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).
* **Path Traversal Protection:** CLI batch processing validates output paths against current working directory.
* **Input Validation:** Rejects NaN, Inf, and malformed payloads at the Pydantic model layer.

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC-SHA256 audit signing | Ephemeral random (warns if unset) |
| `MODEL_PROVIDER` | LLM provider (`mock`, `ollama`, `claude`, `openai`) | `mock` |

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

### Test Coverage

- **PHI Guard Enforcement** — verifies detection of MRNs, SSNs, phone numbers, emails, DOBs, and patient names.
- **Input Validation** — rejects NaN, Inf, empty identifiers, and whitespace-only strings.
- **Audit Trail Integrity** — validates HMAC-SHA256 chain integrity and genesis block references.
- **CLI Security** — path traversal protection and error handling for batch processing.
- **Worker & Supervisor** — consensus logic and alert generation.

---

## 🐳 Container Deployment

```bash
docker build -t hrd-parp-triager-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key hrd-parp-triager-agent
```

Or using Docker Compose:

```bash
AUDIT_SECRET_KEY=your-secret-key docker-compose up
```

---

## 📁 Project Structure

```
hrd-parp-triager-agent/
├── agents/                       # Core agent modules
│   ├── __init__.py
│   ├── api.py                    # FastAPI REST server
│   ├── base.py                   # Security, PHI guard, audit trail
│   ├── learning.py               # Bayesian calibration engine
│   ├── llm_factory.py            # LLM provider factory
│   ├── metrics.py                # Prometheus metrics collector
│   ├── models.py                 # Pydantic data models
│   ├── streamer.py               # WebSocket telemetry
│   ├── supervisor.py             # Supervisor orchestrator
│   └── workers.py                # Specialized worker agents
├── hrd_parp_triager_agent/       # Clinical agent module
│   ├── __init__.py
│   ├── agents.py                 # BRCA, genomic scar, PARP agents
│   ├── cli.py                    # Clinical CLI
│   ├── engine.py                 # Clinical domain engine
│   ├── models.py                 # Clinical data models
│   └── server.py                 # Clinical FastAPI server
├── tests/                        # Test suite
│   ├── test_enrichment.py        # Enrichment engine tests
│   ├── test_hrd_parp_triager_agent.py  # Core agent tests
│   └── test_security_and_validation.py # Security & validation tests
├── web/
│   └── index.html                # Operations console UI
├── cli.py                        # Main CLI entry point
├── enrichment.py                 # Domain enrichment engines
├── hrd_parp_sentinel.py          # Sentinel agent (standalone)
├── simulator.py                  # High-throughput simulator
├── benchmark_dataset.json        # Golden benchmark test cases
├── sample.csv                    # Sample batch input
├── sample_payload.json           # Sample API payload
├── Dockerfile                    # Container build
├── docker-compose.yml            # Multi-container orchestration
├── openapi_spec.json             # OpenAPI 3.1 specification
└── pyproject.toml                # Project metadata & dependencies
```

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
