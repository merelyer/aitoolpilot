# 🤖 AI Income Automation

**Fully automated DeepSeek-powered revenue engine. Zero human touch required.**

A self-running system that researches trending topics, generates SEO-optimized content using DeepSeek, builds a static website, and monetizes via affiliate marketing — all on autopilot.

---

## 💰 Revenue Model

| Stream | Description | Timeline |
|--------|-------------|----------|
| **Affiliate Commissions** | SaaS/tool recommendations earn 20-33% recurring | Month 3+ |
| **Display Ads (AdSense)** | Once traffic exceeds 10K monthly visits | Month 6+ |
| **Sponsored Posts** | Once domain authority builds | Month 12+ |

### Estimated Revenue Trajectory
```
Month 1-3:   $0-50     (building content, search engines indexing)
Month 4-6:   $50-500   (traffic growing, first conversions)
Month 6-12:  $500-2000 (established rankings, steady traffic)
Month 12+:   $2000+    (authority site with 200+ indexed posts)
```

### Cost Structure
```
DeepSeek API:          low-cost per generated post
Cloudflare Pages:      Free
Domain (optional):     ~$10/year
Total monthly:         ~$1-3 (at 3 posts/day)
```

---

## 🚀 Quick Start

### 1. Setup
```bash
# Clone or navigate to project
cd ai-income-automation

# Install dependencies
pip install -r requirements.txt

# Set your DeepSeek API key
export DEEPSEEK_API_KEY=sk-...

# Get a key at: https://platform.deepseek.com/
```

### 2. Run
```bash
# Generate content and build site (one cycle)
python run.py --once

# Generate AND deploy to Cloudflare Pages
python run.py --once --deploy

# Run continuously (generates every 8 hours)
python run.py --daemon

# Check environment status
python run.py --status

# Show cron setup instructions
python run.py --schedule
```

### 3. Deploy
```bash
# Deploy to Cloudflare Pages (requires: npm install -g wrangler)
python run.py --deploy-only

# Or manually deploy the site/ directory to:
# - Cloudflare Pages (wrangler pages deploy site/)
# - Netlify (netlify deploy --dir=site --prod)
# - GitHub Pages (push site/ to gh-pages branch)
# - Any static host (S3, Vercel, Render, etc.)
```

### 4. Automate
```bash
# Add to crontab (Linux/macOS):
0 */8 * * * cd /path/to/ai-income-automation && python run.py --once >> logs/cron.log 2>&1

# Or run as daemon:
python run.py --daemon
```

---

## 📊 Project Structure

```
ai-income-automation/
├── run.py                  # Main entry point
├── src/
│   ├── content_engine.py   # DeepSeek-powered content generation
│   ├── deploy.py           # Deployment to Cloudflare/Netlify/GitHub
│   └── scheduler.py        # Scheduled recurring runs
├── config/
│   └── settings.json       # All configuration
├── site/                   # Generated static site (deployable)
│   ├── index.html          # Homepage
│   ├── sitemap.xml         # SEO sitemap
│   ├── robots.txt          # Crawler instructions
│   ├── ai-writing-tools/   # Category pages
│   └── best-ai-.../        # Individual post pages
├── data/
│   ├── posts/              # Generated post JSON files
│   └── topics/             # Researched topic data
└── logs/                   # Runtime logs
```

---

## ⚙️ Configuration

Edit `config/settings.json`:

```json
{
  "site": {
    "name": "AIToolPilot",
    "posts_per_run": 3,        // Posts per generation cycle
    "max_posts_total": 500     // Stop after this many total posts
  },
  "claude": {
    "model": "deepseek-chat",
    "max_tokens_per_post": 4000,
    "temperature": 0.7
  },
  "schedule": {
    "frequency_hours": 8,      // How often to generate (daemon mode)
    "publish_time_utc": "09:00"
  },
  "seo": {
    "categories": [
      "ai-writing-tools",
      "ai-image-generators",
      "ai-code-assistants",
      "ai-marketing-tools",
      "ai-productivity-tools",
      "ai-data-analysis",
      "ai-customer-service",
      "ai-video-editing"
    ]
  }
}
```

---

## 🎯 How It Works

1. **Research**: DeepSeek researches trending topics in each category
2. **Write**: DeepSeek generates 1200+ word SEO-optimized articles with comparison tables, pricing, pros/cons, FAQs
3. **Build**: System generates a complete static website with proper HTML structure
4. **SEO**: Auto-generates sitemap.xml, robots.txt, meta descriptions, canonical URLs, schema-optimized content
5. **Publish**: Deploys to Cloudflare Pages (or other static host) 
6. **Repeat**: Runs on schedule, continuously adding fresh content
7. **Monetize**: Affiliate links in content convert readers to buyers

---

## 🔑 Before Going Live

1. **Add your DEEPSEEK_API_KEY** for high-quality generated content
2. **Replace AFFILIATE_URL_PLACEHOLDER** with real affiliate links:
   - Sign up for PartnerStack, Impact, or ShareASale
   - Find AI/SaaS tools with affiliate programs
   - Replace placeholders in generated posts or in the fallback template
3. **Get a domain** (optional, Cloudflare Pages gives free subdomain)
4. **Set up Google Analytics & Search Console** for tracking
5. **Add AdSense** once you have 30+ quality posts

---

## 📈 Scaling Up

- **More categories**: Add new niches to `settings.json`
- **Better model**: adjust `config/settings.json` if you later choose a different model/provider
- **Multi-language**: Add translated categories
- **Social automation**: Add auto-posting to Twitter/X, LinkedIn
- **Email capture**: Add newsletter signup forms
- **Programmatic SEO**: Build data-driven comparison pages at scale

---

## ⚠️ Important Notes

- **Affiliate disclosure**: The FTC requires clear disclosure. All generated posts include it.
- **Content quality**: With `DEEPSEEK_API_KEY` set, DeepSeek generates publication-ready content. Without it, templates are used.
- **SEO takes time**: Expect 3-6 months before significant organic traffic.
- **This is a real business**: Tax implications apply to income generated.

---

## 📝 License

MIT — Build your automated income stream. Good luck! 🚀
