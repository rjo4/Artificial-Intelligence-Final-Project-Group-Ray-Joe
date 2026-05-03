"""
• Separate Fall and Spring course sections
• Per-row search bar that filters the dropdown in real time
• Major filter checkboxes per section (supports dual-major / mixed selections)
• Capstone suggestion engine (reads capstone_data.json + courses_data.json)
• Interests & Goals free-text field feeds the suggestion engine
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path

# ── Shared data paths ──────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
CAPSTONE_FILE   = BASE_DIR / "capstone_data.json"
COURSES_FILE    = BASE_DIR / "courses_data.json"   # professor-managed overrides

# ── Palette ────────────────────────────────────────────────────────────────────
BG       = "#f0f2f5"
DARK     = "#1e293b"
WHITE    = "#ffffff"
GREEN    = "#10b981"
BLUE     = "#3b82f6"
RED      = "#ef4444"
MUTED    = "#6b7280"
PURPLE   = "#7c3aed"
AMBER    = "#f59e0b"
FALL_C   = "#b45309"   # warm amber
SPRING_C = "#15803d"   # forest green

# ── Major labels (shared between fall & spring) ────────────────────────────────
MAJORS = [
    "Foundational Engineering",
    "Electrical, Computer Engineering & Computer Science",
    "Civil Engineering",
    "Mechanical Engineering",
]
MAJOR_SHORT = {           # abbreviated button labels
    "Foundational Engineering":                               "Found Eng.",
    "Electrical, Computer Engineering & Computer Science":    "ECE / CS",
    "Civil Engineering":                                       "Civil",
    "Mechanical Engineering":                                  "Mechanical",
}

# ── Built-in Fall courses (can be overridden by courses_data.json) ─────────────
_DEFAULT_FALL: dict[str, list[str]] = {
    "Foundational Engineering": [
        "Engineering Orientation",
        "Foundations of Design 1",
        "Foundations of Design 2",
        "Statistics",
        "Engineering Traditions and Culture in Rome",
        "Professional Practice",
        "Industrial Controllers",
    ],
    "Electrical, Computer Engineering & Computer Science": [
        "Introduction to Programming",
        "Electric Circuits",
        "Web Development",
        "Data Structures and Algorithms",
        "Research Experience",
        "Big Data Analytics",
        "Applied Electromagnetics",
        "Signals and Systems",
        "Embedded Hardware-Software Code Design",
        "Embedded Real-Time Applications",
        "Software Development",
        "UI/UX Design",
        "Computer Architecture",
        "Networks and Data Communication",
        "Professional Certification Preparation",
        "Power Systems",
        "Information Science",
        "Advanced Electronics",
        "Theory of Computation",
    ],
    "Civil Engineering": [
        "Surveying",
        "Surveying Lab",
        "Environmental Engineering",
        "Geotechnical Engineering",
        "Structural Analysis",
        "Transportation Engineering",
        "Water Resources Engineering",
        "CFE Fundamentals",
        "CFE Design Seminar 1",
    ],
    "Mechanical Engineering": [
        "Engineering Material Science",
        "Thermodynamics",
        "Design for Manufacturing",
        "Computer Applications",
        "Fundamentals of Experimentation",
        "Machine Component Design",
        "3-D Modeling and Design",
        "Dynamic Systems Modeling",
        "Fluid Mechanics",
        "Sensors and Measurements",
        "Process of Design",
        "Mechatronics",
        "Computational Fluid Dynamics",
        "Advanced Thermodynamics",
        "Engineering Analysis",
    ],
}

# ── Built-in Spring courses ────────────────────────────────────────────────────
_DEFAULT_SPRING: dict[str, list[str]] = {
    "Foundational Engineering": [
        "Engineering Graphics",
        "Technical Writing for Engineers",
        "Engineering Economics",
        "Ethics in Engineering",
        "Project Management",
        "Capstone Preparation",
        "Innovation and Entrepreneurship",
        "Sustainability in Engineering",
    ],
    "Electrical, Computer Engineering & Computer Science": [
        "Object-Oriented Programming",
        "Digital Logic Design",
        "Machine Learning",
        "Cybersecurity Fundamentals",
        "Database Systems",
        "Operating Systems",
        "Computer Vision",
        "Wireless Communications",
        "VLSI Design",
        "Compiler Design",
        "Robotics Programming",
        "Artificial Intelligence",
        "Mobile App Development",
        "Cloud Computing",
        "Parallel Computing",
        "Natural Language Processing",
        "Internet of Things",
        "Quantum Computing Fundamentals",
        "Deep Learning",
        "Human-Computer Interaction",
    ],
    "Civil Engineering": [
        "Reinforced Concrete Design",
        "Steel Structure Design",
        "Foundation Engineering",
        "Construction Management",
        "GIS and Remote Sensing",
        "Hydraulics Lab",
        "Bridge Design",
        "Urban Planning",
        "Earthquake Engineering",
        "Building Information Modeling",
        "CFE Design Seminar 2",
        "Coastal Engineering",
        "Traffic Engineering",
        "Environmental Remediation",
    ],
    "Mechanical Engineering": [
        "Heat Transfer",
        "Mechanical Vibrations",
        "Manufacturing Processes",
        "Control Systems",
        "Finite Element Analysis",
        "Robotics",
        "HVAC Systems",
        "Aerospace Fundamentals",
        "Renewable Energy Systems",
        "Composite Materials",
        "Advanced Manufacturing",
        "Capstone Design",
        "Biomechanics",
        "Additive Manufacturing",
        "Tribology",
        "Acoustics and Noise Control",
    ],
}


def _load_courses() -> tuple[dict, dict]:
    """Return (fall_dict, spring_dict), merging professor overrides if present."""
    fall   = {k: list(v) for k, v in _DEFAULT_FALL.items()}
    spring = {k: list(v) for k, v in _DEFAULT_SPRING.items()}
    if COURSES_FILE.exists():
        try:
            data = json.loads(COURSES_FILE.read_text(encoding="utf-8"))
            for maj, courses in data.get("fall", {}).items():
                fall[maj] = courses
            for maj, courses in data.get("spring", {}).items():
                spring[maj] = courses
        except Exception:
            pass
    return fall, spring


def _flat(by_cat: dict[str, list[str]], majors: list[str]) -> list[str]:
    """Flatten selected majors into 'Major  |  Course' strings."""
    out = []
    for m in majors:
        for c in by_cat.get(m, []):
            out.append(f"{m}  |  {c}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
class StudentTrackerApp:
# ══════════════════════════════════════════════════════════════════════════════

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Student Course Tracker")
        self.root.geometry("1000x860")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.fall_dict, self.spring_dict = _load_courses()

        # Row lists:  each entry is a dict with keys:
        #   frame, search_var, search_entry, combo_var, combo, btn
        self.fall_rows:   list[dict] = []
        self.spring_rows: list[dict] = []

        # Major filter checkboxes (BooleanVar per season per major)
        self.fall_major_vars:   dict[str, tk.BooleanVar] = {}
        self.spring_major_vars: dict[str, tk.BooleanVar] = {}

        self._build_ui()

    # ── Layout scaffolding ──────────────────────────────────────────────────

    def _build_ui(self):
        canvas    = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.inner    = tk.Frame(canvas, bg=BG)
        self.inner_id = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(self.inner_id, width=e.width),
        )
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"),
        )

        self._build_header()
        self._build_name_card()
        self._build_semester_card("Fall",   "🍂", FALL_C,   self.fall_rows,   self.fall_dict,   self.fall_major_vars)
        self._build_semester_card("Spring", "🌸", SPRING_C, self.spring_rows, self.spring_dict, self.spring_major_vars)
        self._build_interests_card()
        self._build_capstone_frame()
        self._build_save_bar()

    def _card(self, title: str, accent: str = DARK) -> tk.Frame:
        wrapper = tk.Frame(self.inner, bg=BG, pady=8, padx=20)
        wrapper.pack(fill="x")
        card = tk.Frame(wrapper, bg=WHITE, highlightbackground="#d1d5db", highlightthickness=1)
        card.pack(fill="x")
        bar = tk.Frame(card, bg=accent, pady=10, padx=16)
        bar.pack(fill="x")
        tk.Label(bar, text=title, font=("Helvetica", 13, "bold"), fg="white", bg=accent).pack(anchor="w")
        body = tk.Frame(card, bg=WHITE, padx=16, pady=14)
        body.pack(fill="x")
        return body

    # ── Header ──────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.inner, bg=DARK, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🎓  Student Course Tracker",
                 font=("Helvetica", 22, "bold"), fg="white", bg=DARK).pack()
        tk.Label(hdr,
                 text="Track completed courses · Filter by major · Discover matching capstones",
                 font=("Helvetica", 10), fg="#94a3b8", bg=DARK).pack(pady=(3, 0))

    # ── Name card ───────────────────────────────────────────────────────────

    def _build_name_card(self):
        body = self._card("👤  Student Information")
        tk.Label(body, text="Full Name:", font=("Helvetica", 11),
                 bg=WHITE, fg="#374151").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(body, textvariable=self.name_var,
                  font=("Helvetica", 11), width=44).grid(row=1, column=0, sticky="ew", pady=(4, 0))
        body.columnconfigure(0, weight=1)

    # ── Semester card (reused for both Fall and Spring) ──────────────────────

    def _build_semester_card(
        self,
        season: str,
        emoji: str,
        accent: str,
        rows: list,
        course_dict: dict,
        major_vars: dict,
    ):
        body = self._card(f"{emoji}  {season} Classes", accent)

        # ── Major filter bar ────────────────────────────────────────────────
        filter_frame = tk.Frame(body, bg=WHITE)
        filter_frame.pack(fill="x", pady=(0, 10))

        tk.Label(filter_frame, text="Filter by major:",
                 font=("Helvetica", 10, "bold"), bg=WHITE, fg=DARK).pack(side="left", padx=(0, 10))

        for maj in MAJORS:
            var = tk.BooleanVar(value=True)
            major_vars[maj] = var
            cb = tk.Checkbutton(
                filter_frame,
                text=MAJOR_SHORT[maj],
                variable=var,
                font=("Helvetica", 9),
                bg=WHITE, fg=DARK,
                activebackground=WHITE,
                selectcolor=WHITE,
                cursor="hand2",
                command=lambda s=season: self._on_major_filter_changed(s),
            )
            cb.pack(side="left", padx=4)

        tk.Label(filter_frame,
                 text="  ← uncheck to hide a major's courses",
                 font=("Helvetica", 8, "italic"), bg=WHITE, fg=MUTED).pack(side="left")

        # ── Column header ───────────────────────────────────────────────────
        hdr = tk.Frame(body, bg="#f8fafc", pady=4, padx=4,
                       highlightbackground="#e2e8f0", highlightthickness=1)
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text="#",      width=4,  font=("Helvetica", 9, "bold"), bg="#f8fafc", fg=MUTED).pack(side="left")
        tk.Label(hdr, text="Search", width=18, font=("Helvetica", 9, "bold"), bg="#f8fafc", fg=MUTED).pack(side="left", padx=(4, 0))
        tk.Label(hdr, text="Course (Major  |  Name)",
                 font=("Helvetica", 9, "bold"), bg="#f8fafc", fg=MUTED).pack(side="left", padx=(8, 0))

        # ── Rows container ──────────────────────────────────────────────────
        container = tk.Frame(body, bg=WHITE)
        container.pack(fill="x")

        if season == "Fall":
            self.fall_container = container
        else:
            self.spring_container = container

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=10)

        tk.Button(
            body, text="＋  Add Class",
            command=lambda: self._add_row(rows, container, course_dict, major_vars, season),
            bg=GREEN, fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=7, cursor="hand2",
            activebackground="#059669", activeforeground="white",
        ).pack(anchor="w")

        # Start with two rows
        self._add_row(rows, container, course_dict, major_vars, season)
        self._add_row(rows, container, course_dict, major_vars, season)

    # ── Course row ───────────────────────────────────────────────────────────

    def _add_row(
        self,
        rows: list,
        container: tk.Frame,
        course_dict: dict,
        major_vars: dict,
        season: str,
    ):
        idx = len(rows) + 1

        row_frame = tk.Frame(container, bg=WHITE, pady=3)
        row_frame.pack(fill="x")

        # Row number label
        num_lbl = tk.Label(row_frame, text=f"{idx}.",
                           font=("Helvetica", 10), bg=WHITE, fg=MUTED, width=4, anchor="e")
        num_lbl.pack(side="left")

        # ── Search entry ────────────────────────────────────────────────────
        search_var = tk.StringVar()
        search_entry = ttk.Entry(row_frame, textvariable=search_var,
                                 font=("Helvetica", 10), width=16)
        search_entry.pack(side="left", padx=(4, 4))

        # Placeholder-style hint
        search_entry.insert(0, "🔍 search…")
        search_entry.configure(foreground=MUTED)

        def _on_focus_in(e, se=search_entry, sv=search_var):
            if se.get() == "🔍 search…":
                se.delete(0, "end")
                se.configure(foreground=DARK)

        def _on_focus_out_search(e, se=search_entry, sv=search_var):
            if not se.get().strip():
                se.delete(0, "end")
                se.insert(0, "🔍 search…")
                se.configure(foreground=MUTED)

        search_entry.bind("<FocusIn>",  _on_focus_in)
        search_entry.bind("<FocusOut>", _on_focus_out_search)

        # ── Combobox ────────────────────────────────────────────────────────
        combo_var = tk.StringVar(value="")
        combo = ttk.Combobox(row_frame, textvariable=combo_var,
                             state="readonly", font=("Helvetica", 10), width=58)
        combo.pack(side="left", padx=(0, 8))

        # ── Remove button ───────────────────────────────────────────────────
        rm_btn = tk.Button(
            row_frame, text="✕",
            bg=RED, fg="white",
            font=("Helvetica", 9, "bold"),
            relief="flat", padx=6, pady=2, cursor="hand2",
            activebackground="#dc2626", activeforeground="white",
        )
        rm_btn.pack(side="left")

        row = {
            "frame":       row_frame,
            "num_lbl":     num_lbl,
            "search_var":  search_var,
            "search_entry": search_entry,
            "combo_var":   combo_var,
            "combo":       combo,
            "btn":         rm_btn,
            "rows":        rows,
            "course_dict": course_dict,
            "major_vars":  major_vars,
            "season":      season,
        }
        rows.append(row)

        # Wire callbacks
        search_var.trace_add("write", lambda *_, r=row: self._on_search_changed(r))
        combo_var.trace_add("write",  lambda *_, s=season: self._on_combo_changed(s))
        rm_btn.config(command=lambda r=row: self._remove_row(r))

        self._refresh_combos_for_season(season)
        self._update_remove_buttons(rows)

    def _remove_row(self, row: dict):
        rows = row["rows"]
        if len(rows) <= 1:
            return
        rows.remove(row)
        row["frame"].destroy()
        self._renumber(rows)
        self._refresh_combos_for_season(row["season"])
        self._update_remove_buttons(rows)

    def _renumber(self, rows: list):
        for i, r in enumerate(rows):
            r["num_lbl"].config(text=f"{i + 1}.")

    def _update_remove_buttons(self, rows: list):
        only_one = len(rows) == 1
        for r in rows:
            if only_one:
                r["btn"].config(state="disabled", bg="#9ca3af", cursor="arrow")
            else:
                r["btn"].config(state="normal", bg=RED, cursor="hand2")

    # ── Filter logic ────────────────────────────────────────────────────────

    def _on_major_filter_changed(self, season: str):
        self._refresh_combos_for_season(season)

    def _on_search_changed(self, row: dict):
        self._refresh_single_combo(row)

    def _on_combo_changed(self, season: str):
        self._refresh_combos_for_season(season)

    def _active_major_list(self, major_vars: dict) -> list[str]:
        """Return majors whose checkbox is ticked."""
        return [m for m in MAJORS if major_vars[m].get()]

    def _refresh_combos_for_season(self, season: str):
        rows = self.fall_rows if season == "Fall" else self.spring_rows
        for row in rows:
            self._refresh_single_combo(row)

    def _refresh_single_combo(self, row: dict):
        season     = row["season"]
        rows       = row["rows"]
        major_vars = row["major_vars"]
        course_dict = row["course_dict"]

        active_majors = self._active_major_list(major_vars)
        full_list     = _flat(course_dict, active_majors)

        # Remove courses already chosen by other rows in the same section
        chosen_by_others = {
            r["combo_var"].get()
            for r in rows
            if r is not row and r["combo_var"].get()
        }
        available = [c for c in full_list if c not in chosen_by_others]

        # Apply search filter
        raw_search = row["search_var"].get()
        if raw_search and raw_search != "🔍 search…":
            q = raw_search.lower()
            available = [c for c in available if q in c.lower()]

        # Keep current selection even if it's hidden by filter
        current = row["combo_var"].get()
        if current and current not in available:
            available = [current] + available

        row["combo"].config(values=available)

    # ── Interests card ───────────────────────────────────────────────────────

    def _build_interests_card(self):
        body = self._card("💡  Interests & Goals", PURPLE)
        tk.Label(
            body,
            text=(
                "Describe your career goals, research interests, or any topic areas you'd "
                "like your capstone to focus on. The suggestion engine weighs these keywords "
                "alongside your completed courses."
            ),
            font=("Helvetica", 11), bg=WHITE, fg="#374151",
            wraplength=820, justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self.interests_text = tk.Text(
            body, font=("Helvetica", 11), height=4,
            wrap="word", relief="solid", bd=1,
        )
        self.interests_text.pack(fill="x")

        tk.Button(
            body, text="🔄  Refresh Capstone Suggestions",
            command=self._load_and_show_suggestions,
            bg=PURPLE, fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=7, cursor="hand2",
            activebackground="#6d28d9", activeforeground="white",
        ).pack(anchor="w", pady=(10, 0))

    # ── Capstone suggestions ─────────────────────────────────────────────────

    def _build_capstone_frame(self):
        body = self._card("🚀  Capstone Project Suggestions", AMBER)
        self.capstone_body = body
        tk.Label(
            body,
            text='Fill in your courses and interests above, then click "Refresh Capstone Suggestions".',
            font=("Helvetica", 10, "italic"), bg=WHITE, fg=MUTED,
            wraplength=820,
        ).pack(anchor="w", pady=8)

    def _load_and_show_suggestions(self):
        for w in self.capstone_body.winfo_children():
            w.destroy()

        capstones: list[dict] = []
        if CAPSTONE_FILE.exists():
            try:
                capstones = json.loads(CAPSTONE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass

        if not capstones:
            tk.Label(
                self.capstone_body,
                text="No capstone projects found. Ask a professor to run professor_capstone.py.",
                font=("Helvetica", 10, "italic"), bg=WHITE, fg=MUTED,
            ).pack(anchor="w", pady=8)
            return

        student_courses: set[str] = set()
        for r in self.fall_rows + self.spring_rows:
            val = r["combo_var"].get()
            if val:
                student_courses.add(val.split("  |  ")[-1].lower())

        interests = self.interests_text.get("1.0", "end").strip().lower()

        scored: list[tuple[float, dict]] = []
        for cap in capstones:
            related = [c.lower() for c in cap.get("related_courses", [])]
            tags    = [t.lower() for t in cap.get("tags", [])]
            cs = sum(1 for c in related if c in student_courses) / max(len(related), 1)
            ts = sum(1 for t in tags    if t in interests)       / max(len(tags), 1)
            scored.append((round(cs * 0.65 + ts * 0.35, 4), cap))

        scored.sort(key=lambda x: x[0], reverse=True)

        if scored[0][0] == 0.0:
            tk.Label(
                self.capstone_body,
                text=(
                    "No strong matches yet — make sure your interest keywords align with "
                    "capstone tags, and that you have selected completed courses."
                ),
                font=("Helvetica", 10, "italic"), bg=WHITE, fg=MUTED, wraplength=820,
            ).pack(anchor="w", pady=8)
            return

        n = min(5, len(scored))
        tk.Label(self.capstone_body,
                 text=f"Top {n} matching capstone project{'s' if n != 1 else ''}:",
                 font=("Helvetica", 11, "bold"), bg=WHITE, fg=DARK).pack(anchor="w", pady=(0, 8))

        palette = [GREEN, BLUE, PURPLE, AMBER, "#ec4899"]
        for i, (score, cap) in enumerate(scored[:n]):
            self._render_suggestion(cap, score, palette[i % len(palette)])

    def _render_suggestion(self, cap: dict, score: float, color: str):
        pct   = int(score * 100)
        outer = tk.Frame(self.capstone_body, bg="#f8fafc",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        outer.pack(fill="x", pady=4)
        tk.Frame(outer, bg=color, width=6).pack(side="left", fill="y")

        body = tk.Frame(outer, bg="#f8fafc", padx=12, pady=10)
        body.pack(side="left", fill="x", expand=True)

        title_row = tk.Frame(body, bg="#f8fafc")
        title_row.pack(fill="x")
        required_badge = "  ⭐ Required" if cap.get("required") else ""
        tk.Label(title_row, text=cap.get("title", "Untitled"),
                 font=("Helvetica", 12, "bold"), bg="#f8fafc", fg=DARK).pack(side="left")
        tk.Label(title_row, text=f"  {pct}% match{required_badge}",
                 font=("Helvetica", 10, "bold"), bg="#f8fafc", fg=color).pack(side="left")

        if cap.get("summary"):
            tk.Label(body, text=cap["summary"], font=("Helvetica", 10),
                     bg="#f8fafc", fg="#374151", wraplength=760, justify="left").pack(anchor="w", pady=(4, 4))

        related = cap.get("related_courses", [])
        if related:
            f = tk.Frame(body, bg="#f8fafc"); f.pack(anchor="w", pady=(0, 4))
            tk.Label(f, text="Courses: ", font=("Helvetica", 9, "bold"),
                     bg="#f8fafc", fg=MUTED).pack(side="left")
            for c in related[:7]:
                tk.Label(f, text=c, font=("Helvetica", 9),
                         bg="#dcfce7", fg="#166534", padx=5, pady=1).pack(side="left", padx=(0, 3))

        tags = cap.get("tags", [])
        if tags:
            f = tk.Frame(body, bg="#f8fafc"); f.pack(anchor="w")
            for t in tags[:10]:
                tk.Label(f, text=f"#{t}", font=("Helvetica", 9),
                         bg="#ede9fe", fg="#4c1d95", padx=5, pady=1).pack(side="left", padx=(0, 3))

    # ── Save bar ─────────────────────────────────────────────────────────────

    def _build_save_bar(self):
        bar = tk.Frame(self.inner, bg=BG, pady=14, padx=20)
        bar.pack(fill="x")
        tk.Button(
            bar, text="💾  Save All",
            command=self._save_all,
            bg=BLUE, fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat", padx=24, pady=10, cursor="hand2",
            activebackground="#2563eb", activeforeground="white",
        ).pack(side="left")
        self.save_status = tk.Label(bar, text="", font=("Helvetica", 10, "italic"),
                                    bg=BG, fg="#16a34a")
        self.save_status.pack(side="left", padx=14)

    def _save_all(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter the student name before saving.")
            return

        fall_sel   = [r["combo_var"].get().split("  |  ")[-1]
                      for r in self.fall_rows   if r["combo_var"].get()]
        spring_sel = [r["combo_var"].get().split("  |  ")[-1]
                      for r in self.spring_rows if r["combo_var"].get()]

        if not fall_sel and not spring_sel:
            messagebox.showwarning("No Courses", "Please select at least one course.")
            return

        lines = [f"Student: {name}"]
        if fall_sel:
            lines.append(f"\n🍂 Fall ({len(fall_sel)}): {', '.join(fall_sel)}")
        if spring_sel:
            lines.append(f"\n🌸 Spring ({len(spring_sel)}): {', '.join(spring_sel)}")

        messagebox.showinfo("Saved ✓", "\n".join(lines))
        total = len(fall_sel) + len(spring_sel)
        self.save_status.config(
            text=f"✔  Saved {name}  ·  {total} course(s)  "
                 f"[{len(fall_sel)} fall / {len(spring_sel)} spring]"
        )


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TCombobox", padding=4)
    style.configure("TEntry",    padding=4)
    StudentTrackerApp(root)
"""
student_tracker.py  –  Student Course Tracker
• Separate Fall and Spring course sections
• Per-row search bar that filters the dropdown in real time
• Major filter checkboxes per section (supports dual-major / mixed selections)
• Capstone suggestion engine (reads capstone_data.json + courses_data.json)
• Interests & Goals free-text field feeds the suggestion engine
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path

