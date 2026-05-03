"""
test_suite.py — Student Course Tracker & Capstone Suggester
===========================================================
Full unit and integration test suite.
Uses ONLY Python standard library (unittest, tempfile, json, csv, pathlib).
No GUI is created. No external dependencies required.

Run:
    python test_suite.py
    python -m unittest test_suite -v
"""

import unittest
import json
import csv
import tempfile
import os
import re
from pathlib import Path
from datetime import datetime


# ── Helpers replicated from source files (pure logic, no tkinter) ──────────────

MAJORS = [
    "Foundational Engineering",
    "Electrical, Computer Engineering & Computer Science",
    "Civil Engineering",
    "Mechanical Engineering",
]

_DEFAULT_FALL = {
    "Foundational Engineering": [
        "Engineering Orientation", "Foundations of Design 1", "Foundations of Design 2",
        "Statistics", "Engineering Traditions and Culture in Rome",
        "Professional Practice", "Industrial Controllers",
    ],
    "Electrical, Computer Engineering & Computer Science": [
        "Introduction to Programming", "Electric Circuits", "Web Development",
        "Data Structures and Algorithms", "Research Experience", "Big Data Analytics",
        "Applied Electromagnetics", "Signals and Systems",
        "Embedded Hardware-Software Code Design", "Embedded Real-Time Applications",
        "Software Development", "UI/UX Design", "Computer Architecture",
        "Networks and Data Communication", "Professional Certification Preparation",
        "Power Systems", "Information Science", "Advanced Electronics",
        "Theory of Computation",
    ],
    "Civil Engineering": [
        "Surveying", "Surveying Lab", "Environmental Engineering",
        "Geotechnical Engineering", "Structural Analysis", "Transportation Engineering",
        "Water Resources Engineering", "CFE Fundamentals", "CFE Design Seminar 1",
    ],
    "Mechanical Engineering": [
        "Engineering Material Science", "Thermodynamics", "Design for Manufacturing",
        "Computer Applications", "Fundamentals of Experimentation",
        "Machine Component Design", "3-D Modeling and Design", "Dynamic Systems Modeling",
        "Fluid Mechanics", "Sensors and Measurements", "Process of Design",
        "Mechatronics", "Computational Fluid Dynamics", "Advanced Thermodynamics",
        "Engineering Analysis",
    ],
}

_DEFAULT_SPRING = {
    "Foundational Engineering": [
        "Engineering Graphics", "Technical Writing for Engineers",
        "Engineering Economics", "Ethics in Engineering", "Project Management",
        "Capstone Preparation", "Innovation and Entrepreneurship",
        "Sustainability in Engineering",
    ],
    "Electrical, Computer Engineering & Computer Science": [
        "Object-Oriented Programming", "Digital Logic Design", "Machine Learning",
        "Cybersecurity Fundamentals", "Database Systems", "Operating Systems",
        "Computer Vision", "Wireless Communications", "VLSI Design", "Compiler Design",
        "Robotics Programming", "Artificial Intelligence", "Mobile App Development",
        "Cloud Computing", "Parallel Computing", "Natural Language Processing",
        "Internet of Things", "Quantum Computing Fundamentals", "Deep Learning",
        "Human-Computer Interaction",
    ],
    "Civil Engineering": [
        "Reinforced Concrete Design", "Steel Structure Design", "Foundation Engineering",
        "Construction Management", "GIS and Remote Sensing", "Hydraulics Lab",
        "Bridge Design", "Urban Planning", "Earthquake Engineering",
        "Building Information Modeling", "CFE Design Seminar 2", "Coastal Engineering",
        "Traffic Engineering", "Environmental Remediation",
    ],
    "Mechanical Engineering": [
        "Heat Transfer", "Mechanical Vibrations", "Manufacturing Processes",
        "Control Systems", "Finite Element Analysis", "Robotics", "HVAC Systems",
        "Aerospace Fundamentals", "Renewable Energy Systems", "Composite Materials",
        "Advanced Manufacturing", "Capstone Design", "Biomechanics",
        "Additive Manufacturing", "Tribology", "Acoustics and Noise Control",
    ],
}


def _flat(by_cat: dict, majors: list) -> list:
    """Replicate student_tracker._flat()"""
    out = []
    for m in majors:
        for c in by_cat.get(m, []):
            out.append(f"{m}  |  {c}")
    return out


