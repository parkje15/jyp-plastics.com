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
        f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n")
    print(f"Built {len(PAGES)} pages → {DIST}")


if __name__ == "__main__":
    main()