# ── Shared data paths ──────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
CAPSTONE_FILE   = BASE_DIR / "capstone_data.json"
COURSES_FILE    = BASE_DIR / "courses_data.json"   # professor-managed overrides

# ── Palette ────────────────────────────────────────────────────────────────────
BG       = "#f0f2f5"
DARK     = "#1e293b"
WHITE    = "#ffffff"
GREEN    = "#10b981"
BLUE     = "#3b82f6"
RED      = "#ef4444"
MUTED    = "#6b7280"
PURPLE   = "#7c3aed"
AMBER    = "#f59e0b"
FALL_C   = "#b45309"   # warm amber
SPRING_C = "#15803d"   # forest green

# ── Major labels (shared between fall & spring) ────────────────────────────────
MAJORS = [
    "Foundational Engineering",
    "Electrical, Computer Engineering & Computer Science",
    "Civil Engineering",
    "Mechanical Engineering",
]
MAJOR_SHORT = {           # abbreviated button labels
    "Foundational Engineering":                               "Found Eng.",
    "Electrical, Computer Engineering & Computer Science":    "ECE / CS",
    "Civil Engineering":                                       "Civil",
    "Mechanical Engineering":                                  "Mechanical",
}

# ── Built-in Fall courses (can be overridden by courses_data.json) ─────────────
_DEFAULT_FALL: dict[str, list[str]] = {
    "Foundational Engineering": [
        "Engineering Orientation",
        "Foundations of Design 1",
        "Foundations of Design 2",
        "Statistics",
        "Engineering Traditions and Culture in Rome",
        "Professional Practice",
        "Industrial Controllers",
    ],
    "Electrical, Computer Engineering & Computer Science": [
        "Introduction to Programming",
        "Electric Circuits",
        "Web Development",
        "Data Structures and Algorithms",
        "Research Experience",
        "Big Data Analytics",
        "Applied Electromagnetics",
        "Signals and Systems",
        "Embedded Hardware-Software Code Design",
        "Embedded Real-Time Applications",
        "Software Development",
        "UI/UX Design",
        "Computer Architecture",
        "Networks and Data Communication",
        "Professional Certification Preparation",
        "Power Systems",
        "Information Science",
        "Advanced Electronics",
        "Theory of Computation",
    ],
    "Civil Engineering": [
        "Surveying",
        "Surveying Lab",
        "Environmental Engineering",
        "Geotechnical Engineering",
        "Structural Analysis",
        "Transportation Engineering",
        "Water Resources Engineering",
        "CFE Fundamentals",
        "CFE Design Seminar 1",
    ],
    "Mechanical Engineering": [
        "Engineering Material Science",
        "Thermodynamics",
        "Design for Manufacturing",
        "Computer Applications",
        "Fundamentals of Experimentation",
        "Machine Component Design",
        "3-D Modeling and Design",
        "Dynamic Systems Modeling",
        "Fluid Mechanics",
        "Sensors and Measurements",
        "Process of Design",
        "Mechatronics",
        "Computational Fluid Dynamics",
        "Advanced Thermodynamics",
        "Engineering Analysis",
    ],
}

