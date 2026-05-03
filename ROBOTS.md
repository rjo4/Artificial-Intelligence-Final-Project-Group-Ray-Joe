# ROBOTS.md — AI Agent Project Map
# Student Course Tracker & Capstone Suggester
# ONU College of Engineering · 2026-27

> This file is the authoritative reference for AI agents working on this codebase.
> It defines file purposes, data schemas, class contracts, inter-file communication,
> scoring logic, and safe modification zones.

---

## PROJECT IDENTITY

```
name:        Student Course Tracker & Capstone Suggester
language:    Python 3.10+
gui:         tkinter (stdlib — zero external dependencies)
entry_points:
  - student_tracker.py      # run for student interface
  - professor_capstone.py   # run for instructor interface
ipc_mechanism: shared JSON files on disk (same directory)
test_runner: python test_suite.py  OR  python -m unittest test_suite -v
```

---

## FILE MAP

```
student-course-tracker/
│
├── student_tracker.py        ROLE: Student GUI application
├── professor_capstone.py     ROLE: Instructor admin GUI application
├── capstone_data.json        ROLE: Shared capstone project catalogue (source of truth)
├── courses_data.json         ROLE: Professor-managed course overrides (may not exist)
├── test_suite.py             ROLE: Full test suite (stdlib unittest only)
├── README.md                 ROLE: Human documentation
└── ROBOTS.md                 ROLE: This file — AI agent structural reference
```

---

## INTER-FILE COMMUNICATION

```
student_tracker.py   ──reads──►  capstone_data.json   (at suggestion-refresh time)
student_tracker.py   ──reads──►  courses_data.json    (at startup only)

professor_capstone.py ──reads/writes──►  capstone_data.json  (live on every change)
professor_capstone.py ──reads/writes──►  courses_data.json   (live on every change)

student_tracker.py  and  professor_capstone.py  DO NOT import each other.
Communication is file-only. No sockets, no shared memory, no subprocesses.
```

---

## DATA SCHEMAS

### capstone_data.json

Top-level: JSON array of project objects.

```jsonc
[
  {
    "title":           string,          // REQUIRED — unique display name
    "summary":         string,          // REQUIRED — 1–3 sentence description
    "contact":         string,          // sponsor or faculty contact (may be empty)
    "majors":          string[],        // abbreviated major codes shown in instructor UI
    "tags":            string[],        // LOWERCASE interest keywords for scoring
    "related_courses": string[],        // EXACT course names matching tracker dropdowns
    "required":        boolean          // true = asterisk project (must pick ≥3)
  }
]
```

**CRITICAL:** Values in `related_courses` must exactly match course name strings
defined in `_DEFAULT_FALL` or `_DEFAULT_SPRING` in `student_tracker.py`, or
courses added by a professor via `courses_data.json`. Case and spacing are exact.

Example of CORRECT value:  `"Embedded Hardware-Software Code Design"`
Example of WRONG value:    `"Embedded HW/SW Code Design"`

### courses_data.json

```jsonc
{
  "fall": {
    "<major_name>": string[]    // list of course name strings
  },
  "spring": {
    "<major_name>": string[]
  }
}
```

Valid `<major_name>` keys (must match exactly):
- `"Foundational Engineering"`
- `"Electrical, Computer Engineering & Computer Science"`
- `"Civil Engineering"`
- `"Mechanical Engineering"`

This file is OPTIONAL. If absent, both apps fall back to built-in defaults.
Only keys present in the file override the defaults; missing keys use defaults.

---

## CLASS CONTRACTS

### student_tracker.py

#### Module-level helpers
```
_load_courses() -> (dict, dict)
    Loads fall_dict and spring_dict.
    Merges courses_data.json overrides onto _DEFAULT_FALL / _DEFAULT_SPRING.
    Called once at StudentTrackerApp.__init__.

_flat(by_cat: dict, majors: list[str]) -> list[str]
    Returns ["Major  |  Course Name", ...] for the given major subset.
    Separator is exactly "  |  " (two spaces, pipe, two spaces).
```

