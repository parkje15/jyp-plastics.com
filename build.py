"""연구실 홈페이지 빌드 스크립트.

data/*.yaml (내용) + templates/*.html (화면) → dist/ (완성된 웹사이트)
사용법:  python build.py
"""
import re
import shutil
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DIST = ROOT / "dist"


def load(name):
    with open(ROOT / "data" / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


NAV = [
    {"label": "Home", "href": "index.html", "children": [
        {"label": "Research Interests", "href": "research.html"}]},
    {"label": "Team", "children": [
        {"label": "Main Advisor", "href": "advisor.html"},
        {"label": "Members", "href": "members.html"},
        {"label": "Co-advisors/Co-members", "href": "coadvisors.html"},
        {"label": "Alumni", "href": "alumni.html"}]},
    {"label": "Achievements", "children": [
        {"label": "SCI Papers", "href": "sci-papers.html"},
        {"label": "General papers", "href": "general-papers.html"},
        {"label": "Patents", "href": "patents.html"},
        {"label": "Hall of Fame", "href": "hall-of-fame.html"},
        {"label": "Youtube-Highlights", "href": "youtube.html"}]},
    {"label": "News", "children": [
        {"label": "Notification and News", "href": "lab-news.html"},
        {"label": "General Plastics News", "href": "plastics-news.html"},
        {"label": "News and Media (Int.)", "href": "media-int.html"},
        {"label": "News and Media (Domestic)", "href": "media-domestic.html"},
        {"label": "Team Proud", "href": "team-proud.html"}]},
    {"label": "Life", "children": [
        {"label": "Friends and Gallery", "href": "gallery.html"},
        {"label": "Networking", "href": "networking.html"}]},
    {"label": "Lecture", "href": "lecture.html"},
    {"label": "Contact", "href": "contact.html"},
]

PAGES = [
    # (출력 파일, 템플릿, 제목, 메뉴 그룹)
    ("index.html", "home.html", None, "Home"),
    ("research.html", "research.html", "Research Interests", "Home"),
    ("advisor.html", "advisor.html", "Main Advisor", "Team"),
    ("members.html", "members.html", "Members", "Team"),
    ("coadvisors.html", "coadvisors.html", "Co-advisors", "Team"),
    ("alumni.html", "alumni.html", "Alumni", "Team"),
    ("sci-papers.html", "sci_papers.html", "SCI Papers", "Achievements"),
    ("general-papers.html", "general_papers.html", "General papers", "Achievements"),
    ("patents.html", "patents.html", "Patents (Registered)", "Achievements"),
    ("hall-of-fame.html", "hall_of_fame.html", "Hall of Fame", "Achievements"),
    ("youtube.html", "youtube.html", "Youtube-Highlights", "Achievements"),
    ("lab-news.html", "lab_news.html", "Notification and News", "News"),
    ("plastics-news.html", "news_list.html", "General Plastics News", "News"),
    ("media-int.html", "news_list.html", "News and Media (Int.)", "News"),
    ("media-domestic.html", "news_list.html", "News and Media (Domestic)", "News"),
    ("team-proud.html", "team_proud.html", "Team Proud", "News"),
    ("gallery.html", "photo_grid.html", "Friends and Gallery", "Life"),
    ("networking.html", "photo_grid.html", "Networking", "Life"),
    ("lecture.html", "lecture.html", "Lecture", "Lecture"),
    ("contact.html", "contact.html", "Contact", "Contact"),
]


def paper_chart(groups):
    """연도별 논문 수·IF·인용수를 한 그래프(dot-line)에 그림.
    단위가 서로 달라 각 지표를 '최고 연도 = 100%'로 맞춰 같은 축에 표시하고,
    점에 마우스를 올리면 실제 값이 보임."""
    from html import escape
    series = [
        ("Papers", "count", "{:,}", "#2a78d6"),
        ("Total IF", "if_total", "{:,.1f}", "#eb6834"),
        ("Avg IF", "if_avg", "{:,.1f}", "#1baf7a"),
        ("Citations", "cite_total", "{:,}", "#eda100"),
        ("Avg citations", "cite_avg", "{:,.1f}", "#e87ba4"),
    ]
    series = [s for s in series if any(g.get(s[1]) for g in groups)]
    W, H, L, R, T, B = 640, 300, 44, 132, 16, 34
    pw, ph = W - L - R, H - T - B
    n = len(groups)
    xs = [L + (pw * i / (n - 1) if n > 1 else pw / 2) for i in range(n)]
    y = lambda pct: T + ph * (1 - pct / 100)
    out = [f'<figure class="ychart"><figcaption>Papers, IF and citations per year '
           f'<small>(each line scaled to its own best year = 100%; hover a dot for the value)</small></figcaption>',
           '<ul class="ylegend">' + "".join(
               f'<li><i style="background:{c}"></i>{escape(nm)}</li>' for nm, _, _, c in series) + '</ul>',
           f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Papers, IF and citations per year">']
    for pct in (0, 50, 100):
        out.append(f'<line x1="{L}" x2="{L + pw}" y1="{y(pct):.1f}" y2="{y(pct):.1f}" class="grid"/>'
                   f'<text x="{L - 6}" y="{y(pct) + 4:.1f}" class="tick" text-anchor="end">{pct}%</text>')
    for i, g in enumerate(groups):
        out.append(f'<text x="{xs[i]:.1f}" y="{H - 10}" class="tick" text-anchor="middle">{g["year"]}</text>')
    labels = []
    for nm, key, fmt, c in series:
        vals = [g.get(key) for g in groups]
        mx = max(v for v in vals if v) or 1
        pts = [(xs[i], y(v / mx * 100), v, groups[i]["year"]) for i, v in enumerate(vals) if v is not None]
        if len(pts) > 1:
            out.append(f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py, _, _ in pts)}" '
                       f'fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>')
        for px, py, v, yr in pts:
            out.append(f'<g class="dot"><title>{yr} · {escape(nm)}: {fmt.format(v)}</title>'
                       f'<circle cx="{px:.1f}" cy="{py:.1f}" r="11" class="hit"/>'
                       f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{c}" stroke="#fff" stroke-width="2"/></g>')
        if pts:
            px, py, v, _ = pts[-1]
            labels.append([py, f"{nm} {fmt.format(v)}", px])
    labels.sort()
    for k in range(1, len(labels)):  # 끝 라벨 겹침 방지
        labels[k][0] = max(labels[k][0], labels[k - 1][0] + 14)
    for ly, txt, px in labels:
        out.append(f'<text x="{px + 10:.1f}" y="{ly + 4:.1f}" class="elab">{escape(txt)}</text>')
    out.append('</svg></figure>')
    return "".join(out)


def main():
    data = {n: load(n) for n in [
        "site", "research", "advisor", "team", "sci_papers", "seo",
        "lab_news", "achievements", "media", "life"]}
    papers = data["sci_papers"]
    for key in ("after_sogang", "before_sogang"):
        for p in papers[key]:
            m = re.search(r",\s*((?:19|20)\d\d)\b", p.get("journal", ""))
            p["year"] = m.group(1) if m else "Other"
            # 출판 기준 카운트: DOI가 있는 논문만 셈 (자리표시 항목 제외)
            p["published"] = bool(p.get("doi"))
        groups = {}
        for p in papers[key]:
            groups.setdefault(p["year"], []).append(p)
        papers[key + "_by_year"] = [
            {"year": y, "papers": groups[y], "count": sum(1 for p in groups[y] if p["published"])}
            for y in sorted(groups, reverse=True)]

    # 첫 화면 슬라이드: 최근 1년 사진 (설명 속 날짜로 자동 판단)
    import datetime
    today = datetime.date.today()
    def cap_date(c):
        m = re.search(r"((?:19|20)\d\d)\.(\d{1,2})(?:\.(\d{1,2}))?", c)
        if m:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3) or 1))
        m = re.search(r"\b((?:19|20)\d\d)\b", c)
        return datetime.date(int(m.group(1)), 1, 1) if m else None
    slides = []
    for it in data["life"]["gallery"] + data["life"]["networking"]:
        d = cap_date(it.get("caption", ""))
        if it.get("image") and d and (today - d).days <= 365:
            slides.append({"image": it["image"], "caption": it["caption"]})
    data["slides"] = slides
    import json
    cpath = ROOT / "data" / "citations.json"
    cites = json.loads(cpath.read_text()) if cpath.exists() else {}
    for key in ("after_sogang", "before_sogang"):
        for p in papers[key]:
            if p.get("doi") and p["doi"].lower() in cites:
                p["cited_by"] = cites[p["doi"].lower()]
    # 연도별 통계: 총합/평균 IF (IF 숫자가 있는 출판 논문 기준), 총합/평균 인용수 (OpenAlex)
    for key in ("after_sogang", "before_sogang"):
        for g in papers[key + "_by_year"]:
            pub = [p for p in g["papers"] if p["published"]]
            ifs = []
            for p in pub:
                m = re.search(r"IF\s*\([^)]*\)\s*:\s*([\d.]+)", p.get("if_info") or "")
                if m:
                    try:
                        ifs.append(float(m.group(1).rstrip(".")))
                    except ValueError:
                        pass
            cs = [p["cited_by"] for p in pub if "cited_by" in p]
            g["if_total"] = round(sum(ifs), 1) if ifs else None
            g["if_avg"] = round(sum(ifs) / len(ifs), 1) if ifs else None
            g["if_n"] = len(ifs)
            g["cite_total"] = sum(cs) if cs else None
            g["cite_avg"] = round(sum(cs) / len(cs), 1) if cs else None
    data["paper_chart"] = paper_chart(list(reversed(papers["after_sogang_by_year"])))
    def short_cite(p):
        j = re.split(r",\s*(?:19|20)\d\d\b", p.get("journal", ""))[0].strip()
        return f"{j} {p.get('year', '')}".strip()
    data["paper_by_num"] = {p["num"]: dict(p, short=short_cite(p))
                            for k in ("after_sogang", "before_sogang") for p in papers[k]}
    import hashlib
    h = hashlib.md5()
    for f in ("static/css/style.css", "static/js/site.js"):
        h.update((ROOT / f).read_bytes())
    data["asset_v"] = h.hexdigest()[:8]

    lists = {
        "plastics-news.html": data["media"]["plastics_news"],
        "media-int.html": data["media"]["international"],
        "media-domestic.html": data["media"]["domestic"],
        "gallery.html": data["life"]["gallery"],
        "networking.html": data["life"]["networking"],
    }

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html"]))

    def yt_id(url):
        m = re.search(r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})", url or "")
        return m.group(1) if m else ""
    env.filters["yt_id"] = yt_id

    def by_year(items):
        groups = {}
        for it in items or []:
            m = re.match(r"\s*((?:19|20)\d\d)", str(it.get("date", "")))
            groups.setdefault(m.group(1) if m else "Other", []).append(it)
        return [{"year": y, "rows": groups[y]} for y in sorted(groups, reverse=True)]
    env.filters["by_year"] = by_year

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    # 연결된 도메인 (GitHub Pages용)
    (DIST / "CNAME").write_text("jyp-plastics.com\n")

    # 검색엔진용 구조화 데이터 (schema.org JSON-LD)
    BASE = "https://jyp-plastics.com/"
    person = {"@type": "Person", "@id": BASE + "advisor.html#person",
              "name": "Jeyoung Park", "alternateName": "박제영",
              "jobTitle": "Professor", "url": BASE + "advisor.html",
              "affiliation": {"@type": "CollegeOrUniversity", "name": "Sogang University"},
              "sameAs": ["https://scholar.google.co.kr/citations?user=0iebYc0AAAAJ",
                         "https://orcid.org/0000-0002-9369-1597",
                         "https://jeypark.owlstown.net/"]}
    org = {"@type": "ResearchOrganization", "@id": BASE + "#lab",
           "name": "Sustainable Plastics Lab. (JYP-Research Team)", "url": BASE,
           "logo": BASE + "img/favicon.png",
           "parentOrganization": {"@type": "CollegeOrUniversity",
               "name": "Sogang University, Dept. of Chemical and Biomolecular Engineering"},
           "address": {"@type": "PostalAddress", "streetAddress": "35 Baekbeom-ro, Mapo-gu",
                       "addressLocality": "Seoul", "postalCode": "04107", "addressCountry": "KR"},
           "founder": {"@id": person["@id"]}}
    arts = []
    for key in ("after_sogang", "before_sogang"):
        for p in papers[key]:
            if not p.get("doi"):
                continue
            a = {"@type": "ScholarlyArticle", "headline": p["title"],
                 "author": [{"@type": "Person", "name": n.strip().rstrip("*")}
                            for n in p.get("authors", "").split(",") if n.strip()],
                 "sameAs": "https://doi.org/" + p["doi"]}
            jn = re.split(r",\s*(?:19|20)\d\d\b", p.get("journal", ""))[0].strip()
            if jn:
                a["isPartOf"] = {"@type": "Periodical", "name": jn}
            if p.get("year"):
                a["datePublished"] = str(p["year"])
            arts.append(a)
    ld = {"index.html": [org, person], "advisor.html": [person, org],
          "sci-papers.html": arts}

    for out, tpl, title, group in PAGES:
        jsonld = ""
        if out in ld:
            jsonld = json.dumps({"@context": "https://schema.org", "@graph": ld[out]},
                                ensure_ascii=False).replace("</", "<\\/")
        html = env.get_template(tpl).render(
            nav=NAV, current=out, group=group, page_title=title,
            items=lists.get(out), page_desc=data["seo"]["descriptions"].get(out, ""),
            page_url=BASE + ("" if out == "index.html" else out), jsonld=jsonld, **data)
        (DIST / out).write_text(html, encoding="utf-8")

    # 검색엔진용: 페이지 목록(sitemap.xml)과 robots.txt
    base = "https://jyp-plastics.com/"
    today = __import__("datetime").date.today().isoformat()
    urls = "".join(
        f"  <url><loc>{base}{'' if out == 'index.html' else out}</loc>"
        f"<lastmod>{today}</lastmod></url>\n" for out, *_ in PAGES)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}</urlset>\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n\n#DaumWebMasterTool:e926d6cd441fec93a07bb74fdc65fa6a8ed8006166fc2762690fdfe8c4f5a4a4:kHsTc7yt7rZFR+42wFNLLw==\n")
    print(f"Built {len(PAGES)} pages → {DIST}")


if __name__ == "__main__":
    main()