# ── Built-in Spring courses ────────────────────────────────────────────────────
_DEFAULT_SPRING: dict[str, list[str]] = {
    "Foundational Engineering": [
        "Engineering Graphics",
        "Technical Writing for Engineers",
        "Engineering Economics",
        "Ethics in Engineering",
        "Project Management",
        "Capstone Preparation",
        "Innovation and Entrepreneurship",
        "Sustainability in Engineering",
    ],
    "Electrical, Computer Engineering & Computer Science": [
        "Object-Oriented Programming",
        "Digital Logic Design",
        "Machine Learning",
        "Cybersecurity Fundamentals",
        "Database Systems",
        "Operating Systems",
        "Computer Vision",
        "Wireless Communications",
        "VLSI Design",
        "Compiler Design",
        "Robotics Programming",
        "Artificial Intelligence",
        "Mobile App Development",
        "Cloud Computing",
        "Parallel Computing",
        "Natural Language Processing",
        "Internet of Things",
        "Quantum Computing Fundamentals",
        "Deep Learning",
        "Human-Computer Interaction",
    ],
    "Civil Engineering": [
        "Reinforced Concrete Design",
        "Steel Structure Design",
        "Foundation Engineering",
        "Construction Management",
        "GIS and Remote Sensing",
        "Hydraulics Lab",
        "Bridge Design",
        "Urban Planning",
        "Earthquake Engineering",
        "Building Information Modeling",
        "CFE Design Seminar 2",
        "Coastal Engineering",
        "Traffic Engineering",
        "Environmental Remediation",
    ],
    "Mechanical Engineering": [
        "Heat Transfer",
        "Mechanical Vibrations",
        "Manufacturing Processes",
        "Control Systems",
        "Finite Element Analysis",
        "Robotics",
        "HVAC Systems",
        "Aerospace Fundamentals",
        "Renewable Energy Systems",
        "Composite Materials",
        "Advanced Manufacturing",
        "Capstone Design",
        "Biomechanics",
        "Additive Manufacturing",
        "Tribology",
        "Acoustics and Noise Control",
    ],
}


