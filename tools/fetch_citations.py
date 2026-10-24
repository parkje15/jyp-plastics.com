"""논문 인용수(OpenAlex)를 DOI로 가져와 data/citations.json에 저장.
GitHub Actions가 배포할 때마다(매주 자동 포함) 실행합니다. 실패해도 사이트 빌드는 계속됩니다."""
import json, time, urllib.parse, urllib.request
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
papers = yaml.safe_load(open(ROOT / "data" / "sci_papers.yaml", encoding="utf-8"))
dois = sorted({p["doi"].lower() for k in ("after_sogang", "before_sogang") for p in papers[k] if p.get("doi")})
out = {}
for i in range(0, len(dois), 40):
    chunk = dois[i:i + 40]
    q = "|".join("https://doi.org/" + d for d in chunk)
    url = ("https://api.openalex.org/works?per-page=50&select=doi,cited_by_count&mailto=parkje15@gmail.com&filter=doi:"
           + urllib.parse.quote(q, safe=":/|"))
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            for w in json.load(r).get("results", []):
                if w.get("doi"):
                    out[w["doi"].lower().replace("https://doi.org/", "")] = w.get("cited_by_count", 0)
    except Exception as e:
        print("OpenAlex request failed:", e)
    time.sleep(1)
(ROOT / "data" / "citations.json").write_text(json.dumps(out, indent=1, sort_keys=True))
print(f"citations for {len(out)}/{len(dois)} papers")
