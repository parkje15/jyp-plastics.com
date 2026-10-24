"""data/*.yaml 안의 Google Sites 이미지 주소를 찾아 내려받고,
사이트 내부 경로(img/g/...)로 바꿔 적습니다. (중국 접속용: Google 서버 의존 제거)
GitHub Actions에서 자동 실행됩니다. 이미 받은 이미지는 건너뜁니다."""
import hashlib, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "img" / "g"
OUT.mkdir(parents=True, exist_ok=True)
PAT = re.compile(r'https://(?:sites\.google\.com/sitesv-images-rt|lh3\.googleusercontent\.com/sitesv)/[A-Za-z0-9_\-=]+')
EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}

failed = 0
for yml in sorted((ROOT / "data").glob("*.yaml")):
    text = yml.read_text(encoding="utf-8")
    urls = sorted(set(PAT.findall(text)))
    for url in urls:
        key = hashlib.sha1(url.encode()).hexdigest()[:16]
        existing = list(OUT.glob(key + ".*"))
        if existing:
            local = existing[0]
        else:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    ctype = r.headers.get_content_type()
                    data = r.read()
                local = OUT / (key + EXT.get(ctype, ".jpg"))
                local.write_bytes(data)
                print("saved", local.name, len(data))
            except Exception as e:  # 실패한 주소는 원래대로 둠
                failed += 1
                print("FAILED", url[:80], e, file=sys.stderr)
                continue
        text = text.replace(url, "img/g/" + local.name)
    yml.write_text(text, encoding="utf-8")
print("done, failed:", failed)
