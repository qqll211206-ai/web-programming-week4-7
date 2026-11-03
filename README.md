# 4주차: JavaScript 실습

## 페이지

GitHub Pages에 배포할 경우 경로는 다음과 같습니다. 현재 배포 여부는 확인하지 못했습니다.

- 장소 탐색: https://womanliuxintian-collab.github.io/liuxintian/week4/
- 통계: https://womanliuxintian-collab.github.io/liuxintian/week4/statistics.html
- 게임: https://womanliuxintian-collab.github.io/liuxintian/week4/game.html

장소 버튼은 학교 식당, 스터디룸, 학교 잔디밭의 사진·설명과 지도 상태를 페이지 새로고침 없이 함께 전환합니다. 사진은 사용자가 제공한 원본과 일치하는 GitHub 사진을 `week4/images/`에 저장하여 상대 경로로 불러옵니다.

- 학교 식당: 사용자가 제공한 [Naver 지도](https://naver.me/xG0qbUkd). 사용자가 알려 준 다솔관 건물 이름과 학교의 [주소 안내](https://ctl.catholic.ac.kr/ctl/info/direction.do)를 사용해 [Google Maps 건물 검색 임베드](https://www.google.com/maps?q=%EA%B0%80%ED%86%A8%EB%A6%AD%EB%8C%80%ED%95%99%EA%B5%90%20%EC%84%B1%EC%8B%AC%EA%B5%90%EC%A0%95%20%EB%8B%A4%EC%86%94%EA%B4%80%20%EA%B2%BD%EA%B8%B0%EB%8F%84%20%EB%B6%80%EC%B2%9C%EC%8B%9C%20%EC%9B%90%EB%AF%B8%EA%B5%AC%20%EC%A7%80%EB%B4%89%EB%A1%9C%2043&output=embed)를 설정했습니다. Google 검색 결과와 건물 내 식당의 정확한 위치는 확인되지 않았습니다.
- 스터디룸: [Naver 지도](https://naver.me/539hXnME) 및 사용자가 제공한 [Google Maps 임베드](https://www.google.com/maps/embed?pb=!1m3!2m1!1z6rCA7Yao66at64yA7ZWZ6rWQIOyEseyLrOq1kOygleq1reygnOq1kOulmOq0gA!5e1!3m2!1szh-CN!2sus!4v1793628354279!5m2!1szh-CN!2sus). 실제 표시 결과와 정확한 위치는 확인되지 않았습니다.
- 학교 잔디밭: [Naver 지도](https://naver.me/GbydUuk9) 및 사용자가 제공한 [Google Maps 임베드](https://www.google.com/maps/embed?pb=!1m5!3m3!1m2!1s0x357cbcd317239033%3A0x6c91adb86f8948e1!2z6Z-p5Zu95aSp5Li75pWZ5aSn5a2m5qCh!5e1!3m2!1szh-CN!2sus!4v1793628507894!5m2!1szh-CN!2sus). 실제 표시 결과와 정확한 위치는 확인되지 않았습니다.

세 Naver 단축 링크는 이 환경에서 열리지 않아 최종 목적지나 좌표를 추출하지 못했습니다. 로컬 HTTP 및 headless Chrome에서 세 버튼의 선택 상태, 제목·설명·사진 경로·Naver 링크 및 지도 상태의 동기화, 문서가 새로고침되지 않는 점, 1280·375·320px에서 가로 넘침이 없는 점과 JavaScript 예외가 없음을 확인했습니다. iframe 주소 설정과 별개로 이 환경은 Google 지도에 연결하지 못해 실제 지도 표시나 위치 정확도를 확인하지 못했습니다. 실제 휴대전화와 GitHub Pages도 수동 확인이 필요합니다.

## CSV와 차트

- 원자료: R. A. Fisher, Iris (1936), UCI Machine Learning Repository, https://doi.org/10.24432/C56C76
- 제공 CSV: https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv (GitHub 연결 도구로 2026-11-02에 가져옴). 파일은 수정하지 않았습니다.
- 원자료 사용 조건: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), 출처와 변경 사항 표시. UCI 설명: https://archive.ics.uci.edu/dataset/53/iris
- 대상: 붓꽃 세 종, 각 50개 표본. 1936년 Fisher 자료이며 이 CSV에는 채집 장소와 개별 채집 날짜가 없습니다.
- 필드: sepal_length, sepal_width, petal_length, petal_width는 cm, species는 종 이름입니다. 차트는 종별 꽃받침 길이와 꽃잎 길이의 평균을 각각 비교합니다. 범주별 평균 비교에 막대그래프를 사용합니다. 표본 평균은 개체별 분포나 모든 붓꽃을 대변하지 않습니다.
- 전처리: 파일을 행별로 읽고 공백을 제거하며 네 수치와 종 이름을 검증한 뒤 종별 산술평균을 계산합니다. 필수 열 누락, 중복 열, 빈 값, 잘못된 열 수·종·수치, 요청 실패 또는 Chart.js 로딩 실패는 화면에 표시합니다. 이 파일 형식은 따옴표나 필드 내 쉼표가 없는 단순 CSV입니다.
- 독립 Python 계산: setosa/versicolor/virginica의 평균 꽃받침 길이는 5.006/5.936/6.588 cm, 꽃잎 길이는 1.462/4.260/5.552 cm입니다. JS에서 같은 결과를 확인했습니다.

## 캠퍼스 별 모으기

방향키/WASD 또는 캔버스를 누르거나 끌어서 이동합니다. 별을 모으면 1점, 돌에 닿으면 생명 1개가 줄고 잠시 무적 상태가 됩니다. 30초 또는 생명 0에서 끝나며 다시 하기 버튼으로 점수, 생명, 시간과 애니메이션을 초기화합니다.

실제 코드 자가 테스트에서 초기 별이 플레이어 위치에 생성되면 시작과 동시에 1점이 되는 문제를 발견했습니다. 별이 플레이어에 너무 가까우면 먼 위치로 옮기도록 변경했고, 같은 난수 조건에서 초기 0점, 한 번 수집 후 1점, 연속 재시작 후 점수 0·생명 3·시간 30 및 대기 애니메이션 프레임 1개를 확인했습니다. 이는 모의 Canvas/프레임 환경의 테스트입니다.

## 실행과 확인

프로젝트 루트에서 `python -m http.server 8765` 실행 후 http://127.0.0.1:8765/week4/ 에 접속합니다. `file://`로 열면 CSV 요청이 제한될 수 있습니다. Chart.js CDN과 Google 지도는 네트워크가 필요합니다.

앞선 실험 확인: 세 JS 파일의 `node --check` 통과, 로컬 HTTP에서 페이지와 스크립트 및 CSV 8개 경로가 모두 200 응답, Python과 JS 모의 환경에서 CSV 150행과 두 평균 일치, 게임 로직의 초기 점수·수집·연속 재시작 확인. 헤드리스 Chrome은 외부 Chart.js를 불러오지 못했습니다. 통계·게임 화면의 실제 상호작용과 기기별 확인은 여전히 필요합니다. 장소 전환의 후속 브라우저 검사 결과는 위 지도 설명을 참고하세요.

수동 확인: 브라우저에서 세 장소 버튼을 차례로 누르고 설명과 사진이 바뀌는지 확인합니다. 통계 탭 두 개를 전환하고 두 차트와 설명을 확인합니다. 게임을 시작해 키보드와 마우스로 별을 수집하고 충돌·종료·재시작을 확인합니다. 개발자 도구의 좁은 화면에서 가로 스크롤과 터치를 확인합니다. 실제 휴대전화, 각 지도 위치, GitHub Pages 배포는 **수동 확인 필요**입니다.

Codex가 HTML/CSS/JavaScript 작성과 위 자동 검사를 도왔습니다. 작성자의 핵심 코드 확인 및 실제 기기 검토는 아직 확인되지 않았습니다.

# 5주차 · 나만의 취향 밸런스 게임

## 캠퍼스 하루 취향 밸런스 게임

대학생 친구들이 캠퍼스에서의 하루를 상상하며 8개의 선택을 하고 서로의 취향을 비교하는 게임입니다. 조별 과제 역할, 비 오는 공강, 하루를 마친 저녁, 주말 동아리 활동을 비롯한 상황을 직접 구성했습니다. 공식 주차 페이지에 접근할 수 없어 공식 예제와의 중복 여부는 확인하지 못했습니다.

각 질문의 A는 조용한 선택, B는 활동적인 선택입니다. B가 0~2개면 고요한 충전형, 3~5개면 느긋한 균형형, 6~8개면 활동 탐험형입니다. 각 유형에 맞는 짧은 하루 제안을 제공합니다. 두 번째 참가자가 완료하면 직전의 다른 완료 기록과 같은 선택 및 다른 선택의 개수를 보여 줍니다. 별명은 선택 사항이며 빈 값은 ‘캠퍼스 친구’가 됩니다. 실명이나 학번, 연락처를 입력하지 않도록 안내합니다.

예상 GitHub Pages 경로: https://womanliuxintian-collab.github.io/liuxintian/week5/ (배포 및 접속 **미확인**).

## 저장 방식

`sessionStorage`의 `week5.balance.draft`에는 참가 ID, 버전, 별명, 현재 문항 및 답변이 들어갑니다. 같은 탭을 새로고침하면 이어 할 수 있습니다. 독립적으로 연 새 탭은 일반적으로 별도 세션을 갖지만 브라우저가 opener가 있는 탭을 만들거나 탭을 복제할 때 초기 sessionStorage가 복사될 수 있습니다. 이후에는 서로 독립적으로 변경됩니다.

`localStorage`의 `week5.balance.history`에는 참가 ID, 버전, 별명, 답변, 결과, 완료 시각을 최근 20개까지 저장합니다. 완료 ID를 확인해 중복 저장을 막고 저장에 성공한 뒤 진행 기록을 지웁니다. 저장에 실패하면 경고하고 진행 기록을 유지합니다. JSON.stringify/JSON.parse를 사용하며 버전, 자료형, 질문 ID, 선택값, 결과 등을 검사합니다. 잘못된 JSON이나 구조 및 저장소 접근 실패는 안내하고 안전한 기본값으로 화면을 유지합니다. ‘저장 데이터 다시 보기’는 저장소를 다시 읽습니다.

진행 기록 삭제, 개별 완료 기록 삭제, 완료 기록 전체 삭제는 지정된 이 게임의 키만 수정하며 다른 주차의 저장소는 건드리지 않습니다. 별명과 기록은 textContent로 표시합니다.

## 실행 및 검증

프로젝트 루트에서 `python -m http.server 8766 --bind 127.0.0.1`을 실행하고 http://127.0.0.1:8766/week5/ 를 엽니다. 별도의 백엔드, API, 라이브러리는 필요하지 않습니다.

2026-11-02에 로컬 HTTP와 headless Chrome(375×800)을 사용해 다음을 자동 확인했습니다. 두 문제 선택 후 새로고침과 이어하기, 별명 및 선택 보존, 독립 새 탭의 빈 진행 기록, 완료 후 새 탭과 새로고침에서 이력 보존, 완료 버튼 연속 클릭의 중복 방지, 다음 친구 시작 시 기존 이력 보존, 두 참가자 선택 0개 일치/8개 차이 비교, 개별·진행·전체 삭제 후 새로고침, 다른 저장 키 유지, 잘못된 JSON과 숫자 구조, 저장 쓰기 실패 시 안내, `<b>test</b>`의 문자 표시, 가로 넘침과 콘솔 예외 없음을 확인했습니다. 브라우저를 완전히 종료한 뒤 다시 켜는 검사와 실제 휴대전화 검사는 수행하지 않았습니다.

재현 스크립트는 `week5/tests/cdp-test.js`입니다. 위 HTTP 서버와 Chrome DevTools 포트 9223이 필요합니다. 예를 들어 별도의 임시 프로필로 Chrome을 `--headless=new --remote-debugging-port=9223 --remote-allow-origins=* --user-data-dir=<임시경로>` 옵션으로 실행한 다음 `node week5/tests/cdp-test.js`를 실행합니다. 이 테스트는 해당 로컬 출처의 이 게임 저장 데이터를 변경하므로 기존 기록이 없는 테스트 프로필에서만 실행하세요.

Codex가 질문, 결과 로직, 화면과 저장·검증·삭제 코드를 작성하고 위 자동 검사를 수행했습니다. 친구나 작성자의 수동 테스트는 확인되지 않았습니다. 실제 휴대전화와 온라인 배포는 수동 확인이 필요합니다.

# 6주차 · Flask 서버 계산 실습

교수님의 주차 페이지와 starter ZIP에 접근하지 못해 공식 파일을 사용하지 않고 요구사항을 바탕으로 별도 구현했습니다. 기존 주차 파일은 변경하지 않았습니다.

## 실습 1: 이미지 처리

`week6`에서 Python 3.12 가상환경을 만들고 `python -m pip install -r requirements.txt`를 실행한 뒤 `python -m flask --app app run --port 5000`으로 시작합니다. http://127.0.0.1:5000/ 에서 JPEG/PNG를 선택하고 흑백, Gaussian Blur, Canny 중 하나를 고릅니다. 일반 form은 결과 PNG로 페이지를 이동하고, fetch는 원본과 결과를 현재 페이지에서 비교합니다. 이미지는 메모리에서 처리하며 디스크에 저장하지 않습니다.

서버는 파일 크기 5 MiB, 원본 픽셀 수 800만 이하, 파일 내용의 JPEG/PNG 형식, 처리 종류 및 3~51 홀수 커널을 검사합니다. 긴 변이 1600px를 넘으면 비율을 유지해 축소합니다. `GET /health`는 `{"status":"ok"}`를 반환합니다.

알고리즘 시간은 OpenCV 변환만, 서버 시간은 요청 처리 시작부터 응답을 만들 때까지의 검증·디코딩·축소·계산·PNG 인코딩 등을 포함합니다. 브라우저 왕복 시간은 fetch 시작부터 응답 본문 Blob 수신 완료까지이며 네트워크와 서버 시간을 포함합니다. 측정 도구의 오버헤드와 캐시·워밍업에 따라 달라집니다.

2026-11-02 Windows 로컬 Flask 개발 서버, Python 3.13.9, OpenCV 4.13.0, headless Chrome에서 직접 만든 동일 패턴의 JPEG를 크기별로 각각 한 번 처리한 결과입니다. 배포된 서버나 실제 사진의 성능은 아닙니다.

| 입력 크기 | Gaussian 커널 | 결과 크기 | 알고리즘 ms | 서버 ms | 브라우저 왕복 ms |
| --- | ---: | --- | ---: | ---: | ---: |
| 400×300 | 3 | 400×300 | 1.095 | 8.533 | 13.8 |
| 400×300 | 31 | 400×300 | 2.178 | 10.323 | 14.9 |
| 2400×1800 | 3 | 1600×1200 | 1.212 | 97.087 | 109.5 |
| 2400×1800 | 31 | 1600×1200 | 5.025 | 108.696 | 121.7 |

Flask 테스트 클라이언트에서 세 효과의 PNG 디코딩, 빈 파일, 잘못된 파일·효과·커널, 5 MiB 초과, 픽셀 초과, 축소, 404, 413, `/health`를 확인했습니다. Chrome에서 fetch 성공과 결과 표시, 일반 form의 PNG 응답, 버튼 복구 및 375px 너비를 확인했습니다. 실제 휴대전화 검사는 미실시입니다.

### Render 배포

아직 배포하지 않았으며 외부 URL 및 외부 `/health` 확인 결과는 없습니다. GitHub에 `week6/`을 반영한 뒤 Render에서 New → Web Service로 저장소를 연결하고 다음을 설정합니다.

- Runtime: Python 3; Root Directory: `week6`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120`
- 환경 변수: `PYTHON_VERSION=3.12.12`; Health Check Path: `/health`
- 사용 가능하면 Free 선택. 배포 후 실제 `https://<서비스>.onrender.com/health`와 이미지 업로드, 휴대전화 접근을 확인합니다.

Render [Free 안내](https://render.com/docs/free)에 따르면 무료 서비스는 유휴 시 중지될 수 있습니다. 실제 계정의 가용 플랜과 한도는 배포 시 확인하세요. 지정 의존성의 Render 빌드는 아직 확인하지 못했습니다.

## 실습 2: Piper TTS (Windows 로컬)

`week6`에서:

```text
python -m pip install -r requirements-tts.txt
python -m piper.download_voices en_US-lessac-low --download-dir models
python -m flask --app tts_app run --debug --port 5000
```

http://127.0.0.1:5000/tts 에서 영어 문장과 발화 길이 배율을 선택합니다. 모델은 [Piper voices](https://huggingface.co/rhasspy/piper-voices)의 `en_US-lessac-low`이며 `models/en_US-lessac-low.onnx`와 `.onnx.json`이 필요합니다. 서버는 첫 요청에서 모델을 불러와 재사용하고 실제 WAV를 생성하도록 작성했습니다. 브라우저는 WAV를 디코딩해 파형을 그리며 생성 시간·길이·크기를 표시합니다. 도서관 및 동아리 행사 방송 문장을 한 번에 입력하는 버튼을 추가했습니다.

빈 문자열, 500자 초과, 비영문, 잘못된 배율은 400이고 모델이 없으면 503입니다. 테스트에서 이 오류 경로와 모델 부재 시 브라우저 안내 및 버튼 복구를 확인했습니다. 로컬 환경에 Piper가 없었고 패키지 설치는 장시간 완료되지 않아 중단했습니다. 모델 호스트에도 직접 연결할 수 없었으며 다운로드 명령은 모듈 부재로 실행되지 않았습니다. 따라서 **두 문장의 실제 추론, WAV 길이·크기·파형 비교 및 파형 스크린샷은 미완료**입니다. 모델을 설치한 환경에서 두 예시 버튼으로 각각 생성해 이 항목을 기록해야 합니다.

## 재현 가능한 테스트와 AI 사용

`python -m unittest discover -s week6/tests -v`로 API 검사를 재현할 수 있습니다. Chrome DevTools 포트 9224와 각각 8767(이미지), 8768(TTS) 포트의 로컬 서버를 준비하면 `node week6/tests/browser-image.js`와 `node week6/tests/browser-tts.js`를 실행할 수 있습니다. TTS 브라우저 테스트는 모델이 없는 상태를 전제로 합니다.

Codex가 서버와 화면을 작성하고 위 테스트 및 시간 측정을 수행했습니다. Python 3.12, Render, 실제 기기, Piper 추론 및 파형은 확인하지 못했으며 사용자의 수동 확인이 필요합니다.

# 7주차 · 로그인하는 한 줄 게시판

## 캠퍼스 한 줄 이야기

캠퍼스에서 발견한 작은 기쁨과 바라는 점을 나누는 게시판입니다. `week7/app.py`의 게시판 제목과 질문, `templates/comments.html`, `static/style.css`를 캠퍼스 테마로 구성했습니다. [실제 로컬 브라우저 화면](week7/screenshots/board.png)은 로그인하지 않은 빈 게시판을 캡처한 것입니다.

주차 공식 페이지와 세 단계 ZIP에 접근할 수 없어 공식 코드를 사용하지 않고 하나의 Flask/SQLite 앱으로 구현했습니다. 사용자와 댓글의 기존 기본 테이블에 관리자·차단·연습 계정 표시와 작성 시각이 없으면 추가합니다. `reports`와 작성 제한 기록 테이블은 기존 행을 지우지 않고 생성하며, 새로운 외래 키는 cascade를 사용합니다. 이전 스키마의 cascade 유무와 관계없이 앱의 삭제·연습 데이터 정리는 관련 행을 명시적으로 삭제합니다. 공식 ZIP의 실제 스키마와는 대조하지 못했습니다.

## Windows PowerShell에서 실행

`week7` 폴더에서 Python 3.12 가상환경을 활성화한 뒤:

```powershell
python -m pip install -r requirements.txt
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
python -m flask --app app init-db
python -m flask --app app run --debug --port 5000
```

http://127.0.0.1:5000/ 에서 계정을 등록하고 로그인합니다. 개발 세션이 유지되는 동안 같은 `SECRET_KEY`를 사용하세요. `init-db`는 반복해도 기존 계정과 게시물을 삭제하지 않습니다. 로컬 관리자 설정은 웹에서 별도 계정을 먼저 등록한 다음, 같은 PowerShell에서 `$env:WEEK7_ADMIN_USERNAME = '<등록한 전용 관리자 ID>'`와 `python -m flask --app app promote-admin`을 사용합니다. 비밀번호·실제 키·데이터베이스는 공개 저장소에 올리지 않습니다.

## 기능 및 실제 테스트

비밀번호는 Werkzeug 해시로 저장합니다. 로그인·로그아웃과 모든 변경 POST에 CSRF 토큰 검증이 있으며 사용자와 관리자 권한, 차단 여부는 서버에서 검사합니다. 로그인 사용자는 1~300자의 한 줄을 쓰고 자기 글을 삭제할 수 있습니다. 계정별 1분 3개 제한은 삭제 후에도 유지됩니다. 다른 사람의 글은 이유를 적어 한 번만 신고할 수 있습니다.

관리자는 내용 검색, 신고 글 필터와 이유 확인, 삭제, 계정 이용 제한 및 해제, 연습 계정 생성과 삭제를 할 수 있습니다. 연습 계정 두 개와 각 두 개의 `[연습]` 글을 만들며 임시 비밀번호는 생성 직후 응답에만 표시하고 DB에는 해시만 남깁니다. 삭제는 연습 계정에 연결된 데이터만 대상으로 합니다.

2026-11-02에 Windows Python 3.13.9와 Flask 테스트 클라이언트의 격리된 임시 DB에서 다음을 확인했습니다. 등록·중복·잘못된 비밀번호·해시, CSRF 누락과 잘못된 토큰, 일반 사용자의 관리자 403, A의 글을 B가 보고 삭제하지 못하는 동작, B의 글을 A가 확인하는 동작, 별도 Python 프로세스에서 기존 글 보존, HTML 이스케이프, 자기 글 신고 거부와 중복 신고 방지, 관리자 대소문자 검색·신고 필터·삭제·차단·해제, 연습 데이터 반복 생성 및 정리 후 일반 데이터 보존, 빈도 제한과 삭제 후 우회 방지, 이전 기본 스키마의 반복 마이그레이션을 자동 검사했습니다. 관리자 승격 및 환경변수 기반 초기화 명령도 임시 계정으로 검사했습니다.

```text
python -m unittest discover -s week7/tests -v
Ran 5 tests
OK
```

별도로 로컬 HTTP 서버와 headless Chrome에서 게시판 화면, 375px 화면 가로 넘침 없음, 비관리자 403 및 CSRF 누락 400을 확인했습니다. 실제 휴대전화와 Python 3.12 환경은 확인하지 않았습니다. 브라우저 검사는 포트 8769의 서버와 Chrome DevTools 포트 9225를 준비한 후 `node week7/tests/browser-smoke.js`로 재현할 수 있습니다.

## Render 및 학교 제출

Render 외부 URL: **미배포·미확인**. 저장소에 코드를 반영한 다음 Render New → Web Service에서 저장소를 연결합니다.

- Runtime: Python 3; Root Directory: `week7`
- Build: `pip install -r requirements.txt`
- Start: `python -m flask --app app init-db && python -m flask --app app ensure-admin && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2`
- 환경 변수: 별도로 생성한 강력한 `SECRET_KEY`, 전용 `WEEK7_ADMIN_USERNAME`, 12자 이상 전용 `WEEK7_ADMIN_PASSWORD`, `APP_HTTPS=1`, `PYTHON_VERSION=3.12.12`

`ensure-admin`은 계정이 없으면 생성합니다. 같은 이름의 기존 계정이 있으면 환경 변수의 비밀번호가 기존 해시와 일치해야 하며, 임의의 이름 일치만으로 권한을 부여하거나 비밀번호를 덮어쓰지 않습니다. 환경 변수를 변경한 뒤 불일치 오류가 나면 계정 상태를 안전하게 확인해야 합니다.

[Render의 무료 서비스](https://render.com/docs/free)는 재시작·재배포·유휴 중지 시 로컬 SQLite 데이터가 사라질 수 있어 영구 저장을 보장하지 않습니다. 배포 후 외부 URL에서 계정·권한·신고·관리 기능을 확인해야 합니다. Cyber Campus 최종 제출의 GitHub URL, Render URL, 실험 관리자 ID와 PW 중 ID/PW는 학교의 **비공개 제출란에만** 입력합니다. 공개 README, 코드, 스크린샷에는 적지 않습니다.

Codex가 구현, 위 자동 테스트 및 스크린샷을 수행했습니다. 실제 배포, 휴대전화 검사와 학생의 수동 검토는 아직 확인되지 않았습니다.