def _parse_tags(s: str) -> list:
    """Replicate professor_capstone._parse_tags()"""
    return [t.strip().lower() for t in re.split(r"[,;]+", s) if t.strip()]


def _load_courses(courses_file: Path) -> tuple:
    """Replicate student_tracker._load_courses()"""
    fall   = {k: list(v) for k, v in _DEFAULT_FALL.items()}
    spring = {k: list(v) for k, v in _DEFAULT_SPRING.items()}
    if courses_file.exists():
        try:
            data = json.loads(courses_file.read_text(encoding="utf-8"))
            for maj, courses in data.get("fall", {}).items():
                fall[maj] = courses
            for maj, courses in data.get("spring", {}).items():
                spring[maj] = courses
        except Exception:
            pass
    return fall, spring


def _score_capstone(cap: dict, student_courses: set, interests: str) -> float:
    """Replicate student_tracker scoring formula."""
    related = [c.lower() for c in cap.get("related_courses", [])]
    tags    = [t.lower() for t in cap.get("tags", [])]
    cs = sum(1 for c in related if c in student_courses) / max(len(related), 1)
    ts = sum(1 for t in tags    if t in interests.lower()) / max(len(tags), 1)
    return round(cs * 0.65 + ts * 0.35, 4)


def _load_capstones(path: Path) -> list:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _save_capstones(path: Path, data: list):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _save_courses(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


SAMPLE_CAPSTONE = {
    "title": "Test Robotics Project",
    "summary": "A robotics capstone for testing purposes.",
    "contact": "Dr. Test",
    "majors": ["ME", "ECCS"],
    "tags": ["robotics", "sensors", "embedded systems", "control systems"],
    "related_courses": ["Robotics", "Sensors and Measurements", "Control Systems"],
    "required": False,
}


# ══════════════════════════════════════════════════════════════════════════════
class TestDataLoading(unittest.TestCase):
# ══════════════════════════════════════════════════════════════════════════════

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_load_capstones_missing_file_returns_empty_list(self):
        result = _load_capstones(self.tmpdir / "nonexistent.json")
        self.assertEqual(result, [])

    def test_load_capstones_valid_file(self):
        path = self.tmpdir / "capstone_data.json"
        _save_capstones(path, [SAMPLE_CAPSTONE])
        result = _load_capstones(path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Test Robotics Project")

    def test_load_capstones_malformed_json_returns_empty(self):
        path = self.tmpdir / "bad.json"
        path.write_text("{ this is not valid json }", encoding="utf-8")
        result = _load_capstones(path)
        self.assertEqual(result, [])

    def test_load_courses_missing_file_uses_defaults(self):
        fall, spring = _load_courses(self.tmpdir / "no_courses.json")
        self.assertIn("Foundational Engineering", fall)
        self.assertIn("Mechanical Engineering", spring)
        self.assertIn("Engineering Orientation", fall["Foundational Engineering"])

    def test_load_courses_override_replaces_major(self):
        path = self.tmpdir / "courses_data.json"
        override = {"fall": {"Foundational Engineering": ["Custom Course A", "Custom Course B"]}, "spring": {}}
        _save_courses(path, override)
        fall, spring = _load_courses(path)
        self.assertEqual(fall["Foundational Engineering"], ["Custom Course A", "Custom Course B"])
        # Other majors should still be defaults
        self.assertIn("Electric Circuits", fall["Electrical, Computer Engineering & Computer Science"])

    def test_load_courses_malformed_json_falls_back_to_defaults(self):
        path = self.tmpdir / "courses_data.json"
        path.write_text("not json at all", encoding="utf-8")
        fall, spring = _load_courses(path)
        self.assertIn("Engineering Orientation", fall["Foundational Engineering"])

    def test_save_load_round_trip_capstones(self):
        path = self.tmpdir / "capstone_data.json"
        projects = [SAMPLE_CAPSTONE, {**SAMPLE_CAPSTONE, "title": "Second Project"}]
        _save_capstones(path, projects)
        loaded = _load_capstones(path)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[1]["title"], "Second Project")

    def test_capstone_file_is_valid_json_after_save(self):
        path = self.tmpdir / "capstone_data.json"
        _save_capstones(path, [SAMPLE_CAPSTONE])
        content = path.read_text(encoding="utf-8")
        parsed  = json.loads(content)  # must not raise
        self.assertIsInstance(parsed, list)

    def test_default_fall_course_counts(self):
        self.assertEqual(len(_DEFAULT_FALL["Foundational Engineering"]), 7)
        self.assertEqual(len(_DEFAULT_FALL["Electrical, Computer Engineering & Computer Science"]), 19)
        self.assertEqual(len(_DEFAULT_FALL["Civil Engineering"]), 9)
        self.assertEqual(len(_DEFAULT_FALL["Mechanical Engineering"]), 15)

    def test_default_spring_course_counts(self):
        self.assertEqual(len(_DEFAULT_SPRING["Foundational Engineering"]), 8)
        self.assertEqual(len(_DEFAULT_SPRING["Electrical, Computer Engineering & Computer Science"]), 20)
        self.assertEqual(len(_DEFAULT_SPRING["Civil Engineering"]), 14)
        self.assertEqual(len(_DEFAULT_SPRING["Mechanical Engineering"]), 16)


# ══════════════════════════════════════════════════════════════════════════════
class TestScoringEngine(unittest.TestCase):
# ══════════════════════════════════════════════════════════════════════════════

    def test_perfect_course_and_interest_match(self):
        cap = {
            "related_courses": ["Robotics", "Sensors and Measurements"],
            "tags": ["robotics", "sensors"],
        }
        courses   = {"robotics", "sensors and measurements"}
        interests = "I love robotics and sensors"
        score = _score_capstone(cap, courses, interests)
        self.assertAlmostEqual(score, 1.0, places=3)

    def test_zero_score_no_match(self):
        cap = {
            "related_courses": ["Robotics", "Sensors and Measurements"],
            "tags": ["robotics", "sensors"],
        }
        score = _score_capstone(cap, set(), "I like cooking")
        self.assertEqual(score, 0.0)

    def test_course_only_match(self):
        cap = {
            "related_courses": ["Robotics", "Control Systems"],
            "tags": ["unrelated", "nothing"],
        }
        courses = {"robotics", "control systems"}
        score   = _score_capstone(cap, courses, "no matching interests")
        self.assertAlmostEqual(score, 0.65, places=3)

    def test_interest_only_match(self):
        cap = {
            "related_courses": ["Advanced Thermodynamics"],
            "tags": ["robotics", "automation"],
        }
        score = _score_capstone(cap, set(), "I enjoy robotics and automation work")
        self.assertAlmostEqual(score, 0.35, places=3)

    def test_partial_course_match_scales_correctly(self):
        cap = {
            "related_courses": ["Robotics", "Control Systems", "Mechatronics", "Sensors and Measurements"],
            "tags": [],
        }
        # 2 of 4 courses matched
        courses = {"robotics", "control systems"}
        score   = _score_capstone(cap, courses, "")
        self.assertAlmostEqual(score, 0.65 * 0.5, places=3)

    def test_empty_related_courses_does_not_divide_by_zero(self):
        cap = {"related_courses": [], "tags": ["robotics"]}
        score = _score_capstone(cap, {"robotics"}, "robotics")
        self.assertGreaterEqual(score, 0.0)

    def test_empty_tags_does_not_divide_by_zero(self):
        cap = {"related_courses": ["Robotics"], "tags": []}
        score = _score_capstone(cap, {"robotics"}, "robotics")
        self.assertGreaterEqual(score, 0.0)

    def test_score_is_between_0_and_1(self):
        cap = {
            "related_courses": ["Robotics", "Mechatronics", "Control Systems"],
            "tags": ["robotics", "embedded systems", "automation", "sensors"],
        }
        courses   = {"robotics", "mechatronics"}
        interests = "embedded systems automation"
        score = _score_capstone(cap, courses, interests)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_interest_matching_is_case_insensitive(self):
        cap = {"related_courses": [], "tags": ["robotics", "sensors"]}
        score1 = _score_capstone(cap, set(), "ROBOTICS and SENSORS")
        score2 = _score_capstone(cap, set(), "robotics and sensors")
        self.assertAlmostEqual(score1, score2, places=4)

    def test_ranking_order_is_correct(self):
        full_match    = {"related_courses": ["Robotics"], "tags": ["robotics"]}
        partial_match = {"related_courses": ["Robotics"], "tags": ["unmatched"]}
        no_match      = {"related_courses": ["Quantum Computing Fundamentals"], "tags": ["quantum"]}

        courses   = {"robotics"}
        interests = "I love robotics"

        s_full    = _score_capstone(full_match,    courses, interests)
        s_partial = _score_capstone(partial_match, courses, interests)
        s_none    = _score_capstone(no_match,      courses, interests)

        self.assertGreater(s_full, s_partial)
        self.assertGreater(s_partial, s_none)

    def test_required_flag_does_not_affect_score(self):
        cap_req = {**SAMPLE_CAPSTONE, "required": True}
        cap_opt = {**SAMPLE_CAPSTONE, "required": False}
        courses = {"robotics", "sensors and measurements", "control systems"}
        s1 = _score_capstone(cap_req, courses, "robotics sensors")
        s2 = _score_capstone(cap_opt, courses, "robotics sensors")
        self.assertEqual(s1, s2)


# ══════════════════════════════════════════════════════════════════════════════
class TestCourseFiltering(unittest.TestCase):
# ══════════════════════════════════════════════════════════════════════════════

    def test_flat_all_majors_returns_all_courses(self):
        result = _flat(_DEFAULT_FALL, MAJORS)
        self.assertGreater(len(result), 0)
        total_expected = sum(len(v) for v in _DEFAULT_FALL.values())
        self.assertEqual(len(result), total_expected)

    def test_flat_single_major_filters_correctly(self):
        result = _flat(_DEFAULT_FALL, ["Foundational Engineering"])
        for item in result:
            self.assertTrue(item.startswith("Foundational Engineering  |  "))

    def test_flat_no_majors_returns_empty(self):
        result = _flat(_DEFAULT_FALL, [])
        self.assertEqual(result, [])

    def test_flat_separator_format(self):
        result = _flat(_DEFAULT_FALL, ["Foundational Engineering"])
        for item in result:
            self.assertIn("  |  ", item)
            parts = item.split("  |  ")
            self.assertEqual(len(parts), 2)
            self.assertEqual(parts[0], "Foundational Engineering")

    def test_flat_unknown_major_returns_empty(self):
        result = _flat(_DEFAULT_FALL, ["Nonexistent Major"])
        self.assertEqual(result, [])

    def test_flat_dual_major_combines_courses(self):
        result = _flat(_DEFAULT_FALL, ["Foundational Engineering", "Civil Engineering"])
        basic  = [r for r in result if r.startswith("Foundational Engineering")]
        civil  = [r for r in result if r.startswith("Civil Engineering")]
        self.assertEqual(len(basic), len(_DEFAULT_FALL["Foundational Engineering"]))
        self.assertEqual(len(civil), len(_DEFAULT_FALL["Civil Engineering"]))

    def test_course_name_extraction_from_flat_string(self):
        flat_list = _flat(_DEFAULT_FALL, ["Foundational Engineering"])
        for item in flat_list:
            course_name = item.split("  |  ")[-1]
            self.assertIn(course_name, _DEFAULT_FALL["Foundational Engineering"])

    def test_no_duplicate_courses_within_single_major(self):
        result = _flat(_DEFAULT_FALL, ["Mechanical Engineering"])
        self.assertEqual(len(result), len(set(result)))

    def test_search_filter_logic(self):
        """Simulate the per-row search filter applied in _refresh_single_combo."""
        full_list = _flat(_DEFAULT_FALL, MAJORS)
        query     = "thermodynamics"
        filtered  = [c for c in full_list if query in c.lower()]
        self.assertGreater(len(filtered), 0)
        for item in filtered:
            self.assertIn("thermodynamics", item.lower())

    def test_search_filter_empty_query_returns_all(self):
        full_list = _flat(_DEFAULT_FALL, MAJORS)
        query     = ""
        filtered  = full_list if not query else [c for c in full_list if query in c.lower()]
        self.assertEqual(len(filtered), len(full_list))

    def test_already_chosen_exclusion(self):
        """Simulate the chosen-by-others exclusion logic."""
        full_list = _flat(_DEFAULT_FALL, ["Foundational Engineering"])
        chosen_by_others = {"Foundational Engineering  |  Statistics"}
        available = [c for c in full_list if c not in chosen_by_others]
        self.assertNotIn("Foundational Engineering  |  Statistics", available)
        self.assertEqual(len(available), len(full_list) - 1)


# ══════════════════════════════════════════════════════════════════════════════
class TestCSVImport(unittest.TestCase):
# ══════════════════════════════════════════════════════════════════════════════

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_csv(self, rows: list[dict], filename="test.csv") -> Path:
        path = self.tmpdir / filename
        if not rows:
            path.write_text("title,summary\n", encoding="utf-8-sig")
            return path
        fieldnames = list(rows[0].keys())
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def _simulate_import(self, path: Path, existing: list) -> tuple[list, int, int]:
        """Returns (capstones_after, imported_count, skipped_count)."""
        required_cols = {"title", "summary"}
        imported = 0
        skipped  = 0
        result   = list(existing)
        existing_titles = {c.get("title", "").lower() for c in existing}

        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            cols   = {c.strip().lower() for c in (reader.fieldnames or [])}
            if not required_cols.issubset(cols):
                return result, 0, -1  # -1 signals missing columns error

            for row in reader:
                r     = {k.strip().lower(): v.strip() for k, v in row.items()}
                title = r.get("title", "").strip()
                summary = r.get("summary", "").strip()
                if not title or not summary:
                    skipped += 1
                    continue
                if title.lower() in existing_titles:
                    skipped += 1
                    continue
                entry = {
                    "title":           title,
                    "summary":         summary,
                    "contact":         r.get("contact", r.get("sponsor", "")),
                    "majors":          [m.strip() for m in r.get("majors", "").split(",") if m.strip()],
                    "tags":            _parse_tags(r.get("tags", "")),
                    "related_courses": [c.strip() for c in r.get("related_courses", r.get("courses", "")).split(",") if c.strip()],
                    "required":        r.get("required", "").strip().lower() in ("yes", "true", "1", "y"),
                }
                result.append(entry)
                existing_titles.add(title.lower())
                imported += 1

        return result, imported, skipped

    def test_import_valid_csv_adds_projects(self):
        path = self._write_csv([
            {"title": "Alpha Project", "summary": "Alpha summary.", "tags": "robotics, iot"},
            {"title": "Beta Project",  "summary": "Beta summary.",  "tags": "software"},
        ])
        result, imported, skipped = self._simulate_import(path, [])
        self.assertEqual(imported, 2)
        self.assertEqual(skipped, 0)
        self.assertEqual(len(result), 2)

    def test_import_missing_required_columns_signals_error(self):
        path = self._write_csv([{"only_title": "No Summary Col"}])
        _, _, skipped = self._simulate_import(path, [])
        self.assertEqual(skipped, -1)  # signals error

    def test_import_skips_rows_with_empty_title(self):
        path = self._write_csv([
            {"title": "",             "summary": "No title row."},
            {"title": "Good Project", "summary": "Good summary."},
        ])
        _, imported, skipped = self._simulate_import(path, [])
        self.assertEqual(imported, 1)
        self.assertEqual(skipped, 1)

    def test_import_skips_rows_with_empty_summary(self):
        path = self._write_csv([
            {"title": "Missing Summary", "summary": ""},
            {"title": "Has Summary",     "summary": "Valid."},
        ])
        _, imported, skipped = self._simulate_import(path, [])
        self.assertEqual(imported, 1)
        self.assertEqual(skipped, 1)

    def test_import_skips_duplicate_titles(self):
        existing = [{"title": "Existing Project", "summary": "Already there."}]
        path = self._write_csv([
            {"title": "Existing Project", "summary": "Duplicate."},
            {"title": "New Project",      "summary": "Fresh."},
        ])
        result, imported, skipped = self._simulate_import(path, existing)
        self.assertEqual(imported, 1)
        self.assertEqual(skipped, 1)
        self.assertEqual(len(result), 2)

    def test_import_required_field_truthy_values(self):
        for val in ("yes", "true", "1", "y", "YES", "True"):
            path = self._write_csv([{"title": f"Project {val}", "summary": "S.", "required": val}])
            result, _, _ = self._simulate_import(path, [])
            self.assertTrue(result[-1]["required"], f"'{val}' should be truthy")

    def test_import_required_field_falsy_values(self):
        for val in ("no", "false", "0", "", "maybe"):
            path = self._write_csv([{"title": f"Project {val}", "summary": "S.", "required": val}])
            result, _, _ = self._simulate_import(path, [])
            self.assertFalse(result[-1]["required"], f"'{val}' should be falsy")

    def test_import_tags_parsed_correctly(self):
        path = self._write_csv([
            {"title": "Tag Test", "summary": "S.", "tags": "robotics; IoT, Machine Learning"}
        ])
        result, _, _ = self._simulate_import(path, [])
        tags = result[0]["tags"]
        self.assertIn("robotics", tags)
        self.assertIn("iot", tags)
        self.assertIn("machine learning", tags)

    def test_import_empty_csv_imports_nothing(self):
        path = self._write_csv([])
        result, imported, skipped = self._simulate_import(path, [])
        self.assertEqual(imported, 0)
        self.assertEqual(len(result), 0)

    def test_import_accepts_courses_column_alias(self):
        """'courses' column should be accepted as alias for 'related_courses'."""
        path = self._write_csv([
            {"title": "Alias Test", "summary": "S.", "courses": "Robotics, Mechatronics"}
        ])
        result, imported, _ = self._simulate_import(path, [])
        self.assertEqual(imported, 1)
        self.assertIn("Robotics", result[0]["related_courses"])


# ══════════════════════════════════════════════════════════════════════════════
class TestCSVExport(unittest.TestCase):
# ══════════════════════════════════════════════════════════════════════════════

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _export(self, capstones: list, path: Path):
        fieldnames = ["title", "summary", "contact", "majors", "tags", "related_courses", "required"]
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for cap in capstones:
                writer.writerow({
                    "title":           cap.get("title", ""),
                    "summary":         cap.get("summary", ""),
                    "contact":         cap.get("contact", ""),
                    "majors":          ", ".join(cap.get("majors", [])),
                    "tags":            ", ".join(cap.get("tags", [])),
                    "related_courses": ", ".join(cap.get("related_courses", [])),
                    "required":        "yes" if cap.get("required") else "no",
                })

    def test_export_creates_file(self):
        path = self.tmpdir / "export.csv"
        self._export([SAMPLE_CAPSTONE], path)
        self.assertTrue(path.exists())

    def test_export_correct_row_count(self):
        projects = [SAMPLE_CAPSTONE, {**SAMPLE_CAPSTONE, "title": "Second"}]
        path = self.tmpdir / "export.csv"
        self._export(projects, path)
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 2)

    def test_export_required_serialised_correctly(self):
        path = self.tmpdir / "export.csv"
        self._export([
            {**SAMPLE_CAPSTONE, "title": "Req",  "required": True},
            {**SAMPLE_CAPSTONE, "title": "Opt",  "required": False},
        ], path)
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["required"], "yes")
        self.assertEqual(rows[1]["required"], "no")

    def test_export_tags_comma_joined(self):
        cap  = {**SAMPLE_CAPSTONE, "tags": ["robotics", "sensors", "iot"]}
        path = self.tmpdir / "export.csv"
        self._export([cap], path)
        with open(path, newline="", encoding="utf-8-sig") as f:
            row = list(csv.DictReader(f))[0]
        self.assertIn("robotics", row["tags"])
        self.assertIn("sensors",  row["tags"])

    def test_export_empty_list_produces_header_only(self):
        path = self.tmpdir / "empty.csv"
        self._export([], path)
        with open(path, newline="", encoding="utf-8-sig") as f:
            content = f.read()
        self.assertIn("title", content)
        lines = [l for l in content.splitlines() if l.strip()]
        self.assertEqual(len(lines), 1)  # header only


