"""Enhanced website scraper - merged from domain_harvester + dealer_email_scraper.
Sitemap-first discovery, nav/footer crawling, data-attributes, obfuscated emails, phones, schema.org."""

import asyncio, json, re, requests
from bs4 import BeautifulSoup
from modules.utils import clean_email, clean_name

class WebsiteScraper:
    def __init__(self, domain, config, logger):
        self.domain = domain
        self.config = config
        self.logger = logger
        self.emails = set()
        self.people = []
        self.phones = {}
        self.base_url = None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config["user_agent"], "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-US,en;q=0.9"})

    async def run(self):
        self.base_url = await self._resolve_domain()
        if not self.base_url: return {"emails":[],"people":[],"phones":{},"tech_stack":None,"base_url":None}
        homepage = self._fetch(f"{self.base_url}/")
        if not homepage: return {"emails":[],"people":[],"phones":{},"tech_stack":None,"base_url":self.base_url}
        self._extract_all(homepage, "homepage")
        tech = self._detect_tech(homepage)
        pages = await self._discover_pages(homepage)
        crawled, n = {"/"}, 0
        for path in pages:
            if n >= self.config.get("max_pages",10) or path in crawled: continue
            crawled.add(path)
            html = self._fetch(f"{self.base_url}{path}")
            if html:
                self._extract_all(html, f"web:{path}")
                n += 1
                if len(self.people) > 10: break
                await asyncio.sleep(self.config.get("delay",2)/2)
        return {"emails":list(self.emails),"people":self.people,"phones":self.phones,"tech_stack":tech,"base_url":self.base_url}

    async def _resolve_domain(self):
        clean = self.domain.replace("https://","").replace("http://","").replace("www.","").rstrip("/")
        for url in [f"https://www.{clean}",f"https://{clean}",f"http://www.{clean}",f"http://{clean}"]:
            try:
                r = self.session.get(url, timeout=self.config["timeout"], allow_redirects=True)
                if r.status_code < 400: return r.url.rstrip("/")
            except: continue
        return f"https://{clean}"

    async def _discover_pages(self, html):
        pages = set()
        for surl in [f"{self.base_url}/sitemap.xml",f"{self.base_url}/sitemap_index.xml",f"{self.base_url}/sitemap.txt"]:
            try:
                r = self.session.get(surl, timeout=self.config["timeout"])
                if r.status_code == 200:
                    for u in re.findall(r'<loc>(.*?)</loc>', r.text):
                        if self.domain in u: pages.add(re.sub(r'^https?://[^/]+','',u) or "/")
                    if pages: break
            except: continue
        try:
            r = self.session.get(f"{self.base_url}/robots.txt", timeout=self.config["timeout"])
            if r.status_code == 200:
                for ref in re.findall(r'Sitemap:\s*(.*?)$', r.text, re.M|re.I):
                    try:
                        sr = self.session.get(ref.strip(), timeout=self.config["timeout"])
                        if sr.status_code == 200:
                            for u in re.findall(r'<loc>(.*?)</loc>', sr.text):
                                if self.domain in u: pages.add(re.sub(r'^https?://[^/]+','',u) or "/")
                    except: continue
        except: pass
        soup = BeautifulSoup(html, "html.parser")
        for sel in ["nav a","header a",".nav a",".menu a","footer a",".footer a","[class*='nav'] a","[class*='menu'] a","[class*='footer'] a"]:
            try:
                for link in soup.select(sel):
                    href = link.get("href","")
                    if href.startswith("/") and len(href)<200: pages.add(href.split("?")[0].split("#")[0])
            except: continue
        patterns = [r'\b(contact|team|staff|people|about|leadership|management|employees|personnel|service|sales|our.?team|meet.?team|who.?we.?are)\b']
        return [p for p in pages if any(re.search(pat, p.lower()) for pat in patterns)][:30] or ["/about","/about-us","/team","/our-team","/staff","/people","/leadership","/contact","/contact-us"]

    def _extract_all(self, html, source):
        soup = BeautifulSoup(html, "html.parser")
        for e in re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', html):
            c = clean_email(e)
            if c: self.emails.add(c)
        for link in soup.find_all("a", href=True):
            if link["href"].startswith("mailto:"):
                e = clean_email(link["href"].replace("mailto:","").split("?")[0])
                if e:
                    self.emails.add(e)
                    n = link.get("data-staff-name") or link.get("data-name") or link.get_text(strip=True)
                    t = link.get("data-staff-title") or link.get("data-title") or ""
                    if n and n.lower() not in ["email","email me","contact","email us"]:
                        nm = clean_name(n)
                        if nm: self._add_person(nm, t, source, email=e)
                    parent = link.parent
                    if parent:
                        pm = re.search(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', parent.get_text())
                        if pm: self.phones[e] = pm.group()
        for m in re.findall(r'\b[a-zA-Z0-9._-]+\s*\[?at\]?\s*[a-zA-Z0-9.-]+\s*\[?dot\]?\s*[a-zA-Z]{2,}\b', html, re.I):
            c = clean_email(re.sub(r'\s*\[?at\]?\s*','@',re.sub(r'\s*\[?dot\]?\s*','.',m,flags=re.I),flags=re.I))
            if c: self.emails.add(c)
        for el in soup.find_all(attrs={"data-email":True}):
            c = clean_email(el["data-email"])
            if c: self.emails.add(c)
        for el in soup.find_all(attrs={"data-staff-name":True}):
            nm = clean_name(el["data-staff-name"])
            t = el.get("data-staff-title") or el.get("data-title") or ""
            ea = clean_email(el.get("data-email")) if el.get("data-email") else None
            if nm: self._add_person(nm, t, source, email=ea)
        for sel in [".team-member",".team-card",".staff-member",".person","[class*='team']","[class*='staff']","[class*='employee']","[class*='leadership']"]:
            try:
                for card in soup.select(sel):
                    n,t = self._card_name_title(card)
                    if n: self._add_person(n, t, source, email=self._card_email(card))
            except: continue
        for tag in ["h2","h3","h4"]:
            for h in soup.find_all(tag):
                txt = h.get_text(strip=True)
                if self._is_name(txt):
                    nx = h.find_next_sibling()
                    t = nx.get_text(strip=True) if nx and self._is_title(nx.get_text(strip=True)) else ""
                    self._add_person(txt, t, source)
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                items = data if isinstance(data,list) else [data]
                if isinstance(data,dict) and "@graph" in data: items.extend(data["@graph"])
                for item in items:
                    if not isinstance(item,dict): continue
                    if "Person" in str(item.get("@type","")):
                        nm,t,e = item.get("name"),item.get("jobTitle",""),clean_email(item.get("email"))
                        if nm:
                            self._add_person(nm, t, "schema", email=e)
                            if e: self.emails.add(e)
                    elif "Organization" in str(item.get("@type","")):
                        e = clean_email(item.get("email"))
                        if e: self.emails.add(e)
            except: continue

    def _card_name_title(self, el):
        n,t = None, ""
        for tag in ["h2","h3","h4","h5","strong","b"]:
            f = el.find(tag)
            if f and self._is_name(f.get_text(strip=True)): n = f.get_text(strip=True); break
        if n:
            for p in el.find_all(["p","span","div"]):
                txt = p.get_text(strip=True)
                if self._is_title(txt) and txt != n: t = txt; break
        return clean_name(n), t

    def _card_email(self, el):
        for link in el.find_all("a", href=True):
            if link["href"].startswith("mailto:"):
                c = clean_email(link["href"].replace("mailto:","").split("?")[0])
                if c: self.emails.add(c); return c
        da = el.get("data-email") or el.get("data-mail")
        if da:
            c = clean_email(da)
            if c: self.emails.add(c); return c
        return None

    def _add_person(self, name, title, source, email=None):
        name = clean_name(name)
        if not name: return
        for ex in self.people:
            if ex["name"].lower() == name.lower():
                if not ex.get("title") and title: ex["title"] = title
                if not ex.get("email") and email: ex["email"] = email
                return
        p = {"name":name,"title":title or "","source":source}
        if email: p["email"] = email
        self.people.append(p)

    def _is_name(self, t):
        if not t or len(t)<3 or len(t)>60: return False
        w = t.split()
        if len(w)<2 or len(w)>5: return False
        if sum(1 for x in w if x[0].isupper()) < len(w)*0.5: return False
        if sum(c.isalpha() or c==" " for c in t)/len(t) < 0.8: return False
        bad = ["click","read","learn","view","more","our","the","http","www","email","phone","book","schedule","call"]
        return not any(b in t.lower() for b in bad)

    def _is_title(self, t):
        if not t or len(t)<3 or len(t)>120: return False
        kw = ["ceo","cto","cfo","coo","chief","president","vp","director","manager","head","lead","senior","founder","partner","owner","counsel","attorney","engineer","developer","specialist","coordinator","executive","sales","service","finance","general"]
        return any(k in t.lower() for k in kw)

    def _detect_tech(self, html):
        if not html: return None
        ind = {"WordPress":["wp-content"],"Shopify":["cdn.shopify.com"],"Squarespace":["squarespace.com"],"Wix":["wix.com"],"Webflow":["webflow.com"],"HubSpot":["hubspot.com"],"Next.js":["_next/static"],"Astra":["themes/astra"],"Yoast":["yoast"]}
        d = [k for k,v in ind.items() if any(p.lower() in html.lower() for p in v)]
        return ", ".join(d) if d else None

    def _fetch(self, url):
        try:
            r = self.session.get(url, timeout=self.config["timeout"], allow_redirects=True)
            if r.status_code == 200 and "text/html" in r.headers.get("content-type",""): return r.text
        except: pass
        return None
