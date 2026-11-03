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
    for attempt in range(4):  # 요청 제한(429) 등 일시 오류는 잠시 쉬었다가 재시도
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                for w in json.load(r).get("results", []):
                    if w.get("doi"):
                        out[w["doi"].lower().replace("https://doi.org/", "")] = w.get("cited_by_count", 0)
            break
        except Exception as e:
            print(f"OpenAlex request failed (try {attempt + 1}):", e)
            time.sleep(15 * (attempt + 1))
    time.sleep(1)
# 못 가져온 논문은 지난번 배포된 값을 그대로 사용 (인용수가 사라지지 않게)
missing = [d for d in dois if d not in out]
if missing:
    try:
        with urllib.request.urlopen("https://jyp-plastics.com/citations.json", timeout=30) as r:
            prev = json.load(r)
        kept = {d: prev[d] for d in missing if d in prev}
        out.update(kept)
        print(f"reused previous values for {len(kept)} papers")
    except Exception as e:
        print("could not load previous citations:", e)
(ROOT / "data" / "citations.json").write_text(json.dumps(out, indent=1, sort_keys=True))
print(f"citations for {len(out)}/{len(dois)} papers")
