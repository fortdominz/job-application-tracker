# 🎯 Job Application Tracker

A Python command-line tool I built to solve a real problem — keeping track of every job and internship application in one place, without losing track of deadlines or forgetting what stage each one is at.

This is a personal-use project built from scratch as part of my programming journey. It started simple and grew phase by phase into something I actually use every day.

---

## 📺 Demo

[![Demo Video](https://img.youtube.com/vi/IAcH4Dfapi8/0.jpg)](https://www.youtube.com/watch?v=IAcH4Dfapi8)

---

## 🧠 Why I Built This

Every application cycle, I found myself juggling spreadsheets, sticky notes, and browser bookmarks trying to remember:
- Did I apply to this company already?
- When is this deadline?
- Did they respond or did I just forget to follow up?

Instead of patching together a messy spreadsheet again, I decided to build something properly — a structured tool that tracks every application through its full pipeline, warns me about upcoming deadlines, and gives me real analytics about my job search.

---

## ✨ What It Does

- **Add applications** — store company, role, location, job type, source, deadline, salary, notes, and status
- **Track status** — move applications through a 9-stage pipeline: `Saved → Applied → Online Assessment → Phone Screen → Interview → Final Round → Offer / Rejected / Withdrawn`
- **Deadline alerts** — warnings on startup for any deadline within the next 7 days
- **Full detail view** — open any application to see every field at once
- **Sort** — sort by deadline, date applied, company name, status, or date added. Sort preference remembered for the session
- **Filter & search** — filter by status, company, or upcoming deadlines. Keyword search across all 10 fields simultaneously
- **Needs attention** — automatically surfaces urgent deadlines, stalled applications, active stages, and incomplete records
- **Analytics dashboard** — status breakdown bar chart, response rate, monthly activity chart, and a quick insight line. All built with pure Python — no libraries
- **CSV export** — export all applications to a `.csv` file that opens in Excel or Google Sheets
- **Help screen** — full reference for every feature, accessible from the main menu at any time

---

## 🗂️ Project Structure

```
job-application-tracker/
├── db.py          # All data storage — reads and writes to applications.json
├── models.py      # Defines what an application looks like and validates input
├── ui.py          # Everything visual — colors, tables, menus, prompts
├── main.py        # All screens and app flow — the entry point
└── .gitignore     # Excludes personal data and cache files from GitHub
```

> **Note:** `applications.json` is intentionally excluded from this repo via `.gitignore` — it contains personal application data and gets created automatically on first run.

---

## 🚀 How to Run

**Requirements:** Python 3.8 or higher. No third-party packages needed — everything uses Python's built-in standard library.

```bash
# Clone the repo
git clone https://github.com/fortdominz/job-application-tracker.git

# Navigate into the folder
cd job-application-tracker

# Run the app
python main.py
```

The app will create `applications.json` automatically the first time you add an application.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Core language |
| `json` module | Reading and writing application data to a local file |
| `os` module | Checking if the data file exists, clearing the terminal |
| `datetime` module | Validating date input, calculating days until deadlines |
| `sys` module | Cleanly exiting the application |
| `csv` module | Exporting applications to a spreadsheet-ready file |
| `collections` module | defaultdict for grouping monthly activity |
| ANSI escape codes | Terminal colors for status badges and deadline urgency |
| JSON file | Local data storage (temporary — upgrade planned) |

---

## 📋 Application Fields

Each application stores the following:

| Field | Required | Notes |
|---|---|---|
| Company | ✅ | |
| Role | ✅ | |
| Job Type | ✅ | Internship, Full-Time, Part-Time, Co-op, Contract, or custom |
| Status | ✅ | 9-stage pipeline |
| Location | Optional | e.g. Remote, New York NY |
| Source | Optional | e.g. LinkedIn, Handshake |
| Deadline | Optional | YYYY-MM-DD format |
| Date Applied | Optional | YYYY-MM-DD format |
| Salary / Stipend | Optional | e.g. $8,000/month |
| Notes | Optional | Contacts, links, thoughts |

---

## 🗺️ Build Roadmap

This project was built phase by phase. Each phase produces working, runnable code.

| Phase | Name | Status |
|---|---|---|
| Phase 1 | Core Data Layer | ✅ Complete |
| Phase 2 | CLI Menu & Navigation | ✅ Complete |
| Phase 3 | CRUD Deep Dive | ✅ Complete |
| Phase 4 | Filtering & Search | ✅ Complete |
| Phase 5 | Analytics Dashboard | ✅ Complete |
| Phase 6 | Polish & CSV Export | ✅ Complete |

---

## 💡 What's Next

The CLI version is complete but this is just the beginning.
The data layer (`db.py`) is deliberately isolated so the
storage can be upgraded without touching anything else.
More coming.

---

## 📝 Notes

- Written in a beginner-friendly style with detailed comments explaining the *why* behind each decision, not just the *what*
- Commit history follows the build phases so you can see how the project grew from nothing
- Feedback and suggestions are welcome

---

*Built by [@fortdominz](https://github.com/fortdominz)*