def _load_courses() -> tuple[dict, dict]:
    """Return (fall_dict, spring_dict), merging professor overrides if present."""
    fall   = {k: list(v) for k, v in _DEFAULT_FALL.items()}
    spring = {k: list(v) for k, v in _DEFAULT_SPRING.items()}
    if COURSES_FILE.exists():
        try:
            data = json.loads(COURSES_FILE.read_text(encoding="utf-8"))
            for maj, courses in data.get("fall", {}).items():
                fall[maj] = courses
            for maj, courses in data.get("spring", {}).items():
                spring[maj] = courses
        except Exception:
            pass
    return fall, spring


def _flat(by_cat: dict[str, list[str]], majors: list[str]) -> list[str]:
    """Flatten selected majors into 'Major  |  Course' strings."""
    out = []
    for m in majors:
        for c in by_cat.get(m, []):
            out.append(f"{m}  |  {c}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
class StudentTrackerApp:
# ══════════════════════════════════════════════════════════════════════════════

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Student Course Tracker")
        self.root.geometry("1000x860")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.fall_dict, self.spring_dict = _load_courses()

        # Row lists:  each entry is a dict with keys:
        #   frame, search_var, search_entry, combo_var, combo, btn
        self.fall_rows:   list[dict] = []
        self.spring_rows: list[dict] = []

        # Major filter checkboxes (BooleanVar per season per major)
        self.fall_major_vars:   dict[str, tk.BooleanVar] = {}
        self.spring_major_vars: dict[str, tk.BooleanVar] = {}

        self._build_ui()

    # ── Layout scaffolding ──────────────────────────────────────────────────

    def _build_ui(self):
        canvas    = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.inner    = tk.Frame(canvas, bg=BG)
        self.inner_id = canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(self.inner_id, width=e.width),
        )
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"),
        )

        self._build_header()
        self._build_name_card()
        self._build_semester_card("Fall",   "🍂", FALL_C,   self.fall_rows,   self.fall_dict,   self.fall_major_vars)
        self._build_semester_card("Spring", "🌸", SPRING_C, self.spring_rows, self.spring_dict, self.spring_major_vars)
        self._build_interests_card()
        self._build_capstone_frame()
        self._build_save_bar()

    def _card(self, title: str, accent: str = DARK) -> tk.Frame:
        wrapper = tk.Frame(self.inner, bg=BG, pady=8, padx=20)
        wrapper.pack(fill="x")
        card = tk.Frame(wrapper, bg=WHITE, highlightbackground="#d1d5db", highlightthickness=1)
        card.pack(fill="x")
        bar = tk.Frame(card, bg=accent, pady=10, padx=16)
        bar.pack(fill="x")
        tk.Label(bar, text=title, font=("Helvetica", 13, "bold"), fg="white", bg=accent).pack(anchor="w")
        body = tk.Frame(card, bg=WHITE, padx=16, pady=14)
        body.pack(fill="x")
        return body

    # ── Header ──────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self.inner, bg=DARK, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🎓  Student Course Tracker",
                 font=("Helvetica", 22, "bold"), fg="white", bg=DARK).pack()
        tk.Label(hdr,
                 text="Track completed courses · Filter by major · Discover matching capstones",
                 font=("Helvetica", 10), fg="#94a3b8", bg=DARK).pack(pady=(3, 0))

    # ── Name card ───────────────────────────────────────────────────────────

    def _build_name_card(self):
        body = self._card("👤  Student Information")
        tk.Label(body, text="Full Name:", font=("Helvetica", 11),
                 bg=WHITE, fg="#374151").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(body, textvariable=self.name_var,
                  font=("Helvetica", 11), width=44).grid(row=1, column=0, sticky="ew", pady=(4, 0))
        body.columnconfigure(0, weight=1)

    # ── Semester card (reused for both Fall and Spring) ──────────────────────

    def _build_semester_card(
        self,
        season: str,
        emoji: str,
        accent: str,
        rows: list,
        course_dict: dict,
        major_vars: dict,
    ):
        body = self._card(f"{emoji}  {season} Classes", accent)

        # ── Major filter bar ────────────────────────────────────────────────
        filter_frame = tk.Frame(body, bg=WHITE)
        filter_frame.pack(fill="x", pady=(0, 10))

        tk.Label(filter_frame, text="Filter by major:",
                 font=("Helvetica", 10, "bold"), bg=WHITE, fg=DARK).pack(side="left", padx=(0, 10))

        for maj in MAJORS:
            var = tk.BooleanVar(value=True)
            major_vars[maj] = var
            cb = tk.Checkbutton(
                filter_frame,
                text=MAJOR_SHORT[maj],
                variable=var,
                font=("Helvetica", 9),
                bg=WHITE, fg=DARK,
                activebackground=WHITE,
                selectcolor=WHITE,
                cursor="hand2",
                command=lambda s=season: self._on_major_filter_changed(s),
            )
            cb.pack(side="left", padx=4)

        tk.Label(filter_frame,
                 text="  ← uncheck to hide a major's courses",
                 font=("Helvetica", 8, "italic"), bg=WHITE, fg=MUTED).pack(side="left")

        # ── Column header ───────────────────────────────────────────────────
        hdr = tk.Frame(body, bg="#f8fafc", pady=4, padx=4,
                       highlightbackground="#e2e8f0", highlightthickness=1)
        hdr.pack(fill="x", pady=(0, 6))
        tk.Label(hdr, text="#",      width=4,  font=("Helvetica", 9, "bold"), bg="#f8fafc", fg=MUTED).pack(side="left")
        tk.Label(hdr, text="Search", width=18, font=("Helvetica", 9, "bold"), bg="#f8fafc", fg=MUTED).pack(side="left", padx=(4, 0))
        tk.Label(hdr, text="Course (Major  |  Name)",
                 font=("Helvetica", 9, "bold"), bg="#f8fafc", fg=MUTED).pack(side="left", padx=(8, 0))

        # ── Rows container ──────────────────────────────────────────────────
        container = tk.Frame(body, bg=WHITE)
        container.pack(fill="x")

        if season == "Fall":
            self.fall_container = container
        else:
            self.spring_container = container

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=10)

        tk.Button(
            body, text="＋  Add Class",
            command=lambda: self._add_row(rows, container, course_dict, major_vars, season),
            bg=GREEN, fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=7, cursor="hand2",
            activebackground="#059669", activeforeground="white",
        ).pack(anchor="w")

        # Start with two rows
        self._add_row(rows, container, course_dict, major_vars, season)
        self._add_row(rows, container, course_dict, major_vars, season)

    # ── Course row ───────────────────────────────────────────────────────────

    def _add_row(
        self,
        rows: list,
        container: tk.Frame,
        course_dict: dict,
        major_vars: dict,
        season: str,
    ):
        idx = len(rows) + 1

        row_frame = tk.Frame(container, bg=WHITE, pady=3)
        row_frame.pack(fill="x")

        # Row number label
        num_lbl = tk.Label(row_frame, text=f"{idx}.",
                           font=("Helvetica", 10), bg=WHITE, fg=MUTED, width=4, anchor="e")
        num_lbl.pack(side="left")

        # ── Search entry ────────────────────────────────────────────────────
        search_var = tk.StringVar()
        search_entry = ttk.Entry(row_frame, textvariable=search_var,
                                 font=("Helvetica", 10), width=16)
        search_entry.pack(side="left", padx=(4, 4))

        # Placeholder-style hint
        search_entry.insert(0, "🔍 search…")
        search_entry.configure(foreground=MUTED)

        def _on_focus_in(e, se=search_entry, sv=search_var):
            if se.get() == "🔍 search…":
                se.delete(0, "end")
                se.configure(foreground=DARK)

        def _on_focus_out_search(e, se=search_entry, sv=search_var):
            if not se.get().strip():
                se.delete(0, "end")
                se.insert(0, "🔍 search…")
                se.configure(foreground=MUTED)

        search_entry.bind("<FocusIn>",  _on_focus_in)
        search_entry.bind("<FocusOut>", _on_focus_out_search)

        # ── Combobox ────────────────────────────────────────────────────────
        combo_var = tk.StringVar(value="")
        combo = ttk.Combobox(row_frame, textvariable=combo_var,
                             state="readonly", font=("Helvetica", 10), width=58)
        combo.pack(side="left", padx=(0, 8))

        # ── Remove button ───────────────────────────────────────────────────
        rm_btn = tk.Button(
            row_frame, text="✕",
            bg=RED, fg="white",
            font=("Helvetica", 9, "bold"),
            relief="flat", padx=6, pady=2, cursor="hand2",
            activebackground="#dc2626", activeforeground="white",
        )
        rm_btn.pack(side="left")

        row = {
            "frame":       row_frame,
            "num_lbl":     num_lbl,
            "search_var":  search_var,
            "search_entry": search_entry,
            "combo_var":   combo_var,
            "combo":       combo,
            "btn":         rm_btn,
            "rows":        rows,
            "course_dict": course_dict,
            "major_vars":  major_vars,
            "season":      season,
        }
        rows.append(row)

        # Wire callbacks
        search_var.trace_add("write", lambda *_, r=row: self._on_search_changed(r))
        combo_var.trace_add("write",  lambda *_, s=season: self._on_combo_changed(s))
        rm_btn.config(command=lambda r=row: self._remove_row(r))

        self._refresh_combos_for_season(season)
        self._update_remove_buttons(rows)

    def _remove_row(self, row: dict):
        rows = row["rows"]
        if len(rows) <= 1:
            return
        rows.remove(row)
        row["frame"].destroy()
        self._renumber(rows)
        self._refresh_combos_for_season(row["season"])
        self._update_remove_buttons(rows)

    def _renumber(self, rows: list):
        for i, r in enumerate(rows):
            r["num_lbl"].config(text=f"{i + 1}.")

    def _update_remove_buttons(self, rows: list):
        only_one = len(rows) == 1
        for r in rows:
            if only_one:
                r["btn"].config(state="disabled", bg="#9ca3af", cursor="arrow")
            else:
                r["btn"].config(state="normal", bg=RED, cursor="hand2")

    # ── Filter logic ────────────────────────────────────────────────────────

    def _on_major_filter_changed(self, season: str):
        self._refresh_combos_for_season(season)

    def _on_search_changed(self, row: dict):
        self._refresh_single_combo(row)

    def _on_combo_changed(self, season: str):
        self._refresh_combos_for_season(season)

    def _active_major_list(self, major_vars: dict) -> list[str]:
        """Return majors whose checkbox is ticked."""
        return [m for m in MAJORS if major_vars[m].get()]

    def _refresh_combos_for_season(self, season: str):
        rows = self.fall_rows if season == "Fall" else self.spring_rows
        for row in rows:
            self._refresh_single_combo(row)

    def _refresh_single_combo(self, row: dict):
        season     = row["season"]
        rows       = row["rows"]
        major_vars = row["major_vars"]
        course_dict = row["course_dict"]

        active_majors = self._active_major_list(major_vars)
        full_list     = _flat(course_dict, active_majors)

        # Remove courses already chosen by other rows in the same section
        chosen_by_others = {
            r["combo_var"].get()
            for r in rows
            if r is not row and r["combo_var"].get()
        }
        available = [c for c in full_list if c not in chosen_by_others]

        # Apply search filter
        raw_search = row["search_var"].get()
        if raw_search and raw_search != "🔍 search…":
            q = raw_search.lower()
            available = [c for c in available if q in c.lower()]

        # Keep current selection even if it's hidden by filter
        current = row["combo_var"].get()
        if current and current not in available:
            available = [current] + available

        row["combo"].config(values=available)

    # ── Interests card ───────────────────────────────────────────────────────

    def _build_interests_card(self):
        body = self._card("💡  Interests & Goals", PURPLE)
        tk.Label(
            body,
            text=(
                "Describe your career goals, research interests, or any topic areas you'd "
                "like your capstone to focus on. The suggestion engine weighs these keywords "
                "alongside your completed courses."
            ),
            font=("Helvetica", 11), bg=WHITE, fg="#374151",
            wraplength=820, justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self.interests_text = tk.Text(
            body, font=("Helvetica", 11), height=4,
            wrap="word", relief="solid", bd=1,
        )
        self.interests_text.pack(fill="x")

        tk.Button(
            body, text="🔄  Refresh Capstone Suggestions",
            command=self._load_and_show_suggestions,
            bg=PURPLE, fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=7, cursor="hand2",
            activebackground="#6d28d9", activeforeground="white",
        ).pack(anchor="w", pady=(10, 0))

    # ── Capstone suggestions ─────────────────────────────────────────────────

    def _build_capstone_frame(self):
        body = self._card("🚀  Capstone Project Suggestions", AMBER)
        self.capstone_body = body
        tk.Label(
            body,
            text='Fill in your courses and interests above, then click "Refresh Capstone Suggestions".',
            font=("Helvetica", 10, "italic"), bg=WHITE, fg=MUTED,
            wraplength=820,
        ).pack(anchor="w", pady=8)

    def _load_and_show_suggestions(self):
        for w in self.capstone_body.winfo_children():
            w.destroy()

        capstones: list[dict] = []
        if CAPSTONE_FILE.exists():
            try:
                capstones = json.loads(CAPSTONE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass

        if not capstones:
            tk.Label(
                self.capstone_body,
                text="No capstone projects found. Ask a professor to run professor_capstone.py.",
                font=("Helvetica", 10, "italic"), bg=WHITE, fg=MUTED,
            ).pack(anchor="w", pady=8)
            return

        student_courses: set[str] = set()
        for r in self.fall_rows + self.spring_rows:
            val = r["combo_var"].get()
            if val:
                student_courses.add(val.split("  |  ")[-1].lower())

        interests = self.interests_text.get("1.0", "end").strip().lower()

        scored: list[tuple[float, dict]] = []
        for cap in capstones:
            related = [c.lower() for c in cap.get("related_courses", [])]
            tags    = [t.lower() for t in cap.get("tags", [])]
            cs = sum(1 for c in related if c in student_courses) / max(len(related), 1)
            ts = sum(1 for t in tags    if t in interests)       / max(len(tags), 1)
            scored.append((round(cs * 0.65 + ts * 0.35, 4), cap))

        scored.sort(key=lambda x: x[0], reverse=True)

        if scored[0][0] == 0.0:
            tk.Label(
                self.capstone_body,
                text=(
                    "No strong matches yet — make sure your interest keywords align with "
                    "capstone tags, and that you have selected completed courses."
                ),
                font=("Helvetica", 10, "italic"), bg=WHITE, fg=MUTED, wraplength=820,
            ).pack(anchor="w", pady=8)
            return

        n = min(5, len(scored))
        tk.Label(self.capstone_body,
                 text=f"Top {n} matching capstone project{'s' if n != 1 else ''}:",
                 font=("Helvetica", 11, "bold"), bg=WHITE, fg=DARK).pack(anchor="w", pady=(0, 8))

        palette = [GREEN, BLUE, PURPLE, AMBER, "#ec4899"]
        for i, (score, cap) in enumerate(scored[:n]):
            self._render_suggestion(cap, score, palette[i % len(palette)])

    def _render_suggestion(self, cap: dict, score: float, color: str):
        pct   = int(score * 100)
        outer = tk.Frame(self.capstone_body, bg="#f8fafc",
                         highlightbackground="#e2e8f0", highlightthickness=1)
        outer.pack(fill="x", pady=4)
        tk.Frame(outer, bg=color, width=6).pack(side="left", fill="y")

        body = tk.Frame(outer, bg="#f8fafc", padx=12, pady=10)
        body.pack(side="left", fill="x", expand=True)

        title_row = tk.Frame(body, bg="#f8fafc")
        title_row.pack(fill="x")
        required_badge = "  ⭐ Required" if cap.get("required") else ""
        tk.Label(title_row, text=cap.get("title", "Untitled"),
                 font=("Helvetica", 12, "bold"), bg="#f8fafc", fg=DARK).pack(side="left")
        tk.Label(title_row, text=f"  {pct}% match{required_badge}",
                 font=("Helvetica", 10, "bold"), bg="#f8fafc", fg=color).pack(side="left")

        if cap.get("summary"):
            tk.Label(body, text=cap["summary"], font=("Helvetica", 10),
                     bg="#f8fafc", fg="#374151", wraplength=760, justify="left").pack(anchor="w", pady=(4, 4))

        related = cap.get("related_courses", [])
        if related:
            f = tk.Frame(body, bg="#f8fafc"); f.pack(anchor="w", pady=(0, 4))
            tk.Label(f, text="Courses: ", font=("Helvetica", 9, "bold"),
                     bg="#f8fafc", fg=MUTED).pack(side="left")
            for c in related[:7]:
                tk.Label(f, text=c, font=("Helvetica", 9),
                         bg="#dcfce7", fg="#166534", padx=5, pady=1).pack(side="left", padx=(0, 3))

        tags = cap.get("tags", [])
        if tags:
            f = tk.Frame(body, bg="#f8fafc"); f.pack(anchor="w")
            for t in tags[:10]:
                tk.Label(f, text=f"#{t}", font=("Helvetica", 9),
                         bg="#ede9fe", fg="#4c1d95", padx=5, pady=1).pack(side="left", padx=(0, 3))

    # ── Save bar ─────────────────────────────────────────────────────────────

    def _build_save_bar(self):
        bar = tk.Frame(self.inner, bg=BG, pady=14, padx=20)
        bar.pack(fill="x")
        tk.Button(
            bar, text="💾  Save All",
            command=self._save_all,
            bg=BLUE, fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat", padx=24, pady=10, cursor="hand2",
            activebackground="#2563eb", activeforeground="white",
        ).pack(side="left")
        self.save_status = tk.Label(bar, text="", font=("Helvetica", 10, "italic"),
                                    bg=BG, fg="#16a34a")
        self.save_status.pack(side="left", padx=14)

    def _save_all(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter the student name before saving.")
            return

        fall_sel   = [r["combo_var"].get().split("  |  ")[-1]
                      for r in self.fall_rows   if r["combo_var"].get()]
        spring_sel = [r["combo_var"].get().split("  |  ")[-1]
                      for r in self.spring_rows if r["combo_var"].get()]

        if not fall_sel and not spring_sel:
            messagebox.showwarning("No Courses", "Please select at least one course.")
            return

        lines = [f"Student: {name}"]
        if fall_sel:
            lines.append(f"\n🍂 Fall ({len(fall_sel)}): {', '.join(fall_sel)}")
        if spring_sel:
            lines.append(f"\n🌸 Spring ({len(spring_sel)}): {', '.join(spring_sel)}")

        messagebox.showinfo("Saved ✓", "\n".join(lines))
        total = len(fall_sel) + len(spring_sel)
        self.save_status.config(
            text=f"✔  Saved {name}  ·  {total} course(s)  "
                 f"[{len(fall_sel)} fall / {len(spring_sel)} spring]"
        )


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TCombobox", padding=4)
    style.configure("TEntry",    padding=4)
    StudentTrackerApp(root)
    root.mainloop()
