#!/usr/bin/env python3
"""
AI Income Automation - Content Generation Engine
Uses DeepSeek API to research, write, and optimize SEO content.
Fully automated — zero human touch required.

DeepSeek: $0.14/$0.28 per MTok (5-10x cheaper than Claude)
Compatible with OpenAI SDK, just change base_url.
"""

import os
import sys
import json
import time
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from openai import OpenAI
    HAS_API = True
except ImportError:
    HAS_API = False
    print("[WARN] Run: pip install openai")


class ContentEngine:
    """Core content generation engine powered by DeepSeek."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = ROOT / "config" / "settings.json"
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.site_name = self.config["site"]["name"]
        self.model = self.config["claude"]["model"]
        self.max_tokens = self.config["claude"]["max_tokens_per_post"]
        self.temperature = self.config["claude"]["temperature"]

        # Use DeepSeek API via OpenAI SDK
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))
        self.client = None
        if self.api_key and HAS_API:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com"
            )
            print(f"[OK] DeepSeek API connected (model: {self.model})")

        for sub in ["posts", "topics", "analytics"]:
            (ROOT / "data" / sub).mkdir(parents=True, exist_ok=True)
        (ROOT / "logs").mkdir(parents=True, exist_ok=True)

    def _call_api(self, system_prompt: str, user_prompt: str, max_tokens: int = None, temperature: float = None) -> str:
        """Call DeepSeek API with OpenAI-compatible format."""
        if not self.client:
            return None

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature or self.temperature,
        )
        return response.choices[0].message.content

    def research_topics(self, category: str) -> list:
        """Research trending topics using DeepSeek."""
        if not self.client:
            return self._fallback_topics(category)

        prompt = f"""You are a content strategist for an AI tools review website.
Research 5 trending, high-commercial-intent topics about "{category}" for 2025.

Return ONLY a valid JSON array. Each item must have:
- title: SEO-optimized title (50-65 chars)
- keyword: main search term
- intent: "commercial"
- competition: "low"/"medium"/"high"
- monetization_score: 1-10

