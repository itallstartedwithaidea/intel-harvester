# intel-harvester

[English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [中文](README.zh.md) | [Nederlands](README.nl.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

**Outil gratuit et open-source de renseignement de domaine OSINT.** Extrayez les contacts, e-mails, numéros de téléphone, intitulés de poste, profils sociaux et données publicitaires de n'importe quel domaine — sans clé API payante.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/itallstartedwithaidea/intel-harvester.svg?style=social)](https://github.com/itallstartedwithaidea/intel-harvester)

> Conçu par un praticien gérant plus de 350 M$ en dépenses publicitaires. Combine les meilleures techniques de [theHarvester](https://github.com/laramies/theHarvester), [EmailHarvester](https://github.com/maldevel/EmailHarvester) et [snscrape](https://github.com/JustAnotherArchivist/snscrape) dans un pipeline unifié — avec en plus l'exploration de sites web, la transparence publicitaire et la détection de modèles d'e-mails qu'aucun d'entre eux ne propose.

---

## Ce qu'il fait

Donnez-lui un domaine. Récupérez tout.

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

### Résultat (CSV)

| domain | name | title | email | phone | email_verified | confidence | source | linkedin | twitter |
|--------|------|-------|-------|-------|---------------|------------|--------|----------|---------|
| jamesdean.com | John Smith | VP of Sales | john.smith@jamesdeas. | (215) 555-0123 | True | 100 | website:/team | linkedin.com/in/... | x.com/... |

---

## Démarrage rapide

```bash
git clone https://github.com/itallstartedwithaidea/intel-harvester.git
cd intel-harvester
pip install -r requirements.txt

# Domaine unique
echo "example.com" | python harvest.py - --verbose

# Liste de domaines
python harvest.py domains.txt --output contacts.csv

# Renseignement complet + JSON
python harvest.py domains.txt -o contacts.csv --json-output intel.json -v
```

---

## Le pipeline — 8 modules, tous gratuits

### 1. Reconnaissance DNS & WHOIS
Identifie le fournisseur d'e-mail (Google Workspace, Microsoft 365, Zoho), les serveurs de noms, l'hébergeur, les informations du registrant, les services connectés via les enregistrements TXT/SPF et les sous-domaines via les journaux de transparence des certificats (crt.sh).

### 2. Exploration web (améliorée)
Va au-delà du crawling basique avec des techniques issues de scrapers de production :
- **Découverte par sitemap** — analyse les sitemaps XML/TXT avant de se rabattre sur les chemins courants
- **Exploitation de robots.txt** — extrait les références de sitemaps additionnelles
- **Crawling navigation + pied de page** — scanne les éléments nav, header, menu et footer pour les liens vers les pages d'équipe
- **Résolution de domaine** — teste les variantes www/non-www, https/http et suit les redirections
- **Extraction d'attributs data** — récupère `data-email`, `data-staff-name`, `data-title` des éléments HTML
- **Détection d'e-mails obfusqués** — capture les motifs `nom [at] entreprise [dot] com`
- **Extraction de numéros de téléphone** — trouve les numéros et les associe aux contacts proches
- **Analyse Schema.org** — lit les données structurées JSON-LD pour Person/Organization
- **Détection de fiches personnel** — identifie les patterns CSS de fiches d'équipe pour extraire nom + titre
- **Détection de la stack technique** — identifie WordPress, Shopify, HubSpot, Next.js et plus
- **Arrêt anticipé** — reconnaît les annuaires complets du personnel et arrête le crawling

### 3. Moissonnage via moteurs de recherche
Interroge DuckDuckGo, Bing et Google pour les références d'e-mails `"@domaine.com"`. Recherche dans l'historique des commits GitHub les e-mails de développeurs. Recherche sur LinkedIn via DuckDuckGo les personnes de l'entreprise avec noms et titres.

### 4. Détection de modèles d'e-mails
Analyse les e-mails confirmés pour détecter automatiquement la convention de nommage de l'entreprise. Supporte 14 modèles :

`first.last` · `firstlast` · `first_last` · `flast` · `firstl` · `f.last` · `first` · `last.first` · `lastf` · `last` · `last_first` · `first.l` · `fl`

Génère des e-mails candidats pour chaque personne trouvée sans adresse.

### 5. Vérification SMTP
Se connecte au serveur MX et envoie des commandes `RCPT TO` pour vérifier si une boîte mail existe réellement — sans envoyer aucun e-mail. Retourne des scores de confiance : vérifié (100), généré par pattern (70) ou rejeté (10).

### 6. Enrichissement social
Recherche sur DuckDuckGo les profils LinkedIn et Twitter/X correspondant aux contacts découverts. Associe les profils aux fiches de contact.

### 7. Renseignement de transparence publicitaire *(optionnel)*
Découvre si le domaine diffuse des Google Ads. Identifie l'annonceur, collecte les créations publicitaires, détaille par plateforme (Search, Display, YouTube) et période. Solution de repli gratuite incluse — clé SearchAPI.io optionnelle pour les données créatives complètes.

### 8. Découverte de concurrents *(optionnel)*
Trouve d'autres entreprises qui annoncent dans le même secteur et la même région. Retourne les domaines concurrents, les noms d'annonceurs et les identifiants.

---

## Utilisation avancée

```bash
# Ignorer les étapes lentes pour des résultats rapides
python harvest.py domains.txt --skip-smtp --skip-social --skip-ads

# Renseignement publicitaire (optionnel — clé SearchAPI.io gratuite)
export SEARCHAPI_API_KEY=your_key
python harvest.py domains.txt -v

# Découverte de concurrents
python harvest.py domains.txt --competitors --vertical "plumbing" --region "Phoenix, AZ"

# Requêtes plus lentes pour éviter le rate limiting
python harvest.py domains.txt --delay 5 --max-pages 15

# Pipe depuis stdin
cat my_domains.txt | python harvest.py - -o results.csv
```

---

## Comparaison

| Fonctionnalité | intel-harvester | theHarvester | EmailHarvester | Apollo (49$/mois) | Hunter (49$/mois) |
|---------|:---:|:---:|:---:|:---:|:---:|
| Découverte d'e-mails | ✅ | ✅ | ✅ | ✅ | ✅ |
| Noms + titres | ✅ | ⚠️ limité | ❌ | ✅ | ❌ |
| Numéros de téléphone | ✅ | ❌ | ❌ | ✅ | ❌ |
| Détection de modèles d'e-mails | ✅ | ❌ | ❌ | ❌ | ✅ |
| Vérification SMTP | ✅ | ❌ | ❌ | ✅ | ✅ |
| Découverte de sitemaps | ✅ | ❌ | ❌ | ❌ | ❌ |
| Scraping d'attributs data | ✅ | ❌ | ❌ | ❌ | ❌ |
| E-mails obfusqués | ✅ | ❌ | ❌ | ❌ | ❌ |
| Analyse Schema.org | ✅ | ❌ | ❌ | ❌ | ❌ |
| Recherche LinkedIn | ✅ | ✅ | ⚠️ cassé | ✅ | ❌ |
| E-mails GitHub | ✅ | ✅ | ❌ | ❌ | ❌ |
| DNS/WHOIS | ✅ | ✅ | ❌ | ❌ | ❌ |
| Renseignement publicitaire | ✅ | ❌ | ❌ | ❌ | ❌ |
| Découverte de concurrents | ✅ | ❌ | ❌ | ❌ | ❌ |
| Détection de la stack technique | ✅ | ❌ | ❌ | ❌ | ❌ |
| Coût | **Gratuit** | Gratuit* | Gratuit | 49-99$/mois | 49$/mois |

\* Les meilleurs modules de theHarvester nécessitent des clés API payantes (Shodan, Hunter, SecurityTrails)

---

## Cas d'utilisation

- **Prospection commerciale** — trouvez les décideurs et leurs e-mails directs dans les entreprises cibles
- **Intelligence concurrentielle** — découvrez quelles publicités les concurrents diffusent, sur quelles plateformes et depuis combien de temps
- **Étude de marché** — cartographiez les structures organisationnelles à partir des sites web d'entreprises
- **Génération de leads** — construisez des listes de prospects avec des coordonnées vérifiées à partir de n'importe quelle liste de domaines
- **Développement commercial en agence** — combinez le renseignement de contacts avec les données de transparence publicitaire pour une prospection pertinente
- **Audit de sécurité** — découvrez les e-mails exposés, les sous-domaines et les services connectés

---

## Contribuer

Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives. Issues et PRs bienvenues.

---

## Licence

Licence MIT — Voir [LICENSE](LICENSE) pour les détails.

---

**Créé par [@itallstartedwithaidea](https://github.com/itallstartedwithaidea)** — Des outils conçus par des praticiens, pour ceux qui font le travail.