# ══════════════════════════════════════════════════════════════════════════════
class TestCourseManagement(unittest.TestCase):
# ══════════════════════════════════════════════════════════════════════════════

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)
        self.courses_path = self.tmpdir / "courses_data.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _load(self):
        return _load_courses(self.courses_path)

    def _save(self, data):
        _save_courses(self.courses_path, data)

    def test_add_course_to_fall_major(self):
        fall, spring = self._load()
        fall["Foundational Engineering"].append("New Engineering Course")
        self._save({"fall": fall, "spring": spring})
        fall2, _ = self._load()
        self.assertIn("New Engineering Course", fall2["Foundational Engineering"])

    def test_remove_course_from_spring_major(self):
        fall, spring = self._load()
        target = "Engineering Graphics"
        self.assertIn(target, spring["Foundational Engineering"])
        spring["Foundational Engineering"].remove(target)
        self._save({"fall": fall, "spring": spring})
        _, spring2 = self._load()
        self.assertNotIn(target, spring2["Foundational Engineering"])

    def test_restore_defaults_for_major(self):
        fall, spring = self._load()
        fall["Foundational Engineering"] = ["Only Course"]
        self._save({"fall": fall, "spring": spring})
        # Restore
        fall["Foundational Engineering"] = list(_DEFAULT_FALL["Foundational Engineering"])
        self._save({"fall": fall, "spring": spring})
        fall2, _ = self._load()
        self.assertEqual(
            set(fall2["Foundational Engineering"]),
            set(_DEFAULT_FALL["Foundational Engineering"])
        )

    def test_bulk_add_courses(self):
        fall, spring = self._load()
        new_courses = ["Emerging Tech A", "Emerging Tech B", "Emerging Tech C"]
        for c in new_courses:
            if c not in fall["Civil Engineering"]:
                fall["Civil Engineering"].append(c)
        self._save({"fall": fall, "spring": spring})
        fall2, _ = self._load()
        for c in new_courses:
            self.assertIn(c, fall2["Civil Engineering"])

    def test_duplicate_course_not_added_twice(self):
        fall, spring = self._load()
        original_count = len(fall["Foundational Engineering"])
        existing = fall["Foundational Engineering"][0]
        if existing not in fall["Foundational Engineering"]:
            fall["Foundational Engineering"].append(existing)
        # Count should not grow
        self.assertEqual(len(fall["Foundational Engineering"]), original_count)

    def test_removing_course_does_not_affect_other_majors(self):
        fall, spring = self._load()
        fall["Foundational Engineering"].pop()
        self._save({"fall": fall, "spring": spring})
        fall2, _ = self._load()
        # Civil Engineering should be unchanged
        self.assertEqual(
            set(fall2["Civil Engineering"]),
            set(_DEFAULT_FALL["Civil Engineering"])
        )


