#!/usr/bin/env python3
"""Build the deployable Loads reporting app.

Runs the ETL chain, then injects dashboard_data.json into app/template.html
at the /*__DATA__*/ marker and writes ../index.html.

Usage:  python3 etl/build_app.py   (from the project root, or anywhere)
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # etl/
ROOT = HERE.parent                              # project root

def run(script):
    print(f"== {script} ==")
    r = subprocess.run([sys.executable, str(HERE / script)], cwd=str(HERE))
    if r.returncode != 0:
        sys.exit(f"FAILED: {script}")

def main():
    run("loan_tape_etl.py")
    run("financials_etl.py")
    run("build_dashboard_data.py")

    data = json.loads((HERE / "dashboard_data.json").read_text(encoding="utf-8"))
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    tpl = (ROOT / "app" / "template.html").read_text(encoding="utf-8")
    marker = "/*__DATA__*/"
    if marker not in tpl:
        sys.exit("marker /*__DATA__*/ not found in template")
    out = tpl.replace(marker, payload, 1)

    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html written: {len(out)//1024} KB")

if __name__ == "__main__":
    main()