Focus on comparison posts ("X vs Y"), pricing guides, and "best X" lists."""

        try:
            text = self._call_api(
                "You are an expert SEO content strategist. Return only valid JSON arrays. No markdown, no explanation.",
                prompt, max_tokens=2000, temperature=0.8
            )
            if not text:
                return self._fallback_topics(category)

            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                topics = json.loads(text[start:end])
                self._save_topics(category, topics)
                return topics
        except Exception as e:
            print(f"[ERROR] Research failed: {e}")
        return self._fallback_topics(category)

    def _fallback_topics(self, category: str) -> list:
        all_topics = {
            "ai-writing-tools": [
                {"title": "Best AI Writing Tools for 2025 (Tested & Ranked)", "keyword": "best ai writing tools 2025", "intent": "commercial", "competition": "medium", "monetization_score": 9},
                {"title": "Jasper AI vs Copy.ai vs Writesonic: Full Comparison", "keyword": "jasper vs copy.ai vs writesonic", "intent": "commercial", "competition": "high", "monetization_score": 10},
                {"title": "Best Free AI Writing Tools That Actually Work in 2025", "keyword": "free ai writing tools 2025", "intent": "commercial", "competition": "medium", "monetization_score": 7},
                {"title": "Claude vs ChatGPT vs DeepSeek for Writing: Honest Review", "keyword": "claude vs chatgpt vs deepseek writing", "intent": "commercial", "competition": "high", "monetization_score": 9},
                {"title": "AI Writing Tools Pricing Guide: What to Pay in 2025", "keyword": "ai writing tools pricing 2025", "intent": "commercial", "competition": "low", "monetization_score": 10},
            ],
            "ai-image-generators": [
                {"title": "Best AI Image Generators 2025: DALL-E vs Midjourney vs Stable Diffusion", "keyword": "best ai image generator 2025", "intent": "commercial", "competition": "high", "monetization_score": 9},
                {"title": "Midjourney Pricing 2025: Plans, Cost & Is It Worth It?", "keyword": "midjourney pricing plans 2025", "intent": "commercial", "competition": "low", "monetization_score": 8},
                {"title": "Best Free AI Art Generators No Signup Required 2025", "keyword": "free ai art generator no signup 2025", "intent": "commercial", "competition": "medium", "monetization_score": 7},
            ],
            "ai-code-assistants": [
                {"title": "Best AI Coding Assistants 2025: Copilot vs Cursor vs Claude Code", "keyword": "best ai coding assistant 2025", "intent": "commercial", "competition": "high", "monetization_score": 10},
                {"title": "GitHub Copilot vs Cursor vs Claude Code: Full Developer Comparison", "keyword": "github copilot vs cursor vs claude code", "intent": "commercial", "competition": "medium", "monetization_score": 10},
                {"title": "Cursor AI Pricing: Plans, Features & Is It Worth the Subscription?", "keyword": "cursor ai pricing review 2025", "intent": "commercial", "competition": "low", "monetization_score": 9},
            ],
            "ai-marketing-tools": [
                {"title": "Best AI Marketing Tools to Grow Your Business in 2025", "keyword": "best ai marketing tools 2025", "intent": "commercial", "competition": "medium", "monetization_score": 9},
                {"title": "AI SEO Tools Compared: SurferSEO vs MarketMuse vs Frase 2025", "keyword": "ai seo tools comparison 2025", "intent": "commercial", "competition": "medium", "monetization_score": 9},
            ],
            "ai-productivity-tools": [
                {"title": "Best AI Productivity Tools to 10x Your Workflow in 2025", "keyword": "best ai productivity tools 2025", "intent": "commercial", "competition": "medium", "monetization_score": 8},
                {"title": "Notion AI vs Mem vs Reflect: Best AI Note-Taking App 2025", "keyword": "notion ai vs mem vs reflect 2025", "intent": "commercial", "competition": "low", "monetization_score": 8},
                {"title": "Best AI Scheduling Tools & Calendar Assistants 2025", "keyword": "best ai scheduling tools 2025", "intent": "commercial", "competition": "low", "monetization_score": 8},
            ],
            "ai-data-analysis": [
                {"title": "Best AI Data Analysis Tools 2025: ChatGPT vs Julius vs Tableau", "keyword": "best ai data analysis tools 2025", "intent": "commercial", "competition": "medium", "monetization_score": 9},
                {"title": "AI Spreadsheet Tools Compared: Which One Actually Works?", "keyword": "ai spreadsheet tools comparison 2025", "intent": "commercial", "competition": "low", "monetization_score": 8},
                {"title": "Best AI Tools for Excel & Google Sheets Automation 2025", "keyword": "ai tools excel google sheets automation 2025", "intent": "commercial", "competition": "low", "monetization_score": 9},
            ],
            "ai-customer-service": [
                {"title": "Best AI Chatbots for Customer Service 2025 (Compared)", "keyword": "best ai chatbot customer service 2025", "intent": "commercial", "competition": "medium", "monetization_score": 9},
                {"title": "Zendesk AI vs Intercom vs Freshworks: Full Comparison 2025", "keyword": "zendesk ai vs intercom vs freshworks 2025", "intent": "commercial", "competition": "medium", "monetization_score": 10},
                {"title": "Best AI Help Desk Software for Small Business 2025", "keyword": "best ai help desk software small business 2025", "intent": "commercial", "competition": "low", "monetization_score": 9},
            ],
            "ai-video-editing": [
                {"title": "Best AI Video Editing Tools 2025: Runway vs Descript vs Pika", "keyword": "best ai video editing tools 2025", "intent": "commercial", "competition": "medium", "monetization_score": 9},
                {"title": "Runway AI Pricing: Plans, Features & Is It Worth It 2025?", "keyword": "runway ai pricing review 2025", "intent": "commercial", "competition": "low", "monetization_score": 8},
                {"title": "Best Free AI Video Generators That Actually Look Good 2025", "keyword": "best free ai video generators 2025", "intent": "commercial", "competition": "medium", "monetization_score": 8},
            ],
        }
        return all_topics.get(category, all_topics["ai-writing-tools"])

    def _save_topics(self, category: str, topics: list):
        path = ROOT / "data" / "topics" / f"{category}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"category": category, "date": datetime.now().isoformat(), "topics": topics}, f, indent=2)

    def generate_post(self, topic: dict, category: str) -> dict:
        """Generate a full SEO-optimized blog post using DeepSeek."""
        title = topic.get("title", "")
        keyword = topic.get("keyword", "")

        if not self.client:
            return self._fallback_post(topic, category)

        system_prompt = f"""You are a senior content writer for {self.site_name}, an AI tools review website.
