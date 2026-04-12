# intel-harvester

[English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [中文](README.zh.md) | [Nederlands](README.nl.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

**Бесплатный инструмент разведки доменов OSINT с открытым исходным кодом.** Извлекайте контакты, электронные адреса, номера телефонов, должности, профили в соцсетях и рекламную аналитику из любого домена — без платных API-ключей.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/itallstartedwithaidea/intel-harvester.svg?style=social)](https://github.com/itallstartedwithaidea/intel-harvester)

> Создано практиком, управляющим рекламными бюджетами свыше $350M. Объединяет лучшие техники [theHarvester](https://github.com/laramies/theHarvester), [EmailHarvester](https://github.com/maldevel/EmailHarvester) и [snscrape](https://github.com/JustAnotherArchivist/snscrape) в единый пайплайн — плюс сканирование сайтов, рекламная прозрачность и обнаружение шаблонов e-mail, чего нет ни у одного из них.

---

## Что он делает

Подайте домен. Получите всё.

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

### Вывод (CSV)

| domain | name | title | email | phone | email_verified | confidence | source | linkedin | twitter |
|--------|------|-------|-------|-------|---------------|------------|--------|----------|---------|
| jamesdean.com | John Smith | VP of Sales | john.smith@jamesdeas. | (215) 555-0123 | True | 100 | website:/team | linkedin.com/in/... | x.com/... |

---

## Быстрый старт

```bash
git clone https://github.com/itallstartedwithaidea/intel-harvester.git
cd intel-harvester
pip install -r requirements.txt

# Один домен
echo "example.com" | python harvest.py - --verbose

# Список доменов
python harvest.py domains.txt --output contacts.csv

# Полная разведка + JSON
python harvest.py domains.txt -o contacts.csv --json-output intel.json -v
```

---

## Пайплайн — 8 модулей, все бесплатные

### 1. DNS и WHOIS разведка
Определяет почтового провайдера (Google Workspace, Microsoft 365, Zoho), серверы имён, хостинг-провайдера, данные регистранта, подключённые сервисы из записей TXT/SPF и поддомены из логов прозрачности сертификатов (crt.sh).

### 2. Сканирование сайтов (улучшенное)
Выходит за рамки базового краулинга, используя техники промышленных скраперов:
- **Приоритет sitemap** — парсит XML/TXT-карты сайта перед обращением к стандартным путям
- **Анализ robots.txt** — извлекает дополнительные ссылки на sitemap
- **Краулинг навигации + подвала** — сканирует элементы nav, header, menu и footer в поисках ссылок на страницы команды
- **Разрешение домена** — проверяет варианты www/без www, https/http и следует за перенаправлениями
- **Извлечение data-атрибутов** — получает `data-email`, `data-staff-name`, `data-title` из HTML-элементов
- **Обнаружение замаскированных e-mail** — распознаёт шаблоны `имя [at] компания [dot] com`
- **Извлечение телефонных номеров** — находит номера телефонов и связывает их с ближайшими контактами
- **Парсинг Schema.org** — читает структурированные данные JSON-LD для Person/Organization
- **Обнаружение карточек сотрудников** — определяет CSS-паттерны карточек команды для извлечения имени + должности
- **Определение технологического стека** — идентифицирует WordPress, Shopify, HubSpot, Next.js и другие
- **Ранняя остановка** — распознаёт полные каталоги сотрудников и прекращает краулинг

### 3. Сбор через поисковые системы
Запрашивает DuckDuckGo, Bing и Google для поиска упоминаний e-mail `"@домен.com"`. Ищет в истории коммитов GitHub адреса разработчиков. Ищет людей компании на LinkedIn через DuckDuckGo с именами и должностями.

### 4. Обнаружение шаблонов e-mail
Анализирует подтверждённые адреса для автоматического определения схемы именования компании. Поддерживает 14 шаблонов:

`first.last` · `firstlast` · `first_last` · `flast` · `firstl` · `f.last` · `first` · `last.first` · `lastf` · `last` · `last_first` · `first.l` · `fl`

Генерирует кандидатные адреса для каждого найденного человека без e-mail.

### 5. SMTP-верификация
Подключается к MX-серверу и отправляет команды `RCPT TO` для проверки существования почтового ящика — без отправки писем. Возвращает оценки достоверности: подтверждено (100), сгенерировано по шаблону (70) или отклонено (10).

### 6. Социальное обогащение
Ищет в DuckDuckGo профили LinkedIn и Twitter/X, совпадающие с обнаруженными контактами. Связывает профили с записями контактов.

### 7. Аналитика рекламной прозрачности *(опционально)*
Определяет, размещает ли домен Google Ads. Идентифицирует рекламодателя, собирает рекламные креативы, разбивает по платформам (Поиск, Дисплей, YouTube) и временному диапазону. Бесплатный резервный вариант включён — опциональный ключ SearchAPI.io для полных данных о креативах.

### 8. Обнаружение конкурентов *(опционально)*
Находит другие компании, рекламирующиеся в той же отрасли и регионе. Возвращает домены конкурентов, имена рекламодателей и идентификаторы.

---

## Расширенное использование

```bash
# Пропустить медленные шаги для быстрых результатов
python harvest.py domains.txt --skip-smtp --skip-social --skip-ads

# Рекламная аналитика (опционально — бесплатный ключ SearchAPI.io)
export SEARCHAPI_API_KEY=your_key
python harvest.py domains.txt -v

# Обнаружение конкурентов
python harvest.py domains.txt --competitors --vertical "plumbing" --region "Phoenix, AZ"

# Медленные запросы для избежания ограничений частоты
python harvest.py domains.txt --delay 5 --max-pages 15

# Pipe из stdin
cat my_domains.txt | python harvest.py - -o results.csv
```

---

## Сравнение

| Функция | intel-harvester | theHarvester | EmailHarvester | Apollo ($49/мес) | Hunter ($49/мес) |
|---------|:---:|:---:|:---:|:---:|:---:|
| Обнаружение e-mail | ✅ | ✅ | ✅ | ✅ | ✅ |
| Имена + должности | ✅ | ⚠️ ограничено | ❌ | ✅ | ❌ |
| Номера телефонов | ✅ | ❌ | ❌ | ✅ | ❌ |
| Обнаружение шаблонов e-mail | ✅ | ❌ | ❌ | ❌ | ✅ |
| SMTP-верификация | ✅ | ❌ | ❌ | ✅ | ✅ |
| Обнаружение sitemap | ✅ | ❌ | ❌ | ❌ | ❌ |
| Скрапинг data-атрибутов | ✅ | ❌ | ❌ | ❌ | ❌ |
| Замаскированные e-mail | ✅ | ❌ | ❌ | ❌ | ❌ |
| Парсинг Schema.org | ✅ | ❌ | ❌ | ❌ | ❌ |
| Поиск LinkedIn | ✅ | ✅ | ⚠️ сломан | ✅ | ❌ |
| E-mail GitHub | ✅ | ✅ | ❌ | ❌ | ❌ |
| DNS/WHOIS | ✅ | ✅ | ❌ | ❌ | ❌ |
| Рекламная аналитика | ✅ | ❌ | ❌ | ❌ | ❌ |
| Обнаружение конкурентов | ✅ | ❌ | ❌ | ❌ | ❌ |
| Определение техстека | ✅ | ❌ | ❌ | ❌ | ❌ |
| Стоимость | **Бесплатно** | Бесплатно* | Бесплатно | $49-99/мес | $49/мес |

\* Лучшие модули theHarvester требуют платных API-ключей (Shodan, Hunter, SecurityTrails)

---

## Сценарии использования

- **Продажи** — находите лиц, принимающих решения, и их прямые e-mail в целевых компаниях
- **Конкурентная разведка** — узнайте, какую рекламу запускают конкуренты, на каких платформах и как давно
- **Исследование рынка** — составляйте карту организационных структур по сайтам компаний
- **Лидогенерация** — создавайте списки потенциальных клиентов с проверенной контактной информацией из любого списка доменов
- **Развитие бизнеса агентств** — сочетайте контактную разведку с данными рекламной прозрачности для целевого аутрича
- **Аудит безопасности** — обнаруживайте открытые e-mail, поддомены и подключённые сервисы

---

## Участие в проекте

См. [CONTRIBUTING.md](CONTRIBUTING.md) для руководства. Issues и PR приветствуются.

---

## Лицензия

Лицензия MIT — см. [LICENSE](LICENSE) для подробностей.

---

**Создано [@itallstartedwithaidea](https://github.com/itallstartedwithaidea)** — Инструменты от практиков для тех, кто делает дело.
