#!/usr/bin/env python3
"""Generate a simple index.html from Helm's index.yaml for GitHub Pages."""
import html
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_YAML = REPO_ROOT / "index.yaml"
INDEX_HTML = REPO_ROOT / "index.html"

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Helm chart repository</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
  h1 {{ margin-bottom: 0.25rem; }}
  .sub {{ color: #666; margin-top: 0; }}
  .chart {{ border: 1px solid #ddd; border-radius: 8px; padding: 1rem 1.25rem; margin: 1rem 0; }}
  .chart h2 {{ margin: 0 0 0.25rem; }}
  .chart .desc {{ color: #333; margin: 0.25rem 0 0.75rem; }}
  .versions {{ font-size: 0.9rem; }}
  .versions summary {{ cursor: pointer; color: #555; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 0.5rem; }}
  td, th {{ text-align: left; padding: 0.2rem 0.5rem; }}
  code {{ background: #f4f4f4; padding: 0.1rem 0.3rem; border-radius: 4px; }}
  .usage {{ color: #666; font-size: 0.85rem; margin-top: 0.5rem; }}
</style>
</head>
<body>
<h1>Helm chart repository</h1>
<p class="sub">Add this repo: <code>helm repo add leprechaun https://leprechaun.github.io/</code></p>
{charts}
</body>
</html>
"""

CHART_TEMPLATE = """<div class="chart">
  <h2>{name}</h2>
  <p class="desc">{description}</p>
  <p class="usage"><code>helm install my-{name} leprechaun/{name} --version {latest_version}</code></p>
  <details class="versions">
    <summary>{version_count} version(s)</summary>
    <table>
      <tr><th>Version</th><th>App version</th><th>Created</th><th></th></tr>
      {rows}
    </table>
  </details>
</div>
"""

ROW_TEMPLATE = """<tr>
        <td>{version}</td>
        <td>{app_version}</td>
        <td>{created}</td>
        <td><a href="{url}">download</a></td>
      </tr>"""


def main():
    if not INDEX_YAML.exists():
        print(f"{INDEX_YAML} not found; run `helm repo index ./` first", file=sys.stderr)
        sys.exit(1)

    data = yaml.safe_load(INDEX_YAML.read_text())
    entries = data.get("entries", {})

    chart_blocks = []
    for name in sorted(entries.keys()):
        versions = entries[name]
        rows = []
        for v in versions:
            rows.append(
                ROW_TEMPLATE.format(
                    version=html.escape(str(v.get("version", ""))),
                    app_version=html.escape(str(v.get("appVersion", ""))),
                    created=html.escape(str(v.get("created", ""))[:19].replace("T", " ")),
                    url=html.escape(v.get("urls", [""])[0]),
                )
            )
        latest = versions[0]
        chart_blocks.append(
            CHART_TEMPLATE.format(
                name=html.escape(name),
                description=html.escape(latest.get("description", "")),
                latest_version=html.escape(str(latest.get("version", ""))),
                version_count=len(versions),
                rows="\n      ".join(rows),
            )
        )

    INDEX_HTML.write_text(PAGE_TEMPLATE.format(charts="\n".join(chart_blocks)))
    print(f"wrote {INDEX_HTML}")


if __name__ == "__main__":
    main()
