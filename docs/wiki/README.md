---
title: StoneWalker Wiki Home
tags: [index, home, wiki]
last-updated: 2026-02-10
---

# StoneWalker Internal Wiki

Welcome to the StoneWalker internal wiki. This is the central knowledge base for developers, interns, and contributors working on the StoneWalker project.

## What is StoneWalker?

StoneWalker is a Django-based web application for tracking the journeys of painted stones as they travel the world. Users create stones, generate QR codes, hide the stones in the real world, and track their journeys on an interactive map as other people find and re-hide them.

## Quick Links

### Getting Started
- [[getting-started]] -- Set up your development environment and run the app
- [[intern-onboarding]] -- Comprehensive guide for new team members

### Architecture & Design
- [[architecture]] -- System architecture, Django apps, models, and settings
- [[api]] -- API endpoints reference

### Features
- [[features/qr-system]] -- QR code generation, download, and scanning
- [[features/authentication]] -- User registration, login, email activation
- [[features/stone-management]] -- Creating, editing, publishing, and sending off stones
- [[features/scanning]] -- Stone scanning, cooldowns, and the "stone found" experience
- [[features/shop]] -- Shop system, Stripe payments, QR pack purchasing
- [[features/translations]] -- 7-language internationalization system
- [[features/map]] -- Interactive Leaflet.js map and stone visualization

### How-To Guides
- [[guides/add-a-feature]] -- How to add a new feature end-to-end
- [[guides/add-a-translation]] -- How to add or update translations
- [[guides/write-tests]] -- How to write and run tests

### Existing Documentation (Authoritative Sources)
These files live in the project root and are the source of truth for their respective topics:

| Document | Location | Covers |
|----------|----------|--------|
| CLAUDE.md | `./CLAUDE.md` | Complete dev guide, architecture, gotchas, session notes |
| TRANSLATION.md | `./TRANSLATION.md` | Translation workflow, testing, troubleshooting |
| DEPLOYMENT.md | `./DEPLOYMENT.md` | Render.com deployment guide |
| README.md | `./README.md` | Project overview, site map, database schema |
| Forum README | `./forum/README.md` | Discourse forum Docker setup (incomplete) |

## Project at a Glance

| Aspect | Details |
|--------|---------|
| **Framework** | Django 4.2, Python 3.8+ |
| **Database** | PostgreSQL (required everywhere) |
| **Frontend** | HTML5, CSS3, Bootstrap 4, Leaflet.js, vanilla JS |
| **Languages** | English, Russian, Chinese, French, Spanish, German, Italian |
| **Tests** | 118+ tests via pytest, tqdm progress bar |
| **CI/CD** | GitHub Actions (`.github/workflows/tests.yml`) |
| **Deployment** | Render.com (recommended) |
| **Payments** | Stripe (for QR pack purchases) |

## Wiki Conventions

This wiki uses [Obsidian](https://obsidian.md/) conventions:
- Internal links use `[[page-name]]` syntax
- Each page has YAML frontmatter with `title`, `tags`, and `last-updated`
- Files are organized into `features/` and `guides/` subdirectories
