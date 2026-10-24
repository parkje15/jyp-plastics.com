"""연구실 홈페이지 빌드 스크립트.

data/*.yaml (내용) + templates/*.html (화면) → dist/ (완성된 웹사이트)
사용법:  python build.py
"""
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
        "site", "research", "advisor", "team", "sci_papers",
        "lab_news", "achievements", "media", "life"]}
    papers = data["sci_papers"]
    for key in ("after_sogang", "before_sogang"):
        pass

    lists = {
        "plastics-news.html": data["media"]["plastics_news"],
        "media-int.html": data["media"]["international"],
        "media-domestic.html": data["media"]["domestic"],
        "gallery.html": data["life"]["gallery"],
        "networking.html": data["life"]["networking"],
    }

    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html"]))

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    # 연결된 도메인 (GitHub Pages용)
    (DIST / "CNAME").write_text("jyp-plastics.com\n")

    for out, tpl, title, group in PAGES:
        html = env.get_template(tpl).render(
            nav=NAV, current=out, group=group, page_title=title,
            items=lists.get(out), **data)
        (DIST / out).write_text(html, encoding="utf-8")
    print(f"Built {len(PAGES)} pages → {DIST}")


if __name__ == "__main__":
    main()
