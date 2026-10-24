# JYP-Research Team 홈페이지 (jyp-plastics.com)

## 내용 고치는 법
화면 디자인은 건드리지 않고 `data/` 폴더의 파일만 고치면 됩니다.

| 바꾸고 싶은 것 | 파일 |
|---|---|
| 첫 화면 공지·환영 문구, 주소, 연락처 | `data/site.yaml` |
| 새 소식 (Notification and News) | `data/lab_news.yaml` (맨 위에 한 줄 추가) |
| SCI 논문 | `data/sci_papers.yaml` (맨 위에 추가) |
| 구성원·졸업생·공동지도교수 | `data/team.yaml` |
| 교수 소개 | `data/advisor.yaml` |
| 특허·일반논문·Hall of Fame·YouTube | `data/achievements.yaml` |
| 언론보도·Plastics News·Team Proud | `data/media.yaml` |
| 갤러리·네트워킹·강의 | `data/life.yaml` |
| 연구 분야 소개 | `data/research.yaml` |

https://github.com/parkje15/jyp-plastics.com 에서 파일을 열고 연필(✏️) 버튼으로 수정한 뒤 "Commit changes"를 누르면
1~2분 뒤 사이트에 자동 반영됩니다.

## 직접 만들어 보기 (선택)
```
pip install -r requirements.txt
python build.py      # → dist/ 폴더에 완성된 사이트
```