#### StudentTrackerApp
```
__init__(root)
    Sets self.fall_rows = [], self.spring_rows = [], loads courses, builds UI.

self.fall_rows / self.spring_rows : list[dict]
    Each dict has keys:
      frame, num_lbl, search_var, search_entry, combo_var, combo, btn,
      rows, course_dict, major_vars, season

self.fall_major_vars / self.spring_major_vars : dict[str, tk.BooleanVar]
    Keys are full major name strings. True = major is visible in dropdowns.

_refresh_single_combo(row: dict)
    Core filter function. Applies: major filter → already-chosen exclusion → search.
    Preserves current selection even if hidden by active filters.

_load_and_show_suggestions()
    Reads capstone_data.json.
    Calls _score(cap) for each project.
    Renders top 5 results into self.capstone_body frame.

Scoring formula:
    course_score   = matched_related_courses / total_related_courses
    interest_score = matched_tags_in_interests / total_tags
    final_score    = (course_score * 0.65) + (interest_score * 0.35)
    Matching is case-insensitive substring: tag in interests_text.lower()
    Course matching: course_name.lower() in student_courses (exact set membership)
```

### professor_capstone.py

#### Module-level I/O
```
load_capstones() -> list[dict]    reads capstone_data.json; returns [] on error
save_capstones(data: list[dict])  writes capstone_data.json (indent=2, utf-8)
load_courses()  -> dict           reads courses_data.json; falls back to defaults
save_courses(data: dict)          writes courses_data.json (indent=2, utf-8)
_parse_tags(s: str) -> list[str]  splits on [,;]+ → strips → lowercases each tag
```

#### ProfessorApp
```
self.capstones : list[dict]   in-memory copy; written to disk on every mutation
self.courses   : dict         in-memory copy; written to disk on every mutation

_capstone_dialog(title, prefill) -> dict | None
    Modal Toplevel. Returns filled dict on Save, None on Cancel.
    Validates: title non-empty, summary non-empty.

_import_csv(path)
    Required columns: title, summary (case-insensitive header matching)
    Optional columns: contact, majors, tags, related_courses, required
    Skips rows with empty title or summary.
    Skips rows whose title (lowercased) already exists in self.capstones.
    Accepts 'yes'/'true'/'1'/'y' as truthy for the required field.

_export_csv(path)
    Writes all self.capstones to CSV.
    Columns: title, summary, contact, majors, tags, related_courses, required
    Lists serialised as comma-joined strings. required as 'yes'/'no'.
```

---

## BUILT-IN COURSE LISTS

These are defined as module-level constants `_DEFAULT_FALL` and `_DEFAULT_SPRING`
in **both** `student_tracker.py` and `professor_capstone.py`.
They must stay in sync. If you modify one, modify the other identically.

### Fall majors and course counts (as of 2026-27)
| Major | Courses |
|---|---|
| Foundational Engineering | 7 |
| Electrical, Computer Engineering & Computer Science | 19 |
| Civil Engineering | 9 |
| Mechanical Engineering | 15 |

### Spring majors and course counts (as of 2026-27)
| Major | Courses |
|---|---|
| Foundational Engineering | 8 |
| Electrical, Computer Engineering & Computer Science | 20 |
| Civil Engineering | 14 |
| Mechanical Engineering | 16 |

---

## CAPSTONE CATALOGUE (2026-27)

23 projects total. 11 required (⭐), 12 optional.
Project #10 from original document (Energy Harvesting Device) was struck through
and is NOT included.

### Required projects (required: true)
1. Firecraft Safety Products Inventory Management System
2. OCLC Project
3. GROB Systems: Intelligent Robot Bin Picking Automation
4. Argonne National Lab Quantum Instrumentation Project
5. eSight Go Computer Mouse Design for the Visually Impaired
6. Cenovus: Wireless Instrumentation and OT Infrastructure
7. Blank Part Cutoff Sorting
8. Padrone's Pizza Automated Adjustable Pizza Dough Rounder
9. GPI Project
10. Norada Lanes Bowling Control and Monitoring System
11. Healthwise Mobile Health Clinic Data Services

