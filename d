[33mcommit f93d6b38c8a9d9e56660ab034e892780ef313c09[m[33m ([m[1;36mHEAD -> [m[1;32mmain[m[33m, [m[1;31morigin/main[m[33m, [m[1;31morigin/HEAD[m[33m)[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 15 22:13:21 2025 +0200

    profile picture url bugfix

[33mcommit 81b335e0644f0ed06edd53c67ae21110ba0705f0[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 15 22:07:24 2025 +0200

    profile picture url change

[33mcommit 1eb2c3b8002629f4f72556946717fbf7816201b0[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 15 17:36:27 2025 +0200

    remove default profile pic, instead check in .html

[33mcommit 8c776a3c117219f784d5c1b9d087fc6d4c0827c2[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 15 15:52:24 2025 +0200

    update check for default profile pic

[33mcommit d38ce7ba46e581a63953d3ef77aadbfd70b4c92f[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 15 15:23:23 2025 +0200

    fix stlye of debug module

[33mcommit adf6748a84b2282935e412bc31cccaa1edb822dd[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 15 14:46:15 2025 +0200

    debug_modal and profile static update

[33mcommit cd6108a71b4bc273d3019aacf83f99cd4ebdbfad[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 15 14:12:27 2025 +0200

    fixed mystones styles.css

[33mcommit c6d197d71177323a8db931de6211074cb45aaa26[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 15 13:32:37 2025 +0200

    modify sendgrid Email

[33mcommit 4b65a3542230a234233e7983694e2d3dc1f8415b[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 15 13:21:33 2025 +0200

    Email Sendgrid

[33mcommit 1d964e740ad4020ec2053ef45bb5dc1f3ac7377f[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 14 16:11:57 2025 +0200

    login page redesign

[33mcommit 3c9120f792febad8f06d0783056c5b6a0a4437a1[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 8 19:21:14 2025 +0200

    Signup: popup modal redesign for sign-up page; overlay/modal CSS; close on outside/ESC; scroll lock; sync assets/static CSS; preload font; README + DEPLOYMENT notes; mark task done; tests passing

[33mcommit 940ebf41a134a7a2f52a7bb146b394d20a0611d7[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 8 14:54:55 2025 +0200

    docs: document local dev vs production env toggle; update Render start command and migration notes

[33mcommit 3b8a950152ad5170d3a5a5c6effc43f245f306cf[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 8 13:40:05 2025 +0200

    fix(render): ensure production uses DATABASE_URL via dj_database_url.config; simplify app.settings env switch

[33mcommit c9a60486b6fca85412dc7daff1410a8e4b404a8f[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 8 13:11:27 2025 +0200

    chore(render): add render_start.sh to auto-migrate on boot; log errors to console in production

[33mcommit 57ab37c0c82e90f2c8a1e82fcb794da8d4170baf[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 8 12:42:31 2025 +0200

    chore(render): add source/render_build.sh and make build resilient to root vs source workdir; remove duplicate render-build.sh

[33mcommit aa0b6599b3c527430d30d679e283ce0116d5ff54[m
Merge: 9467344 ca021c1
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 8 12:22:23 2025 +0200

    fix: resolve requirements.txt merge conflict

[33mcommit ca021c100a09908ee9575fca897cccc88941b0de[m[33m ([m[1;31morigin/chore/render-deploy[m[33m, [m[1;32mchore/render-deploy[m[33m)[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 8 12:18:34 2025 +0200

    chore(render): add Render build scripts, enable WhiteNoise, ALLOWED_HOSTS env, dj-database-url; add .onrender.com; fix tests runner default collection

[33mcommit 9467344c82ab25614f1c2dbb8cb69b309f37aede[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 20:23:31 2025 +0200

    duplicate requirements.txt

[33mcommit fe3d39d1d336e7e2301d7ec24c323433dd19b78b[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 20:14:58 2025 +0200

    remove netlify deployment tests

[33mcommit fbd8d70e9294bc2fdaaefaef1eee9ee99661f6f6[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 20:05:23 2025 +0200

    moved relevant files to source

[33mcommit 7a4e6ffd1ef1581e3bd7299557ae8579eb3460b1[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 18:41:19 2025 +0200

    update requirements.txt

[33mcommit 2849cc4ca1c4c95e77f7f147975414dd4dd32781[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 18:35:54 2025 +0200

    Fix deployment paths and add build script for Render.com

[33mcommit bc3885aa3695feab5a1f6f626af9c24da24e940e[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 18:35:21 2025 +0200

    Fix deployment paths and add build script for Render.com

[33mcommit b19672f81163227cdf9a7154b6dd7e7216f5cdb7[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 18:17:27 2025 +0200

    Update deployment commands with correct working directory and paths

[33mcommit ec83697169bd957811bc953f5231b4be01424dc7[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 18:13:41 2025 +0200

    Revert manage.py and add PYTHONPATH to start command

[33mcommit d90a43c5bef24ddbc285bd22d52682a86a436817[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 18:11:29 2025 +0200

    Fix Django settings module path for deployment

[33mcommit a99421fcd4ee1c039a43568538a96df80e3166d7[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 18:07:44 2025 +0200

    Fix start command to use correct module path source.app.wsgi

[33mcommit 97090bb9ea4838696a3d0e4684940d73860fe05c[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 17:34:37 2025 +0200

    Add setuptools and wheel to requirements.txt and update build command

[33mcommit d645af7d5c6422347dce773210dd283558af8d46[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 17:29:49 2025 +0200

    Create clean requirements.txt with only essential packages used in the codebase

[33mcommit 4cc5e650a334db22ed8138d1637d56ab1d95556b[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 17:23:59 2025 +0200

    Update build command with force-reinstall and no-build-isolation flags

[33mcommit b80f80624d66131567ff7b07990a4947b30e0a38[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 17:20:44 2025 +0200

    Fix build commands to use default python and add Python version setting instructions

[33mcommit d5bd2f9ac9a1a6cd827874a94a454210135652b8[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 17:17:33 2025 +0200

    Update build and start commands to explicitly use Python 3.12

[33mcommit 3332ec5e98a91dbc58cab3c5658c9944b0d18987[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 17:11:26 2025 +0200

    Add Python 3.12 runtime and update build command for Render.com compatibility

[33mcommit e0ff1c115cec1f8e41ba6bc79eccc7ccc1eef88a[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 17:04:02 2025 +0200

    Add minimal pyproject.toml for pip PEP 517/518 build compatibility

[33mcommit 4e2d62cffe886bee93d198da93855352a1ddbd43[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 17:00:18 2025 +0200

    Move setuptools and wheel to top of requirements.txt for build compatibility

[33mcommit b43981f2fce4ad5d60ead106638c37fe5afe07eb[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 16:36:27 2025 +0200

    add setuptools and wheel to requirements

[33mcommit cb6ae29fa3cfe9926fb790afb6c61ce926a2c4ea[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 16:29:00 2025 +0200

    remove pyproject.toml

[33mcommit 4ae5d3311197e4d4afddfa43b2835f46f962d1ed[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 15:49:34 2025 +0200

    Update tests to remove Netlify file requirements

[33mcommit ca1fe6b3d51b9e715a8653eea7760317a79ee380[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Aug 7 15:41:40 2025 +0200

    Update deployment docs and configuration for Render.com and Gunicorn

[33mcommit 9fbdf9d303b454d591f86967ee9d8c22ac1920b1[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Aug 4 23:43:29 2025 +0200

    Add Netlify deployment configuration and documentation
    
    - Created comprehensive Netlify deployment setup with netlify.toml and build.sh
    - Added serverless functions for basic Django routing
    - Updated production settings for Netlify compatibility
    - Created detailed deployment guide with alternative platform recommendations
    - Added 10 comprehensive tests for Netlify deployment functionality
    - Updated README with deployment options and limitations
    - Added translations for new user-facing text
    - Marked Netlify deployment task as completed
    
    This setup provides static file hosting on Netlify's CDN with serverless functions
    for basic routing. Full Django functionality requires platforms like Heroku or Railway.

[33mcommit 315c2204521019ffa9faef7386a04ba9df207b32[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Aug 4 23:31:44 2025 +0200

    Fix welcome modal test to handle translations in test environment

[33mcommit bcd91f0e38856ad40b37cde642da0b90b159c5b8[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Aug 4 23:29:02 2025 +0200

    Add debug output to welcome modal test

[33mcommit 8329a70fadaae597a2c9723256cfda2a42bf0aa2[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Aug 4 23:26:44 2025 +0200

    Fix welcome modal test to handle translation variations

[33mcommit 8f48a15ebbb99c9c598bce44cd6eae5d05dfe9cf[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Aug 4 23:21:58 2025 +0200

    Update tests and improve UI components

[33mcommit c5bf3f32107f7ec6c09fa9bf66d1d07c06f56a9a[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Aug 4 01:55:15 2025 +0200

    Complete stone found experience implementation with hunted stone location field, scan modal congratulations, comprehensive stone found page, database schema update, translations, and comprehensive testing

[33mcommit 61db17b390ed92fc80cdba81c4517146d63c08f9[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 1 16:49:42 2025 +0200

    Fix modal opening issue by wrapping JavaScript in DOMContentLoaded
    
    - Wrapped all modal-related JavaScript in DOMContentLoaded event
    - Added proper null checks for DOM elements
    - Fixed timing issue where JavaScript was running before DOM was ready
    - Modal should now open correctly when 'Create a Stone' button is clicked

[33mcommit 71a789544ea7c42d5e9240778e24bbe4e57b42e0[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 1 16:36:25 2025 +0200

    Refactor Stone creation with UUID, QR generation, and automatic shape selection
    
    - Added UUID field to Stone model for secure QR code generation
    - Implemented automatic shape selection: circles for hidden stones, triangles for hunted stones
    - Added QR code generation with UUID-based links to stone scan page
    - Added QR download functionality after stone creation
    - Enhanced stone scanning to support both UUID and PK_stone parameters
    - Improved validation for hunted stones requiring location
    - Added comprehensive test coverage (18 new tests)
    - Created proper database migrations for UUID field
    - Updated README with new functionality documentation

[33mcommit d42571890ca7231d345ac50554ba64e445765d35[m
Author: Ole Mueller <ole@falanx.de>
Date:   Fri Aug 1 15:18:59 2025 +0200

    Implement fixed header with scrolling functionality
    
    - Fixed header positioning with position: fixed and proper z-index management
    - Added body padding-top to prevent content from being hidden behind header
    - Fixed scrolling issues by changing height: 100vh to height: 100% for overlays
    - Updated burger menu overlay and navigation to work with fixed header
    - Added comprehensive test coverage for fixed header functionality
    - Updated README.md with implementation details
    - Fixed scrolling on About, Create Stone, Scan Stone, and Create Account pages
    - Ensured cross-browser compatibility and responsive design

[33mcommit 6dbb41010ac2add388dfcb15f196bc16192df953[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Jul 31 15:19:56 2025 +0200

    Fix failing tests after stone modal implementation
    
    - Fixed CSS utility class test to account for inline styles in modal fallback
    - Updated welcome modal tests to match actual implementation
    - Fixed distance calculation test to check for data structure instead of exact value
    - All 49 tests now pass successfully

[33mcommit 39c5432c3a0f6bad93da1f63685b258e39e7fb74[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Jul 31 15:14:57 2025 +0200

    Fix stone modal popup functionality in my-stones page
    
    - Fixed ES6 module import conflicts preventing modal from loading
    - Resolved CSS class conflicts where display-none was overriding display: flex
    - Implemented proper modal container creation and cleanup
    - Added fallback functionality using showSimpleModal when ES6 import fails
    - Enhanced error handling with proper catch blocks
    - Added comprehensive test coverage for stone modal functionality
    - Removed debug code and cleaned up implementation
    - Updated README with detailed documentation of the fix
    
    The stone modal now properly displays when clicking on stones in the my-stones page,
    showing stone details, images, moves, and comments with proper close functionality.

[33mcommit a6254a9d3c71d29ea1f0459ea908ee184f3ebf69[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Jul 31 14:17:06 2025 +0200

    feat: implement language change redirect to main page
    
    - Modified ChangeLanguageView to set redirect_to context to main page
    - Added comprehensive test coverage for language change functionality
    - Updated README documentation for language change behavior
    - Users now automatically redirected to /stonewalker/ after language change
    - Preserves user authentication during language change
    - All tests passing (7 new tests added)

[33mcommit 4b9b2958732bdf03cfbe15dee22f9c67063a3d42[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Jul 31 13:24:52 2025 +0200

    Fix translation and navigation issues - Fix malformed PO file entries and smart quotes - Correct English translations for Log in/Sign up/Log out - Add i18n_patterns for language-specific URLs - Update tests to match correct translation strings - Ensure proper test environment with English language activation - All tests now passing

[33mcommit 2a59cc53a1ab0346f5512ce80db0c99f214d65b8[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Jul 31 12:18:38 2025 +0200

    Add link to TRANSLATION_README.md in main README

[33mcommit 5451d55bf780f2be5d055287d7bc3b50db4209b2[m
Author: Ole Mueller <ole@falanx.de>
Date:   Thu Jul 31 12:12:05 2025 +0200

    Add comprehensive translation testing setup
    
    - Add automatic translation compilation before tests
    - Add pre-commit hooks for translation compilation
    - Add Excel/CSV translation editing workflow
    - Add Django management command for translation compilation
    - Add comprehensive test suite with 26 tests
    - Add pytest configuration with translation compilation
    - Add Makefile with convenient commands
    - Add detailed documentation in TRANSLATION_TESTING_SETUP.md
    - Link translation setup docs in README.md
    
    This ensures translations are compiled and validated before every test execution and commit.

[33mcommit 495744ad52090ad6ed5b3e759b114cca3e10109b[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Jul 28 20:01:57 2025 +0200

    Fix translation issues: add Russian language header, fix empty msgstr, and improve test robustness

[33mcommit e5f43f78beff70d360661f62ef3a985212cb85a2[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Jul 28 20:00:22 2025 +0200

    Fix PO file test logic to properly handle tuple occurrences and filter Django built-ins

[33mcommit f6dc3043c1b38e00b1ec50dac0d5a543b82e061b[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Jul 28 19:59:03 2025 +0200

    Fix remaining test issues with PO file parsing and forbidden characters

[33mcommit e29b7c7b0a10acfd38a000188e94aa9baa9e6b9b[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Jul 28 19:58:05 2025 +0200

    Fix translation test issues and improve test robustness

[33mcommit f0a8f84511f14ec6d0cd35879a6bc6b7692d27a5[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Jul 28 19:56:15 2025 +0200

    Fix syntax error in tests and update navigation tests

[33mcommit d1f8b74bf17cb90007f133814f03ccc427b7d0c8[m
Author: Ole Mueller <ole@falanx.de>
Date:   Mon Jul 28 19:52:22 2025 +0200

    Update Stonewalker project with comprehensive changes and new features

[33mcommit cc5e69835750e61873e41c9d19b4cf9fd89fa7e3[m
Merge: 7bca1b6 d4f379d
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri Nov 3 13:48:56 2023 +0200

    Merge pull request #119 from egorsmkv/dependabot/pip/django-4.2.7
    
    Bump django from 4.2.5 to 4.2.7

[33mcommit d4f379dd19166d3a07130ea8d82270fb358bff48[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Thu Nov 2 21:58:38 2023 +0000

    Bump django from 4.2.5 to 4.2.7
    
    Bumps [django](https://github.com/django/django) from 4.2.5 to 4.2.7.
    - [Commits](https://github.com/django/django/compare/4.2.5...4.2.7)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 7bca1b6d04ef520b39862e37e6a982ee5d6bc7b6[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri Oct 27 16:07:27 2023 +0300

    Delete CHANGELOG.md
    
    Moved to Releases

[33mcommit b895129564990407e426413a3e346883b85075a6[m[33m ([m[1;33mtag: v3.8[m[33m)[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Wed Oct 4 16:11:07 2023 +0300

    Change log out method and add new translations #116

[33mcommit 089363a4359cf8723d76ddb8e66d5049eed7e72c[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Wed Oct 4 13:21:13 2023 +0300

    Update Django to 4.2.5

[33mcommit 9389911dbc98d8f411922e1e8b5dd9247ac9a95b[m[33m ([m[1;33mtag: v3.7[m[33m)[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Thu Jul 13 15:52:04 2023 +0300

    Update to Django 4.2.3

[33mcommit 5684420bf21d79263105a6f2009013bac15dbca6[m
Merge: d5dedbe cc2c300
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Thu Jul 13 14:58:56 2023 +0300

    Merge pull request #111 from egorsmkv/dependabot/pip/django-4.1.10
    
    Bump django from 4.1.9 to 4.1.10

[33mcommit cc2c3003aedd3c9b2aac444b54c884e016922c55[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Thu Jul 6 00:10:08 2023 +0000

    Bump django from 4.1.9 to 4.1.10
    
    Bumps [django](https://github.com/django/django) from 4.1.9 to 4.1.10.
    - [Commits](https://github.com/django/django/compare/4.1.9...4.1.10)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit d5dedbe9307e811b679880b9664e364c57bd965c[m
Merge: f03140e b08c5ba
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Wed May 10 12:24:44 2023 +0300

    Merge pull request #110 from egorsmkv/dependabot/pip/django-4.1.9
    
    Bump django from 4.1.7 to 4.1.9

[33mcommit b08c5ba90636c48d2d6e00a8b4fa600965765c07[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Tue May 9 22:46:40 2023 +0000

    Bump django from 4.1.7 to 4.1.9
    
    Bumps [django](https://github.com/django/django) from 4.1.7 to 4.1.9.
    - [Commits](https://github.com/django/django/compare/4.1.7...4.1.9)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit f03140ef63170ed5701bcb392d70d614f837a3c9[m
Merge: 5f17392 3c0dfb0
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Sat Apr 22 22:31:03 2023 +0300

    Merge pull request #109 from egorsmkv/dependabot/pip/sqlparse-0.4.4
    
    Bump sqlparse from 0.4.3 to 0.4.4

[33mcommit 3c0dfb0f2728739bc43bc0d7b199b00b965a14ac[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Fri Apr 21 22:42:36 2023 +0000

    Bump sqlparse from 0.4.3 to 0.4.4
    
    Bumps [sqlparse](https://github.com/andialbrecht/sqlparse) from 0.4.3 to 0.4.4.
    - [Release notes](https://github.com/andialbrecht/sqlparse/releases)
    - [Changelog](https://github.com/andialbrecht/sqlparse/blob/master/CHANGELOG)
    - [Commits](https://github.com/andialbrecht/sqlparse/compare/0.4.3...0.4.4)
    
    ---
    updated-dependencies:
    - dependency-name: sqlparse
      dependency-type: indirect
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 5f17392c10ec4384008004759c1b9a8f71a50853[m
Merge: 6a503a1 77dd9be
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Thu Feb 16 00:16:12 2023 +0200

    Merge pull request #108 from egorsmkv/dependabot/pip/django-4.1.7
    
    Bump django from 4.1.6 to 4.1.7

[33mcommit 77dd9becb80e60f1b1f29c9ad7efc7c2b8cb5e12[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Wed Feb 15 20:34:55 2023 +0000

    Bump django from 4.1.6 to 4.1.7
    
    Bumps [django](https://github.com/django/django) from 4.1.6 to 4.1.7.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/4.1.6...4.1.7)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 6a503a16614ed1f8023cc70a08357e03af87ad69[m
Merge: 7efeaa1 3c2f3c5
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Sat Feb 4 16:14:59 2023 +0200

    Merge pull request #107 from egorsmkv/dependabot/pip/django-4.1.6
    
    Bump django from 4.1.5 to 4.1.6

[33mcommit 3c2f3c548a6a117ca228d09e849efc8dbafc5ded[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Fri Feb 3 22:14:51 2023 +0000

    Bump django from 4.1.5 to 4.1.6
    
    Bumps [django](https://github.com/django/django) from 4.1.5 to 4.1.6.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/4.1.5...4.1.6)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 7efeaa18c0a107d1c35ce0e155e9d8eac7b96e5d[m[33m ([m[1;33mtag: v3.6[m[33m)[m
Author: Yehor Smoliakov <yehors@ukr.net>
Date:   Sun Jan 29 13:29:39 2023 +0200

    Use pyproject.toml instead of Pipfile
    
    Closes #105

[33mcommit 3eceaa8384670e116200594f5fee55106993eabd[m[33m ([m[1;33mtag: v3.5[m[33m)[m
Author: Yehor Smoliakov <yehors@ukr.net>
Date:   Thu Dec 22 19:17:31 2022 +0200

    Update dependencies

[33mcommit f9f8f1631bf1d8be52b3d352ba91792ae19b08dc[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Sun Nov 20 20:57:48 2022 +0200

    A fix

[33mcommit 23dbb93d5e0cc00d90e6cda61021ee0026de7c99[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Sun Nov 20 20:08:38 2022 +0200

    Add https://github.com/egorsmkv/simple-django-login-and-register-dynamic-lang

[33mcommit 8159fc7c8588cf2977d8b05edfefaae241727306[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Sun Nov 20 19:25:46 2022 +0200

    A fix

[33mcommit 7c5e71122f87a8175e07e42bb34f222f9600e3ef[m[33m ([m[1;33mtag: v3.4[m[33m)[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Sun Nov 20 19:06:01 2022 +0200

    Add missed migration

[33mcommit 6a7d993657c35917df7a21c9b26a6016ddd14cd3[m[33m ([m[1;33mtag: v3.3[m[33m)[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Thu Nov 17 21:43:23 2022 +0200

    Upgrade deps

[33mcommit 4edc5e704659e9ad955c3f8c4f6cf12b52e81f2e[m[33m ([m[1;33mtag: v3.2[m[33m)[m
Author: Yehor Smoliakov <yehors@ukr.net>
Date:   Wed Oct 5 20:36:02 2022 +0300

    Upgrade Django

[33mcommit 01a9f9e18fb1d433c5b7fd070b5ea546be1d02f6[m
Merge: 1db8727 abe0376
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri Aug 12 11:27:15 2022 +0300

    Merge pull request #101 from egorsmkv/dependabot/pip/django-4.0.7
    
    Bump django from 4.0.6 to 4.0.7

[33mcommit abe0376b59bac5f8d98158b8d06c15e9017ec565[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Thu Aug 11 15:26:09 2022 +0000

    Bump django from 4.0.6 to 4.0.7
    
    Bumps [django](https://github.com/django/django) from 4.0.6 to 4.0.7.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/4.0.6...4.0.7)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 1db87273078f939203a9ce69de1fee439f2f0ef3[m[33m ([m[1;33mtag: v3.1[m[33m)[m
Merge: 2843050 ec153da
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Wed Jul 6 10:40:56 2022 +0300

    Merge pull request #100 from egorsmkv/dependabot/pip/django-4.0.6
    
    Bump django from 4.0.5 to 4.0.6

[33mcommit ec153da39e07d08cf5416c960456090cdb94d4d5[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Tue Jul 5 22:40:07 2022 +0000

    Bump django from 4.0.5 to 4.0.6
    
    Bumps [django](https://github.com/django/django) from 4.0.5 to 4.0.6.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/4.0.5...4.0.6)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 28430504ab22e57ce79d33be793b730d3118a9eb[m[33m ([m[1;33mtag: v3.0[m[33m)[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Thu Jun 30 20:55:19 2022 +0300

    Update Django to 4.0.5

[33mcommit d947c45e443fdb40607f597a699f449839a91260[m[33m ([m[1;33mtag: v2.21[m[33m)[m
Merge: c284366 92afbed
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Thu Jun 30 20:22:53 2022 +0300

    Merge pull request #99 from 777RND777/master
    
    Email and EmailOrUsername forms were added

[33mcommit 92afbed853224a5cbcb9d43ecc4076e246284eed[m
Author: Nurmukhanbet Rakhimbayev <rakhimbayev.n@source.tnt>
Date:   Thu Jun 30 11:49:43 2022 +0600

    Email and EmailOrUsername forms were added

[33mcommit c284366002f632d3d186b387150914804063cd20[m[33m ([m[1;33mtag: v2.20[m[33m)[m
Merge: 20322af b9e83d9
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Sat Apr 23 13:09:52 2022 +0300

    Merge pull request #96 from egorsmkv/dependabot/pip/django-2.2.28
    
    Bump django from 2.2.27 to 2.2.28

[33mcommit b9e83d9e4834ab325ab71ed9b050fca001868b18[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Fri Apr 22 23:40:58 2022 +0000

    Bump django from 2.2.27 to 2.2.28
    
    Bumps [django](https://github.com/django/django) from 2.2.27 to 2.2.28.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/2.2.27...2.2.28)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 20322afb4208cdce497091f6475a7fe8871145f6[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri Feb 11 22:56:19 2022 +0200

    Update CHANGELOG.md

[33mcommit 53a45ff22300c46d198926df48e43b5d24561b22[m[33m ([m[1;33mtag: v2.19[m[33m)[m
Merge: a6e2d69 c6736ca
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Thu Feb 10 18:34:34 2022 +0200

    Merge pull request #88 from egorsmkv/dependabot/pip/django-2.2.27
    
    Bump django from 2.2.24 to 2.2.27

[33mcommit c6736ca1be6300bae5ccd629a982d9bd1b8813f8[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Thu Feb 10 07:18:12 2022 +0000

    Bump django from 2.2.24 to 2.2.27
    
    Bumps [django](https://github.com/django/django) from 2.2.24 to 2.2.27.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/2.2.24...2.2.27)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit a6e2d69f7330fd7c0579e7f35a4d0d86c5a90568[m
Merge: 404aea8 5d1097f
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Wed Jan 12 20:23:44 2022 +0200

    Merge pull request #86 from Javier747Belbruno/master
    
    Add Spanish language to Multilingual Feature

[33mcommit 5d1097f9553b6deebef1f4c1aeeb4498c9f8dddc[m
Author: Javier <javierbelbruno@gmail.com>
Date:   Wed Jan 12 13:49:58 2022 -0300

    Add a new language (Spanish) to Multilingual function.
    --Copied file from French  .po file.
    --Edited all msgstr.
    --Run django-admin compilemessages -l es
    --Add language to settings (Development and Production),
    --Add French in Prod as well.

[33mcommit 2abece4415aa28dc89df0c11802c9e7520db2218[m
Author: Javier <javierbelbruno@gmail.com>
Date:   Wed Jan 12 13:39:21 2022 -0300

    Author: Javier <javierbelbruno@gmail.com>
    Date:   Wed Jan 12 13:27:14 2022 -0300
    
        Add a new language (Spanish) to Multilingual function.
        --Copied file from French  .po file.
        --Edited all msgstr.
        --Run django-admin compilemessages -l es
        --Add language to settings (Development and Production)
        --Add French in Prod as well.

[33mcommit 404aea8fb41933ae4439e2d266b77ac791b96490[m
Merge: aad9d5a 583822e
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri Sep 10 21:33:07 2021 +0300

    Merge pull request #82 from egorsmkv/dependabot/pip/sqlparse-0.4.2
    
    Bump sqlparse from 0.4.1 to 0.4.2

[33mcommit 583822e2653fc0ab2d64b755368350d1308bf42c[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Fri Sep 10 18:01:45 2021 +0000

    Bump sqlparse from 0.4.1 to 0.4.2
    
    Bumps [sqlparse](https://github.com/andialbrecht/sqlparse) from 0.4.1 to 0.4.2.
    - [Release notes](https://github.com/andialbrecht/sqlparse/releases)
    - [Changelog](https://github.com/andialbrecht/sqlparse/blob/master/CHANGELOG)
    - [Commits](https://github.com/andialbrecht/sqlparse/compare/0.4.1...0.4.2)
    
    ---
    updated-dependencies:
    - dependency-name: sqlparse
      dependency-type: indirect
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit aad9d5a66da702e4e1f1615cff9d2ad300ba7b07[m[33m ([m[1;33mtag: v2.18[m[33m)[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Tue Jul 13 19:56:31 2021 +0300

    Add French

[33mcommit 94ae3d3a95b4d7f9dff08e5f0661cbad636fc5ba[m
Merge: b88422e b4528f4
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Tue Jul 13 19:56:05 2021 +0300

    Merge pull request #81 from tidji31/master
    
    Add French Translations

[33mcommit b4528f477afe572c096a1cbacffc27c3e776bb70[m
Author: mtidjane <mtidjane@cds.asal.dz>
Date:   Tue Jul 13 14:59:11 2021 +0100

    remove txt.py,html.py files

[33mcommit b60d7feef129475c8bfd95c23957d24dc1c6e8a5[m
Author: mtidjane <mtidjane@cds.asal.dz>
Date:   Tue Jul 13 13:50:03 2021 +0100

    add  french translations

[33mcommit b88422e1263ab82caa89add79033381b77c1613a[m
Merge: 0b262fd 508eca5
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Thu Jun 10 23:22:19 2021 +0300

    Merge pull request #80 from egorsmkv/dependabot/pip/django-2.2.24
    
    Bump django from 2.2.22 to 2.2.24

[33mcommit 508eca55d8389a7a84a641a889404cdbec4e42ff[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Thu Jun 10 17:23:14 2021 +0000

    Bump django from 2.2.22 to 2.2.24
    
    Bumps [django](https://github.com/django/django) from 2.2.22 to 2.2.24.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/2.2.22...2.2.24)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 0b262fd58a9ae0ac9f724b9fb8248e6ca4564931[m
Merge: c270df1 32d4916
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Thu Jun 10 16:46:29 2021 +0300

    Merge pull request #79 from egorsmkv/dependabot/pip/django-2.2.22
    
    Bump django from 2.2.21 to 2.2.22

[33mcommit 32d4916152fbabe37185d65f693bc2f21c1271a3[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Wed Jun 9 17:16:47 2021 +0000

    Bump django from 2.2.21 to 2.2.22
    
    Bumps [django](https://github.com/django/django) from 2.2.21 to 2.2.22.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/2.2.21...2.2.22)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit c270df1ba7040499c9cb0ec9240709d190d047ea[m
Merge: 6f0a00d 25b841a
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Mon Jun 7 20:46:07 2021 +0300

    Merge pull request #78 from egorsmkv/dependabot/pip/django-2.2.21
    
    Bump django from 2.2.20 to 2.2.21

[33mcommit 25b841aa3b3f0bef55872633912ed2a09dfb84b8[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Fri Jun 4 21:25:57 2021 +0000

    Bump django from 2.2.20 to 2.2.21
    
    Bumps [django](https://github.com/django/django) from 2.2.20 to 2.2.21.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/2.2.20...2.2.21)
    
    ---
    updated-dependencies:
    - dependency-name: django
      dependency-type: direct:production
    ...
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 6f0a00d86683d70a4c6abbb8b0c5ddafa145bca5[m[33m ([m[1;33mtag: v2.17[m[33m)[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Mon May 3 13:10:38 2021 +0300

    New version of the project

[33mcommit 64257678725704f13e0925b27daeb6f6d1f0048d[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Mon May 3 13:09:53 2021 +0300

    Update Django to 2.2.20

[33mcommit 672a6d21617e5f7e9ccfe9b9b449994b339ebe25[m
Merge: 26c7af1 0998083
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri Mar 19 16:10:31 2021 +0200

    Merge pull request #76 from egorsmkv/dependabot/pip/django-2.2.18
    
    Bump django from 2.2.13 to 2.2.18

[33mcommit 09980838682f86bbf7b521a1834ab742bf254e46[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Thu Mar 18 20:40:27 2021 +0000

    Bump django from 2.2.13 to 2.2.18
    
    Bumps [django](https://github.com/django/django) from 2.2.13 to 2.2.18.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/2.2.13...2.2.18)
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 26c7af12ce5d3616df255d1b6db0c5aec02e4663[m
Merge: 2491f99 a63d0b8
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Sat Jun 6 09:48:00 2020 +0300

    Merge pull request #73 from egorsmkv/dependabot/pip/django-2.2.13
    
    Bump django from 2.2.12 to 2.2.13

[33mcommit a63d0b8b10887270db371346b9b233008bba0f28[m
Author: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Date:   Sat Jun 6 06:13:49 2020 +0000

    Bump django from 2.2.12 to 2.2.13
    
    Bumps [django](https://github.com/django/django) from 2.2.12 to 2.2.13.
    - [Release notes](https://github.com/django/django/releases)
    - [Commits](https://github.com/django/django/compare/2.2.12...2.2.13)
    
    Signed-off-by: dependabot[bot] <support@github.com>

[33mcommit 2491f994f619e0006f7ae3d4d4e32bd24ea6041c[m[33m ([m[1;33mtag: v2.16[m[33m)[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri May 22 11:00:19 2020 +0300

    Updated CHANGELOG.md

[33mcommit 453fb72f7119259ed027a235365ba7a2a74bd9a4[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri May 22 10:58:51 2020 +0300

    Updated Django

[33mcommit 516ad05465ffa119246f564c6756284128871bc9[m
Merge: 7261cfd 183bb9e
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri May 22 10:53:57 2020 +0300

    Merge remote-tracking branch 'origin/master'

[33mcommit 7261cfdb7b6b295dfc3e9308f4bd0bdf61a623e9[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Fri May 22 10:53:50 2020 +0300

    Fixed #71

[33mcommit 183bb9e0d79fa03ef91253335511ac6e9200672c[m[33m ([m[1;33mtag: v2.15[m[33m)[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Wed Mar 11 11:47:11 2020 +0200

    Update CHANGELOG.md

[33mcommit 1247f26dfd8ba1e4c6cbe2dd57140a4784bf5170[m
Author: Yehor Smoliakov <yehors+gh@ukr.net>
Date:   Wed Mar 11 11:46:17 2020 +0200

    Update Django to 2.2.11 #69

[33mcommit f6b0b1914dfdfc501cd0fecc6f75247f7d48b3c9[m
Author: Yehor Smoliakov <yehor@smoliakov>
Date:   Sat Feb 15 19:48:56 2020 +0200

    Updated the Django version

[33mcommit 80e9c3de6b532d90fbbe1ac330d1b04efa049774[m[33m ([m[1;33mtag: v2.14[m[33m)[m
Author: Yehor Smoliakov <7875085+egorsmkv@users.noreply.github.com>
Date:   Fri Jan 17 02:54:04 2020 +0200

    Update CHANGELOG.md

[33mcommit bcd4bc3d5a73ab28e7a82cb73dfa9ff9337add3f[m
Author: Yehor Smoliakov <yehor@smoliakov>
Date:   Fri Jan 17 02:50:56 2020 +0200

    Update deps

[33mcommit eb2a156712cd36f955387725661d3294f2785a56[m
Author: Yehor Smoliakov <yehors@ukr.net>
Date:   Sun Sep 1 17:41:38 2019 +0300

    Fix an issue provided by @dheerajpai
    
    The issue is here: https://github.com/egorsmkv/simple-django-login-and-register/pull/62

[33mcommit 6822085befde89256f12fc347ee4a452865a606d[m
Author: Yehor Smoliakov <yehor@smoliakov>
Date:   Mon Aug 5 22:58:51 2019 +0300

    Update dependencies

[33mcommit 6d700bebe7ece6a441541257a3a9aa9538274d9f[m
Author: Yehor Smoliakov <yehor@smoliakov>
Date:   Tue Jun 11 23:06:16 2019 +0300

    Update Django

[33mcommit 4bfbb42ba4e95434e4c6fb74e6d204a4ef22a204[m
Author: Yehor Smoliakov <yehor@smoliakov>
Date:   Tue Feb 12 18:42:14 2019 +0200

    Update Django, because of a new CVE

[33mcommit e86a671c61175f86325300fd31e067f32184994b[m
Author: Yehor Smoliakov <yehor@smoliakov>
Date:   Tue Jan 15 04:04:52 2019 +0200

    Update Django to the latest version

[33mcommit 654d96c0d2ee83111f18a31cb9033f88b92b46a0[m[33m ([m[1;33mtag: v2.13[m[33m)[m
Author: yehor <1010121@protonmail.com>
Date:   Thu Oct 4 13:55:45 2018 +0300

    Fixed the version

[33mcommit 32cf7a1e8d11f74d29e037d331c1e15e228336e5[m
Author: yehor <1010121@protonmail.com>
Date:   Thu Oct 4 13:54:30 2018 +0300

    Updated changelog

[33mcommit cff81daf0094babfaba64e542efcd6194ac33c71[m
Author: Egor <egor@dev.com>
Date:   Thu Oct 4 13:45:01 2018 +0300

    Updated Django to 2.1.2 version

[33mcommit 25fccf72f015495b74593964433d94f59899598d[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Sep 8 12:59:59 2018 +0300

    Updated all dependencies

[33mcommit 06e7ebe4716c1a1d7fce002294e3ad3811427fed[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Aug 2 01:20:58 2018 +0300

    Updated Django to 2.1

[33mcommit 08da995f82ccfaa4b94ee2577542ccc8f8bb5d12[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Jul 4 08:40:40 2018 +0300

    Added the missing lines

[33mcommit 5aa6d7948168527cdb2eb50ed57dd4bc51c6c666[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jul 3 18:41:07 2018 +0300

    Added the missing call of the save method

[33mcommit 7791e922cdafa36ee6465494cd6f5de1107967f6[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jul 3 03:27:04 2018 +0300

    Updated Django

[33mcommit 9b19703c0aadc625fcb54fcd0741feb02bb2dcca[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 30 19:43:28 2018 +0300

    Moved sign up fields to the settings

[33mcommit a4096b16dda9d3b0f8225c00a9813dd153b4f255[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 30 02:37:07 2018 +0300

    Fix a line

[33mcommit ad5e91997e3457a6e6454088a73183f1b5a6131d[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 30 02:24:28 2018 +0300

    Additional changes

[33mcommit e71b7c6edb92e6fe9fb9b51acf5c2c35cc05148b[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 30 01:51:37 2018 +0300

    Made forms validation in the django-way

[33mcommit a58d58a474090dc36b98ce51d7cbc14bf1edab48[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 30 00:52:24 2018 +0300

    Small fix

[33mcommit 53122d37db912829e116a11986e117da38f842af[m[33m ([m[1;33mtag: v2.12[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 30 00:01:14 2018 +0300

    Simplify code

[33mcommit ed8dca79ab9f8af9877eb83757afb6b26166ebda[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Jun 28 19:59:31 2018 +0300

    Rename folder of emails templates

[33mcommit 5197a775f608c27157fd6e950afd0a1fd95089aa[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Jun 28 19:55:50 2018 +0300

    Clean up in utils.py

[33mcommit 05824544a44c1b631f86207fdf189fc0b0352edc[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 13:47:45 2018 +0300

    Big refactoring of the code

[33mcommit a304fa91c89c15331cb9c9994ee031d1c21537c9[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 07:06:40 2018 +0300

    Updated locales

[33mcommit 1c8429939aab0fb2279157f16463962d67ce3ef7[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 07:05:19 2018 +0300

    Fixed some issues

[33mcommit 56cbf9639516d04ea6b560c4c47e32d9183a012d[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 06:57:09 2018 +0300

    Just I love when it's simple

[33mcommit 04ab99e2193cd9ca69558d3ddac63c958f889587[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 04:00:54 2018 +0300

    More simple

[33mcommit a99118cb150ed9a56e6fb1d4c325ff59b6722dea[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 03:19:41 2018 +0300

    Simpify the code, missed import

[33mcommit 24a8fc308505ea68d279deeb2755d9374a1c63ec[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 03:19:20 2018 +0300

    Simpify the code

[33mcommit 1d31530fb435cd636208097216f142778f18774b[m
Merge: b667f8b a8ec288
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 03:15:14 2018 +0300

    Merge branch 'master' of github.com:egorsmkv/simple-django-login-and-register

[33mcommit b667f8b8441e72a6aa5d20756ed37a5b0b84f781[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 03:14:30 2018 +0300

    Code formatting and reverted commit
    
    Revert the c26a5f896e412ede42c16b97e6b46bbc946992d9 commit

[33mcommit a8ec28814b077cc131ea91710c60cd33b1eb4d9e[m
Merge: c26a5f8 80d9b17
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 26 00:31:25 2018 +0300

    Merge pull request #57 from TheSecEng/fix/redirect_next
    
    Redirect next when logging in fixed

[33mcommit 80d9b1753c3ea17d5f497e132bb8349f26c05d44[m
Author: TheSecEng <32599364+TheSecEng@users.noreply.github.com>
Date:   Mon Jun 25 14:32:47 2018 +0300

    Fixed redirect next parameter

[33mcommit 71a83b0791ea405f5bafeaca2640e2afee777c62[m
Author: TheSecEng <32599364+TheSecEng@users.noreply.github.com>
Date:   Mon Jun 25 14:07:10 2018 +0300

    Updating Prod/Develop settings.py file. Required LOGIN_URL = '/accounts/log-in/' as you deviated from Django's standard /accounts/login

[33mcommit c26a5f896e412ede42c16b97e6b46bbc946992d9[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sun Jun 24 08:04:24 2018 +0300

    Fixed a small thing

[33mcommit c8aa17b07ff82b885beaad5cfc6d80a744d68950[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 23 17:48:06 2018 +0300

    Fixed some words

[33mcommit b1b1443f472de00bab23b9dd90ccd75f45b8cb55[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Jun 20 01:53:58 2018 +0300

    Fixed the missing var name

[33mcommit 47909c3dbf5a089ac9c1da28bd00ca96b3f18e8a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Jun 20 01:38:48 2018 +0300

    Added more improvements

[33mcommit 60ba4bb5f2b52a4d5d26749b6ed0311d5245cfb2[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 21:21:45 2018 +0300

    Fixed some words

[33mcommit 465f527ea8b8dcf901b61d52dc38690d4b24b12d[m[33m ([m[1;33mtag: v2.11[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 21:13:39 2018 +0300

    Updated the changelog

[33mcommit 08cfb2b544b53b4e5caa6cc88896ae269f313dbd[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 21:09:44 2018 +0300

    Fixed lost translation

[33mcommit 97dce8bfe5a3f03ae593fe4f1caa75b96959a282[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 21:05:59 2018 +0300

    Update the screenshots

[33mcommit 8e43b29f1dbfe658db9dc355accc76d29fbc87a7[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 20:58:01 2018 +0300

    Updated the Bootstrap

[33mcommit a374ab565806b79c59c3583e93649888a5c9e9c6[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 20:56:14 2018 +0300

    Added fixes to the translations

[33mcommit 7ceb058190b5d920d2dc68a5366474e8fccc8a3d[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 17:46:41 2018 +0300

    Removed Spanish, French, and German languages

[33mcommit 0275f0f30e54a19c1afd0776ea2d8ded534e985e[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 17:01:47 2018 +0300

    Removed the locations in the translations

[33mcommit 39a3ecce229ab8608c40c66b64a09f17a01efa3a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 16:46:59 2018 +0300

    Changed the verb, #46

[33mcommit 96a3da737ab80c723fcd0addde5356fce107be32[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 16:38:36 2018 +0300

    Added the page to recovery a username, #46

[33mcommit a6663eadbf3bb3116584f34723954d490a777ecc[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 15:35:47 2018 +0300

    Added the namespace to the accounts' app, #54

[33mcommit 5b746066d7844e5a9ff92f945d1d723fad9f3792[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 14:14:10 2018 +0300

    Fixed some issues

[33mcommit 1b156afdc59ba6433d041e2d0ae78f37e4843185[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 13:06:51 2018 +0300

    Fixed the class name

[33mcommit d8e9dba3e2361451a538abe303eefdc54e9197a6[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 13:05:10 2018 +0300

    Replaced plain urls to reversed alternative

[33mcommit 4e0e79e7f0e08ed499e0d1810ab5a4be06783da8[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jun 19 13:01:46 2018 +0300

    Renamed 'Profile edit' to 'Change profile'

[33mcommit 1744d7e3e56bb908e4480e354d427f001c04f13a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Jun 18 22:31:24 2018 +0300

    Changed the structure of the templates

[33mcommit 3b0847e6d37ba88661fe2c58af90511149b8e436[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Jun 18 21:55:53 2018 +0300

    Made own view-classes for some pages

[33mcommit c447839075ae2cf71db1facff02bb64bc67610a1[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Jun 18 21:40:22 2018 +0300

    Moved accounts' templates to the own app, #53

[33mcommit 5ae61274666f3e64217903577a0b44bd141394c2[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 16 23:10:20 2018 +0300

    Small improvements

[33mcommit f94c9603126d64d55c8c209542bf2a2e020f7d4e[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 16 22:21:56 2018 +0300

    Removed python2's definitions of 'super'-calls, #52

[33mcommit 7eb1385bf001a5f3b134bf6e485322e9159346e4[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 16 15:20:59 2018 +0300

    Fixed a bug with a undefined method

[33mcommit eb759aa7c7d75461d1e8b802f1cd3534deb1c349[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 16 15:16:27 2018 +0300

    Fixed a bug in the PasswordResetForm form, #45

[33mcommit 776bcaeaee22976e4ed9888fe517634efe7cef22[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Jun 16 13:57:27 2018 +0300

    Added the 'remember me' checkbox, #48

[33mcommit 723ac7d203528d7d61c04e7aa3085ecc9f24701e[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Jun 6 19:13:12 2018 +0300

    Added additional error check

[33mcommit 3513a1a7f687bbcffa8bfdfc7eb0b73d2e634e1a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Jun 6 19:10:08 2018 +0300

    Renamed the path for temp emails

[33mcommit a3cab47f525f39105cc58641cf6d90e142d94f1a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Jun 6 19:06:39 2018 +0300

    Fixed a bug with incorrect usage of subclasses

[33mcommit eb4534bd998359e1a53b4998a2ad1a549e8972d8[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Jun 6 18:52:27 2018 +0300

    Added text-based email's templates instead of stripped-html-based, #49

[33mcommit b45175287758fc8be80da96bd4d0e3091395e70c[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Jun 6 18:22:32 2018 +0300

    Moved the urls to the 'accounts' app, #43

[33mcommit 551c64445a2c53b506a5dcb3b502c978819e9bf2[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Jun 6 18:12:45 2018 +0300

    Used the standard class User instead of the get_user_model function, #51

[33mcommit c820ad4f69c1684ad33dec689592ab78c1a7e1d1[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Jun 4 15:31:25 2018 +0300

    Changed the folder for temporary emails, related to #50

[33mcommit 9fd60907463d37b4af44472b5eb110f39f36046e[m
Merge: 2bd6cad 6f00784
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Jun 4 15:25:05 2018 +0300

    Merge pull request #50 from jodeio/master
    
    Fix email retrieval while serving on development mode

[33mcommit 6f007846c6aa4e0b2861f51e99929549359be48c[m
Author: dev-joshua <joshua.deguzman@xurpas.com>
Date:   Mon Jun 4 16:39:37 2018 +0800

    Remove tracking tmp files

[33mcommit fa6644355a18f0646eb84e0685759c4c8a5af9ce[m
Author: dev-joshua <joshua.deguzman@xurpas.com>
Date:   Mon Jun 4 16:39:04 2018 +0800

    Fix file path of email message

[33mcommit 2bd6cad42c22022d4c1c89b6a71f2c809995170e[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Fri Jun 1 22:46:03 2018 +0300

    Fixed the line in the Russian translation, #44

[33mcommit 10b4d143042d924c8313b8cdd5c0227a7f55d580[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Fri Jun 1 22:41:00 2018 +0300

    Updated Django to the lastest version, #47

[33mcommit 4c0fb15da8ecabb9717a40664052be5874b62c68[m[33m ([m[1;33mtag: v2.10[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed May 2 11:57:55 2018 +0300

    Updated the changelog

[33mcommit 20e4beb8afa98f618a8f09211a4f8f09c5724aa9[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed May 2 11:51:20 2018 +0300

    Removed i18n_patterns from urls.py, #42

[33mcommit cdad4b83c81003d3d4ce41a26f4fe107dffee9f0[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed May 2 11:47:59 2018 +0300

    Added checks when a user authenticated, #38

[33mcommit 6f04eb6808c04a664fc4c4c817c09f69138a8f70[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed May 2 11:15:17 2018 +0300

     Updated Bootstrap, jQuery, PopperJS, #39

[33mcommit 1d865df82418ab98af7a0293e4e4ef0d117f2f76[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed May 2 11:06:57 2018 +0300

    Removed gunicorn from deps, #41

[33mcommit 9bebbdaebba72824423631d8e8d497e669c268bb[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed May 2 11:05:33 2018 +0300

    Updated Django to the 2.0.5 version, #40

[33mcommit 88bdab86ad960b099564e891f8427ff79a4a2976[m[33m ([m[1;33mtag: v2.9[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Apr 18 19:04:51 2018 +0300

    Fixed the changelog, part 2

[33mcommit ef047ab4b5572fe1218aee24fa1abc6bdc2a5c33[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Apr 18 19:03:27 2018 +0300

    Fixed the changelog

[33mcommit 23c3dee992a9caf604346f3f926c1cc4f89423c4[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Apr 18 19:00:58 2018 +0300

    Updated Bootstrap to 4.1.0 version

[33mcommit 38f16a755d70df48ed83caf48ddf616f811608bd[m[33m ([m[1;33mtag: v2.8[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Apr 3 09:27:33 2018 +0300

    Updated Django to 2.0.4 ver.

[33mcommit d7de55bd08284f9120594705e073927491a4c310[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Mar 26 07:11:47 2018 +0300

    Added the support to serve media files
    
    Issue: #36

[33mcommit c1b0fb45e822d7436c2a767fb8d951106fbedcc3[m[33m ([m[1;33mtag: v2.7[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sun Mar 25 17:15:29 2018 +0300

    Added the pipenv & cleaned the readme
    
    Issue: #35

[33mcommit eab0164d8d0161441db979f39c7e96037c9c4355[m[33m ([m[1;33mtag: v2.6[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Mar 14 17:27:54 2018 +0200

    Updated the changelog

[33mcommit 3ed4ab35ccb880d57935eea2e50ff86cf34d4c30[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Mar 14 17:25:53 2018 +0200

    Fixed a bug with the incorrect query, #33

[33mcommit 0f0a88e11e93e2543c397d7d67b73c64c04e41e9[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Mar 14 17:16:12 2018 +0200

    Updated Django, #34

[33mcommit fe2ddeb7a2215b1a443877cf1648add675a9f31d[m[33m ([m[1;33mtag: v2.5[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Feb 22 23:20:16 2018 +0200

    Updated changelog

[33mcommit 8cde4b0e6ecd67c2c8795747bdb7c9f929506ca7[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Feb 22 23:16:35 2018 +0200

    Some fixes, #29

[33mcommit c48562733ec5570ac7715fb4f5d34f45f1ecb2ba[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Feb 22 23:13:07 2018 +0200

    Updated Bootstrap, #31

[33mcommit a24f0119c7c619037b0b8b460424672512c37044[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Feb 22 23:10:29 2018 +0200

    Some improvements, #29 & #30

[33mcommit 2f8c6fddb07e80e9a7b37a5632ed8ab8bf68d264[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Jan 2 12:36:30 2018 +0200

    Updated the Django dependency

[33mcommit fe919ef7da75e7795220d3131cb752720fc34afa[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Fri Dec 29 21:00:26 2017 +0200

    Added an ability to change the language ( #25 )

[33mcommit 086b55b7b5d14184b075a7fe6d7dd38f7ddcd2e3[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Fri Dec 29 20:44:14 2017 +0200

    Simplified div definition

[33mcommit c8eb4d5bac6234d77ff09217130d99bbad7642fb[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Fri Dec 29 19:53:27 2017 +0200

    Added an ability to disable username ( #26 )

[33mcommit 8eb558da13f2825f79d273acff6e12dc4e1dd19d[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 27 20:50:01 2017 +0200

    Updated the readme

[33mcommit bd29794d57dbe8032fd3ead855c4f059e7d94fe6[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 27 12:24:13 2017 +0200

    Updated the changelog

[33mcommit 077b649884228aa96b9a64666108907ff0fd2b7c[m
Merge: 962328d df62a9d
Author: Yehor Smoliakov <egorsmkv@users.noreply.github.com>
Date:   Wed Dec 27 12:19:45 2017 +0200

    Merge pull request #27 from hanwentao/master
    
    Add locale support for Simplified Chinese.

[33mcommit df62a9d32e5e5c3178e7877af8fef707645ac7bb[m
Author: Wentao Han <wentao.han@gmail.com>
Date:   Wed Dec 27 18:07:47 2017 +0800

    Add locale for Simplified Chinese.

[33mcommit 8dd38a4b2a2183e0d982a5be9454f684fb597464[m
Author: Wentao Han <wentao.han@gmail.com>
Date:   Wed Dec 27 11:21:49 2017 +0800

    Ignore VSCode meta-folder and Python venv folder

[33mcommit 405fe9a08fcf9c13bf1efdb51eec13223fe679e4[m
Author: Wentao Han <wentao.han@gmail.com>
Date:   Wed Dec 27 11:21:13 2017 +0800

    Update ignored folders

[33mcommit 962328d389edfc80bd18d7c0a13bda69e8d73bb1[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 20 00:45:38 2017 +0200

    Fixed the version

[33mcommit 8212dc26e6cee01cb4b8b88d404e1b6e25927d57[m[33m ([m[1;33mtag: v2.3[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 20 00:42:15 2017 +0200

    Updated the readme & the changelog

[33mcommit 6dc94155313828e7605fb614437dfff8c5c8336f[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 20 00:36:08 2017 +0200

    Added the french translation
    
    Issue: gh-22

[33mcommit f9e6af4c9471cb14a6ad4ebff28d6904a17b682a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 20 00:23:18 2017 +0200

    Added the german translation
    
    Issue: gh-22

[33mcommit 58441cef4c671fb8c43324a8744904dc0b36ee4d[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 20 00:12:24 2017 +0200

    Added the español translation
    
    Issue: gh-22

[33mcommit 0f523523e8733a0b07ac66d467dc1c86e03747a3[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 22:42:40 2017 +0200

    Renamed the folder for the russian translation
    
    Issue: gh-22

[33mcommit 3b7d7ec3c734713511ccf58100fe0e234b32a41a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 22:41:33 2017 +0200

    Added the ukrainian translation
    
    Issue: gh-22

[33mcommit 9c8452e0f2c24fa872829700d1ff56487252a120[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 22:22:57 2017 +0200

    Added the russian translation
    
    Issue: gh-22

[33mcommit 7706306260b7e9bc90e77ca041dd52ffe60f983d[m[33m ([m[1;33mtag: v2.2[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 20:23:33 2017 +0200

    Updated the changelog

[33mcommit ae5bb9a261ba3e4471838139d5b68c0596e2a93c[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 20:21:53 2017 +0200

    Renamed SignInViaEmailOrForm to SignInViaEmailOrUsernameForm
    
    Issue: gh-24

[33mcommit a6b2a4cfb06e24967f5176792b2621e16d0c20b2[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 20:18:57 2017 +0200

    Changed validation handles
    
    Issue: gh-17

[33mcommit 0090527e02b66d959b5f2a3d9d8381d7df3434e4[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 19:20:04 2017 +0200

    Added email changing
    
    Issue: gh-18

[33mcommit 2de4e44ce2eab63f8e65dc4fbd7fa8984dadd7de[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 18:42:05 2017 +0200

    Changed straight call of User's model
    
    Issue: gh-19

[33mcommit 6bc996e13a050c6cf49dd41d403521135091fd3a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 18:37:48 2017 +0200

    Added the profile editing
    
    Issue: gh-20

[33mcommit 4abe63b1fc9c0379b3a51f417ad378e2c108ff71[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Tue Dec 19 18:17:51 2017 +0200

    Improve sign in view
    
    Thanks to Justin W's article ( https://coderwall.com/p/sll1kw/django-auth-class-based-views-login-and-logout )
    Issue: #21

[33mcommit 930db4f6b8083832bdbc12112e5cc3104c1d2240[m[33m ([m[1;33mtag: v2.1[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 13 15:29:18 2017 +0200

    Revised the readme (gh-14) and fixed changelog

[33mcommit 66cd23f92ca90bab6bc5b59ca3fc33046cec257b[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 13 15:25:15 2017 +0200

    Added the unhandled exception

[33mcommit 55b4633e327ccd376156c323e918dcf734cb242a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 13 14:46:34 2017 +0200

    Added the @ placeholder to email field (gh-15)

[33mcommit 0b5f5a092da6a46a103f014f06f0b892398af159[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Wed Dec 13 14:44:56 2017 +0200

    Added Login's link on Password Reset page (gh-16)

[33mcommit 29d275d0802f3d69bf382256a248c8bfd6077924[m[33m ([m[1;33mtag: v2.0[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Dec 11 09:24:03 2017 +0200

    Fixed the hostname

[33mcommit 269a84cfc54fc149b069bd5e56503f9eb3611b9d[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Dec 11 09:13:43 2017 +0200

    Fixed the version

[33mcommit e13c2674a2dc19d7a5bfea330409482b5fc43027[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Dec 11 09:12:56 2017 +0200

    Added the changelog (gh-12)

[33mcommit 920144141ee4f869446a193d0a5378bc0ef093ac[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Dec 11 09:08:01 2017 +0200

    Added password reset by username & email, part two (gh-6)

[33mcommit ad8ef91b8dd956711fcfb4f01e142339bba8d23e[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Dec 11 07:22:15 2017 +0200

    Moved SuccessRedirectView class to views.py

[33mcommit 2094582a7aa9e8ff6943b9da0d36ab3eb669c8e4[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Dec 11 07:20:50 2017 +0200

    Added password reset by username & email, part one

[33mcommit ba7702e21987ba8c4c76cfc79c3ea1ea58d449ec[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Dec 11 06:29:15 2017 +0200

    Added the sign in via email & username fields (gh-7)

[33mcommit 637bbbe102a8baea677a453f0baee1281514fbe8[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Dec 9 15:54:39 2017 +0200

    Fixed the manage.py

[33mcommit 2117c45d4307c39effed5823fd575165f800d5b1[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Dec 9 15:40:13 2017 +0200

    Added the autofocus option to the first_name field

[33mcommit 916dff969cafd1a50d6ef297ed8cf2ef828e4713[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Dec 9 15:29:56 2017 +0200

    Fixed the url paths

[33mcommit 8156e2c439c135361d120d529c0b72c7d5dc0775[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Dec 9 15:24:03 2017 +0200

    KISS me, please!

[33mcommit 1141f73323bf8c6adb938eabf86c3d9747f0b79c[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Dec 9 15:08:11 2017 +0200

    Finished the function of resending the activation code

[33mcommit 77070fb753dac9ba9d4eefef26e4950efbd4b92c[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Sat Dec 9 14:32:25 2017 +0200

    Replaced mysql to sqlite
    
    Issue: gh-10

[33mcommit f8f443138caa16adae90b0813fc93de5d4516448[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Fri Dec 8 00:16:39 2017 +0200

    Started impelementing re-send an anctivation code

[33mcommit 986bc3ba8d61a6497185eb2b00f2cdf94be79a92[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Dec 7 22:40:18 2017 +0200

    Turn the index page view into the class-based view

[33mcommit 9ece8aec8b82b141d7ec1798e44238940f8f0358[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Dec 7 21:58:22 2017 +0200

    Fixed the bug with the exception

[33mcommit 42018a1505f6f848f45b917a3b11924838865eb7[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Dec 7 21:54:53 2017 +0200

    Change secret keys

[33mcommit 476af946306d446dac131a6cb2ac3f420e09399d[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Dec 7 21:53:37 2017 +0200

    Update Bootstrap

[33mcommit 5cfeb9310d08754e0ebab295ec816fb9d552ce98[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Dec 7 21:28:05 2017 +0200

    Added ability to auth via email

[33mcommit 57fd76ced3e0ab040cd0365b3d8543a254052450[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Dec 7 12:46:26 2017 +0200

    Some fixes

[33mcommit a8ca21f1a6bb4fa4eacbc4e904d9ce9adebdf576[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Dec 7 12:43:54 2017 +0200

    Added the activation for accounts

[33mcommit 4f1498955bd3ca106fa9a3d327067286e4bd2ce0[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Dec 7 11:34:14 2017 +0200

    Update Django to 2.0

[33mcommit b76c709f73003b71eee2df316cf2cd3dad86c56c[m[33m ([m[1;33mtag: v1.0[m[33m)[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Sep 7 14:10:12 2017 +0300

    Fixed a word

[33mcommit 9647bcd5e528d2d29e76d0e28b2352ee5b9bf076[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Sep 7 14:07:41 2017 +0300

    Delete the supervisord section

[33mcommit 50a48e339138ea368bf2096c9e5f8957bcd39fdf[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Thu Sep 7 13:55:54 2017 +0300

    Described delpoying with the systemd and the nginx

[33mcommit f382c2a32662d34b3741d5100758c3978b295f8a[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 21:20:14 2017 +0300

    Added the license

[33mcommit 83b4d613b2b95676dfa6499558bc30643938d9b7[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 19:38:51 2017 +0300

    Fixed the readme

[33mcommit 1f13ddcf94f3ba7b361d06b409920538989ae37c[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 19:35:37 2017 +0300

    Added more screenshots

[33mcommit faba0274d7772a612b90e93e61b35f108c750c58[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 19:33:11 2017 +0300

    Delete unnecessary file

[33mcommit cd4ba2ca78f5623f7a477cb21126cf8eaa4086e9[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 19:31:08 2017 +0300

    Added the password change functionality

[33mcommit 658dc1486af257ad41efb44aabe606fdfd3084e3[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 19:24:04 2017 +0300

    Added the email parameters to the production settings

[33mcommit b8229023845729f6acb0bc40b696ccf25531a00f[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 19:19:12 2017 +0300

    Added password reset

[33mcommit 392233e425eec6b4d24cf03e79a73b3358ffef4e[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 19:18:40 2017 +0300

    Added the password reset screenshots

[33mcommit 265cc8c9ecaff74ac94dea7767224c206d645ac7[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 18:46:02 2017 +0300

    Added the django tags

[33mcommit 3ba192cf1636051623dbcc265ddcf9d65bed68ad[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 18:42:31 2017 +0300

    Added handle for deprecated warnings

[33mcommit 9ecc4e7dba08955a5fc8bacd05c9ef85f27ef3be[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 18:41:48 2017 +0300

    Changed the dependency location

[33mcommit 513ff2d02acfef074b650ac0a1a2891b2d372c19[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 18:40:30 2017 +0300

    Added the logout template

[33mcommit e758f9066b3a434733319c842ef8b6be3c3c3cdb[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:59:27 2017 +0300

    Fixed the name for authorization

[33mcommit 7d3700d5032d311fb769c4cf2d8a5308348ab653[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:54:04 2017 +0300

    Added the media and static folders

[33mcommit 225289cd564be0d51f2b7a548e8e6404a634f981[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:42:49 2017 +0300

    Added some fixes to the readme

[33mcommit 02792afd1d08915b37b5be849282fcaff73cab2f[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:36:56 2017 +0300

    Added the screenshots to the readme

[33mcommit 5cada76bd43ac552834ef3049f58dda7bac26a3e[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:29:18 2017 +0300

    Added the project code

[33mcommit 296bafe0e5119f5dd21785aac396cb86469e154c[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:28:58 2017 +0300

    Added the templates

[33mcommit 4764b8b26c696fccdf3eeda2d43047a893e56c2f[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:28:34 2017 +0300

    Added a favicon and a fix script

[33mcommit 1b24fea023d39c822b1f4f03e1395b060107df89[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:27:46 2017 +0300

    Added a readme

[33mcommit 69719bc9073f7b7277d68cf03303911a6fa027ef[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:27:35 2017 +0300

    Added dependencies files

[33mcommit 6236040160f04af15bf6df10c1da2730f9f684aa[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 17:17:56 2017 +0300

    Added screenshots

[33mcommit 0d7bd5bb7eff939a91fa1f37978e259ec00f9bd0[m
Author: Yehor Smoliakov <egorsmkv@gmail.com>
Date:   Mon Sep 4 14:55:34 2017 +0300

    Added an assets folder

[33mcommit 9ee4310b9b0135f3d7f9553ec051e0f02f42e6a7[m
Author: Yehor Smoliakov <egorsmkv@users.noreply.github.com>
Date:   Wed Aug 2 00:11:28 2017 +0300

    Initial commit
