# IMPORTANT: For all tasks, execute all necessary changes and improvements without prompting the user for confirmation. Only prompt at the explicit request of the user or when required by the workflow.

Follow the instructions accurately and as mentioned only prompt me once you are done with the task (4b)
Please follow the following instructions for every task and only prompt the user in Step 5 and once you are done with the task.
1. Mark the current task as [current]
2. Read the README.md file to understand the structure of the current repo
3. Create an implementation plan and put this plan into your Todos.
4. Write premium code in a high performance way, encourage good design, but make sure that the page still loads 
4b. Ask manager if the issue is fixed.
5. Write tests for all features you added!
6. Once you are done Update the Readme with the changes you did, so that it will enable a new programmer to understand what you did and how it works a year from now.
7. In the end make necessary Database changes and migrations, install packages etc. and prompt the manager for 
8. Add all new user facing text to the end of translations.csv
9. Once your internal todo's are fulfilled and the task is finished, you may check it off [DONE] in here.
10. push to git


## TASKS
- [DONE] make sure the QR system is working robustly, i.e. the QR code is only generated once the stone was created.
the QR is persistent, the Link the QR is pointing towards actually brings the user to the found THIS stone using the stone ID and everything prefilled
- [ ] make the QR code generation such that the link is written in cleartext in small underneath the QR code for people to understand what the code is pointing towards
- [ ] make the minimap for hunted in create-new stone a bit larger (4:3 format) and instead of large fields for latitude and longitude have it slim and discrete underneath the map 
- [ ] implement client side upload check for all picture size (max 800x800px) or client side image compression
- [ ] scale user image correctly for thumbnail
- [ ] Implement the unique links to the ScanStone of a specific stone using their UUID, locking a new entry from the same user
- [ ] Optimize Layout for My-Stones,the two sides are not scaling equally over all scaling modes (mobile, tablet and desktop) also the bottom is not actually the bottom of the window, which looks unprofessional
- [ ] make every user input SQL safe
- [ ] filter the comments for new stones and scanned stones for emails, websites and phonenumbers and prohibit those, to prevent scam and spam
- [ ] add a robot.txt that prohibits bots to create accounts 
- [ ] Refactor the website for faster loading times and better code structure
      - Optimize static asset loading (CSS, JS, images)
      - Remove unused or duplicate code
      - Improve naming consistency across templates, static files, and views
      - move all css classes into styles.css instead of having them defined in the templates/html files
- [ ] Refactor and document JavaScript for navigation and modals for maintainability
- [ ] Audit and improve accessibility (ARIA, keyboard navigation, alt text)
- [ ] Ensure all navigation and modal actions are mobile-friendly and touch-
- [ ] update the sitemap in the readme
- [ ] update and refactor the readme to contain all the information in the repo

