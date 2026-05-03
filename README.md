# 🎓 Student Course Tracker & Capstone Suggester

A two-part desktop application built for Ohio Northern University's College of Engineering.  
Students track completed coursework and receive AI-scored capstone project recommendations.  
Instructors manage the capstone catalogue and course offerings through a separate admin panel.

> **Built entirely in Python using only the standard library — no `pip install` required.**  
> Requires Python 3.10 or later and a system installation of `tkinter` (included by default on Windows and macOS).

---

## 📋 Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Student Tracker — Feature Guide](#student-tracker--feature-guide)
- [Instructor Panel — Feature Guide](#instructor-panel--feature-guide)
- [How the Capstone Suggestion Engine Works](#how-the-capstone-suggestion-engine-works)
- [Shared Data Files](#shared-data-files)
- [CSV Import Format](#csv-import-format)
- [Project Structure](#project-structure)
- [Running the Tests](#running-the-tests)
- [Criteria Compliance](#criteria-compliance)
- [Known Limitations](#known-limitations)

---

## Overview

| App | File | Audience |
|-----|------|----------|
| Student Course Tracker | `student_tracker.py` | Students |
| Instructor Administration Panel | `professor_capstone.py` | Faculty |
| Shared capstone data | `capstone_data.json` | Auto-managed |
| Shared course overrides | `courses_data.json` | Auto-managed |

The two apps share a folder and communicate entirely through JSON files.  
No server, no database engine, no internet connection required.

---

## Requirements

| Requirement | Details |
|---|---|
| **Python** | 3.10 or newer |
| **tkinter** | Included with Python on Windows & macOS. Linux: `sudo apt install python3-tk` |
| **External packages** | **None.** Uses only Python standard library. |

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-org>/student-course-tracker.git
cd student-course-tracker

# 2. (Linux only) Install tkinter if not already present
sudo apt install python3-tk      # Debian / Ubuntu
# sudo dnf install python3-tkinter  # Fedora / RHEL

# 3. No further installation steps needed.
```

---

## Running the App

```bash
# Launch the student-facing tracker
python student_tracker.py

# Launch the instructor administration panel (separate window)
python professor_capstone.py
```

Both apps can be open simultaneously. Changes saved in the instructor panel are  
reflected in the student tracker the next time it starts.

---

## Student Tracker — Feature Guide

### 1 · Enter Your Name
Type your full name in the **Student Information** card at the top.

### 2 · Select Fall and Spring Classes

Each semester section has its own course list.

- **Filter by Major** — tick/untick the checkboxes across the top of each section  
  to show only courses from your major(s). All majors are shown by default,  
  supporting dual-major and cross-disciplinary selections.
- **Per-row search** — type in the small search box on the left of any row  
  to filter that dropdown in real time. Clears itself on focus-out if empty.
- **Add rows** — click **＋ Add Class** to add as many rows as you need.
- **Remove rows** — click **✕** on any row. The last row cannot be removed.

### 3 · Describe Your Interests
Fill in the **Interests & Goals** text box with career goals, research areas,  
or technology topics you want your capstone to focus on.  
Example: *"I am interested in robotics, machine learning, and embedded systems."*

### 4 · Get Capstone Suggestions
Click **🔄 Refresh Capstone Suggestions**.  
The engine scores every capstone project and shows the top 5 matches with a percentage.

### 5 · Save
Click **💾 Save All**. A summary dialog confirms the saved data.

---

## Instructor Panel — Feature Guide

### Tab 1 · Capstone Projects

| Action | How |
|--------|-----|
| View project details | Click any project in the left list |
| Search projects | Type in the search bar (top-right) — filters by title and tags |
| Add a project | **＋ Add Project** → fill in the dialog → Save |
| Edit a project | Select it → **✏️ Edit Selected** |
| Delete a project | Select it → **🗑 Delete** |
| Import from CSV | **📥 Import CSV** → select a `.csv` file (see format below) |
| Export to CSV | **📤 Export CSV** → choose save location |

### Tab 2 · Course Catalogue

| Action | How |
|--------|-----|
| Switch season | **Fall** / **Spring** radio buttons |
| Switch major | Drop-down selector |
| Remove course(s) | Select one or more → **🗑 Remove Selected Course(s)** |
| Add a single course | Type name → **＋ Add Course** |
| Bulk-add courses | Paste one course per line → **📋 Add All Lines** |
| Restore defaults | **↩ Restore All Defaults for This Major** |

All course changes are saved immediately to `courses_data.json` and  
picked up by `student_tracker.py` on its next launch.

---

## How the Capstone Suggestion Engine Works

Each capstone project in `capstone_data.json` has:
- `related_courses` — a list of course names that match the tracker dropdowns exactly
- `tags` — keyword phrases a student might type in the Interests field

The engine computes a weighted score for each project:

```
score = (course_match × 0.65) + (interest_match × 0.35)
```

**course_match** = fraction of the project's `related_courses` the student has completed  
**interest_match** = fraction of the project's `tags` found anywhere in the student's interests text

The top 5 scoring projects are displayed with a percentage badge and colour-coded accent.  
Required projects (marked `"required": true`) are flagged with a ⭐ badge.

---

## Shared Data Files

Both files live in the **same directory** as the two Python scripts.  
They are created automatically on first use.

### `capstone_data.json`
Array of capstone project objects. Pre-loaded with all 23 projects from the  
2026-27 ONU Capstone Proposals document.

```jsonc
[
  {
    "title":           "Project Title",
    "summary":         "One-paragraph description shown to students.",
    "contact":         "Sponsor / faculty contact name",
    "majors":          ["CS", "CpE"],          // abbreviated major codes
    "tags":            ["robotics", "iot"],     // interest keywords (lowercase)
    "related_courses": ["Embedded Real-Time Applications", "Sensors and Measurements"],
    "required":        true                     // true = asterisk project
  }
]
```

### `courses_data.json`
Professor overrides for the built-in course lists.  
Only written when a professor adds or removes a course.  
If absent, both apps fall back to the built-in defaults.

```jsonc
{
  "fall":   { "Foundational Engineering": ["Engineering Orientation", ...], ... },
  "spring": { "Mechanical Engineering": ["Heat Transfer", ...], ... }
}
```

---

## CSV Import Format

When importing capstone projects via CSV, the file must have **at minimum**:

| Column | Required | Notes |
|--------|----------|-------|
| `title` | ✅ | Project title — duplicates are skipped |
| `summary` | ✅ | Project description |
| `contact` | optional | Sponsor or faculty contact |
| `majors` | optional | Comma-separated abbreviations, e.g. `CS, CpE` |
| `tags` | optional | Comma or semicolon separated keywords |
| `related_courses` | optional | Exact course names, comma-separated |
| `required` | optional | `yes` / `true` / `1` = required; anything else = optional |

Column names are case-insensitive. Extra columns are ignored.

---

## Project Structure

```
student-course-tracker/
│
├── student_tracker.py       # Student-facing desktop app (716 lines)
├── professor_capstone.py    # Instructor admin panel (866 lines)
│
├── capstone_data.json       # Capstone project catalogue (auto-managed)
├── courses_data.json        # Course overrides (auto-managed, created on first edit)
│
├── test_suite.py            # Full unit + integration test suite (stdlib unittest)
│
├── README.md                # This file
└── ROBOTS.md                # AI-readable project structure definition
```

---

## Running the Tests

```bash
python test_suite.py
```

Or with verbose output:

```bash
python -m unittest test_suite -v
```

The test suite uses only `unittest` from the Python standard library.  
It covers data loading, scoring logic, course filtering, CSV import/export,  
JSON persistence, and edge cases. No GUI is launched during testing.

---

## Criteria Compliance

| Requirement | Status | Notes |
|---|---|---|
| Written in Python | ✅ | 100% Python 3.10+ |
| Programmed primarily with an AI agent | ✅ | Developed with Claude (Anthropic) |
| Robust testing system | ✅ | `test_suite.py` — stdlib `unittest`, covers all core logic |
| Hosted on GitHub | ✅ | See repository URL above |
| Desktop app — no licenses or dependencies | ✅ | Only Python stdlib + system `tkinter` |
| No command-line apps | ✅ | Both apps open full GUI windows |
| README.md | ✅ | This file |
| ROBOTS.md | ✅ | See `ROBOTS.md` |

---

## Known Limitations

- **Course selections are not persisted between sessions.** The save dialog displays a summary but does not write student data to disk. A future version could add a student profile export.
- **`courses_data.json` changes require a tracker restart.** The student app loads course data once at startup.
- **tkinter appearance varies by OS.** The app is tested on Windows 10/11 and Ubuntu 22.04+. macOS theming may differ slightly.
- **The suggestion engine is keyword-based**, not semantic. Interest phrases must contain words that appear in project tags for the interest score to register.