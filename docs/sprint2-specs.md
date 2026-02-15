# StoneWalker Sprint 2 — Product Specifications

> Comprehensive specs for Terms of Use, Email Notifications, Social Sharing, Social Profiles, Premium Tier, Physical Products, Analytics Dashboard, Content Marketing Blog, Community Events, and Dark Mode.
>
> Author: CreativeMind Agent | Date: February 2026

---

## Table of Contents

1. [Terms of Use](#1-terms-of-use)
2. [Email Notification System](#2-email-notification-system)
3. [Social Sharing Pages](#3-social-sharing-pages)
4. [Social Media Profile Connections](#4-social-media-profile-connections)
5. [Premium Supporter Tier](#5-premium-supporter-tier)
6. [Physical Product Fulfillment](#6-physical-product-fulfillment)
7. [Stone Journey Analytics Dashboard](#7-stone-journey-analytics-dashboard)
8. [Content Marketing Blog](#8-content-marketing-blog)
9. [Community Events System](#9-community-events-system)
10. [Dark Mode UX](#10-dark-mode-ux)
11. [Summary](#summary)

---

## 1. Terms of Use

### 1.1 UX Flow

**On Signup:**
- Add a required checkbox to the registration form (`/accounts/sign-up/`):
  - Label text: `I have read and agree to the <a href="/terms/">Terms of Use</a> and <a href="/privacy/">Privacy Policy</a>.`
  - The checkbox MUST be checked before the form can be submitted. If unchecked, show validation error: "You must accept the Terms of Use to create an account."
  - Store `terms_accepted_at` (DateTimeField) and `terms_version` (CharField) on the user Profile model when signup completes.

**On First Stone Creation (belt-and-suspenders):**
- Before the stone creation modal opens, check `profile.terms_accepted_at`. If null (legacy users who signed up before Terms existed), show an interstitial modal:
  - Title: "One quick thing before you create a stone"
  - Body: Brief summary of the three key commitments (see section 1.2 below) with a checkbox and links to full terms.
  - User must accept before proceeding. This records `terms_accepted_at` and `terms_version` on their profile.
- Users who already accepted skip this step entirely.

**Terms Page:**
- URL: `/terms/`
- Accessible to everyone (no login required).
- Plain HTML page using the standard `layouts/default/page.html` base template.
- Must be translatable (wrap all text in `{% trans %}` tags).

**Privacy Policy Page:**
- URL: `/privacy/`
- Same format and accessibility as Terms page.

### 1.2 Terms of Use — Full Text

Below is the actual terms content to implement on the `/terms/` page. Write it as a Django template with `{% trans %}` wrapping each paragraph for translation.

---

**StoneWalker Terms of Use**

*Last updated: [auto-generated date]*

*Version: 1.0*

Welcome to StoneWalker. By creating an account or using our services, you agree to the following terms. Please read them carefully.

**1. What StoneWalker Is**

StoneWalker is a community platform for tracking the journeys of painted stones around the world using QR codes. Users paint stones, attach QR codes, hide them in public places, and track their journeys as others find and move them.

**2. Your Stones, Your Responsibility**

By creating a stone on StoneWalker, you confirm that:

- **You are the creator of this stone.** You painted or decorated this stone yourself (or supervised its creation in the case of children or group activities).
- **You are not attaching QR codes to stones you did not create.** Attaching StoneWalker QR codes to natural rocks, public art, property markers, memorial stones, or any stone you did not personally create is prohibited and may result in account suspension.
- **You will hide stones in safe, publicly accessible locations.** Do not place stones on private property without permission, in locations that could cause injury, near roads or traffic, in bodies of water, or in environmentally sensitive areas.
- **Your stone is a gift to the community.** Once you hide a stone, you release it into the world. You understand that stones may be kept, lost, damaged, or destroyed, and StoneWalker bears no responsibility for what happens to physical stones after they are hidden.

**3. Content You Upload**

When you upload photos, comments, or descriptions to StoneWalker, you retain ownership of your content. However, you grant StoneWalker a worldwide, non-exclusive, royalty-free license to:

- Display your content on the StoneWalker platform (website, apps, emails).
- Share your content in StoneWalker marketing materials, social media, and promotional content (with attribution to your username when reasonably possible).
- Use anonymized stone photos and journey data to train machine learning models. This may include models for stone recognition (identifying stones without QR codes), image classification, and geographic pattern analysis. **You can opt out of AI training at any time in your profile settings** without affecting your ability to use StoneWalker.

You agree not to upload content that is:
- Obscene, hateful, threatening, or harassing.
- Copyrighted material you do not own or have permission to use.
- Personal information about others (phone numbers, addresses, email addresses).
- Advertising, spam, or commercial solicitation.

StoneWalker reserves the right to remove any content that violates these guidelines without notice.

**4. Age Requirements**

- You must be at least 13 years old to create a StoneWalker account.
- Users between 13 and 16 years old must have a parent or guardian who agrees to these terms on their behalf.
- Users under 13 may participate in StoneWalker through a parent's or guardian's account or through an Educator account (classroom use), but may not create their own accounts.

**5. Account Conduct**

You agree to:
- Provide accurate information during registration.
- Keep your login credentials secure and not share your account.
- Not create multiple accounts to circumvent limits or bans.
- Not use automated tools, bots, or scrapers to access StoneWalker.
- Not attempt to reverse-engineer, decompile, or exploit the platform's code for malicious purposes.

StoneWalker may suspend or terminate accounts that violate these terms, with or without prior notice depending on severity.

**6. QR Codes and Digital Products**

- QR codes purchased or obtained through StoneWalker are for personal, non-commercial use unless you hold an Educator or Business subscription.
- QR code links are permanent. StoneWalker will make commercially reasonable efforts to keep QR code URLs active indefinitely.
- Refunds for digital QR code purchases are available within 14 days of purchase, provided the QR codes have not been printed or claimed.

**7. Premium Subscriptions**

- Premium subscriptions are billed monthly or annually through Stripe.
- You may cancel at any time. Cancellation takes effect at the end of the current billing period.
- No partial refunds for unused subscription time, except where required by law.
- StoneWalker reserves the right to change subscription pricing with 30 days notice to existing subscribers.

**8. Limitation of Liability**

StoneWalker is provided "as is" without warranties of any kind.

- StoneWalker is not responsible for physical injuries, property damage, or any other harm related to hiding, finding, or moving painted stones.
- StoneWalker is not responsible for lost, stolen, or damaged stones.
- StoneWalker is not responsible for interactions between users that occur outside the platform.
- In no event shall StoneWalker's total liability exceed the amount you paid to StoneWalker in the 12 months preceding the claim, or $50 USD, whichever is greater.

**9. Privacy**

Your privacy matters to us. See our [Privacy Policy](/privacy/) for details on how we collect, use, and protect your data. Key points:

- We collect only what we need: account info, stone locations, uploaded photos, and basic usage data.
- We do not sell your personal data to third parties.
- Stone locations are public by design — that is the core of how StoneWalker works.
- You can delete your account and associated data at any time.

**10. Changes to These Terms**

We may update these terms from time to time. When we make significant changes:
- We will update the "Last updated" date at the top.
- We will notify registered users by email.
- Continued use of StoneWalker after changes constitutes acceptance.

**11. Governing Law**

These terms are governed by the laws of the jurisdiction in which StoneWalker operates. Disputes will be resolved through good-faith negotiation before any legal proceedings.

**12. Contact**

Questions about these terms? Email us at terms@stonewalker.org.

---

### 1.3 Privacy Policy Summary (for `/privacy/` page)

Create a companion Privacy Policy page. Key sections to include:

| Section | Content Summary |
|---------|----------------|
| What we collect | Email, username, password hash, profile picture, stone data (names, photos, locations, descriptions), IP address, browser info |
| Why we collect it | Account management, stone tracking, QR code generation, analytics, abuse prevention |
| What we share | Nothing sold. Anonymized aggregate data may be shared. Stone locations and photos are public. |
| Cookies | Session cookie (required), language preference cookie, optional analytics |
| Data retention | Active accounts: indefinitely. Deleted accounts: purged within 30 days. Anonymized analytics: retained. |
| Your rights | Access, correction, deletion, data export (GDPR-style rights for all users) |
| AI training opt-out | Profile setting to exclude your photos from ML training datasets |
| Children | No accounts under 13. Educator accounts handle classroom use. |
| Contact | privacy@stonewalker.org |

### 1.4 Implementation Notes for Developers

**Model changes:**
- Add to Profile model: `terms_accepted_at = DateTimeField(null=True, blank=True)` and `terms_version = CharField(max_length=10, null=True, blank=True)`.
- Add to Profile model: `ai_training_opt_out = BooleanField(default=False)`.

**Template changes:**
- `accounts/templates/accounts/sign_up.html`: Add checkbox field before submit button.
- Create `main/templates/main/terms.html` and `main/templates/main/privacy.html`.
- `main/new_add_stone_modal.html`: Add terms check before modal opens (JS-level check against a data attribute on the page, backed by the view passing `terms_accepted` in context).

**URL additions:**
- `/terms/` -> `TermsView` (TemplateView)
- `/privacy/` -> `PrivacyView` (TemplateView)

**Migration:**
- One migration to add the three new Profile fields.

---

## 2. Email Notification System

### 2.1 Event Triggers

| Event | Email Name | Trigger | Timing |
|-------|-----------|---------|--------|
| Stone scanned | "Your stone was found!" | A user scans a QR code for a stone you own | Immediate (within 5 minutes) |
| Stone moved | "Your stone is on the move!" | A user logs a new location for your stone via the scan form | Immediate (within 5 minutes) |
| Milestone reached | "Your stone hit a milestone!" | Stone crosses distance thresholds (100km, 500km, 1000km, 5000km) or country count (2, 5, 10) | Immediate |
| Weekly digest | "Your Week in StoneWalker" | Cron job every Sunday at 10:00 AM UTC | Weekly |
| Welcome email 1 | "Welcome to StoneWalker!" | User completes email activation | Immediate |
| Welcome email 2 | "Ready to paint?" | 3 days after signup, user has not created a stone | Scheduled (3 days) |
| Welcome email 3 | "Your first stone is waiting" | 7 days after signup, user has not created a stone | Scheduled (7 days) |
| Inactivity nudge | "We miss your stones!" | User has not logged in for 30 days | Scheduled (30 days) |

### 2.2 Email Content Specifications

All emails use the existing branded template system (green header `#4CAF50`, 600px max-width, white content, branded footer). Each email below defines subject line, preview text, and body content.

#### "Your stone was found!"

```
Subject: Someone found [Stone Name]!
Preview: Your stone has been discovered in [City/Country].

Body:
Great news, [Username]!

[Finder Username] just scanned your stone "[Stone Name]" in [City, Country].

[If finder left a comment:]
They said: "[Comment text, truncated to 200 chars]"

[If finder uploaded a photo:]
[Thumbnail image of the finder's photo, 300px wide]

[Stone Name] has now traveled [X] km across [N] locations.

[Button: "View Stone Journey" -> /stone/<pk>/edit/]

Keep painting. Keep hiding. The world is finding your art.
```

#### "Your stone is on the move!"

```
Subject: [Stone Name] just moved to [City/Country]!
Preview: Your stone has traveled [X] km total.

Body:
Hey [Username],

Your stone "[Stone Name]" is on the move again!

New location: [City, Country]
Total distance: [X] km
Total moves: [N]

[Mini map image showing latest two points with a line between them —
 or fallback to text coordinates if map generation is not feasible in v1]

[Button: "See the Full Journey" -> /stone/<pk>/edit/]
```

#### "Your stone hit a milestone!"

```
Subject: [Stone Name] just crossed [milestone]!
Preview: What a journey — [Stone Name] has [milestone description].

Body:
Congratulations, [Username]!

Your stone "[Stone Name]" just reached an incredible milestone:

[Milestone badge/icon — use emoji as placeholder]
[Milestone text, e.g., "Traveled over 1,000 km!" or "Visited 5 different countries!"]

Journey so far:
- Distance: [X] km
- Locations: [N]
- Countries: [list]
- Time traveling: [duration]

[Button: "View Journey" -> /stone/<pk>/edit/]
[Button: "Share This Achievement" -> /stone/<pk>/share/]
```

#### "Your Week in StoneWalker" (Weekly Digest)

```
Subject: Your StoneWalker Week — [date range]
Preview: [N] scans, [X] km traveled this week.

Body:
Hi [Username],

Here's what happened with your stones this week:

THIS WEEK'S ACTIVITY
- Stones scanned: [N] times
- New distance: [X] km
- New locations: [N]

[For each stone that had activity, max 5:]
[Stone Name]: [brief summary — "Found in Berlin, Germany (+230 km)"]

[If no activity:]
Your stones are resting this week. Maybe it's time to hide a new one?

COMMUNITY HIGHLIGHTS
- [N] new users joined StoneWalker
- [N] stones were hidden this week
- Longest journey this week: [Stone Name] traveled [X] km

[Button: "View My Stones" -> /my-stones/]
[Button: "Hide a New Stone" -> /create-stone/]

See you next week!
```

#### Welcome Series

**Email 1: "Welcome to StoneWalker!" (Immediate after activation)**

```
Subject: Welcome to StoneWalker, [Username]!
Preview: You're now part of a global community of stone artists.

Body:
Welcome, [Username]!

You've just joined a community of people who believe a painted stone
can travel the world.

HERE'S HOW IT WORKS:
1. Paint a stone — any stone, any design, any size.
2. Get a QR code — print it and attach it to your stone.
3. Hide your stone — in a park, on a trail, in a city.
4. Watch it travel — when someone finds and scans your stone,
   you'll see its journey on the world map.

[Button: "Get Your Free QR Code" -> /create-stone/]

One stone. One QR code. A journey around the world.
```

**Email 2: "Ready to paint?" (Day 3, only if no stone created)**

```
Subject: Your first QR code is free and waiting
Preview: All you need is a stone and some paint.

Body:
Hi [Username],

Did you know every StoneWalker journey starts with a single stone?

We saved a free QR code for you. Here's what to do:

1. Find a smooth stone (river rocks work great)
2. Paint it however you like — bold colors show up best
3. Seal it with clear spray varnish (so your art survives the elements)
4. Come back here and grab your free QR code
5. Print it, tape or glue it to the back, and hide your stone somewhere fun

[Button: "Claim Your Free QR Code" -> /create-stone/]

TIP: The best hiding spots are public, safe, and a little surprising.
Think park benches, trail markers, cafe window sills, and library steps.
```

**Email 3: "Your first stone is waiting" (Day 7, only if no stone created)**

```
Subject: 7 days in and the world is waiting for your stone
Preview: Here's some inspiration from the community.

Body:
Hey [Username],

It's been a week since you joined StoneWalker. Here's what the
community has been up to:

[If community data available:]
- [N] stones were hidden this week
- Stones traveled a combined [X] km
- Newest member to hide a stone: [recent username] from [country]

[If no community data yet, use generic:]
StoneWalker stones have been found on every continent except Antarctica.
(We're working on that one.)

STILL NOT SURE WHAT TO PAINT?
- A simple heart or smiley face works great
- Use acrylic paint — it's waterproof and bright
- Seal with 2-3 coats of clear spray varnish
- Write "StoneWalker" on the back so finders know what it is

[Button: "Create Your First Stone" -> /create-stone/]

Your free QR code is still waiting.
```

### 2.3 User Notification Preferences

Add a notification settings page accessible from the profile menu.

**URL:** `/accounts/notifications/`

**Settings (all default ON):**

| Setting | Description | Default |
|---------|-------------|---------|
| Stone found alerts | Get emailed when someone scans your stone | ON |
| Stone move alerts | Get emailed when your stone moves to a new location | ON |
| Milestone alerts | Get emailed when your stone hits a distance or country milestone | ON |
| Weekly digest | Receive a weekly summary of stone activity | ON |
| Welcome & tips | Receive onboarding tips after signing up | ON |
| Community news | Occasional updates about StoneWalker features and events | ON |

**Model changes:**
- Create `NotificationPreference` model with a OneToOne to User.
- Fields: `stone_found` (bool), `stone_move` (bool), `milestones` (bool), `weekly_digest` (bool), `welcome_tips` (bool), `community_news` (bool). All default True.

**Unsubscribe mechanism:**
- Every email includes a footer link: "Manage notification preferences" -> `/accounts/notifications/`
- Every email includes a one-click unsubscribe link: `/accounts/unsubscribe/<token>/<category>/` that disables that specific notification type without requiring login.
- The token is an HMAC of user_id + category, so it cannot be forged.

### 2.4 Implementation Architecture

**Sending method:** Use Django's existing email infrastructure (Maileroo in production, console in development).

**Immediate emails:** Trigger from the view that processes the scan/move. Call a `send_notification_email(user, event_type, context)` function that checks preferences before sending.

**Scheduled emails (welcome series, digest, inactivity):**
- Use Django management commands: `send_weekly_digest`, `send_welcome_series`, `send_inactivity_nudge`.
- Run via cron on the VPS (or Render cron jobs):
  - `send_weekly_digest`: Sundays at 10:00 UTC
  - `send_welcome_series`: Daily at 09:00 UTC (checks for users at day 3 and day 7)
  - `send_inactivity_nudge`: Weekly on Mondays at 09:00 UTC

**Template structure:** All notification emails extend a base `emails/notification_base.html` template that includes the green header, footer, and unsubscribe link.

---

## 3. Social Sharing Pages

### 3.1 URL Structure

```
/stone/<pk>/share/
```

This is a public page (no login required). It is the canonical URL for sharing a stone's journey on social media.

### 3.2 Page Layout

```
+--------------------------------------------------+
|  [StoneWalker logo]              [Get Your Own!]  |
+--------------------------------------------------+
|                                                    |
|  [Stone Image — hero, 600x400px max, centered]    |
|                                                    |
|  STONE NAME                                        |
|  "The Blue Wanderer"                               |
|                                                    |
|  Created by [Username] on [Date]                   |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  JOURNEY MAP                                       |
|  [Leaflet map showing all stone locations          |
|   connected by lines, 100% width, 400px height]   |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  JOURNEY STATS                                     |
|  +----------+  +----------+  +-----------+         |
|  | 2,340 km |  | 12 moves |  | 5 finders |        |
|  | traveled |  | so far   |  | & counting|        |
|  +----------+  +----------+  +-----------+         |
|                                                    |
|  +----------+  +----------+                        |
|  | 4 months |  |3 countries|                       |
|  | traveling|  | visited   |                       |
|  +----------+  +----------+                        |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  JOURNEY TIMELINE                                  |
|  [Vertical timeline of moves, most recent first]   |
|                                                    |
|  Feb 12, 2026 — Berlin, Germany                    |
|  Found by @sarah_rocks                             |
|  "Found this beauty near the Spree river!"         |
|  [Thumbnail photo]                                 |
|                                                    |
|  Jan 28, 2026 — Prague, Czech Republic             |
|  Found by @czech_stones                            |
|  [Thumbnail photo]                                 |
|                                                    |
|  Jan 15, 2026 — Vienna, Austria                    |
|  Hidden by @creator_name (origin)                  |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  SHARE THIS JOURNEY                                |
|  [Facebook] [Twitter/X] [WhatsApp] [Copy Link]    |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  WANT TO JOIN THE ADVENTURE?                       |
|  StoneWalker — Paint a stone. Give it a story.     |
|  Watch it travel the world.                        |
|                                                    |
|  [Button: "Sign Up Free" -> /accounts/sign-up/]   |
|  [Button: "Learn More" -> /about/]                 |
|                                                    |
+--------------------------------------------------+
|  Footer: StoneWalker.org | Terms | Privacy         |
+--------------------------------------------------+
```

### 3.3 Open Graph & Twitter Card Meta Tags

The share page must include these meta tags in the `<head>`:

```html
<!-- Open Graph -->
<meta property="og:type" content="article" />
<meta property="og:title" content="[Stone Name] — A StoneWalker Journey" />
<meta property="og:description" content="This stone has traveled [X] km across [N] countries. Follow its journey!" />
<meta property="og:image" content="https://stonewalker.org/stone/[pk]/og-image/" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:url" content="https://stonewalker.org/stone/[pk]/share/" />
<meta property="og:site_name" content="StoneWalker" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="[Stone Name] — A StoneWalker Journey" />
<meta name="twitter:description" content="This stone has traveled [X] km across [N] countries." />
<meta name="twitter:image" content="https://stonewalker.org/stone/[pk]/og-image/" />
```

### 3.4 OG Image Generation

**URL:** `/stone/<pk>/og-image/` (returns a 1200x630 PNG)

**Design specification:**

```
+--------------------------------------------------+
|                                                    |
|  [Background: gradient from #4CAF50 to #2E7D32]   |
|                                                    |
|  [Left 40%]              [Right 60%]               |
|  [Stone photo,           [Stone Name — large,      |
|   rounded corners,        white text, bold]        |
|   centered in left       [X km traveled — white]   |
|   section, 400x400       [N countries — white]     |
|   max, with subtle       [N finders — white]       |
|   drop shadow]           [StoneWalker logo,        |
|                           small, bottom-right]     |
|                                                    |
+--------------------------------------------------+
```

**If no stone photo exists:** Use a placeholder graphic (a painted stone illustration or the StoneWalker logo centered).

**Implementation:** Use Pillow (PIL) to generate the image server-side. Cache the generated image and invalidate when the stone gets a new move. Store in `media/og_images/stone_<pk>.png`.

**Performance:** Cache the OG image URL with a `?v=<move_count>` query parameter so social platforms re-fetch when the journey updates.

### 3.5 Share Button Copy & URLs

| Platform | Button Text | Share URL | Pre-filled Text |
|----------|------------|-----------|-----------------|
| Facebook | "Share on Facebook" | `https://www.facebook.com/sharer/sharer.php?u={share_url}` | (Facebook pulls from OG tags) |
| Twitter/X | "Share on X" | `https://twitter.com/intent/tweet?url={share_url}&text={text}` | "This painted stone has traveled {X} km across {N} countries! Follow its journey on @StoneWalker {share_url}" |
| WhatsApp | "Share on WhatsApp" | `https://wa.me/?text={text}` | "Check out this painted stone's journey! It has traveled {X} km across {N} countries. {share_url}" |
| Copy Link | "Copy Link" | (JavaScript clipboard copy) | Copies `{share_url}` to clipboard, button text changes to "Copied!" for 2 seconds |
| Email | "Share via Email" | `mailto:?subject={subject}&body={body}` | Subject: "Look at this stone's journey!" Body: "I found this on StoneWalker — a painted stone that has traveled {X} km. Check it out: {share_url}" |

### 3.6 Implementation Notes

**New URLs:**
- `/stone/<pk>/share/` -> `StoneShareView` (public TemplateView)
- `/stone/<pk>/og-image/` -> `StoneOGImageView` (public, returns PNG)

**Template:** `main/templates/main/stone_share.html`

**View logic:**
- Fetch Stone with all related moves (prefetch_related).
- Calculate stats: total distance, move count, unique finders, countries visited, time traveling.
- Pass all data to template.
- The share page works for both logged-in and anonymous users.

---

## 4. Social Media Profile Connections

### 4.1 Supported Platforms

| Platform | URL Pattern | Username Format | Icon |
|----------|-------------|-----------------|------|
| Facebook | `https://facebook.com/{username}` | @username or full URL | Facebook "f" icon |
| Instagram | `https://instagram.com/{username}` | @username (no @ stored, just handle) | Instagram camera icon |
| Twitter/X | `https://x.com/{username}` | @username | X logo |
| Mastodon | `https://{instance}/@{username}` | @user@instance.social (full handle stored) | Mastodon icon |
| TikTok | `https://tiktok.com/@{username}` | @username | TikTok icon |

### 4.2 Profile Storage

**Model changes — add to Profile model:**

```python
social_facebook = CharField(max_length=100, blank=True, default='')
social_instagram = CharField(max_length=100, blank=True, default='')
social_twitter = CharField(max_length=100, blank=True, default='')
social_mastodon = CharField(max_length=200, blank=True, default='')
social_tiktok = CharField(max_length=100, blank=True, default='')
social_links_public = BooleanField(default=True)
```

**Input validation:**
- Strip `@` prefix and URL prefixes automatically. Store only the handle/username.
- For Mastodon: store the full `user@instance.social` format.
- Validate against a reasonable character set (alphanumeric, underscores, dots, hyphens).
- Do NOT verify that accounts actually exist — just validate format.

### 4.3 Profile Edit UX

Add a "Social Media" section to the profile edit modal/page (`/accounts/change/profile/`):

```
SOCIAL MEDIA LINKS (optional)

Facebook    [__________________] (your Facebook username)
Instagram   [__________________] (your Instagram handle)
Twitter/X   [__________________] (your X handle)
Mastodon    [__________________] (your@instance.social)
TikTok      [__________________] (your TikTok handle)

[x] Show my social links on my public profile

These links appear on your stone journey pages so finders
can connect with you.
```

### 4.4 Display on Share Pages

On the stone share page (`/stone/<pk>/share/`), below the creator's username, show connected social links as small icons:

```
Created by sarah_rocks
[FB icon] [IG icon] [X icon]
```

Each icon links to the creator's social profile in a new tab (`target="_blank" rel="noopener"`).

Only show icons for platforms the user has connected. If `social_links_public` is False, show no social icons.

### 4.5 Auto-Mention on Social Sharing

When a finder shares that they found a stone, the pre-filled share text should include the stone owner's handle if available:

**Twitter/X example:**
```
I just found a painted stone by @sarah_rocks! It has traveled 2,340 km.
Follow its journey on @StoneWalker: https://stonewalker.org/stone/xyz/share/
```

**Logic:**
- If the stone owner has `social_twitter` set, include `@{handle}` in the Twitter share text.
- If the stone owner has `social_instagram` set, include `@{handle}` in the generic share text.
- For Facebook and WhatsApp: mention by name (no @handle mechanism).
- For Mastodon: include the full handle format.

### 4.6 Privacy Considerations

- Social links are opt-in (blank by default).
- `social_links_public` toggle lets users hide their social links from share pages while still having them saved for their own reference.
- Social handles are never shared via email notifications (to prevent harassment).
- Social handles are not exposed in any API endpoint — they only render in HTML on the share page.
- Changing the privacy toggle takes effect immediately (no cache delay).

---

## 5. Premium Supporter Tier

### 5.1 Tier Structure

Align with the pricing already defined in `docs/BUSINESS_STRATEGY.md`:

| Feature | Free | Explorer ($2.99/mo) | Creator ($5.99/mo) | Educator ($9.99/mo) |
|---------|------|---------------------|---------------------|---------------------|
| Create stones | 1 free QR | Unlimited | Unlimited | Unlimited |
| Track stone journeys | Yes | Yes | Yes | Yes |
| Map view | Yes | Yes | Yes | Yes |
| Journey analytics dashboard | No | Yes | Yes | Yes |
| Stone statistics (distance, countries, finders) | Basic | Full | Full | Full |
| Custom stone page themes | No | No | Yes | Yes |
| Photo gallery per stone | 1 photo | 1 photo | Unlimited | Unlimited |
| Journey photobook PDF export | No | No | Yes | Yes |
| Priority in "Featured Stones" | No | Yes | Yes | Yes |
| Early access to new features | No | Yes | Yes | Yes |
| Bulk QR management dashboard | No | No | No | Yes |
| Student accounts (no email needed) | No | No | No | Yes (up to 35) |
| Classroom activity tracking | No | No | No | Yes |
| Custom QR code styles | No | No | Logo overlay | Logo + colors |
| Support priority | Community | Standard | Priority | Priority |
| Ad-free experience | Yes (no ads) | Yes | Yes | Yes |

**Annual pricing (discount for commitment):**

| Tier | Monthly | Annual | Annual Savings |
|------|---------|--------|----------------|
| Explorer | $2.99/mo | $24.99/yr ($2.08/mo) | 30% off |
| Creator | $5.99/mo | $49.99/yr ($4.17/mo) | 30% off |
| Educator | $9.99/mo | $79.99/yr ($6.67/mo) | 33% off |

### 5.2 Stripe Recurring Billing Integration

**Stripe Products & Prices to create:**

| Product Name | Stripe Price ID Format | Amount | Interval |
|-------------|----------------------|--------|----------|
| StoneWalker Explorer (Monthly) | `price_explorer_monthly` | $2.99 | month |
| StoneWalker Explorer (Annual) | `price_explorer_annual` | $24.99 | year |
| StoneWalker Creator (Monthly) | `price_creator_monthly` | $5.99 | month |
| StoneWalker Creator (Annual) | `price_creator_annual` | $49.99 | year |
| StoneWalker Educator (Monthly) | `price_educator_monthly` | $9.99 | month |
| StoneWalker Educator (Annual) | `price_educator_annual` | $79.99 | year |

Store actual Stripe Price IDs in environment variables (not hardcoded):
```
STRIPE_PRICE_EXPLORER_MONTHLY=price_xxx
STRIPE_PRICE_EXPLORER_ANNUAL=price_xxx
...
```

**Model changes:**

Add to Profile model (or create a new `Subscription` model):

```python
class Subscription(models.Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='subscription')
    tier = CharField(max_length=20, choices=[
        ('free', 'Free'),
        ('explorer', 'Explorer'),
        ('creator', 'Creator'),
        ('educator', 'Educator'),
    ], default='free')
    stripe_customer_id = CharField(max_length=255, blank=True)
    stripe_subscription_id = CharField(max_length=255, blank=True)
    billing_interval = CharField(max_length=10, choices=[
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ], blank=True)
    current_period_end = DateTimeField(null=True, blank=True)
    is_active = BooleanField(default=False)
    canceled_at = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

**Webhook events to handle:**

| Stripe Event | Action |
|-------------|--------|
| `checkout.session.completed` | Create/update Subscription, set tier and period_end |
| `invoice.paid` | Extend current_period_end, ensure is_active=True |
| `invoice.payment_failed` | Send "payment failed" email, grace period of 7 days |
| `customer.subscription.updated` | Update tier if changed, update period_end |
| `customer.subscription.deleted` | Set is_active=False, set canceled_at, revert to free tier |

**Checkout flow:**
1. User clicks "Upgrade" on pricing page (`/premium/`).
2. Backend creates Stripe Checkout Session with the selected price.
3. User completes payment on Stripe-hosted checkout.
4. Stripe sends `checkout.session.completed` webhook.
5. Backend creates Subscription record.
6. User redirected to `/premium/success/`.

**Cancellation flow:**
1. User clicks "Cancel Subscription" in account settings.
2. Backend calls `stripe.Subscription.modify(cancel_at_period_end=True)`.
3. Subscription stays active until `current_period_end`.
4. At period end, Stripe sends `customer.subscription.deleted` webhook.
5. Backend reverts user to free tier.

### 5.3 New URLs

| URL | View | Description |
|-----|------|-------------|
| `/premium/` | `PremiumView` | Pricing page with tier comparison |
| `/premium/checkout/<tier>/<interval>/` | `PremiumCheckoutView` | Creates Stripe session, redirects to Stripe |
| `/premium/success/` | `PremiumSuccessView` | Post-checkout confirmation |
| `/premium/manage/` | `PremiumManageView` | Current subscription details, cancel button |

### 5.4 Pricing Page Design

```
+--------------------------------------------------+
|                                                    |
|  STONEWALKER PREMIUM                               |
|  Support the community. Unlock powerful features.  |
|                                                    |
|  [Monthly] [Annual — Save 30%]   <- toggle switch  |
|                                                    |
|  +------------+ +------------+ +--------------+    |
|  | EXPLORER   | | CREATOR    | | EDUCATOR     |    |
|  |            | |            | |              |    |
|  | $2.99/mo   | | $5.99/mo   | | $9.99/mo     |    |
|  |            | | Most       | |              |    |
|  |            | | Popular    | |              |    |
|  |            | |            | |              |    |
|  | - Unlimited| | Everything | | Everything   |    |
|  |   stones   | |   in       | |   in         |    |
|  | - Analytics| |   Explorer | |   Creator    |    |
|  |   dashboard| | - Custom   | | - 35 student |    |
|  | - Featured | |   themes   | |   accounts   |    |
|  |   stones   | | - Photo    | | - Classroom  |    |
|  | - Early    | |   galleries| |   tracking   |    |
|  |   access   | | - Photobook| | - Bulk QR    |    |
|  |            | |   export   | |   management |    |
|  |            | | - Priority | | - Custom QR  |    |
|  |            | |   support  | |   colors     |    |
|  |            | |            | |              |    |
|  | [Upgrade]  | | [Upgrade]  | | [Upgrade]    |    |
|  +------------+ +------------+ +--------------+    |
|                                                    |
|  Already premium? [Manage Subscription]            |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  FREQUENTLY ASKED QUESTIONS                        |
|                                                    |
|  Can I cancel anytime?                             |
|  Yes. Cancel from your account settings. Your      |
|  premium features stay active until the end of     |
|  your current billing period.                      |
|                                                    |
|  What happens to my stones if I cancel?            |
|  Nothing! Your stones, journey data, and QR codes  |
|  are yours forever, regardless of subscription     |
|  status. You just lose access to premium features. |
|                                                    |
|  Is StoneWalker free without premium?              |
|  Absolutely. You get 1 free QR code, full map      |
|  access, and full stone tracking. Premium is for   |
|  power users who want more.                        |
|                                                    |
|  Do you offer refunds?                             |
|  Contact us within 14 days of purchase for a full  |
|  refund if you're not satisfied.                   |
|                                                    |
+--------------------------------------------------+
```

---

## 6. Physical Product Fulfillment

### 6.1 Starter Kit

**Product: "StoneWalker Starter Kit"**

**Contents:**
- 5 smooth river stones (pre-washed, flat, 3-4 inch diameter)
- 6 acrylic paint pots (red, blue, yellow, green, white, black — 2ml each)
- 2 fine-tip brushes (sizes 0 and 2)
- 1 mini clear spray sealant (travel size, enough for 5 stones)
- 5 weatherproof vinyl QR code stickers (pre-linked to user's account)
- 1 instruction card (painting tips + "How to hide your stone" guide)
- Branded packaging (kraft box with StoneWalker logo)

**Pricing:**
- COGS estimate: $8-12
- Retail price: $29.99
- Shipping: $5.99 flat rate (domestic), $12.99 international
- Margin: ~55-65%

**Fulfillment model (Phase 1 — low volume):**
- Manual assembly and shipping by the team (or a single hired assistant).
- Store inventory in a home/garage setting.
- Use USPS Priority Mail for domestic, USPS First Class International for international.
- Print shipping labels via Pirate Ship (cheapest USPS rates).

**Fulfillment model (Phase 2 — scale):**
- Partner with a 3PL (third-party logistics) provider: ShipBob, ShipStation, or Fulfillment by Amazon.
- Pre-assemble kits and ship to 3PL warehouse.
- 3PL handles storage, packing, and shipping.

**Shop integration:**
- Add to `shop_config.json` as a physical product category.
- Checkout captures shipping address (new AddressForm).
- Order creates a `PhysicalOrder` record with status tracking.
- Admin dashboard shows pending orders for fulfillment.

### 6.2 Metal QR Plaques

**Product: "StoneWalker Forever Plaque"**

**Specs:**
- Material: Anodized aluminum (outdoor-grade, corrosion-resistant)
- Size options:
  - Small: 1.5" x 1" (for stones 2-3 inches) — $12.99
  - Standard: 2" x 1.25" (for stones 3-5 inches) — $14.99
  - Large: 2.5" x 1.5" (for stones 5+ inches) — $17.99
- Finish: Matte black with laser-engraved QR code (white fill)
- Attachment: Pre-applied 3M VHB adhesive on the back + included 2-part marine epoxy packet
- Each plaque has a unique QR code pre-linked to the user's account

**Pricing:**

| Option | COGS | Retail | Margin |
|--------|------|--------|--------|
| Small single | $3.50 | $12.99 | 73% |
| Standard single | $4.00 | $14.99 | 73% |
| Large single | $5.00 | $17.99 | 72% |
| Standard 5-pack | $18.00 | $59.99 | 70% |
| Standard 10-pack | $32.00 | $99.99 | 68% |

**Sourcing:**
- Primary: Alibaba suppliers (MOQ 500 units, ~$2-4/unit at volume)
- Secondary: Domestic via PlaqueMaker.com or LaserStar (higher cost but faster, for initial testing)
- Lead time: 4-6 weeks from Alibaba, 1-2 weeks domestic

**Marketing copy:**
> "Your art deserves to last. The StoneWalker Forever Plaque is a laser-engraved aluminum tag that survives years of rain, sun, and snow. While paper QR codes last months, a Forever Plaque lasts decades. Epoxy it to your stone and send it on a journey that outlasts the weather."

### 6.3 Apparel

**All apparel uses print-on-demand to avoid inventory risk.**

**Fulfillment partner:** Printful (integrates with Stripe, handles printing and shipping, no minimum order).

#### T-Shirts

**Design options:**
1. "Classic Logo" — StoneWalker logo centered on chest, small QR code on back leading to stonewalker.org
2. "Stone Journey" — A stylized painted stone with a dotted line circling a globe
3. "I Hide Stones" — Bold text front, StoneWalker logo back
4. "Stone Found!" — Illustration of a hand picking up a colorful stone

**Specs:**
- Fabric: 100% combed ringspun cotton (Bella + Canvas 3001 or equivalent)
- Sizes: XS, S, M, L, XL, 2XL, 3XL
- Colors: Black, White, Forest Green, Navy
- Retail: $24.99
- COGS (Printful): ~$11-13
- Margin: ~48-55%

#### Caps

**Design:** Embroidered StoneWalker logo on front, small stone icon on side.

**Specs:**
- Style: Unstructured dad cap (relaxed fit)
- Fabric: 100% cotton twill
- Closure: Adjustable metal buckle
- Colors: Black, Olive Green, Navy, Stone Gray
- Retail: $22.99
- COGS (Printful): ~$10-12
- Margin: ~47-56%

#### Beanies

**Design:** Embroidered StoneWalker logo (small, centered on fold).

**Specs:**
- Style: Cuffed beanie
- Fabric: 100% acrylic knit
- One size fits most
- Colors: Black, Forest Green, Burgundy, Charcoal
- Retail: $19.99
- COGS (Printful): ~$8-10
- Margin: ~50-60%

### 6.4 Shop Integration for Physical Products

**New product category in `shop_config.json`:**

```json
{
  "id": "physical",
  "name": "Physical Products",
  "description": "Real-world StoneWalker gear",
  "order": 4,
  "requires_shipping": true
}
```

**New models needed:**

```python
class ShippingAddress(models.Model):
    user = ForeignKey(User, on_delete=CASCADE)
    name = CharField(max_length=200)
    street = CharField(max_length=200)
    city = CharField(max_length=100)
    state = CharField(max_length=100, blank=True)
    postal_code = CharField(max_length=20)
    country = CharField(max_length=2)  # ISO country code
    is_default = BooleanField(default=False)

class PhysicalOrder(models.Model):
    user = ForeignKey(User, on_delete=CASCADE)
    stripe_payment_id = CharField(max_length=255)
    shipping_address = ForeignKey(ShippingAddress, on_delete=PROTECT)
    status = CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ], default='pending')
    tracking_number = CharField(max_length=100, blank=True)
    tracking_url = URLField(blank=True)
    created_at = DateTimeField(auto_now_add=True)
    shipped_at = DateTimeField(null=True, blank=True)
    notes = TextField(blank=True)

class PhysicalOrderItem(models.Model):
    order = ForeignKey(PhysicalOrder, on_delete=CASCADE, related_name='items')
    product_id = CharField(max_length=50)
    product_name = CharField(max_length=200)
    quantity = PositiveIntegerField(default=1)
    unit_price_cents = IntegerField()
    size = CharField(max_length=10, blank=True)  # For apparel
    color = CharField(max_length=50, blank=True)  # For apparel
```

---

## 7. Stone Journey Analytics Dashboard

### 7.1 Access

- **URL:** `/my-stones/analytics/` (premium users only)
- **Free users:** See a preview/teaser with blurred data and "Upgrade to unlock" overlay.
- **Gate:** Check `request.user.subscription.tier` in view — redirect free users to `/premium/` with a message.

### 7.2 Key Metrics

Display these at the top of the dashboard as large stat cards:

| Metric | Calculation | Icon Suggestion |
|--------|------------|-----------------|
| Total Distance | Sum of all `distance_km` across user's stones | Globe with path |
| Countries Visited | Distinct countries from all StoneMove locations | Flag |
| Unique Finders | Distinct users who scanned any of the user's stones | People |
| Total Moves | Count of all StoneMoves for user's stones | Arrow path |
| Active Stones | Stones with a move in the last 90 days | Green dot |
| Time Traveling | Duration from first stone creation to now | Clock |
| Longest Journey | Stone with the highest distance_km | Trophy |
| Most Found Stone | Stone with the most moves | Star |

### 7.3 Charts and Visualizations

#### Journey Timeline (Line Chart)
- X-axis: Time (months)
- Y-axis: Cumulative distance traveled (all stones combined)
- Each stone is a separate colored line
- Hover shows: stone name, date, location, distance at that point

#### Distance Over Time (Bar Chart)
- X-axis: Months
- Y-axis: km traveled that month
- Stacked bars with each stone as a segment
- Shows growth trends

#### Geographic Heatmap (Map)
- Full-width Leaflet map
- Heatmap overlay showing concentration of stone finds
- Brighter = more scans in that area
- Toggle between: All time / Last 30 days / Last 7 days

#### Finder Distribution (Pie/Donut Chart)
- Shows what percentage of scans come from repeat finders vs. new finders
- Segments: "First-time finders", "Returning finders", "Self-scans"

#### Activity Calendar (GitHub-style)
- 52-week grid showing daily scan activity
- Color intensity: 0 scans (gray), 1 (light green), 2-3 (medium), 4+ (dark green)
- Hover shows: date, number of scans, stone names

### 7.4 Comparison Features

**Stone-to-Stone Comparison:**
- Select 2-3 stones from a dropdown
- Side-by-side stats: distance, moves, finders, countries
- Overlay their journey lines on the same map
- "Which stone traveled fastest?" metric (km per day)

**Time Period Comparison:**
- Compare this month vs. last month
- Compare this year vs. last year
- Show delta (growth/decline) with green/red arrows

### 7.5 Data Export

Premium users can export their data:

| Format | Contents | Button Text |
|--------|----------|-------------|
| CSV | All stones with stats (name, distance, moves, countries, dates) | "Download Stone Data (CSV)" |
| JSON | Full stone + move data with coordinates | "Download Raw Data (JSON)" |
| PDF | Analytics summary with charts (uses reportlab) | "Download Analytics Report (PDF)" |

### 7.6 Implementation Notes

**Charts library:** Use Chart.js (CDN, lightweight, responsive) for line/bar/pie charts. Use Leaflet.heat plugin for the heatmap.

**Data endpoint:** Create an API endpoint `/api/analytics/` that returns aggregated data as JSON. The dashboard page fetches this via AJAX and renders charts client-side.

**Caching:** Cache analytics data for 1 hour (premium users with active stones might check frequently, but real-time is not necessary).

---

## 8. Content Marketing Blog

### 8.1 URL Structure

```
/blog/                          — Blog index (paginated, 10 posts per page)
/blog/<slug>/                   — Individual blog post
/blog/category/<category>/      — Posts filtered by category
/blog/tag/<tag>/                — Posts filtered by tag
```

### 8.2 Blog Post Model

```python
class BlogPost(models.Model):
    title = CharField(max_length=200)
    slug = SlugField(max_length=200, unique=True)
    author = ForeignKey(User, on_delete=CASCADE)
    category = CharField(max_length=50, choices=[
        ('tutorial', 'Tutorials & How-Tos'),
        ('featured', 'Featured Stones'),
        ('community', 'Community Stories'),
        ('tips', 'Tips & Tricks'),
        ('news', 'News & Updates'),
        ('events', 'Events'),
    ])
    content = TextField()  # Markdown content
    excerpt = TextField(max_length=300)  # Preview text
    cover_image = ImageField(upload_to='blog/', blank=True)
    tags = CharField(max_length=500, blank=True)  # Comma-separated
    is_published = BooleanField(default=False)
    published_at = DateTimeField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    og_title = CharField(max_length=200, blank=True)
    og_description = CharField(max_length=300, blank=True)
```

### 8.3 Categories and Content Plan

#### Tutorials & How-Tos
Target audience: Beginners who found StoneWalker through search.

Sample posts:
1. "How to Paint Your First Stone and Send It on an Adventure" (SEO: "rock painting for beginners")
2. "The Best Sealant for Outdoor Painted Rocks: A Complete Guide" (SEO: "sealant for painted rocks")
3. "How to Attach a QR Code to a Painted Stone" (SEO: "QR code on rocks")
4. "10 Easy Rock Painting Ideas for Kids" (SEO: "rock painting ideas for kids")
5. "How to Use StoneWalker: A Complete Beginner's Guide"

#### Featured Stones
Target audience: Existing users, social sharing.

Sample posts:
1. "Stone of the Month: The Blue Wanderer's 5,000 km Journey"
2. "5 Stones That Crossed the Atlantic Ocean"
3. "The Stone That Made It to 10 Countries in 3 Months"

#### Community Stories
Target audience: Community building, social proof.

Sample posts:
1. "How a Teacher in Munich Used StoneWalker for a Geography Lesson"
2. "Meet the Family That Paints Stones Together Every Sunday"
3. "From Hobby to Obsession: One Painter's 100-Stone Challenge"

#### Tips & Tricks
Target audience: Intermediate users, retention.

Sample posts:
1. "5 Tips for Hiding Stones Where They'll Actually Be Found"
2. "How to Paint Weather-Resistant Designs"
3. "The Art of the Stone Drop: Organizing Your First Event"

#### News & Updates
Target audience: All users.

Sample posts:
1. "StoneWalker 2.0: What's New This Month"
2. "Introducing Premium: Analytics, Galleries, and More"
3. "StoneWalker in the Press: [publication] Feature"

### 8.4 Content Calendar Framework

| Week | Monday | Wednesday | Friday |
|------|--------|-----------|--------|
| Week 1 | Tutorial post | — | Featured Stone |
| Week 2 | Tips & Tricks | — | Community Story |
| Week 3 | Tutorial post | — | News/Update |
| Week 4 | Community Story | — | Featured Stone |

Minimum cadence: 2 posts per week. Maximum: 3 per week (more causes quality to drop).

### 8.5 SEO Strategy per Post

Every blog post must include:
- Title tag: `[Post Title] | StoneWalker Blog`
- Meta description: First 155 characters of excerpt
- OG image: Cover image or auto-generated (use the OG image system from section 3)
- Internal links: At least 2 links to other StoneWalker pages (shop, signup, other blog posts)
- Call to action: Every post ends with a CTA ("Get your free QR code", "Join the community", "Try StoneWalker today")

### 8.6 Admin Interface

Use Django Admin for blog management (no custom CMS needed in v1):
- List view: title, category, published status, published date
- Filters: category, published status, date
- Search: title, content
- Preview button that shows the post as it would render on the site

---

## 9. Community Events System

### 9.1 Concept: "Stone Drops"

A Stone Drop is a community event where a group of people hide painted stones in a specific area, and others try to find them. Think geocaching events meets Easter egg hunt meets public art installation.

### 9.2 Event Model

```python
class StoneDropEvent(models.Model):
    title = CharField(max_length=200)
    slug = SlugField(max_length=200, unique=True)
    organizer = ForeignKey(User, on_delete=CASCADE)
    description = TextField()
    location_name = CharField(max_length=200)  # "Central Park, New York"
    latitude = FloatField()
    longitude = FloatField()
    radius_km = FloatField(default=2.0)  # Event area radius
    start_date = DateTimeField()
    end_date = DateTimeField()
    cover_image = ImageField(upload_to='events/', blank=True)
    max_participants = IntegerField(null=True, blank=True)
    is_public = BooleanField(default=True)
    status = CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], default='draft')
    created_at = DateTimeField(auto_now_add=True)

class EventParticipant(models.Model):
    event = ForeignKey(StoneDropEvent, on_delete=CASCADE, related_name='participants')
    user = ForeignKey(User, on_delete=CASCADE)
    role = CharField(max_length=20, choices=[
        ('hider', 'Stone Hider'),
        ('seeker', 'Stone Seeker'),
        ('both', 'Hider & Seeker'),
    ], default='both')
    stones_hidden = IntegerField(default=0)
    stones_found = IntegerField(default=0)
    joined_at = DateTimeField(auto_now_add=True)

class EventStone(models.Model):
    event = ForeignKey(StoneDropEvent, on_delete=CASCADE, related_name='stones')
    stone = ForeignKey('Stone', on_delete=CASCADE)
    hidden_at = DateTimeField(null=True, blank=True)
    found_at = DateTimeField(null=True, blank=True)
    found_by = ForeignKey(User, null=True, blank=True, on_delete=SET_NULL)
```

### 9.3 Event Creation Flow

**URL:** `/events/create/` (login required)

**Step 1: Event Details**
```
CREATE A STONE DROP EVENT

Event Name:     [________________________]
Description:    [________________________]
                [________________________]
                [________________________]

Location:       [________________________]
                [Interactive map — click to set center point]

Event Radius:   [___] km (area where stones will be hidden)

Start Date:     [____/____/________] [__:__]
End Date:       [____/____/________] [__:__]

Cover Image:    [Upload]

Max Participants: [___] (leave blank for unlimited)

Public Event:   [x] Anyone can join
                [ ] Invite only (share link to join)

[Create Event]
```

**Step 2: Confirm & Share**
- Shows event preview.
- Generates a shareable link: `/events/<slug>/`
- Share buttons for social media.

### 9.4 Event Page (`/events/<slug>/`)

```
+--------------------------------------------------+
|                                                    |
|  [Cover Image — full width, 300px height]          |
|                                                    |
|  EVENT TITLE                                       |
|  Organized by [Username]                           |
|                                                    |
|  [Date range] | [Location] | [N] participants     |
|                                                    |
|  [Join This Event]  or  [You're In!]               |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  ABOUT THIS EVENT                                  |
|  [Description text]                                |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  EVENT MAP                                         |
|  [Leaflet map showing event area circle]           |
|  [Stone markers for found stones]                  |
|  [Grayed-out markers for hidden but unfound]       |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  LEADERBOARD                                       |
|                                                    |
|  TOP HIDERS          TOP SEEKERS                   |
|  1. @alice (8)       1. @bob (6)                   |
|  2. @charlie (5)     2. @diana (4)                 |
|  3. @eve (4)         3. @frank (3)                 |
|                                                    |
|  STATS                                             |
|  Stones hidden: 42                                 |
|  Stones found: 28                                  |
|  Find rate: 67%                                    |
|  Participants: 31                                  |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  RECENT ACTIVITY                                   |
|  [Activity feed of finds, most recent first]       |
|                                                    |
|  @bob found "Sunset Dream" — 5 min ago             |
|  @alice hid "Ocean Blue" — 12 min ago              |
|  @diana found "Rainbow Rock" — 18 min ago          |
|                                                    |
+--------------------------------------------------+
|                                                    |
|  SHARE THIS EVENT                                  |
|  [Facebook] [Twitter/X] [WhatsApp] [Copy Link]    |
|                                                    |
+--------------------------------------------------+
```

### 9.5 Leaderboard Design

**Scoring system:**
- Hiding a stone: 1 point
- Finding a stone: 2 points (finding is harder)
- Finding a stone within 1 hour of it being hidden: 3 points (speed bonus)
- First find of the event: 5 points (bonus)

**Leaderboard display:**
- Top 10 participants by total points
- Show rank, username, profile picture, points, stones hidden, stones found
- Highlight the current user's position (even if not in top 10)
- Update in real-time (or near-real-time with 60-second polling)

### 9.6 Social Proof Elements

**On the main StoneWalker page (`/stonewalker/`):**
- "Upcoming Events" section if any events exist in the next 30 days
- "N stones were found at [Event Name] last weekend!" banner after events

**On the Events index page (`/events/`):**
- List of upcoming events with join buttons
- Past events with stats (stones hidden, found, participants)
- "Organize Your Own Event" CTA button

**After finding a stone in an event:**
- Confetti animation (CSS only, no JS library)
- "You found a Stone Drop stone!" special message
- Leaderboard position update: "You're now #3 on the leaderboard!"

### 9.7 URL Structure

| URL | View | Description |
|-----|------|-------------|
| `/events/` | `EventListView` | Upcoming and past events |
| `/events/create/` | `EventCreateView` | Create new event (login required) |
| `/events/<slug>/` | `EventDetailView` | Event page with map and leaderboard |
| `/events/<slug>/join/` | `EventJoinView` | Join event (POST, login required) |
| `/events/<slug>/leaderboard/` | `EventLeaderboardView` | Full leaderboard (API, returns JSON) |

---

## 10. Dark Mode UX

### 10.1 Color Palette

**Core principle:** Dark mode should feel warm and inviting, not harsh or clinical. StoneWalker is about art and nature — the dark theme should complement that.

#### Background Colors

| Element | Light Mode | Dark Mode | CSS Variable |
|---------|-----------|-----------|--------------|
| Page background | `#FFFFFF` | `#1A1A2E` | `--color-bg` |
| Card/surface background | `#F5F5F5` | `#16213E` | `--color-surface` |
| Elevated surface (modals, dropdowns) | `#FFFFFF` | `#0F3460` | `--color-surface-elevated` |
| Input/form field background | `#FFFFFF` | `#1A1A2E` | `--color-input-bg` |
| Header background | `#FFFFFF` | `#0F3460` | `--color-header-bg` |
| Footer background | `#333333` | `#0A0A1A` | `--color-footer-bg` |

#### Text Colors

| Element | Light Mode | Dark Mode | CSS Variable |
|---------|-----------|-----------|--------------|
| Primary text | `#212121` | `#E0E0E0` | `--color-text` |
| Secondary text | `#757575` | `#9E9E9E` | `--color-text-secondary` |
| Muted text | `#BDBDBD` | `#616161` | `--color-text-muted` |
| Link text | `#4CAF50` | `#66BB6A` | `--color-link` |
| Link hover | `#388E3C` | `#81C784` | `--color-link-hover` |

#### Accent & Brand Colors

| Element | Light Mode | Dark Mode | CSS Variable |
|---------|-----------|-----------|--------------|
| Primary accent (StoneWalker green) | `#4CAF50` | `#4CAF50` | `--color-primary` |
| Primary hover | `#388E3C` | `#66BB6A` | `--color-primary-hover` |
| Secondary accent | `#2196F3` | `#42A5F5` | `--color-secondary` |
| Danger/error | `#F44336` | `#EF5350` | `--color-danger` |
| Warning | `#FF9800` | `#FFA726` | `--color-warning` |
| Success | `#4CAF50` | `#66BB6A` | `--color-success` |

#### Border & Divider Colors

| Element | Light Mode | Dark Mode | CSS Variable |
|---------|-----------|-----------|--------------|
| Border (default) | `#E0E0E0` | `#2A2A4A` | `--color-border` |
| Border (focused) | `#4CAF50` | `#4CAF50` | `--color-border-focus` |
| Divider | `#EEEEEE` | `#2A2A4A` | `--color-divider` |

### 10.2 Elements Requiring Special Treatment

#### Map (Leaflet)
- Use a dark tile layer: `CartoDB.DarkMatter` or `Stadia.AlidadeSmoothDark`
- Tile URL: `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`
- Stone markers should use slightly brighter colors in dark mode for contrast
- Polylines (journey paths) should use a lighter green (`#66BB6A`) with `opacity: 0.8`

#### Cards (Stone cards, stat cards)
- Add subtle `box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3)` in dark mode (vs. `rgba(0,0,0,0.1)` in light)
- Stone images should have a thin `1px solid var(--color-border)` border to separate them from the dark background
- Hover state: lighten the card background slightly (`#1E2A4A`)

#### Forms & Inputs
- Input fields: `background: var(--color-input-bg)`, `border: 1px solid var(--color-border)`, `color: var(--color-text)`
- Focus state: `border-color: var(--color-border-focus)`, subtle `box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.3)`
- Placeholder text: `color: var(--color-text-muted)`
- Checkboxes and radio buttons: use `accent-color: var(--color-primary)`

#### Modals
- Modal overlay: `background: rgba(0, 0, 0, 0.7)` (darker than light mode's `rgba(0,0,0,0.5)`)
- Modal content: `background: var(--color-surface-elevated)`
- Close button: white icon on dark, dark icon on light

#### Images & Avatars
- Profile pictures and stone photos: add `border: 2px solid var(--color-border)` to prevent them from blending into the dark background
- QR code displays: ensure the QR code area has a white background regardless of theme (QR codes need high contrast to scan)

#### Buttons
- Primary button: same green (`#4CAF50`), but use white text in both modes
- Secondary/outline button: `border-color: var(--color-border)`, `color: var(--color-text)` — adjust for readability
- Ghost buttons: slightly more visible border in dark mode

#### Welcome Modal & Decorative Elements
- The gradient circles (decorative background elements) should use darker, more muted gradient colors
- Replace light gradients with dark-compatible versions that still provide visual interest without being jarring

### 10.3 Toggle Implementation

**Toggle location:** Header bar, next to the language switcher.

**Toggle icon:** Sun icon (light mode active) / Moon icon (dark mode active). Use SVG icons.

**Toggle HTML:**
```html
<button id="theme-toggle" aria-label="Toggle dark mode" title="Toggle dark mode">
  <svg class="icon-sun">...</svg>
  <svg class="icon-moon">...</svg>
</button>
```

**Behavior:**
1. On click, toggle `data-theme="dark"` on `<html>` element.
2. Save preference to `localStorage.setItem('theme', 'dark')`.
3. On page load, check (in this order):
   a. `localStorage.getItem('theme')` — user's explicit choice
   b. `window.matchMedia('(prefers-color-scheme: dark)').matches` — system preference
   c. Default to light mode
4. Apply theme before first paint (inline `<script>` in `<head>` to prevent flash of wrong theme).

**CSS structure:**
```css
:root {
  --color-bg: #FFFFFF;
  --color-surface: #F5F5F5;
  --color-text: #212121;
  /* ... all light mode values ... */
}

[data-theme="dark"] {
  --color-bg: #1A1A2E;
  --color-surface: #16213E;
  --color-text: #E0E0E0;
  /* ... all dark mode values ... */
}
```

### 10.4 Transition Animation

When toggling between modes, apply a smooth transition to prevent jarring color changes:

```css
html {
  transition: background-color 0.3s ease, color 0.3s ease;
}

html * {
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
}

/* Disable transitions on page load to prevent flash */
html.no-transition,
html.no-transition * {
  transition: none !important;
}
```

On page load, add `no-transition` class, apply theme, then remove the class after a frame:
```javascript
document.documentElement.classList.add('no-transition');
applyTheme();
requestAnimationFrame(() => {
  document.documentElement.classList.remove('no-transition');
});
```

### 10.5 Testing Considerations

- Test all pages in both modes: home, map, my-stones, stone edit, stone scan, shop, about, signup, login, profile modal, all modals.
- Verify QR codes remain scannable (white background preserved).
- Verify map readability with dark tiles.
- Verify form validation errors are visible (red on dark can be hard to see — use the specified `#EF5350`).
- Test the flash-prevention script works (no white flash on dark mode page load).
- Verify the toggle persists across navigation and page reloads.
- Test system preference detection when no localStorage value exists.

---

## Summary

This document specifies 10 major features for StoneWalker Sprint 2. Here is a prioritized implementation order based on user impact, revenue potential, and dependency chains:

### Priority 1 — Foundation (implement first)
1. **Terms of Use** (Section 1) — Legal requirement before any growth push. Blocks nothing but is a prerequisite for responsible scaling. Relatively small implementation effort.
2. **Email Notification System** (Section 2) — Core retention mechanism. "Your stone was found!" is the single most exciting moment in the product. This drives repeat engagement.
3. **Dark Mode** (Section 10) — Large UX improvement that touches all pages. Should be done early because it establishes the CSS variable system that all future features will use.

### Priority 2 — Growth (implement after foundation)
4. **Social Sharing Pages** (Section 3) — Every shared stone is free marketing. OG images make shares compelling. Directly drives new user acquisition.
5. **Social Media Profile Connections** (Section 4) — Small feature that amplifies sharing. Quick to implement once sharing pages exist.
6. **Content Marketing Blog** (Section 8) — SEO play that compounds over time. Start publishing content as soon as the blog infrastructure is ready.

### Priority 3 — Revenue (implement after growth mechanics)
7. **Premium Supporter Tier** (Section 5) — Recurring revenue is the backbone of sustainability. Requires Stripe subscription integration.
8. **Stone Journey Analytics Dashboard** (Section 7) — Key premium feature that justifies the subscription. Implement alongside or shortly after premium tier.

### Priority 4 — Physical & Community (implement when volume justifies)
9. **Physical Product Fulfillment** (Section 6) — Only implement when there is enough traffic to justify inventory and shipping logistics. Start with the metal plaques (highest margin, simplest fulfillment).
10. **Community Events System** (Section 9) — Implement when the community is large enough to sustain events (50+ active users in a geographic area). The leaderboard and social proof elements are powerful but need critical mass.

### Cross-Cutting Concerns
- All user-facing text must be wrapped in `{% trans %}` tags for the translation system.
- All new pages must work with the existing responsive breakpoint system.
- All new forms must include CSRF protection.
- All new API endpoints must require authentication where appropriate.
- All new models need migrations and corresponding admin registrations.
- All features need test coverage following the project's testing conventions.

### Estimated Model Changes Summary

| Model | New Fields / New Model |
|-------|----------------------|
| Profile | `terms_accepted_at`, `terms_version`, `ai_training_opt_out`, `social_facebook`, `social_instagram`, `social_twitter`, `social_mastodon`, `social_tiktok`, `social_links_public` |
| NotificationPreference (new) | `user`, `stone_found`, `stone_move`, `milestones`, `weekly_digest`, `welcome_tips`, `community_news` |
| Subscription (new) | `user`, `tier`, `stripe_customer_id`, `stripe_subscription_id`, `billing_interval`, `current_period_end`, `is_active`, `canceled_at` |
| BlogPost (new) | `title`, `slug`, `author`, `category`, `content`, `excerpt`, `cover_image`, `tags`, `is_published`, `published_at`, `og_title`, `og_description` |
| StoneDropEvent (new) | `title`, `slug`, `organizer`, `description`, `location_name`, `latitude`, `longitude`, `radius_km`, `start_date`, `end_date`, `cover_image`, `max_participants`, `is_public`, `status` |
| EventParticipant (new) | `event`, `user`, `role`, `stones_hidden`, `stones_found` |
| EventStone (new) | `event`, `stone`, `hidden_at`, `found_at`, `found_by` |
| ShippingAddress (new) | `user`, `name`, `street`, `city`, `state`, `postal_code`, `country`, `is_default` |
| PhysicalOrder (new) | `user`, `stripe_payment_id`, `shipping_address`, `status`, `tracking_number`, `tracking_url`, `shipped_at`, `notes` |
| PhysicalOrderItem (new) | `order`, `product_id`, `product_name`, `quantity`, `unit_price_cents`, `size`, `color` |

### New URL Endpoints Summary

| URL | Section | Auth Required |
|-----|---------|---------------|
| `/terms/` | 1 | No |
| `/privacy/` | 1 | No |
| `/accounts/notifications/` | 2 | Yes |
| `/accounts/unsubscribe/<token>/<category>/` | 2 | No |
| `/stone/<pk>/share/` | 3 | No |
| `/stone/<pk>/og-image/` | 3 | No |
| `/premium/` | 5 | No |
| `/premium/checkout/<tier>/<interval>/` | 5 | Yes |
| `/premium/success/` | 5 | Yes |
| `/premium/manage/` | 5 | Yes |
| `/my-stones/analytics/` | 7 | Yes (Premium) |
| `/api/analytics/` | 7 | Yes (Premium) |
| `/blog/` | 8 | No |
| `/blog/<slug>/` | 8 | No |
| `/blog/category/<category>/` | 8 | No |
| `/events/` | 9 | No |
| `/events/create/` | 9 | Yes |
| `/events/<slug>/` | 9 | No |
| `/events/<slug>/join/` | 9 | Yes |
| `/events/<slug>/leaderboard/` | 9 | No |

---

*This spec was produced by the CreativeMind agent as part of the StoneWalker Sprint 2 planning session, February 2026.*
