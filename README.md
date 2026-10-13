# HRD/PARP Triager Agent

A Python and browser-based **research demonstration** of rule-based alert classification and case-workflow orchestration. Includes FastAPI, command-line tools, and a static browser console.

**Not validated for patient care.** Despite its name, this project does not calculate LOH/TAI/LST genomic scars, classify BRCA variants against a curated knowledge base, establish HRD status, or predict PARP-inhibitor benefit. Numeric thresholds and descriptor keywords are illustrative, not guideline cut-offs. Do not submit real patient identifiers or use outputs for diagnosis, treatment, or clinical escalation.

## Browser demonstration

Open [web/index.html](web/index.html) in a modern browser. Supply synthetic task/target IDs, two numeric metrics, a status descriptor, and optionally a critical flag. The page displays an evaluation dossier and allows JSON export. It runs entirely in-browser using JavaScript, with no backend, account, Python runtime, Pyodide, or external requests. Input values are not uploaded or stored. The GitHub Pages workflow publishes the folder when Pages is correctly enabled.

This browser mirrors the **supervisor demonstration rules**: primary metric greater than 25, secondary metric greater than 12, or status containing DISCORDANT, ANOMALY, MUTANT, VIOLATION, FAIL, or REJECT yields an elevated alert. An explicit critical flag yields a critical alert. These are not clinical thresholds. The page does **not** create HMAC signatures.

## Python installation

Python 3.9 or newer is required. From the repository directory:

    python -m pip install -e '.[api,test]'
    python -m pytest -q

### Supervisor CLI and API

    python cli.py audit --task-id SYNTH-001 --target SAMPLE-001 --primary 28 --secondary 14 --status DISCORDANT
    python cli.py batch -i examples/supervisor_sample.csv -o results.csv
    python cli.py chat "status"
    python cli.py serve --host 127.0.0.1 --port 8000

The API offers GET /health, GET /metrics, POST /api/audit, POST /api/chat, and GET /api/audit/logs. Interactive documentation is at http://127.0.0.1:8000/docs. Direct server entry point: uvicorn agents.api:app --host 127.0.0.1 --port 8000.

**The API has no authentication** and should not be exposed to an untrusted network without a separate security boundary. The batch CSV requires task_id, target_identifier, and primary_metric headers; optional fields are secondary_metric, status_descriptor, and is_critical_flag. Invalid records are skipped with generic errors; output paths are restricted to the current working directory or system temporary directory.

The HMAC audit trail is **in-memory only**. Set AUDIT_SECRET_KEY to a securely generated secret when running multiple instances with a consistent signing key, but logs are not persisted across restarts. The verify-audit CLI command checks only the current process's trail: starting a new process does not recover old logs. Regex-based identifier screening is limited; it does **not** constitute de-identification, HIPAA certification, or a guarantee of absent PHI.

### Other retained entry points

For compatibility, the repository retains different rules and schemas:

- Legacy sentinel: python hrd_parp_sentinel.py audit, or python hrd_parp_sentinel.py batch -i sample.csv; uses metric_primary and metric_secondary.
- Packaged demonstration: python hrd_parp_triager_agent_app.py audit, or python hrd_parp_triager_agent_app.py serve; uses primary_metric and secondary_metric.
- Synthetic load test: python simulator.py 100 (takes a positional count; no --tasks or --concurrency options).

The three rule sets are **not mathematically equivalent** and must not be interpreted as interchangeable clinical classifications.

## Docker

    docker build -t hrd-parp-triager-agent .
    docker run --rm -p 127.0.0.1:8000:8000 -e AUDIT_SECRET_KEY="replace-with-long-random-secret" hrd-parp-triager-agent

The container uses a non-root account. The Docker Compose file remains available for local use; review its port binding before deployment.

## Testing, privacy and technology

CI installs the package with optional API/test dependencies, runs Python tests across 3.10–3.12, checks Python syntax and the installed CLI, and runs a dependency-free Node.js smoke test for the web interface. Locally, use node tests/web_smoke.cjs. The stack is Python, Pydantic, optional FastAPI/Uvicorn, and plain HTML/CSS/JavaScript. Modern desktop and mobile browsers with ES2017 support are expected; real-device coverage has not been confirmed.

Use synthetic data only. The repository is not a production-grade clinical data-processing or decision-support system.

## License

MIT; see [LICENSE](LICENSE).
