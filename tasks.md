# IMPORTANT: For all tasks, execute all necessary changes and improvements without prompting the user for confirmation. Only prompt at the explicit request of the user or when required by the workflow.

Follow the instructions accurately and as mentioned only prompt me in step 5. or once you are done with the task.
Please follow the following instructions for every task and only prompt the user in Step 5 and once you are done with the task.
1. Mark the current task as [current]
2. Read the README.md file to understand the structure of the current repo
3. Create an implementation plan and put this plan into your Todos.
4. Write premium code in a high performance way, encourage good design, but make sure that the page still loads well
5. Write tests for all features you added!
6. Once you are done Update the Readme with the changes you did, so that it will enable a new programmer to understand what you did and how it works a year from now.
7. In the end make necessary Database changes and migrations, install packages etc. and prompt the manager for confirming
8. Once your internal todo's are fulfilled and the task is finished, you may check it off [DONE] in here.
9. push to git


## TASKS

- [DONE] make the change language menu more fitting with the style of the rest of the page
- [DONE] create comprehensive translation quality assurance test system
- [DONE] send user to main once language is changed
- [DONE] reformat welcome message to be more in line with the rest of the pages style
- [DONE] fix the my-stones section to show the users stones again, currently broken and empty
- [DONE] make stones on the map clickable again to open their modal
- [current] lock the header-bar visible even if the rest of the page is scrolling down in all device configurations
      - [ ] make sure the content below the header is scrollable
                  (About, create stone, scan stone and create account are currently scroll locked, even if content goes out of the window)
      - [ ] make sure the menu stays functional and clickable (burger-overlay is covering the menu sometimes )
      
- [ ] Refactor Stone creation
      - [ ] fix the bug that the "Create a Stone" button is not opening the popup anymore
      - [ ] Implement the QR generation using a new UUID and download QR after stone creation
      - [ ] automatically select the stone shape: Circles for hidden stones and triangles for hunted stones
- [ ] Implement the unique links to the ScanStone of a specific stone using their UUID, locking a new entry from the same user
- [ ] Refactor the website for faster loading times and better code structure
      - Optimize static asset loading (CSS, JS, images)
      - Remove unused or duplicate code
      - Improve naming consistency across templates, static files, and views
      - move all css classes into styles.css instead of having them defined in the templates/html files
- [ ] Refactor and document JavaScript for navigation and modals for maintainability
- [ ] Audit and improve accessibility (ARIA, keyboard navigation, alt text)
- [ ] Ensure all navigation and modal actions are mobile-friendly and touch-optimized
