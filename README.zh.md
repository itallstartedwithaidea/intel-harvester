# intel-harvester

[English](README.md) | [Français](README.fr.md) | [Español](README.es.md) | [中文](README.zh.md) | [Nederlands](README.nl.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

**免费开源的 OSINT 域名情报工具。** 从任何域名中提取联系人、电子邮件、电话号码、职位、社交媒体资料和广告情报——无需付费 API 密钥。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GitHub stars](https://img.shields.io/github/stars/itallstartedwithaidea/intel-harvester.svg?style=social)](https://github.com/itallstartedwithaidea/intel-harvester)

> 由管理超过 3.5 亿美元广告支出的从业者构建。将 [theHarvester](https://github.com/laramies/theHarvester)、[EmailHarvester](https://github.com/maldevel/EmailHarvester) 和 [snscrape](https://github.com/JustAnotherArchivist/snscrape) 的最佳技术整合到一个统一的管道中——外加网站爬取、广告透明度和电子邮件模式检测，这些都是它们所不具备的。

---

## 功能介绍

输入一个域名，获取一切信息。

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

### 输出（CSV）

| domain | name | title | email | phone | email_verified | confidence | source | linkedin | twitter |
|--------|------|-------|-------|-------|---------------|------------|--------|----------|---------|
| jamesdean.com | John Smith | VP of Sales | john.smith@jamesdeas. | (215) 555-0123 | True | 100 | website:/team | linkedin.com/in/... | x.com/... |

---

## 快速开始

```bash
git clone https://github.com/itallstartedwithaidea/intel-harvester.git
cd intel-harvester
pip install -r requirements.txt

# 单个域名
echo "example.com" | python harvest.py - --verbose

# 域名列表
python harvest.py domains.txt --output contacts.csv

# 完整情报 + JSON
python harvest.py domains.txt -o contacts.csv --json-output intel.json -v
```

---

## 管道——8 个模块，全部免费

### 1. DNS 和 WHOIS 侦察
识别邮件服务商（Google Workspace、Microsoft 365、Zoho）、域名服务器、托管商、注册人信息、通过 TXT/SPF 记录发现的关联服务，以及通过证书透明度日志（crt.sh）发现的子域名。

### 2. 网站爬取（增强版）
超越基础爬取，采用生产级爬虫技术：
- **Sitemap 优先发现** — 先解析 XML/TXT 站点地图，再回退到常见路径
- **robots.txt 挖掘** — 提取额外的站点地图引用
- **导航 + 页脚爬取** — 扫描 nav、header、menu 和 footer 元素以寻找团队页面链接
- **域名解析** — 测试 www/非 www、https/http 变体并跟随重定向
- **Data 属性提取** — 从 HTML 元素中提取 `data-email`、`data-staff-name`、`data-title`
- **混淆邮件检测** — 捕获 `name [at] company [dot] com` 模式
- **电话号码提取** — 发现电话号码并与附近的联系人关联
- **Schema.org 解析** — 读取 Person/Organization 的 JSON-LD 结构化数据
- **员工卡片检测** — 匹配团队卡片 CSS 模式以提取姓名 + 职位
- **技术栈检测** — 识别 WordPress、Shopify、HubSpot、Next.js 等
- **提前停止** — 识别完整的员工目录后停止爬取

### 3. 搜索引擎采集
查询 DuckDuckGo、Bing 和 Google 搜索 `"@domain.com"` 电子邮件引用。搜索 GitHub 提交历史中的开发者邮件。通过 DuckDuckGo 在 LinkedIn 上搜索公司人员的姓名和职位。

### 4. 邮件模式检测
分析已确认的邮件以自动检测公司的命名规则。支持 14 种模式：

`first.last` · `firstlast` · `first_last` · `flast` · `firstl` · `f.last` · `first` · `last.first` · `lastf` · `last` · `last_first` · `first.l` · `fl`

为每个没有邮箱的已发现人员生成候选邮件。

### 5. SMTP 验证
连接到 MX 服务器并发出 `RCPT TO` 命令以检查邮箱是否真实存在——不发送任何邮件。返回置信度分数：已验证（100）、模式生成（70）或已拒绝（10）。

### 6. 社交充实
在 DuckDuckGo 上搜索与已发现联系人匹配的 LinkedIn 和 Twitter/X 资料。将资料链接到联系人记录。

### 7. 广告透明度情报 *（可选）*
发现域名是否在投放 Google Ads。识别广告主，收集广告创意，按平台（搜索、展示、YouTube）和日期范围进行分类。包含免费备用方案——可选的 SearchAPI.io 密钥用于获取完整创意数据。

### 8. 竞争对手发现 *（可选）*
发现在同一行业和地区投放广告的其他公司。返回竞争对手域名、广告主名称和 ID。

---

## 高级用法

```bash
# 跳过慢速步骤以获得快速结果
python harvest.py domains.txt --skip-smtp --skip-social --skip-ads

# 广告情报（可选——免费 SearchAPI.io 密钥）
export SEARCHAPI_API_KEY=your_key
python harvest.py domains.txt -v

# 竞争对手发现
python harvest.py domains.txt --competitors --vertical "plumbing" --region "Phoenix, AZ"

# 降低请求速度以避免速率限制
python harvest.py domains.txt --delay 5 --max-pages 15

# 从 stdin 管道输入
cat my_domains.txt | python harvest.py - -o results.csv
```

---

## 功能对比

| 功能 | intel-harvester | theHarvester | EmailHarvester | Apollo（49$/月） | Hunter（49$/月） |
|---------|:---:|:---:|:---:|:---:|:---:|
| 邮件发现 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 姓名 + 职位 | ✅ | ⚠️ 有限 | ❌ | ✅ | ❌ |
| 电话号码 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 邮件模式检测 | ✅ | ❌ | ❌ | ❌ | ✅ |
| SMTP 验证 | ✅ | ❌ | ❌ | ✅ | ✅ |
| Sitemap 发现 | ✅ | ❌ | ❌ | ❌ | ❌ |
| Data 属性抓取 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 混淆邮件 | ✅ | ❌ | ❌ | ❌ | ❌ |
| Schema.org 解析 | ✅ | ❌ | ❌ | ❌ | ❌ |
| LinkedIn 搜索 | ✅ | ✅ | ⚠️ 已损坏 | ✅ | ❌ |
| GitHub 邮件 | ✅ | ✅ | ❌ | ❌ | ❌ |
| DNS/WHOIS | ✅ | ✅ | ❌ | ❌ | ❌ |
| 广告情报 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 竞争对手发现 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 技术栈检测 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 成本 | **免费** | 免费* | 免费 | 49-99$/月 | 49$/月 |

\* theHarvester 的最佳模块需要付费 API 密钥（Shodan、Hunter、SecurityTrails）

---

## 使用场景

- **销售开发** — 在目标公司中找到决策者及其直接邮箱
- **竞争情报** — 发现竞争对手正在投放什么广告、在哪些平台以及持续了多长时间
- **市场调研** — 从公司网站映射组织架构
- **潜在客户开发** — 从任何域名列表构建带有验证联系信息的潜客名单
- **代理商业务拓展** — 将联系人情报与广告透明度数据相结合，进行有针对性的外展
- **安全审计** — 发现暴露的邮件、子域名和关联服务

---

## 贡献

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。欢迎提交 Issues 和 PR。

---

## 许可证

MIT 许可证 — 详见 [LICENSE](LICENSE)。

---

**由 [@itallstartedwithaidea](https://github.com/itallstartedwithaidea) 构建** — 由从业者打造的工具，服务于实干者。