Your articles must be:
- 1200+ words, genuinely helpful and detailed
- SEO-optimized with natural keyword placement
- Structured for Google featured snippets (use tables, comparison lists, clear H2/H3 headers)
- Honest and balanced — mention real pros AND cons
- Include actual pricing, feature comparisons, and use cases
- End with a practical FAQ section (5+ questions)
- Written in natural, engaging English (not AI-sounding)

CRITICAL: Return ONLY valid JSON. No markdown code blocks, no explanations.
The JSON must have these exact fields:
- title, slug, meta_description, category, content_html, featured_image_alt, keywords (array), affiliate_links (array of {{text, url, product}}), faq (array of {{question, answer}}), read_time_minutes (int)

content_html must be publication-ready HTML with proper <h2>, <h3>, <p>, <ul>, <li>, <table>, <tr>, <th>, <td>, <strong>, <div class="summary-box"> tags."""

        user_prompt = f"""Write a comprehensive comparison/review article:

TITLE: {title}
PRIMARY KEYWORD: {keyword}
CATEGORY: {category}

Structure:
1. Engaging introduction (state the problem, hook readers)
2. TL;DR summary box (<div class="summary-box"> with our #1 pick)
3. Quick comparison table (columns: Tool | Best For | Starting Price | Rating out of 5)
4. Detailed review of each option (with real features, pricing, pros/cons)
5. Pricing comparison table (columns: Tool | Free Tier | Starter | Pro | Enterprise)
6. "Who Should Use What" section (match tools to use cases)
7. Bottom Line verdict
8. FAQ section (5+ questions answering common search queries)
9. Call to action with affiliate link

IMPORTANT:
- Use AFFILIATE_URL_PLACEHOLDER for all affiliate links
- Include real, accurate pricing whenever possible
- Write naturally — this content will be read by real humans
- Make comparisons genuinely useful for decision-making

Return as JSON with content_html containing the full article HTML."""

        try:
            text = self._call_api(system_prompt, user_prompt, max_tokens=self.max_tokens)
            if not text:
                return self._fallback_post(topic, category)

            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                post = json.loads(text[start:end])
                post["generated_at"] = datetime.now(timezone.utc).isoformat()
                post["model"] = self.model
                post["topic"] = topic
                return post
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
        return self._fallback_post(topic, category)

    def _fallback_post(self, topic: dict, category: str) -> dict:
        title = topic.get("title", "Best AI Tools Comparison")
        keyword = topic.get("keyword", "ai tools")
        slug = title.lower().replace(" ", "-").replace("?", "").replace(":", "").replace("&", "and")[:80]

        return {
            "title": title,
            "slug": slug,
            "meta_description": f"Compare {keyword}. We tested the top options with real pricing, features, pros & cons. Find the best tool for your needs in 2025.",
            "category": category,
            "content_html": f"""<h2>Quick Summary</h2>
<div class="summary-box"><p><strong>TL;DR:</strong> After testing the top {keyword} options, our #1 recommendation is <a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored">Top Pick</a> — it offers the best combination of features, pricing, and ease of use for most people.</p></div>

<h2>Our Top Picks at a Glance</h2>
<table class="comparison-table">
<tr><th>Tool</th><th>Best For</th><th>Starting Price</th><th>Our Rating</th></tr>
<tr><td><a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored">Top Pick</a></td><td>Overall Best</td><td>$12/month</td><td>4.8 / 5</td></tr>
<tr><td><a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored">Runner Up</a></td><td>Power Users</td><td>$30/month</td><td>4.5 / 5</td></tr>
<tr><td><a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored">Budget Pick</a></td><td>Beginners & Budget</td><td>Free / $10/month</td><td>4.3 / 5</td></tr>
</table>

<h2>Detailed Reviews</h2>
<h3>1. Top Pick — Best Overall</h3>
<p>After extensive hands-on testing, Top Pick impressed us with its intuitive interface, powerful AI capabilities, and reasonable pricing. Starting at just $12/month, it delivers exceptional value for most users — from beginners to professionals.</p>
<p><strong>Key Features:</strong> AI-powered generation, easy-to-use dashboard, multiple export formats, team collaboration tools, API access.</p>
<p><strong>Pros:</strong> Excellent output quality, intuitive UI, affordable pricing tiers, great customer support, regular feature updates.</p>
<p><strong>Cons:</strong> Free tier has limited credits, occasional slowdowns during peak usage, advanced features require Pro plan.</p>
<p><a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored" class="cta-button">Try Top Pick Free →</a></p>

<h3>2. Runner Up — Best for Power Users</h3>
<p>Runner Up offers more advanced features and customization options, making it ideal for professional users who need granular control. At $30/month, it's pricier but delivers enterprise-grade capabilities.</p>
<p><strong>Pros:</strong> Advanced customization, excellent API, powerful automation, great for teams.</p>
<p><strong>Cons:</strong> Steeper learning curve, more expensive, overkill for basic needs.</p>
<p><a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored" class="cta-button">Try Runner Up Free →</a></p>

<h3>3. Budget Pick — Best for Beginners</h3>
<p>Budget Pick proves you don't need to spend a lot to get great results. With a generous free tier and affordable paid plans starting at $10/month, it's perfect for those just getting started.</p>
<p><strong>Pros:</strong> Great free tier, simple interface, fast learning curve, solid output quality.</p>
<p><strong>Cons:</strong> Limited advanced features, fewer integrations, smaller template library.</p>
<p><a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored" class="cta-button">Try Budget Pick Free →</a></p>

<h2>Pricing Comparison</h2>
<table class="comparison-table">
<tr><th>Tool</th><th>Free Tier</th><th>Starter Plan</th><th>Pro Plan</th><th>Enterprise</th></tr>
<tr><td>Top Pick</td><td>Yes (limited credits)</td><td>$12/month</td><td>$49/month</td><td>Custom quote</td></tr>
<tr><td>Runner Up</td><td>No</td><td>$30/month</td><td>$79/month</td><td>Custom quote</td></tr>
<tr><td>Budget Pick</td><td>Yes (generous)</td><td>$10/month</td><td>$35/month</td><td>Custom quote</td></tr>
</table>

<h2>Which One Should You Choose?</h2>
<ul>
<li><strong>Most users:</strong> Start with <a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored">Top Pick</a> — it's the best all-rounder at a fair price.</li>
<li><strong>Power users & teams:</strong> <a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored">Runner Up</a> gives you advanced features worth the premium.</li>
<li><strong>Budget-conscious:</strong> <a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored">Budget Pick</a> has a free tier that's surprisingly capable.</li>
</ul>

<h2>Bottom Line</h2>
<p>After comparing the top {keyword}, <a href="AFFILIATE_URL_PLACEHOLDER" rel="nofollow sponsored">Top Pick</a> emerges as the clear winner for most people. It strikes the perfect balance between powerful features, ease of use, and affordable pricing. Runner Up is worth the upgrade if you need advanced capabilities, and Budget Pick is great for those watching their wallet.</p>

<h2>Frequently Asked Questions</h2>
<h3>Which option is best for most users in 2025?</h3>
<p>The best choice depends on your specific needs and budget. For most people, Top Pick offers the best balance of features, quality, and price at $12/month.</p>
<h3>How much do these tools typically cost?</h3>
<p>Quality tools in this category range from free tiers to $100+/month for enterprise plans. Most individual users find the sweet spot at $12-49/month for professional-grade features.</p>
<h3>Are free options worth using?</h3>
<p>Yes! Several tools offer genuinely useful free tiers. Budget Pick's free plan is particularly generous and can handle basic needs well. However, paid plans unlock more features, higher limits, and better support.</p>
<h3>Can I use multiple tools together?</h3>
<p>Absolutely. Many professionals use 2-3 different tools for different purposes. Most offer free trials, so you can test which combination works best for your workflow before committing.</p>
<h3>Do these tools offer refunds or money-back guarantees?</h3>
<p>Most providers offer either a free trial period or a 7-30 day money-back guarantee. We recommend starting with free trials to find your best fit before paying.</p>""",
            "featured_image_alt": f"Comparison of the best {keyword} tools in 2025",
            "keywords": [keyword, f"best {keyword}", f"{keyword} review", f"{keyword} comparison", f"{keyword} pricing"],
            "affiliate_links": [
                {"text": "Top Pick", "url": "AFFILIATE_URL_PLACEHOLDER", "product": "Top Pick"},
                {"text": "Runner Up", "url": "AFFILIATE_URL_PLACEHOLDER", "product": "Runner Up"},
                {"text": "Budget Pick", "url": "AFFILIATE_URL_PLACEHOLDER", "product": "Budget Pick"},
            ],
            "faq": [
                {"question": "Which option is best for most users?", "answer": "For most people, Top Pick offers the best balance of features, quality, and price. We recommend starting with free trials to find your best fit."},
                {"question": "How much do these tools cost?", "answer": "Pricing ranges from free tiers to $100+/month for enterprise plans. Most professional plans cost $12-49/month."},
                {"question": "Are free options good enough?", "answer": "Yes, several tools offer excellent free tiers. Budget Pick's free plan is particularly generous. However, professional users will benefit from paid plans."},
            ],
            "read_time_minutes": 8,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "model": "fallback-template",
            "topic": topic,
        }

    def save_post(self, post: dict) -> Path:
        slug = post.get("slug", f"post-{random.randint(1000, 9999)}")
        path = ROOT / "data" / "posts" / f"{slug}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(post, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved: {post.get('title', slug)[:80]}")
        return path

    def build_site(self, posts: list) -> str:
        site_dir = ROOT / "site"
        site_dir.mkdir(parents=True, exist_ok=True)

        template = self._load_template()

        for post in posts:
            slug = post.get("slug", "")
            page = template
            page = page.replace("{{TITLE}}", post.get("title", ""))
            page = page.replace("{{META_DESC}}", post.get("meta_description", ""))
            page = page.replace("{{CONTENT}}", post.get("content_html", ""))
            page = page.replace("{{CATEGORY}}", post.get("category", ""))
            page = page.replace("{{DATE}}", post.get("generated_at", "")[:10])
            page = page.replace("{{READ_TIME}}", str(post.get("read_time_minutes", 7)))
            page = page.replace("{{SITE_NAME}}", self.site_name)
            page = page.replace("POST_SLUG", slug)
            page = page.replace("{{AFFILIATE_DISCLOSURE}}",
                '<p class="affiliate-disclosure">💡 <em>Disclosure: Some links on this page are affiliate links. If you click through and make a purchase, we may earn a commission at no additional cost to you. We only recommend products we have tested and believe in.</em></p>')

            post_dir = site_dir / slug
            post_dir.mkdir(parents=True, exist_ok=True)
            with open(post_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(page)

        with open(site_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(self._build_homepage(posts))

        for cat in set(p.get("category", "uncategorized") for p in posts):
            cat_dir = site_dir / cat
            cat_dir.mkdir(parents=True, exist_ok=True)
            cat_posts = [p for p in posts if p.get("category") == cat]
            with open(cat_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(self._build_category_page(cat, cat_posts))

        self._write_seo_files(posts)
        return str(site_dir)

    def _load_template(self) -> str:
        tpl_path = ROOT / "src" / "template.html"
        if tpl_path.exists():
            return tpl_path.read_text(encoding="utf-8")
        return """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{{TITLE}} | {{SITE_NAME}}</title><meta name="description" content="{{META_DESC}}"><meta name="robots" content="index,follow"><link rel="canonical" href="https://aitoolpilot.com/POST_SLUG/"><style>:root{--bg:#fff;--text:#1a1a2e;--accent:#6c63ff;--border:#e0e0e0;--card:#f8f9fa}*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui,-apple-system,sans-serif;line-height:1.8;color:var(--text);background:var(--bg);max-width:800px;margin:0 auto;padding:20px}header{padding:20px 0;border-bottom:2px solid var(--accent);margin-bottom:30px}header h1{font-size:1.5em;color:var(--accent)}header a{text-decoration:none}h2{font-size:1.6em;margin:30px 0 15px;color:#16213e;border-bottom:1px solid var(--border);padding-bottom:10px}h3{font-size:1.2em;margin:20px 0 10px;color:#0f3460}p{margin-bottom:15px}table{width:100%;border-collapse:collapse;margin:20px 0}th{background:var(--accent);color:#fff;padding:12px;text-align:left}td{padding:10px 12px;border-bottom:1px solid var(--border)}tr:nth-child(even){background:var(--card)}.summary-box{background:var(--card);border-left:4px solid var(--accent);padding:20px;margin:20px 0;border-radius:4px}.affiliate-disclosure{font-size:.85em;color:#666;background:#fff3cd;padding:10px 15px;border-radius:4px;margin:20px 0}.meta{color:#888;font-size:.9em}.category-tag{display:inline-block;background:var(--accent);color:#fff;padding:2px 10px;border-radius:12px;font-size:.8em;margin-right:8px}a{color:var(--accent)}.cta-button{display:inline-block;background:var(--accent);color:#fff!important;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:600;margin:10px 0;transition:opacity .2s}.cta-button:hover{opacity:.9}footer{margin-top:40px;padding:20px 0;border-top:1px solid var(--border);text-align:center;font-size:.9em;color:#888}ul,ol{margin:10px 0 15px 25px}li{margin-bottom:5px}</style></head><body><header><a href="/"><h1>🤖 {{SITE_NAME}}</h1></a><p style="color:#666">Expert reviews of the best AI tools — tested & compared</p></header><main><article><h1>{{TITLE}}</h1><div class="meta">📅 {{DATE}} · ⏱️ {{READ_TIME}} min read · <span class="category-tag">{{CATEGORY}}</span></div>{{AFFILIATE_DISCLOSURE}}{{CONTENT}}</article></main><footer><p>&copy; 2025 {{SITE_NAME}}. <a href="/privacy/">Privacy Policy</a> | <a href="/affiliate-disclosure/">Affiliate Disclosure</a> | <a href="/sitemap.xml">Sitemap</a></p></footer></body></html>"""

    def _build_homepage(self, posts: list) -> str:
        cards = ""
        for p in posts[:15]:
            cards += f"""<div class="post-card" style="background:var(--card);padding:20px;margin:15px 0;border-radius:8px;border:1px solid var(--border)">
<span class="category-tag">{p.get('category','')}</span>
<h3 style="margin:8px 0"><a href="/{p.get('slug','')}/">{p.get('title','')}</a></h3>
<p>{p.get('meta_description','')[:150]}...</p>
<p class="meta">⏱️ {p.get('read_time_minutes',7)} min read · 📅 {p.get('generated_at','')[:10]}</p>
</div>"""
        return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{self.site_name} - Best AI Tools Reviews & Comparisons</title><meta name="description" content="Expert reviews and comparisons of the best AI tools for writing, coding, design, marketing, and more. Find the perfect AI software for your needs."><style>:root{{--bg:#fff;--text:#1a1a2e;--accent:#6c63ff;--border:#e0e0e0;--card:#f8f9fa}}*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui,-apple-system,sans-serif;line-height:1.8;color:var(--text);background:var(--bg);max-width:960px;margin:0 auto;padding:20px}}header{{padding:30px 0;text-align:center;border-bottom:3px solid var(--accent);margin-bottom:30px}}header h1{{font-size:2.2em;color:var(--accent)}}header p{{font-size:1.2em;color:#666;margin-top:10px}}.hero{{text-align:center;padding:50px 20px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-radius:12px;margin-bottom:30px}}.hero h2{{color:#fff;font-size:2em;border:none;padding:0;margin:0 0 10px}}.hero p{{font-size:1.1em;opacity:.95}}h2{{font-size:1.5em;margin:30px 0 20px}}.category-tag{{display:inline-block;background:var(--accent);color:#fff;padding:2px 10px;border-radius:12px;font-size:.8em}}.meta{{color:#888;font-size:.9em}}a{{color:var(--accent);text-decoration:none;font-weight:600}}a:hover{{text-decoration:underline}}footer{{margin-top:40px;padding:20px 0;border-top:1px solid var(--border);text-align:center;font-size:.9em;color:#888}}</style></head><body><header><h1>🤖 {self.site_name}</h1><p>Expert Reviews & Comparisons of the Best AI Tools</p></header><main><div class="hero"><h2>Find the Perfect AI Tool for Every Task</h2><p>We test and compare AI writing tools, image generators, code assistants, and more — so you don't have to. All reviews are honest, detailed, and regularly updated.</p></div><h2>📝 Latest Comparisons & Reviews</h2>{cards}</main><footer><p>&copy; 2025 {self.site_name}. <a href="/privacy/">Privacy</a> | <a href="/affiliate-disclosure/">Disclosure</a> | <a href="/sitemap.xml">Sitemap</a></p></footer></body></html>"""

    def _build_category_page(self, category: str, posts: list) -> str:
        cards = ""
        for p in posts[:10]:
            cards += f"""<div class="post-card" style="background:var(--card);padding:20px;margin:15px 0;border-radius:8px;border:1px solid var(--border)">
<h3 style="margin:0 0 10px"><a href="/{p.get('slug','')}/">{p.get('title','')}</a></h3>
<p>{p.get('meta_description','')[:160]}...</p>
<p class="meta">⏱️ {p.get('read_time_minutes',7)} min read</p>
</div>"""
        cat_title = category.replace("-", " ").title()
        return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Best {cat_title} Reviews | {self.site_name}</title><meta name="description" content="Expert reviews and comparisons of the best {cat_title.lower()} tools. Honest ratings, pricing comparisons, and buying guides."><meta name="robots" content="index,follow"><style>:root{{--bg:#fff;--text:#1a1a2e;--accent:#6c63ff;--border:#e0e0e0;--card:#f8f9fa}}*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:system-ui,-apple-system,sans-serif;line-height:1.8;color:var(--text);background:var(--bg);max-width:800px;margin:0 auto;padding:20px}}header{{padding:20px 0;border-bottom:2px solid var(--accent);margin-bottom:30px}}header a{{text-decoration:none}}header h1{{font-size:1.5em;color:var(--accent)}}h2{{margin:25px 0 15px}}.meta{{color:#888;font-size:.9em}}a{{color:var(--accent);text-decoration:none;font-weight:600}}a:hover{{text-decoration:underline}}footer{{margin-top:40px;padding:20px 0;border-top:1px solid var(--border);text-align:center;font-size:.9em;color:#888}}</style></head><body><header><a href="/"><h1>🤖 {self.site_name}</h1></a></header><main><h2>📂 {cat_title}</h2><p>Expert reviews and comparisons of the best {cat_title.lower()} tools available today. We test each tool hands-on and provide honest, detailed reviews to help you choose.</p>{cards}</main><footer><p>&copy; 2025 {self.site_name}.</p></footer></body></html>"""

    def _write_seo_files(self, posts: list):
        urls = ""
        for p in posts:
            urls += f"  <url><loc>https://aitoolpilot.com/{p.get('slug','')}/</loc><lastmod>{p.get('generated_at','')[:10]}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n"
        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aitoolpilot.com/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>{urls}</urlset>"""
        (ROOT / "site" / "sitemap.xml").write_text(sitemap, encoding="utf-8")
        (ROOT / "site" / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://aitoolpilot.com/sitemap.xml\n")

    def run_auto(self, category: str = None) -> list:
        print(f"\n{'='*60}\n🚀 AI Income Automation - Content Engine\n   API: DeepSeek ({self.model})\n   Time: {datetime.now().isoformat()}\n{'='*60}\n")
        categories = [category] if category else self.config["seo"]["categories"]
        all_posts = []
        for cat in categories:
            print(f"📊 Researching: {cat}")
            topics = self.research_topics(cat)
            print(f"   Found {len(topics)} topics")
            for i, topic in enumerate(topics[:self.config["site"]["posts_per_run"]]):
                print(f"\n✍️  Post {i+1}/{min(len(topics), self.config['site']['posts_per_run'])}: {topic.get('title','')[:80]}...")
                post = self.generate_post(topic, cat)
                if post:
                    self.save_post(post)
                    all_posts.append(post)
                time.sleep(1)
        if all_posts:
            print(f"\n🏗️  Building site with {len(all_posts)} posts...")
            path = self.build_site(all_posts)
            print(f"✅ Site built: {path}")
        print(f"\n✅ Done! {len(all_posts)} posts generated.")
        return all_posts


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Income Automation - Content Engine")
    parser.add_argument("--topic", type=str, help="Specific topic")
    parser.add_argument("--category", type=str, default=None)
    parser.add_argument("--auto", action="store_true", help="Full auto pipeline")
    args = parser.parse_args()
    engine = ContentEngine()
    if args.auto:
        engine.run_auto(category=args.category)
    elif args.topic:
        topic = {"title": args.topic, "keyword": args.topic, "intent": "commercial", "competition": "medium", "monetization_score": 8}
        post = engine.generate_post(topic, args.category or "ai-tools")
        if post:
            engine.save_post(post)
            engine.build_site([post])
    else:
        engine.run_auto(category="ai-writing-tools")

if __name__ == "__main__":
    main()
