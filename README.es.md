# intel-harvester

[English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [中文](README.zh.md) | [Nederlands](README.nl.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

**Herramienta gratuita y de código abierto de inteligencia de dominios OSINT.** Extrae contactos, correos electrónicos, números de teléfono, cargos, perfiles sociales e inteligencia publicitaria de cualquier dominio — sin claves API de pago.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/itallstartedwithaidea/intel-harvester.svg?style=social)](https://github.com/itallstartedwithaidea/intel-harvester)

> Desarrollado por un profesional que gestiona más de 350 M$ en inversión publicitaria. Combina las mejores técnicas de [theHarvester](https://github.com/laramies/theHarvester), [EmailHarvester](https://github.com/maldevel/EmailHarvester) y [snscrape](https://github.com/JustAnotherArchivist/snscrape) en un pipeline unificado — además de rastreo web, transparencia publicitaria y detección de patrones de correo que ninguno de ellos ofrece.

---

## Qué hace

Dale un dominio. Obtén todo.

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

### Resultado (CSV)

| domain | name | title | email | phone | email_verified | confidence | source | linkedin | twitter |
|--------|------|-------|-------|-------|---------------|------------|--------|----------|---------|
| jamesdean.com | John Smith | VP of Sales | john.smith@jamesdeas. | (215) 555-0123 | True | 100 | website:/team | linkedin.com/in/... | x.com/... |

---

## Inicio rápido

```bash
git clone https://github.com/itallstartedwithaidea/intel-harvester.git
cd intel-harvester
pip install -r requirements.txt

# Dominio único
echo "example.com" | python harvest.py - --verbose

# Lista de dominios
python harvest.py domains.txt --output contacts.csv

# Inteligencia completa + JSON
python harvest.py domains.txt -o contacts.csv --json-output intel.json -v
```

---

## El pipeline — 8 módulos, todos gratuitos

### 1. Reconocimiento DNS y WHOIS
Identifica el proveedor de correo (Google Workspace, Microsoft 365, Zoho), servidores de nombres, proveedor de hosting, información del registrante, servicios conectados desde registros TXT/SPF y subdominios desde los registros de transparencia de certificados (crt.sh).

### 2. Rastreo web (mejorado)
Va más allá del crawling básico con técnicas de scrapers de nivel de producción:
- **Descubrimiento por sitemap** — analiza sitemaps XML/TXT antes de recurrir a rutas comunes
- **Minería de robots.txt** — extrae referencias adicionales de sitemaps
- **Crawling de navegación + pie de página** — escanea elementos nav, header, menú y footer en busca de enlaces a páginas de equipo
- **Resolución de dominio** — prueba variantes www/no-www, https/http y sigue redirecciones
- **Extracción de atributos data** — obtiene `data-email`, `data-staff-name`, `data-title` de elementos HTML
- **Detección de correos ofuscados** — captura patrones `nombre [at] empresa [dot] com`
- **Extracción de números de teléfono** — encuentra números y los asocia con contactos cercanos
- **Análisis Schema.org** — lee datos estructurados JSON-LD para Person/Organization
- **Detección de fichas de personal** — identifica patrones CSS de tarjetas de equipo para extraer nombre + cargo
- **Detección del stack tecnológico** — identifica WordPress, Shopify, HubSpot, Next.js y más
- **Parada anticipada** — reconoce directorios completos de personal y detiene el crawling

### 3. Recolección en motores de búsqueda
Consulta DuckDuckGo, Bing y Google buscando referencias de correos `"@dominio.com"`. Busca en el historial de commits de GitHub correos de desarrolladores. Busca en LinkedIn vía DuckDuckGo personas de la empresa con nombres y cargos.

### 4. Detección de patrones de correo
Analiza los correos confirmados para detectar automáticamente la convención de nombres de la empresa. Soporta 14 patrones:

`first.last` · `firstlast` · `first_last` · `flast` · `firstl` · `f.last` · `first` · `last.first` · `lastf` · `last` · `last_first` · `first.l` · `fl`

Genera correos candidatos para cada persona encontrada sin dirección.

### 5. Verificación SMTP
Se conecta al servidor MX y emite comandos `RCPT TO` para verificar si un buzón existe realmente — sin enviar ningún correo. Devuelve puntuaciones de confianza: verificado (100), generado por patrón (70) o rechazado (10).

### 6. Enriquecimiento social
Busca en DuckDuckGo perfiles de LinkedIn y Twitter/X que coincidan con los contactos descubiertos. Vincula los perfiles a los registros de contacto.

### 7. Inteligencia de transparencia publicitaria *(opcional)*
Descubre si el dominio está ejecutando Google Ads. Identifica al anunciante, recopila creatividades publicitarias, desglosa por plataforma (Search, Display, YouTube) y rango de fechas. Método alternativo gratuito incluido — clave SearchAPI.io opcional para datos creativos completos.

### 8. Descubrimiento de competidores *(opcional)*
Encuentra otras empresas que anuncian en el mismo sector y región. Devuelve dominios de competidores, nombres de anunciantes e identificadores.

---

## Uso avanzado

```bash
# Omitir pasos lentos para resultados rápidos
python harvest.py domains.txt --skip-smtp --skip-social --skip-ads

# Inteligencia publicitaria (opcional — clave SearchAPI.io gratuita)
export SEARCHAPI_API_KEY=your_key
python harvest.py domains.txt -v

# Descubrimiento de competidores
python harvest.py domains.txt --competitors --vertical "plumbing" --region "Phoenix, AZ"

# Solicitudes más lentas para evitar el rate limiting
python harvest.py domains.txt --delay 5 --max-pages 15

# Pipe desde stdin
cat my_domains.txt | python harvest.py - -o results.csv
```

---

## Comparación

| Característica | intel-harvester | theHarvester | EmailHarvester | Apollo (49$/mes) | Hunter (49$/mes) |
|---------|:---:|:---:|:---:|:---:|:---:|
| Descubrimiento de correos | ✅ | ✅ | ✅ | ✅ | ✅ |
| Nombres + cargos | ✅ | ⚠️ limitado | ❌ | ✅ | ❌ |
| Números de teléfono | ✅ | ❌ | ❌ | ✅ | ❌ |
| Detección de patrones de correo | ✅ | ❌ | ❌ | ❌ | ✅ |
| Verificación SMTP | ✅ | ❌ | ❌ | ✅ | ✅ |
| Descubrimiento de sitemaps | ✅ | ❌ | ❌ | ❌ | ❌ |
| Scraping de atributos data | ✅ | ❌ | ❌ | ❌ | ❌ |
| Correos ofuscados | ✅ | ❌ | ❌ | ❌ | ❌ |
| Análisis Schema.org | ✅ | ❌ | ❌ | ❌ | ❌ |
| Búsqueda LinkedIn | ✅ | ✅ | ⚠️ roto | ✅ | ❌ |
| Correos GitHub | ✅ | ✅ | ❌ | ❌ | ❌ |
| DNS/WHOIS | ✅ | ✅ | ❌ | ❌ | ❌ |
| Inteligencia publicitaria | ✅ | ❌ | ❌ | ❌ | ❌ |
| Descubrimiento de competidores | ✅ | ❌ | ❌ | ❌ | ❌ |
| Detección del stack técnico | ✅ | ❌ | ❌ | ❌ | ❌ |
| Coste | **Gratis** | Gratis* | Gratis | 49-99$/mes | 49$/mes |

\* Los mejores módulos de theHarvester requieren claves API de pago (Shodan, Hunter, SecurityTrails)

---

## Casos de uso

- **Prospección comercial** — encuentra a los responsables de decisión y sus correos directos en empresas objetivo
- **Inteligencia competitiva** — descubre qué anuncios están ejecutando los competidores, en qué plataformas y durante cuánto tiempo
- **Investigación de mercado** — mapea estructuras organizacionales desde sitios web de empresas
- **Generación de leads** — construye listas de prospectos con información de contacto verificada desde cualquier lista de dominios
- **Desarrollo de negocio en agencias** — combina inteligencia de contactos con datos de transparencia publicitaria para una prospección relevante
- **Auditoría de seguridad** — descubre correos expuestos, subdominios y servicios conectados

---

## Contribuir

Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para las directrices. Issues y PRs bienvenidas.

---

## Licencia

Licencia MIT — Ver [LICENSE](LICENSE) para más detalles.

---

**Creado por [@itallstartedwithaidea](https://github.com/itallstartedwithaidea)** — Herramientas creadas por profesionales, para quienes hacen el trabajo.
