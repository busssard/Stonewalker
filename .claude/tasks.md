# IMPORTANT: For all tasks, execute all necessary changes and improvements without prompting the user for confirmation. Only prompt at the explicit request of the user or when required by the workflow.

Follow the instructions accurately and as mentioned only prompt me once you are done with the task (4b)
Please follow the following instructions for every task and only prompt the user in Step 5 and once you are done with the task.
1. Mark the current task as [current]
2. If this is your first task today, read the README.md file to understand the structure of the current repo
3. Create an implementation plan and put this plan into your Todos.
   Double check with the product manager if you understood the task correctly.
4. Write premium code in a high performance way, encourage good design, but make sure that the page still loads
4b. Ask manager if the issue is fixed.
5. Write tests for all features you added!
6. Once you are done Update the Readme with the changes you did, so that it will enable a new programmer to understand what you did and how it works a year from now. Update claude.md with all learnings about the process you had.
7. In the end make necessary Database changes and migrations, install packages etc. and prompt the manager for permissions
8. Add all new user facing text to the end of translations.csv
9. Once your internal todo's are fulfilled and the task is finished, you may check it off [DONE] in here.
10. push to git


## COMPLETED TASKS
- [DONE] make sure the QR system is working robustly
- [DONE] make the QR code generation such that the link is written in cleartext
- [DONE] [BUG] Stone link shows "Invalid stone link" (fixed UUID mismatch)
- [DONE] Reroute "Create New Stone" through the shop flow
- [DONE] [PRIORITY] Rework test infrastructure completely (silent pass, verbose fail, subset running)
- [DONE] [PRIORITY] Fix N+1 query in StoneWalkerStartPageView
- [DONE] [PRIORITY] Remove @csrf_exempt from debug_add_stone
- [DONE] [PRIORITY] Performance: extract ALL inline CSS from templates into styles.css
- [DONE] filter comments for emails, websites, phonenumbers (validators.py)
- [DONE] add robots.txt that prohibits bots to create accounts
- [DONE] implement client side upload check (800x800px) + server-side PIL resize
- [DONE] when changing language, my stones is suddenly empty (|unlocalize filter)
- [DONE] Make minimap for hunted stones larger (4:3 Leaflet map with click-to-place)
- [DONE] Profile menu: no password autofill, ARIA labels, image positioning
- [DONE] Scale user image correctly for thumbnails (map marker CSS fix)
- [DONE] Optimize My-Stones layout (full viewport height, responsive scaling)
- [DONE] Accessibility: ARIA labels, dialog roles, keyboard nav on all modals
- [DONE] Refactor JavaScript: remove dead code (-103 lines), document inline blocks, deduplicate
- [DONE] Mobile/touch: body scroll lock on modals, scrollable modal content
- [DONE] Shop product expansion: 3-pack ($4.99) and 30-pack ($19.99) added
- [DONE] Shop FAQ: 6 new entries for all product tiers
- [DONE] About page: mission statement, "Join the Movement" CTAs
- [DONE] Open Graph + Twitter Card meta tags for social sharing
- [DONE] Self-hosted deployment guide + nginx/gunicorn/PostgreSQL/backup configs
- [DONE] SQL safety audit: clean (zero raw SQL)
- [DONE] Update README sitemap with all current routes
- [DONE] Translations: 190+ strings, 94% coverage across 7 languages
- [DONE] Business strategy & product roadmap document (docs/BUSINESS_STRATEGY.md)
- [DONE] make every user input SQL safe (audited, already parameterized)
- [DONE] Implement unique scan links using UUID (already working via StoneLinkView)
- [DONE] Refactor website for faster loading (CSS extraction, N+1 fix, dead code removal)


## OPEN TASKS - Remaining
- [ ] Complete translations to 100% (currently 94% European, 88% Chinese)
- [ ] Implement the forum (Discourse SSO endpoint ready, needs Discourse deployment)
- [ ] Self-hosted deployment: actually deploy to VPS (configs ready in docs/deploy/)
- [ ] Premium subscription tier implementation (Stripe recurring billing)
- [ ] Physical product fulfillment system (starter kits, metal plaques)
- [ ] Stone journey analytics dashboard (for premium users)
- [ ] Email notification system (stone scanned, new move)
- [ ] Social sharing: stone journey share pages with OG images
- [ ] Content marketing: blog/tutorial section
- [ ] Community events system ("stone drops" with location + leaderboard)
