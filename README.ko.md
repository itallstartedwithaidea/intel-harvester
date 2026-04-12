# intel-harvester

[English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [中文](README.zh.md) | [Nederlands](README.nl.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

**무료 오픈소스 OSINT 도메인 인텔리전스 도구.** 유료 API 키 없이 모든 도메인에서 연락처, 이메일, 전화번호, 직책, 소셜 프로필, 광고 인텔리전스를 추출합니다.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/itallstartedwithaidea/intel-harvester.svg?style=social)](https://github.com/itallstartedwithaidea/intel-harvester)

> 3억 5천만 달러 이상의 광고 예산을 관리하는 실무자가 구축했습니다. [theHarvester](https://github.com/laramies/theHarvester), [EmailHarvester](https://github.com/maldevel/EmailHarvester), [snscrape](https://github.com/JustAnotherArchivist/snscrape)의 최고 기술을 하나의 통합 파이프라인으로 결합하고, 이들 중 어디에도 없는 웹사이트 크롤링, 광고 투명성, 이메일 패턴 감지 기능을 추가했습니다.

---

## 기능 소개

도메인을 입력하면 모든 정보를 가져옵니다.

```
$ python harvest.py domains.txt --verbose

══════ Harvesting: jamesdean.com ══════
  ► Step 1: DNS & WHOIS Recon
    Found 3 emails, MX: Google Workspace
  ► Step 2: Website Scraping
    Found 8 emails, 14 people
  ► Step 3: Search Engine Harvesting
    Found 5 emails, 7 people
  ► Step 4: Email Pattern Detection
    Pattern: first.last, generated 9 new emails
  ► Step 5: SMTP Verification
    Verified 12 / 16 emails
  ► Step 6: Social Enrichment
    Enriched 8 profiles
  ► Step 6b: Ads Transparency Intelligence
    Advertising: YES | Creatives: 23 | Platforms: ['Search', 'Display']
  ► Step 7: Correlating Results
  ✓ Total contacts: 21
```

### 출력 (CSV)

| domain | name | title | email | phone | email_verified | confidence | source | linkedin | twitter |
|--------|------|-------|-------|-------|---------------|------------|--------|----------|---------|
| jamesdean.com | John Smith | VP of Sales | john.smith@jamesdeas. | (215) 555-0123 | True | 100 | website:/team | linkedin.com/in/... | x.com/... |

---

## 빠른 시작

```bash
git clone https://github.com/itallstartedwithaidea/intel-harvester.git
cd intel-harvester
pip install -r requirements.txt

# 단일 도메인
echo "example.com" | python harvest.py - --verbose

# 도메인 목록
python harvest.py domains.txt --output contacts.csv

# 전체 인텔리전스 + JSON
python harvest.py domains.txt -o contacts.csv --json-output intel.json -v
```

---

## 파이프라인 — 8개 모듈, 모두 무료

### 1. DNS & WHOIS 정찰
이메일 제공업체(Google Workspace, Microsoft 365, Zoho), 네임서버, 호스팅 제공업체, 등록자 정보, TXT/SPF 레코드에서 연결된 서비스, 인증서 투명성 로그(crt.sh)에서 서브도메인을 식별합니다.

### 2. 웹사이트 스크래핑 (향상)
프로덕션 수준 스크래퍼 기술로 기본 크롤링을 넘어섭니다:
- **Sitemap 우선 탐색** — 일반 경로로 돌아가기 전에 XML/TXT 사이트맵을 먼저 파싱
- **robots.txt 마이닝** — 추가 사이트맵 참조 추출
- **내비게이션 + 푸터 크롤링** — nav, header, menu, footer 요소에서 팀 페이지 링크 스캔
- **도메인 해석** — www/비www, https/http 변형을 테스트하고 리다이렉트를 따라감
- **Data 속성 추출** — HTML 요소에서 `data-email`, `data-staff-name`, `data-title` 추출
- **난독화된 이메일 감지** — `name [at] company [dot] com` 패턴 포착
- **전화번호 추출** — 전화번호를 찾아 인접 연락처와 연결
- **Schema.org 파싱** — Person/Organization의 JSON-LD 구조화 데이터 읽기
- **직원 카드 감지** — 팀 카드 CSS 패턴을 매칭하여 이름 + 직책 추출
- **기술 스택 감지** — WordPress, Shopify, HubSpot, Next.js 등 식별
- **조기 중단** — 완전한 직원 디렉토리를 인식하면 크롤링 중단

### 3. 검색 엔진 수집
DuckDuckGo, Bing, Google에서 `"@domain.com"` 이메일 참조를 검색합니다. GitHub 커밋 이력에서 개발자 이메일을 검색합니다. DuckDuckGo를 통해 LinkedIn에서 회사 구성원의 이름과 직책을 검색합니다.

### 4. 이메일 패턴 감지
확인된 이메일을 분석하여 회사의 이름 규칙을 자동으로 감지합니다. 14가지 패턴 지원:

`first.last` · `firstlast` · `first_last` · `flast` · `firstl` · `f.last` · `first` · `last.first` · `lastf` · `last` · `last_first` · `first.l` · `fl`

이메일이 없는 모든 발견된 인물에 대해 후보 이메일을 생성합니다.

### 5. SMTP 검증
MX 서버에 연결하여 `RCPT TO` 명령을 발행해 메일함이 실제로 존재하는지 확인합니다 — 이메일을 보내지 않고. 신뢰도 점수 반환: 검증됨(100), 패턴 생성(70), 거부됨(10).

### 6. 소셜 보강
DuckDuckGo에서 발견된 연락처와 일치하는 LinkedIn 및 Twitter/X 프로필을 검색합니다. 프로필을 연락처 레코드에 연결합니다.

### 7. 광고 투명성 인텔리전스 *(선택)*
도메인이 Google Ads를 집행하고 있는지 확인합니다. 광고주를 식별하고, 광고 크리에이티브를 수집하며, 플랫폼(검색, 디스플레이, YouTube)과 날짜 범위별로 분류합니다. 무료 대체 방법 포함 — 전체 크리에이티브 데이터를 위한 선택적 SearchAPI.io 키.

### 8. 경쟁사 발견 *(선택)*
같은 업종과 지역에서 광고하는 다른 기업을 찾습니다. 경쟁사 도메인, 광고주 이름 및 ID를 반환합니다.

---

## 고급 사용법

```bash
# 빠른 결과를 위해 느린 단계 건너뛰기
python harvest.py domains.txt --skip-smtp --skip-social --skip-ads

# 광고 인텔리전스 (선택 — 무료 SearchAPI.io 키)
export SEARCHAPI_API_KEY=your_key
python harvest.py domains.txt -v

# 경쟁사 발견
python harvest.py domains.txt --competitors --vertical "plumbing" --region "Phoenix, AZ"

# 속도 제한 방지를 위한 느린 요청
python harvest.py domains.txt --delay 5 --max-pages 15

# stdin에서 파이프
cat my_domains.txt | python harvest.py - -o results.csv
```

---

## 비교

| 기능 | intel-harvester | theHarvester | EmailHarvester | Apollo ($49/월) | Hunter ($49/월) |
|---------|:---:|:---:|:---:|:---:|:---:|
| 이메일 발견 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 이름 + 직책 | ✅ | ⚠️ 제한적 | ❌ | ✅ | ❌ |
| 전화번호 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 이메일 패턴 감지 | ✅ | ❌ | ❌ | ❌ | ✅ |
| SMTP 검증 | ✅ | ❌ | ❌ | ✅ | ✅ |
| Sitemap 발견 | ✅ | ❌ | ❌ | ❌ | ❌ |
| Data 속성 스크래핑 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 난독화된 이메일 | ✅ | ❌ | ❌ | ❌ | ❌ |
| Schema.org 파싱 | ✅ | ❌ | ❌ | ❌ | ❌ |
| LinkedIn 검색 | ✅ | ✅ | ⚠️ 고장 | ✅ | ❌ |
| GitHub 이메일 | ✅ | ✅ | ❌ | ❌ | ❌ |
| DNS/WHOIS | ✅ | ✅ | ❌ | ❌ | ❌ |
| 광고 인텔리전스 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 경쟁사 발견 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 기술 스택 감지 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 비용 | **무료** | 무료* | 무료 | $49-99/월 | $49/월 |

\* theHarvester의 최고 모듈은 유료 API 키가 필요합니다 (Shodan, Hunter, SecurityTrails)

---

## 활용 사례

- **영업 개발** — 대상 기업에서 의사결정자와 직접 이메일을 찾기
- **경쟁 정보** — 경쟁사가 어떤 광고를 어떤 플랫폼에서 얼마나 오래 집행하는지 파악
- **시장 조사** — 기업 웹사이트에서 조직 구조 매핑
- **리드 생성** — 도메인 목록에서 검증된 연락처 정보가 포함된 잠재 고객 목록 구축
- **에이전시 비즈니스 개발** — 연락처 인텔리전스와 광고 투명성 데이터를 결합한 맞춤형 아웃리치
- **보안 감사** — 노출된 이메일, 서브도메인, 연결된 서비스 발견

---

## 기여

가이드라인은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요. Issue와 PR을 환영합니다.

---

## 라이선스

MIT 라이선스 — 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.

---

**[@itallstartedwithaidea](https://github.com/itallstartedwithaidea) 제작** — 실무자가 만든 도구, 일하는 사람들을 위해.