### Optional projects (required: false)
12. Pharmacy Patient Simulator
13. Low-Power Mesh-Based Sensor Network for Remote Monitoring
14. Fashion Interface — Virtual Fitting System
15. Hardware Password Manager
16. Smart Trash Sorting Attachment for Standard Waste Bins
17. FridgeApp — Smart Refrigerator Inventory System
18. CleanSlate: Autonomous Whiteboard Cleaning Robot
19. IEEE Micromouse
20. Robotic Football Advanced Center
21. SafeSmart Bike Rack
22. IoT-Based Smart Waste Management System for the JLK Building
23. Smart Vent — Retrofit HVAC Airflow Control Device

---

## SAFE MODIFICATION ZONES

### ✅ Safe to add/change without risk of breakage
- Adding new courses to `_DEFAULT_FALL` or `_DEFAULT_SPRING` (update BOTH files)
- Adding new capstone projects to `capstone_data.json` (follow schema exactly)
- Colour constants at top of either file
- `MAJOR_SHORT` abbreviation labels in `student_tracker.py`
- Text in messagebox strings and label widgets
- Score weights (0.65 / 0.35) in `_load_and_show_suggestions`
- Number of top suggestions shown (currently `min(5, len(scored))`)

### ⚠️ Change carefully — has downstream effects
- `MAJORS` list — must match keys in `_DEFAULT_FALL`, `_DEFAULT_SPRING`, and
  `courses_data.json`. Order determines checkbox rendering order.
- `_flat()` separator string `"  |  "` — used by `.split("  |  ")` in `_save_all`.
  If changed, update both the flat builder AND every split call.
- `capstone_data.json` → `related_courses` values — must exactly match course
  name strings or the course-match scorer returns 0 for those entries.

### 🚫 Do not modify
- The `rows` back-reference inside each row dict (used by `_remove_row`)
- The `on_save` / `on_cancel` closures inside `_capstone_dialog` (capture locals)
- The `canvas.bind_all("<MouseWheel>", ...)` scroll handler (global binding)

---

## TESTING

```
test_suite.py
  TestDataLoading          — JSON load/save round-trips, missing-file fallback
  TestScoringEngine        — score formula, edge cases (empty courses, no tags)
  TestCourseFiltering      — _flat(), major filter logic, search filter logic
  TestCSVImport            — valid CSV, missing columns, duplicate titles, bad rows
  TestCSVExport            — round-trip export → re-import produces identical data
  TestCourseManagement     — add course, remove course, restore defaults, bulk add
  TestCapstoneManagement   — add, edit, delete capstone; required flag toggling
  TestEdgeCases            — empty capstone file, malformed JSON, empty interests
```

Run with: `python test_suite.py`
All tests use stdlib `unittest` and `tempfile` only. No GUI is created.
Expected result: all tests pass in under 5 seconds.

---

## EXTENSION POINTS

If you need to add a feature, here is where to do it:

| Feature | Where to add it |
|---|---|
| New semester (e.g. Summer) | Add season dict to `_DEFAULT_*`, add radio button in `_build_courses_tab` |
| Export student data to file | Add button in `_build_save_bar`, write to JSON/CSV in `_save_all` |
| Multi-student profiles | Add a profile selector card above the name field; store in a profiles JSON |
| Semantic interest matching | Replace tag substring check with cosine similarity on TF-IDF vectors |
| Auto-reload courses.json | Add `root.after(30000, self._reload_courses)` poll in student tracker |
| Dark mode | Replace colour constants with a theme dict; add a toggle button |
| Password-protect instructor panel | Add a login dialog in `ProfessorApp.__init__` before `_build_ui()` |