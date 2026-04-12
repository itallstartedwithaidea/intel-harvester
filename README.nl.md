# intel-harvester

[English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [中文](README.zh.md) | [Nederlands](README.nl.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

**Gratis, open-source OSINT domeinintelligentie-tool.** Extraheer contacten, e-mails, telefoonnummers, functietitels, sociale profielen en advertentie-intelligence van elk domein — geen betaalde API-sleutels nodig.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/itallstartedwithaidea/intel-harvester.svg?style=social)](https://github.com/itallstartedwithaidea/intel-harvester)

> Gebouwd door een practitioner die meer dan $350M aan advertentie-uitgaven beheert. Combineert de beste technieken van [theHarvester](https://github.com/laramies/theHarvester), [EmailHarvester](https://github.com/maldevel/EmailHarvester) en [snscrape](https://github.com/JustAnotherArchivist/snscrape) in één uniforme pipeline — plus websitecrawling, advertentietransparantie en e-mailpatroondetectie die geen van hen biedt.

---

## Wat het doet

Geef het een domein. Krijg alles terug.

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

### Uitvoer (CSV)

| domain | name | title | email | phone | email_verified | confidence | source | linkedin | twitter |
|--------|------|-------|-------|-------|---------------|------------|--------|----------|---------|
| jamesdean.com | John Smith | VP of Sales | john.smith@jamesdeas. | (215) 555-0123 | True | 100 | website:/team | linkedin.com/in/... | x.com/... |

---

## Snel starten

```bash
git clone https://github.com/itallstartedwithaidea/intel-harvester.git
cd intel-harvester
pip install -r requirements.txt

# Enkel domein
echo "example.com" | python harvest.py - --verbose

# Domeinlijst
python harvest.py domains.txt --output contacts.csv

# Volledige intelligence + JSON
python harvest.py domains.txt -o contacts.csv --json-output intel.json -v
```

---

## De pipeline — 8 modules, allemaal gratis

### 1. DNS & WHOIS Verkenning
Identificeert e-mailprovider (Google Workspace, Microsoft 365, Zoho), nameservers, hostingprovider, registrantinformatie, verbonden diensten vanuit TXT/SPF-records en subdomeinen via certificaattransparantielogs (crt.sh).

### 2. Websitescraping (verbeterd)
Gaat verder dan basiscrawling met technieken van productie-grade scrapers:
- **Sitemap-eerst ontdekking** — parseert XML/TXT-sitemaps voordat wordt teruggevallen op gangbare paden
- **Robots.txt mining** — extraheert aanvullende sitemapverwijzingen
- **Navigatie + footercrawling** — scant nav-, header-, menu- en footer-elementen op links naar teampagina's
- **Domeinresolutie** — test www/niet-www, https/http-varianten en volgt redirects
- **Data-attribuut extractie** — haalt `data-email`, `data-staff-name`, `data-title` uit HTML-elementen
- **Versluierde e-maildetectie** — vangt `naam [at] bedrijf [dot] com`-patronen op
- **Telefoonnummer extractie** — vindt telefoonnummers en koppelt ze aan nabijgelegen contacten
- **Schema.org parsing** — leest JSON-LD gestructureerde data voor Person/Organization
- **Personeelskaart detectie** — herkent CSS-patronen van teamkaarten om naam + titel te extraheren
- **Techstack detectie** — identificeert WordPress, Shopify, HubSpot, Next.js en meer
- **Vroeg stoppen** — herkent uitgebreide personeelsdirectories en stopt met crawlen

### 3. Zoekmachine harvesting
Bevraagt DuckDuckGo, Bing en Google naar `"@domein.com"` e-mailverwijzingen. Doorzoekt GitHub-commitgeschiedenis op ontwikkelaar-e-mails. Zoekt LinkedIn via DuckDuckGo naar mensen bij het bedrijf met namen en titels.

### 4. E-mailpatroondetectie
Analyseert bevestigde e-mails om automatisch de naamconventie van het bedrijf te detecteren. Ondersteunt 14 patronen:

`first.last` · `firstlast` · `first_last` · `flast` · `firstl` · `f.last` · `first` · `last.first` · `lastf` · `last` · `last_first` · `first.l` · `fl`

Genereert kandidaat-e-mails voor elke persoon die zonder adres is gevonden.

### 5. SMTP-verificatie
Verbindt met de MX-server en stuurt `RCPT TO`-opdrachten om te controleren of een mailbox daadwerkelijk bestaat — zonder e-mail te verzenden. Retourneert betrouwbaarheidsscores: geverifieerd (100), patroon-gegenereerd (70) of afgewezen (10).

### 6. Sociale verrijking
Zoekt op DuckDuckGo naar LinkedIn- en Twitter/X-profielen die overeenkomen met ontdekte contacten. Koppelt profielen aan contactrecords.

### 7. Advertentietransparantie-intelligence *(optioneel)*
Ontdekt of het domein Google Ads draait. Identificeert de adverteerder, verzamelt advertentiecreatives, splitst uit naar platform (Search, Display, YouTube) en datumbereik. Gratis terugvaloptie inbegrepen — optionele SearchAPI.io-sleutel voor volledige creatieve data.

### 8. Concurrentontdekking *(optioneel)*
Vindt andere bedrijven die adverteren in dezelfde branche en regio. Retourneert concurrentdomeinen, adverteerdernamen en ID's.

---

## Geavanceerd gebruik

```bash
# Sla trage stappen over voor snelle resultaten
python harvest.py domains.txt --skip-smtp --skip-social --skip-ads

# Advertentie-intelligence (optioneel — gratis SearchAPI.io-sleutel)
export SEARCHAPI_API_KEY=your_key
python harvest.py domains.txt -v

# Concurrentontdekking
python harvest.py domains.txt --competitors --vertical "plumbing" --region "Phoenix, AZ"

# Langzamere verzoeken om rate limiting te voorkomen
python harvest.py domains.txt --delay 5 --max-pages 15

# Pipe vanuit stdin
cat my_domains.txt | python harvest.py - -o results.csv
```

---

## Vergelijking

| Functie | intel-harvester | theHarvester | EmailHarvester | Apollo ($49/mnd) | Hunter ($49/mnd) |
|---------|:---:|:---:|:---:|:---:|:---:|
| E-mailontdekking | ✅ | ✅ | ✅ | ✅ | ✅ |
| Namen + titels | ✅ | ⚠️ beperkt | ❌ | ✅ | ❌ |
| Telefoonnummers | ✅ | ❌ | ❌ | ✅ | ❌ |
| E-mailpatroondetectie | ✅ | ❌ | ❌ | ❌ | ✅ |
| SMTP-verificatie | ✅ | ❌ | ❌ | ✅ | ✅ |
| Sitemapontdekking | ✅ | ❌ | ❌ | ❌ | ❌ |
| Data-attribuut scraping | ✅ | ❌ | ❌ | ❌ | ❌ |
| Versluierde e-mails | ✅ | ❌ | ❌ | ❌ | ❌ |
| Schema.org parsing | ✅ | ❌ | ❌ | ❌ | ❌ |
| LinkedIn zoeken | ✅ | ✅ | ⚠️ kapot | ✅ | ❌ |
| GitHub e-mails | ✅ | ✅ | ❌ | ❌ | ❌ |
| DNS/WHOIS | ✅ | ✅ | ❌ | ❌ | ❌ |
| Advertentie-intelligence | ✅ | ❌ | ❌ | ❌ | ❌ |
| Concurrentontdekking | ✅ | ❌ | ❌ | ❌ | ❌ |
| Techstack detectie | ✅ | ❌ | ❌ | ❌ | ❌ |
| Kosten | **Gratis** | Gratis* | Gratis | $49-99/mnd | $49/mnd |

\* De beste modules van theHarvester vereisen betaalde API-sleutels (Shodan, Hunter, SecurityTrails)

---

## Toepassingen

- **Verkoopprospectie** — vind beslissers en hun directe e-mails bij doelbedrijven
- **Concurrentie-intelligence** — ontdek welke advertenties concurrenten draaien, op welke platforms en hoe lang
- **Marktonderzoek** — breng organisatiestructuren in kaart vanaf bedrijfswebsites
- **Leadgeneratie** — bouw prospectlijsten met geverifieerde contactgegevens vanuit elke domeinlijst
- **Bureau business development** — combineer contactintelligentie met advertentietransparantiedata voor relevante outreach
- **Beveiligingsaudit** — ontdek blootgestelde e-mails, subdomeinen en verbonden diensten

---

## Bijdragen

Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor richtlijnen. Issues en PR's zijn welkom.

---

## Licentie

MIT-licentie — Zie [LICENSE](LICENSE) voor details.

---

**Gebouwd door [@itallstartedwithaidea](https://github.com/itallstartedwithaidea)** — Tools gebouwd door practitioners, voor mensen die het werk doen.
