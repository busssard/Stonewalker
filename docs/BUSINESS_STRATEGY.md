# StoneWalker Business Strategy & Product Roadmap

> From hobby project to self-sustaining open-source business.
> Last updated: February 2026

---

## Table of Contents

1. [The Opportunity](#the-opportunity)
2. [Shop Product Ideas](#shop-product-ideas)
3. [Growth Strategy](#growth-strategy)
4. [Monetization Philosophy](#monetization-philosophy)
5. [Self-Sufficiency Financials](#self-sufficiency-financials)
6. [This Week Actions](#this-week-actions)
7. [90-Day Roadmap](#90-day-roadmap)

---

## The Opportunity

### The Market Is Real and Proven

**Geocaching** proves the model works at scale:
- 3.4 million active geocaches hidden worldwide
- 3+ million active players globally
- Geocaching HQ (Seattle, ~124 employees) sustains itself through Premium subscriptions at $39.99/year ($6.99/month)
- Started with 144 t-shirt sales, grew into a sustainable business

**Painted stone communities** are massive and underserved:
- The Kindness Rocks Project (founded 2015) operates in 90+ countries with certified facilitators
- Single city Facebook groups reach 6,800+ members (e.g., Hide Tucson Rocks), with 100-200 new members joining weekly
- Rock Painting 101, I Love Painted Rocks, and dozens of YouTube/TikTok channels serve millions of crafters
- Pinterest has 340+ curated boards for "kindness rocks" ideas

**The gap**: Nobody has combined stone painting with digital tracking. Geocaching has the tech but no art. Kindness Rocks has the art but no tech. StoneWalker sits in the exact intersection -- collaborative art meets treasure hunting meets world map tracking.

### Competitive Landscape

| Feature | Geocaching | Kindness Rocks | StoneWalker |
|---------|-----------|----------------|-------------|
| Digital tracking | Yes (GPS) | No | Yes (QR + map) |
| Creative expression | No (containers) | Yes (painted stones) | Yes (painted stones) |
| World map | Yes | No | Yes |
| QR codes | No | No | Yes |
| Open source | No | N/A | Yes |
| Free tier | Limited | N/A | Generous |
| Community events | Mega-events | Rock drops | Stone drops |
| Revenue model | Subscription | Donations | Products + Premium |

---

## Shop Product Ideas

### Tier 1: Digital Products (Immediate, Zero Inventory)

These can be added to the Django shop RIGHT NOW using the existing `shop_config.json` + Stripe infrastructure.

#### QR Code Packs

| Product | Price | Pack Size | Per-Unit | Margin |
|---------|-------|-----------|----------|--------|
| Free Single QR | Free | 1 | Free | Loss leader |
| Starter 3-Pack | $4.99 | 3 | $1.66 | ~95% (digital) |
| Explorer 10-Pack | $9.99 | 10 | $1.00 | ~95% |
| Classroom 30-Pack | $19.99 | 30 | $0.67 | ~95% |
| Event 100-Pack | $49.99 | 100 | $0.50 | ~95% |

Why this works: The current shop has `free_single` (1 QR, free) and `paid_10pack` (10 QR, $9.99). Adding 3-pack and 30-pack fills the natural gaps. Digital products have near-100% margin after Stripe's 2.9% + $0.30 fee.

#### Premium Subscriptions (StoneWalker Pro)

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | 1 free QR, basic stone page, map view |
| **Explorer** | $2.99/mo or $24.99/yr | Unlimited stones, journey analytics, stone stats dashboard, priority in "Featured Stones" |
| **Creator** | $5.99/mo or $49.99/yr | Everything in Explorer + custom stone page themes, photo galleries per stone, journey photobook PDF export, early access features |
| **Educator** | $9.99/mo or $79.99/yr | Everything in Creator + bulk QR management dashboard, student accounts (no email needed), classroom activity tracking, lesson plan templates |

Benchmark: Geocaching charges $39.99/year for Premium. StoneWalker's Explorer at $24.99/year is positioned below Geocaching but with a creative angle they don't have.

#### Digital Downloads

| Product | Price | Description |
|---------|-------|-------------|
| Journey Photobook PDF | $4.99 | Auto-generated PDF showing a stone's complete journey with photos, maps, and finder messages |
| Stone Certificate | $1.99 | Printable "birth certificate" for a stone showing creator, creation date, journey stats |
| Analytics Dashboard (yearly) | Included in Pro | Heat maps, distance traveled, countries visited, scan frequency |

### Tier 2: Physical Products (1-3 Months, Requires Fulfillment)

These require manufacturing partnerships but carry strong margins in the craft/hobby sector (40-60% gross margin is standard for art supplies).

#### StoneWalker Starter Kit

**Contents**: 5 river stones (pre-washed, flat), 6 acrylic paint pots, 2 fine-tip brushes, 1 can of clear sealant spray, 5 printed QR code stickers (weatherproof vinyl), instruction card with tips

**Pricing**:
- COGS estimate: $8-12 (stones $1, paint set $3, brushes $1, sealant sample $2, QR stickers $0.50, packaging $1-3)
- Retail price: $24.99
- Margin: ~55-65%

**Sourcing**: River stones from landscape supply (bulk: $0.10-0.20/stone), acrylic paint kits from craft wholesale (kits of 6 for $2-3 at volume), weatherproof vinyl QR stickers printed in-house or via StickerMule/StickerGiant ($0.10-0.20 each at 1000+).

#### Premium Metal QR Plaques

**The flagship premium product.** A laser-engraved stainless steel or anodized aluminum tag (2"x1") with the stone's QR code, designed to be epoxied to a stone. Survives years outdoors.

**Pricing**:
- Manufacturing: $3-8/unit at volume (stainless steel tags on Alibaba: MOQ 500 units, ~$2-4/unit; domestic via PlaqueMaker.com: ~$8-15/unit for small runs)
- Retail price: $14.99 (single) or $99.99 (10-pack at $10/unit)
- Margin: 50-75% depending on sourcing

**Why it sells**: "Your stone art deserves to last forever." A painted stone with a paper QR code lasts months. A stone with a steel plaque lasts decades. This is the premium upsell for serious stone artists.

#### Weatherproof QR Sticker Packs

Vinyl, UV-resistant, waterproof QR code stickers. Pre-printed with unique URLs.

**Pricing**:
- COGS: $0.08-0.15/sticker at volume (custom vinyl stickers, UV-laminated)
- Pack of 10: $5.99 (margin: ~85%)
- Pack of 50: $19.99 (margin: ~90%)

#### Branded Merchandise

| Product | COGS | Retail | Margin |
|---------|------|--------|--------|
| StoneWalker T-shirt (print-on-demand) | $8-12 | $24.99 | ~55% |
| Canvas Tote Bag | $4-6 | $14.99 | ~65% |
| Sticker Pack (logo + designs) | $1-2 | $5.99 | ~70% |
| Enamel Pin (stone + QR design) | $1.50-3 | $9.99 | ~70% |

Fulfillment: Start with print-on-demand (Printful, Gooten) to avoid inventory risk. Zero upfront cost, ~45% margin. Move to bulk ordering when a design proves popular.

### Tier 3: Experiences & Group Products (3-6 Months)

#### School & Scout Packs

**"StoneWalker Classroom Adventure"** -- everything a teacher needs for a class of 30 students:
- 30 QR code stickers (weatherproof)
- Educator account with student dashboard
- Lesson plan PDF (art + geography + STEM)
- Classroom poster with "How It Works" steps
- Price: $49.99 (one-time) or included in Educator subscription

This sells because: Teachers already do rock painting as an activity. StoneWalker adds the STEM angle (geography, data tracking, map reading) that justifies the activity to administration.

#### Birthday Party Kit

- 10 smooth stones, 10 paint pots, 10 QR stickers, party invitation templates, "Best Stone" voting cards
- Price: $34.99
- Market: Parents searching "rock painting birthday party" (real search trend)

#### Corporate Team Building

- Custom-branded stones and QR codes
- Company leaderboard (which team's stones travel farthest?)
- Event facilitation guide
- Price: $199-499 depending on group size
- Market: Corporate wellness and team-building budgets ($300+ billion global market)

#### Stone Drop Events

Community events where people hide stones in a park/city and others find them. StoneWalker provides:
- Event landing page
- Bulk QR codes
- Real-time leaderboard
- Social sharing integration
- Price: Free for community organizers (drives growth), sponsored tier for businesses

---

## Growth Strategy

### Phase 1: Content & Community (Months 1-3)

#### YouTube / TikTok: The Stone Painting Angle

**The play**: Stone painting time-lapse videos are already viral content. Adding the "hide and track" element is the hook that makes StoneWalker content uniquely shareable.

**Content formula**:
1. Time-lapse painting a beautiful stone (satisfying, ASMR-like)
2. Attach QR code and hide it somewhere interesting
3. Wait for notifications that someone found it
4. Show the finder's reaction and the stone's map journey

**Target creators** (real channels/communities):
- Rock Painting 101 (rockpainting101.com) -- the largest stone painting tutorial site
- I Love Painted Rocks (ilovepaintedrocks.com) -- major blog with YouTube presence
- TikTok #paintedrocks and #rockpainting channels (millions of views)
- Life of Colour (lifeofcolourproducts.com) -- art supply brand that already makes rock painting content

**Creator partnership model**: Send free Starter Kits + premium metal plaques to 20-50 art/craft creators. No payment needed at first -- the product IS the content. Offer affiliate links (20% commission on shop sales from their referral link).

**Own content**: Start a StoneWalker YouTube/TikTok with:
- "Stone of the Week" -- most traveled stone
- "Painting Tutorial + Hide" series
- "Stone Journey" compilations showing stones traveling across countries

#### SEO & Content Marketing

**Target keywords** (real search volume):
- "rock painting ideas" (90K+ monthly searches)
- "kindness rocks" (40K+)
- "painted rocks" (33K+)
- "stone painting for beginners" (8K+)
- "hide painted rocks" (5K+)
- "rock painting supplies" (12K+)

**Content to create**:
- Blog at stonewalker.org/blog with painting tutorials, stone tracking stories, community spotlights
- SEO-optimized landing pages: "What is StoneWalker?", "How to Paint Rocks for Beginners", "The Best Sealant for Outdoor Painted Rocks"
- Each piece of content naturally leads to "Get your free QR code and start tracking"

#### Reddit & Community

- /r/PaintedRocks (small but growing)
- /r/geocaching (large, receptive to new outdoor games)
- /r/crafts, /r/DIY, /r/ArtTherapy
- Post genuine content (stone journeys, community stories), never spam

### Phase 2: Partnerships (Months 3-6)

#### Geocaching Community Crossover

Geocachers already love the "hide and find" mechanic. StoneWalker adds creative expression.

**Approach**: Post in geocaching forums and subreddits. Frame it as "geocaching for artists" or "geocaching meets rock painting."

**Partnership with Geocaching HQ**: Long shot, but a "StoneWalker x Geocaching" collaboration where geocachers can find specially marked stones would expose StoneWalker to millions of users.

#### Scout Groups & Youth Organizations

- Scouts BSA, Girl Scouts, Guides worldwide
- StoneWalker as a "Digital Citizenship" or "Art + Technology" badge activity
- Approach regional councils with free Educator accounts and lesson plans
- Each scout troop = 10-30 potential users who tell their families

#### Schools & STEM Programs

- Rock painting + QR tracking = Art + STEM in one activity
- Approach through teacher marketplaces: Teachers Pay Teachers, education conferences
- Free Educator tier for the first 100 schools (seeds the network)

#### Art Supply Stores

- Approach Michaels, Hobby Lobby, Blick Art Materials for cross-promotion
- "Buy rock painting supplies, get a free StoneWalker QR code" insert in purchases
- Affiliate partnerships: StoneWalker recommends supplies, earns commission (8-12% typical for Amazon Associates, higher for direct partnerships)

### Phase 3: Viral Mechanics & Retention (Months 6-12)

#### Built-In Virality

Every stone IS marketing. When someone finds a stone and scans the QR code:
1. They see the stone's page with journey history
2. They're prompted to "Join StoneWalker to log your find"
3. They're prompted to "Get your own free QR code"
4. They share their find on social media

**The viral coefficient**: If each stone is found by 3 people, and 30% sign up, and 30% of those create their own stone... 100 initial stones create ~100 x 3 x 0.3 x 0.3 = 27 new stone creators. Each of those creates stones found by others. This is a genuine viral loop.

#### Gamification

- **Leaderboards**: Most stones hidden, most stones found, longest journey, most countries
- **Achievements**: "Globetrotter" (stone found on 3 continents), "Artist" (10 stones created), "Explorer" (found 50 stones)
- **Seasonal Events**: "Summer Stone Drop 2026" -- hide stones during July, top participants win prizes
- **Streak Rewards**: Find or hide a stone every week for a month, earn bonus QR codes

#### Email & Notification Loops

- "Your stone was found!" push notification and email (the most exciting moment)
- "Your stone has traveled 500 km!" milestone notifications
- "New stone hidden near you!" geo-based alerts
- Weekly digest: "This week in StoneWalker" with community highlights

---

## Monetization Philosophy

### Core Principles

1. **The free tier must be genuinely great.** One free QR code, full map access, full stone tracking, full community participation. Never cripple the core experience.

2. **No ads on stone pages or the map. Ever.** These are the emotional core of the product. Ads there would destroy the magic.

3. **Open source stays open source.** The Django codebase remains MIT licensed. Premium features are server-side (analytics, PDF generation, bulk management) -- they don't restrict the core.

4. **Revenue from value, not extraction.** Physical products people actually want. Premium features that save time. Never dark patterns, never engagement manipulation.

### Revenue Mix Target (Month 12)

| Revenue Stream | % of Total | Monthly Target |
|----------------|-----------|----------------|
| QR Code Packs (digital) | 35% | $525 |
| Premium Subscriptions | 25% | $375 |
| Physical Products (kits, plaques) | 25% | $375 |
| Group/Education Packs | 15% | $225 |
| **Total** | **100%** | **$1,500** |

### Open Source + Premium Model

Following the proven model of companies like GitLab, Sentry, and Discourse:

**Open Core**: The Django application, models, views, QR generation, map, authentication -- all open source. Anyone can self-host.

**Premium Layer (Server-Side)**:
- Advanced analytics engine
- PDF generation (photobooks, certificates)
- Bulk QR management API
- White-label options for organizations
- Priority email support

**Why this works**: Self-hosters contribute code, file bugs, and spread the word. They rarely overlap with paying customers (who want convenience, not to run a server). Discourse has proven this model works -- their open-source forum is deployed by thousands, and their hosted service generates $50M+ ARR.

---

## Self-Sufficiency Financials

### Monthly Operating Costs

| Expense | Cost | Notes |
|---------|------|-------|
| Render.com Web Service | $7/mo | Starter plan, 512MB RAM |
| Render.com PostgreSQL | $7/mo | Starter plan, 1GB storage |
| Domain (stonewalker.org) | $1/mo | ~$12/year |
| Mailjet Email Service | $0/mo | Free tier (200 emails/day, 6000/month) |
| Stripe Fees | Variable | 2.9% + $0.30 per transaction |
| CDN (Cloudflare) | $0/mo | Free tier sufficient |
| GitHub | $0/mo | Free for open source |
| **Total Fixed** | **~$15/mo** | **Without physical product costs** |

### Break-Even Analysis

With $15/month in fixed costs, break-even is nearly immediate once any revenue comes in. The real target is **self-sustaining growth** -- enough revenue to fund marketing, product development, and eventually part-time help.

**Milestone 1: Ramen Profitable** -- $200/month
- Covers hosting 10x over + domain + email upgrade
- Requires: ~20 paid 10-packs/month or ~7 Explorer subscribers

**Milestone 2: Sustainable** -- $500/month
- Covers hosting + paid email tier + small marketing budget
- Requires: ~50 mixed sales/month or 20 subscribers + product sales

**Milestone 3: Growth Mode** -- $1,500/month
- Covers one part-time contractor + all operations + marketing
- Requires: ~150 subscribers or equivalent product sales

### Revenue Scenarios

#### Conservative (Month 12)

| Metric | Value |
|--------|-------|
| Total registered users | 2,000 |
| Monthly active users | 500 |
| Paid subscribers | 25 (1.25% conversion) |
| Monthly digital sales | 40 packs |
| Monthly physical sales | 10 kits |
| **Monthly Revenue** | **~$450** |

#### Moderate (Month 12)

| Metric | Value |
|--------|-------|
| Total registered users | 5,000 |
| Monthly active users | 1,500 |
| Paid subscribers | 75 (1.5% conversion) |
| Monthly digital sales | 100 packs |
| Monthly physical sales | 30 kits |
| **Monthly Revenue** | **~$1,500** |

#### Optimistic (Month 12)

| Metric | Value |
|--------|-------|
| Total registered users | 15,000 |
| Monthly active users | 5,000 |
| Paid subscribers | 300 (2% conversion) |
| Monthly digital sales | 300 packs |
| Monthly physical sales | 80 kits |
| **Monthly Revenue** | **~$5,000** |

### Key Metrics to Track

1. **Viral coefficient**: Stones created per finder (target: > 0.3)
2. **Free-to-paid conversion**: % of free users who buy anything (target: 2-5%)
3. **Monthly Recurring Revenue (MRR)**: Subscription + repeat purchase revenue
4. **Customer Acquisition Cost (CAC)**: Total marketing spend / new paying customers
5. **Lifetime Value (LTV)**: Average revenue per customer over their lifetime
6. **Stone activation rate**: % of QR codes that get scanned at least once (target: 60%+)
7. **Retention (D7, D30)**: % of users returning after 7 and 30 days

---

## This Week Actions

### Immediate Shop Improvements (Can Do Today)

1. **Add 3-Pack product to shop_config.json**

   The infrastructure already supports it -- just add a new entry:
   ```json
   {
     "id": "paid_3pack",
     "category": "starter",
     "name": "Starter 3-Pack",
     "description": "Three QR codes to share with friends or hide a trail of stones",
     "price_cents": 499,
     "is_free": false,
     "pack_size": 3,
     "enabled": true,
     "limit_per_user": null
   }
   ```

2. **Add 30-Pack product for educators**

   ```json
   {
     "id": "paid_30pack",
     "category": "classroom",
     "name": "Classroom 30-Pack",
     "description": "Thirty QR codes for school classes, scout troops, or community events",
     "price_cents": 1999,
     "is_free": false,
     "pack_size": 30,
     "enabled": true,
     "limit_per_user": null
   }
   ```

3. **Improve shop page copy**

   The current "How It Works" section is good but could emphasize the emotional hook: "See your stone travel the world." Add a testimonial placeholder and a "Featured Stone Journeys" section showing real stones that have traveled far.

4. **Add shop FAQ entries**

   Add questions: "Can I buy QR codes as a gift?", "Do the QR codes work outdoors?", "What if my stone gets lost?" -- these address real buyer hesitations.

### Content to Create This Week

1. **Landing page copy**: "What is StoneWalker?" -- a standalone page explaining the concept for people who arrive via search or social
2. **First blog post**: "How to Paint Your First Stone and Send It on an Adventure" -- SEO target for "rock painting for beginners"
3. **Social media accounts**: Create or activate Instagram, TikTok, YouTube channel with consistent branding
4. **README.md community section**: Add a "StoneWalker Community" section linking to social channels and the forum (when ready)

### External Outreach This Week

1. **Email 5 rock painting bloggers/YouTubers** offering free Starter Kit (once physical product exists) or free 10-pack QR codes to try
2. **Post in 3 Facebook rock painting groups** with a genuine "I built this app" story (not spammy marketing)
3. **Submit to Product Hunt** (queue it for a good launch day, typically Tuesday-Thursday)
4. **Create a "Show HN" post** on Hacker News -- open-source angle resonates there

---

## 90-Day Roadmap

### Month 1: Foundation

**Product**:
- [x] Shop with free single QR and 10-pack (already built)
- [ ] Add 3-pack and 30-pack to shop
- [ ] Implement subscription billing (Stripe recurring)
- [ ] Build analytics dashboard for Pro users (stones traveled, distances, scan counts)
- [ ] Launch Discourse forum for community

**Growth**:
- [ ] Create Instagram, TikTok, YouTube accounts
- [ ] Post first 5 pieces of content (painting tutorials + stone hiding)
- [ ] Submit to Product Hunt
- [ ] Contact 10 rock painting influencers

**Target**: 200 registered users, 10 paid transactions

### Month 2: Product-Market Fit

**Product**:
- [ ] Premium subscription tiers live
- [ ] Journey Photobook PDF generation (Creator tier feature)
- [ ] Stone achievement/badge system
- [ ] Notification system (stone found, milestones)
- [ ] Source and test weatherproof QR stickers (first physical product)

**Growth**:
- [ ] First influencer partnership live (content published)
- [ ] 3 blog posts published (SEO play)
- [ ] First stone drop community event
- [ ] Reddit presence in 3-5 subreddits

**Target**: 800 registered users, 30 paid transactions, 5 subscribers

### Month 3: Scale

**Product**:
- [ ] Starter Kit designed and sourced (ready to ship)
- [ ] Metal QR plaque samples from 2-3 manufacturers
- [ ] Educator dashboard for classroom management
- [ ] Mobile notifications (PWA or push)
- [ ] Event/stone drop organizer tools

**Growth**:
- [ ] 2-3 active influencer partnerships
- [ ] First school pilot (1-3 classrooms)
- [ ] First corporate team-building inquiry
- [ ] Community of 20+ active stone creators

**Target**: 2,000 registered users, $500/month revenue, 25 subscribers

---

## Closing Thoughts

StoneWalker doesn't need to compete with Geocaching head-on. It occupies a unique space: **creative expression meets outdoor adventure meets global tracking**. The painted stone community is millions strong but has zero digital infrastructure. StoneWalker provides that infrastructure.

The path to sustainability is straightforward:
1. Generous free tier drives adoption
2. Content marketing drives discovery
3. Built-in virality (every stone IS marketing) drives growth
4. Physical products and subscriptions drive revenue
5. Open source community drives trust and contribution

The hardest part is already done -- the product exists, works, and has real features. Now it's about getting it in front of the right people.

Let's go drop some stones.

---

*This document is a living strategy. Update it as market conditions, user feedback, and growth data come in.*