# ══════════════════════════════════════════════════════════════════════════════
class TestCapstoneManagement(unittest.TestCase):
# ══════════════════════════════════════════════════════════════════════════════

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "capstone_data.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_capstone(self):
        capstones = _load_capstones(self.path)
        capstones.append(SAMPLE_CAPSTONE)
        _save_capstones(self.path, capstones)
        result = _load_capstones(self.path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], SAMPLE_CAPSTONE["title"])

    def test_edit_capstone(self):
        _save_capstones(self.path, [dict(SAMPLE_CAPSTONE)])
        capstones = _load_capstones(self.path)
        capstones[0]["title"] = "Updated Title"
        _save_capstones(self.path, capstones)
        result = _load_capstones(self.path)
        self.assertEqual(result[0]["title"], "Updated Title")

    def test_delete_capstone(self):
        projects = [SAMPLE_CAPSTONE, {**SAMPLE_CAPSTONE, "title": "To Delete"}]
        _save_capstones(self.path, projects)
        capstones = _load_capstones(self.path)
        capstones = [c for c in capstones if c["title"] != "To Delete"]
        _save_capstones(self.path, capstones)
        result = _load_capstones(self.path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], SAMPLE_CAPSTONE["title"])

    def test_required_flag_preserved(self):
        cap = {**SAMPLE_CAPSTONE, "required": True}
        _save_capstones(self.path, [cap])
        result = _load_capstones(self.path)
        self.assertTrue(result[0]["required"])

    def test_required_false_preserved(self):
        cap = {**SAMPLE_CAPSTONE, "required": False}
        _save_capstones(self.path, [cap])
        result = _load_capstones(self.path)
        self.assertFalse(result[0]["required"])

    def test_all_fields_preserved_in_round_trip(self):
        _save_capstones(self.path, [SAMPLE_CAPSTONE])
        result = _load_capstones(self.path)
        for key in SAMPLE_CAPSTONE:
            self.assertEqual(result[0][key], SAMPLE_CAPSTONE[key])

    def test_multiple_projects_order_preserved(self):
        titles   = ["Alpha", "Beta", "Gamma", "Delta"]
        projects = [{**SAMPLE_CAPSTONE, "title": t} for t in titles]
        _save_capstones(self.path, projects)
        result = _load_capstones(self.path)
        self.assertEqual([r["title"] for r in result], titles)


# ══════════════════════════════════════════════════════════════════════════════
class TestParseTagsHelper(unittest.TestCase):
# ══════════════════════════════════════════════════════════════════════════════

    def test_comma_separated(self):
        self.assertEqual(_parse_tags("robotics, iot, sensors"), ["robotics", "iot", "sensors"])

    def test_semicolon_separated(self):
        self.assertEqual(_parse_tags("robotics; iot; sensors"), ["robotics", "iot", "sensors"])

    def test_mixed_separators(self):
        result = _parse_tags("robotics; iot, sensors")
        self.assertIn("robotics", result)
        self.assertIn("iot", result)
        self.assertIn("sensors", result)

    def test_lowercases_all_tags(self):
        result = _parse_tags("Robotics, IoT, Machine Learning")
        self.assertEqual(result, ["robotics", "iot", "machine learning"])

    def test_strips_whitespace(self):
        result = _parse_tags("  robotics  ,  sensors  ")
        self.assertEqual(result, ["robotics", "sensors"])

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(_parse_tags(""), [])

    def test_only_separators_returns_empty_list(self):
        self.assertEqual(_parse_tags(",,,;;;"), [])

    def test_single_tag(self):
        self.assertEqual(_parse_tags("robotics"), ["robotics"])


# ══════════════════════════════════════════════════════════════════════════════
class TestEdgeCases(unittest.TestCase):
# ══════════════════════════════════════════════════════════════════════════════

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_scoring_with_empty_interests_string(self):
        cap   = {**SAMPLE_CAPSTONE}
        score = _score_capstone(cap, set(), "")
        self.assertEqual(score, 0.0)

    def test_scoring_with_no_student_courses_and_matching_interests(self):
        cap   = {"related_courses": ["Robotics"], "tags": ["robotics"]}
        score = _score_capstone(cap, set(), "I love robotics")
        self.assertAlmostEqual(score, 0.35, places=3)

    def test_capstone_with_no_tags_and_no_courses(self):
        cap   = {"related_courses": [], "tags": []}
        score = _score_capstone(cap, set(), "anything")
        self.assertEqual(score, 0.0)

    def test_flat_preserves_all_course_names_exactly(self):
        flat = _flat(_DEFAULT_FALL, ["Mechanical Engineering"])
        for item in flat:
            name = item.split("  |  ")[-1]
            self.assertIn(name, _DEFAULT_FALL["Mechanical Engineering"])

    def test_no_course_name_contains_separator_string(self):
        """Ensure the separator '  |  ' doesn't appear inside any course name."""
        sep = "  |  "
        for major, courses in _DEFAULT_FALL.items():
            for c in courses:
                self.assertNotIn(sep, c, f"Separator found in course name: '{c}'")
        for major, courses in _DEFAULT_SPRING.items():
            for c in courses:
                self.assertNotIn(sep, c, f"Separator found in course name: '{c}'")

    def test_all_majors_present_in_both_default_dicts(self):
        for m in MAJORS:
            self.assertIn(m, _DEFAULT_FALL,   f"Major '{m}' missing from _DEFAULT_FALL")
            self.assertIn(m, _DEFAULT_SPRING, f"Major '{m}' missing from _DEFAULT_SPRING")

    def test_no_empty_course_names_in_defaults(self):
        for major, courses in _DEFAULT_FALL.items():
            for c in courses:
                self.assertTrue(c.strip(), f"Empty course name in fall {major}")
        for major, courses in _DEFAULT_SPRING.items():
            for c in courses:
                self.assertTrue(c.strip(), f"Empty course name in spring {major}")

    def test_capstone_json_with_missing_optional_fields_does_not_crash_scorer(self):
        minimal = {"title": "Minimal", "summary": "Just title and summary."}
        score   = _score_capstone(minimal, {"robotics"}, "robotics")
        self.assertGreaterEqual(score, 0.0)

    def test_large_course_set_does_not_affect_correctness(self):
        all_courses = {c.lower() for m in _DEFAULT_FALL.values() for c in m}
        cap = {
            "related_courses": list(_DEFAULT_FALL["Mechanical Engineering"]),
            "tags": ["thermodynamics", "fluid mechanics"],
        }
        score = _score_capstone(cap, all_courses, "thermodynamics fluid mechanics")
        self.assertAlmostEqual(score, 1.0, places=3)

    def test_write_then_read_courses_file_is_idempotent(self):
        fall, spring = _load_courses(self.tmpdir / "none.json")
        path = self.tmpdir / "courses_data.json"
        _save_courses(path, {"fall": fall, "spring": spring})
        fall2, spring2 = _load_courses(path)
        self.assertEqual(fall, fall2)
        self.assertEqual(spring, spring2)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    test_classes = [
        TestDataLoading,
        TestScoringEngine,
        TestCourseFiltering,
        TestCSVImport,
        TestCSVExport,
        TestCourseManagement,
        TestCapstoneManagement,
        TestParseTagsHelper,
        TestEdgeCases,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total  = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    print(f"\n{'='*60}")
    print(f"  {passed}/{total} tests passed")
    if result.failures or result.errors:
        print(f"  {len(result.failures)} failure(s), {len(result.errors)} error(s)")
    print(f"{'='*60}")

    exit(0 if result.wasSuccessful() else 1)