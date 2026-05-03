"""
professor_capstone.py  –  Instructor Administration Panel
==========================================================
Communicates with student_tracker.py through two shared JSON files:
  • capstone_data.json   – capstone project catalogue
  • courses_data.json    – professor-managed course overrides (add / remove)

Run either program independently; changes are reflected instantly in the other.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, csv, re
from pathlib import Path
from datetime import datetime

# ── Shared data paths (same folder as this script) ────────────────────────────
BASE_DIR      = Path(__file__).parent
CAPSTONE_FILE = BASE_DIR / "capstone_data.json"
COURSES_FILE  = BASE_DIR / "courses_data.json"

# ── Palette ────────────────────────────────────────────────────────────────────
BG       = "#f0f2f5"
DARK     = "#1e293b"
WHITE    = "#ffffff"
GREEN    = "#10b981"
BLUE     = "#3b82f6"
RED      = "#ef4444"
AMBER    = "#f59e0b"
PURPLE   = "#7c3aed"
MUTED    = "#6b7280"
TEAL     = "#0d9488"
ROSE     = "#e11d48"
HEADER   = "#1e3a5f"

# ── Major definitions mirrored from student_tracker ───────────────────────────
MAJORS = [
    "Foundational Engineering",
    "Electrical, Computer Engineering & Computer Science",
    "Civil Engineering",
    "Mechanical Engineering",
]

_DEFAULT_FALL: dict[str, list[str]] = {
    "Foundational Engineering": [
        "Engineering Orientation","Foundations of Design 1","Foundations of Design 2",
        "Statistics","Engineering Traditions and Culture in Rome","Professional Practice",
        "Industrial Controllers",
    ],
    "Electrical, Computer Engineering & Computer Science": [
        "Introduction to Programming","Electric Circuits","Web Development",
        "Data Structures and Algorithms","Research Experience","Big Data Analytics",
        "Applied Electromagnetics","Signals and Systems","Embedded Hardware-Software Code Design",
        "Embedded Real-Time Applications","Software Development","UI/UX Design",
        "Computer Architecture","Networks and Data Communication",
        "Professional Certification Preparation","Power Systems","Information Science",
        "Advanced Electronics","Theory of Computation",
    ],
    "Civil Engineering": [
        "Surveying","Surveying Lab","Environmental Engineering","Geotechnical Engineering",
        "Structural Analysis","Transportation Engineering","Water Resources Engineering",
        "CFE Fundamentals","CFE Design Seminar 1",
    ],
    "Mechanical Engineering": [
        "Engineering Material Science","Thermodynamics","Design for Manufacturing",
        "Computer Applications","Fundamentals of Experimentation","Machine Component Design",
        "3-D Modeling and Design","Dynamic Systems Modeling","Fluid Mechanics",
        "Sensors and Measurements","Process of Design","Mechatronics",
        "Computational Fluid Dynamics","Advanced Thermodynamics","Engineering Analysis",
    ],
}

_DEFAULT_SPRING: dict[str, list[str]] = {
    "Foundational Engineering": [
        "Engineering Graphics","Technical Writing for Engineers","Engineering Economics",
        "Ethics in Engineering","Project Management","Capstone Preparation",
        "Innovation and Entrepreneurship","Sustainability in Engineering",
    ],
    "Electrical, Computer Engineering & Computer Science": [
        "Object-Oriented Programming","Digital Logic Design","Machine Learning",
        "Cybersecurity Fundamentals","Database Systems","Operating Systems",
        "Computer Vision","Wireless Communications","VLSI Design","Compiler Design",
        "Robotics Programming","Artificial Intelligence","Mobile App Development",
        "Cloud Computing","Parallel Computing","Natural Language Processing",
        "Internet of Things","Quantum Computing Fundamentals","Deep Learning",
        "Human-Computer Interaction",
    ],
    "Civil Engineering": [
        "Reinforced Concrete Design","Steel Structure Design","Foundation Engineering",
        "Construction Management","GIS and Remote Sensing","Hydraulics Lab",
        "Bridge Design","Urban Planning","Earthquake Engineering",
        "Building Information Modeling","CFE Design Seminar 2","Coastal Engineering",
        "Traffic Engineering","Environmental Remediation",
    ],
    "Mechanical Engineering": [
        "Heat Transfer","Mechanical Vibrations","Manufacturing Processes","Control Systems",
        "Finite Element Analysis","Robotics","HVAC Systems","Aerospace Fundamentals",
        "Renewable Energy Systems","Composite Materials","Advanced Manufacturing",
        "Capstone Design","Biomechanics","Additive Manufacturing","Tribology",
        "Acoustics and Noise Control",
    ],
}


# ══════════════════════════════════════════════════════════════════════════════
#  Data helpers
# ══════════════════════════════════════════════════════════════════════════════

def load_capstones() -> list[dict]:
    if CAPSTONE_FILE.exists():
        try:
            return json.loads(CAPSTONE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_capstones(data: list[dict]):
    CAPSTONE_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def load_courses() -> dict:
    """Returns {'fall': {major: [...]}, 'spring': {major: [...]}}"""
    if COURSES_FILE.exists():
        try:
            return json.loads(COURSES_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "fall":   {m: list(v) for m, v in _DEFAULT_FALL.items()},
        "spring": {m: list(v) for m, v in _DEFAULT_SPRING.items()},
    }


def save_courses(data: dict):
    COURSES_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _tags_str(tags: list[str]) -> str:
    return ", ".join(tags)


def _parse_tags(s: str) -> list[str]:
    return [t.strip().lower() for t in re.split(r"[,;]+", s) if t.strip()]


# ══════════════════════════════════════════════════════════════════════════════
#  Main application
# ══════════════════════════════════════════════════════════════════════════════

class ProfessorApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Instructor Administration Panel")
        self.root.geometry("1080x820")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.capstones: list[dict] = load_capstones()
        self.courses:   dict      = load_courses()

        self._build_ui()

    # ── Top-level layout ──────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=HEADER, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🏛️  Instructor Administration Panel",
                 font=("Helvetica", 20, "bold"), fg="white", bg=HEADER).pack()
        tk.Label(hdr, text="Manage capstone projects and course catalogue  ·  Changes sync instantly with student_tracker.py",
                 font=("Helvetica", 10), fg="#93c5fd", bg=HEADER).pack(pady=(2, 0))

        # ── Notebook tabs ─────────────────────────────────────────────────────
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"), padding=[14, 6])
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=16, pady=12)

        self.tab_capstone = tk.Frame(nb, bg=BG)
        self.tab_courses  = tk.Frame(nb, bg=BG)

        nb.add(self.tab_capstone, text="🚀  Capstone Projects")
        nb.add(self.tab_courses,  text="📚  Course Catalogue")

        self._build_capstone_tab()
        self._build_courses_tab()

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 1 — Capstone Projects
    # ══════════════════════════════════════════════════════════════════════════

    def _build_capstone_tab(self):
        tab = self.tab_capstone

        # ── Toolbar ───────────────────────────────────────────────────────────
        toolbar = tk.Frame(tab, bg=BG, pady=8)
        toolbar.pack(fill="x", padx=12)

        def btn(parent, text, cmd, color, active):
            tk.Button(
                parent, text=text, command=cmd,
                bg=color, fg="white", font=("Helvetica", 10, "bold"),
                relief="flat", padx=12, pady=6, cursor="hand2",
                activebackground=active, activeforeground="white",
            ).pack(side="left", padx=(0, 8))

        btn(toolbar, "＋  Add Project",  self._add_capstone,    GREEN,  "#059669")
        btn(toolbar, "✏️  Edit Selected", self._edit_capstone,   BLUE,   "#2563eb")
        btn(toolbar, "🗑  Delete",        self._delete_capstone, RED,    "#dc2626")
        btn(toolbar, "📥  Import CSV",    self._import_csv,      PURPLE, "#6d28d9")
        btn(toolbar, "📤  Export CSV",    self._export_csv,      TEAL,   "#0f766e")

        # Search bar
        sf = tk.Frame(toolbar, bg=BG)
        sf.pack(side="right")
        tk.Label(sf, text="🔍", font=("Helvetica", 12), bg=BG).pack(side="left")
        self.cap_search_var = tk.StringVar()
        self.cap_search_var.trace_add("write", lambda *_: self._refresh_capstone_list())
        ttk.Entry(sf, textvariable=self.cap_search_var,
                  font=("Helvetica", 10), width=24).pack(side="left", padx=4)

        # ── Paned layout: list on left, detail on right ───────────────────────
        pane = tk.PanedWindow(tab, orient="horizontal", bg=BG, sashwidth=6)
        pane.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Left – list
        list_frame = tk.Frame(pane, bg=WHITE, highlightbackground="#d1d5db", highlightthickness=1)
        pane.add(list_frame, minsize=280, stretch="never")

        tk.Label(list_frame, text="Projects", font=("Helvetica", 11, "bold"),
                 bg=HEADER, fg="white", pady=8).pack(fill="x")

        self.cap_listbox = tk.Listbox(
            list_frame, font=("Helvetica", 10), selectbackground=BLUE,
            selectforeground="white", activestyle="none",
            relief="flat", bd=0, highlightthickness=0,
        )
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical",
                                    command=self.cap_listbox.yview)
        self.cap_listbox.configure(yscrollcommand=list_scroll.set)
        list_scroll.pack(side="right", fill="y")
        self.cap_listbox.pack(fill="both", expand=True, padx=4, pady=4)
        self.cap_listbox.bind("<<ListboxSelect>>", self._on_capstone_select)

        # Right – detail
        detail_frame = tk.Frame(pane, bg=WHITE,
                                highlightbackground="#d1d5db", highlightthickness=1)
        pane.add(detail_frame, stretch="always")

        tk.Label(detail_frame, text="Project Details", font=("Helvetica", 11, "bold"),
                 bg=HEADER, fg="white", pady=8).pack(fill="x")

        self.detail_canvas = tk.Canvas(detail_frame, bg=WHITE, highlightthickness=0)
        detail_scroll = ttk.Scrollbar(detail_frame, orient="vertical",
                                      command=self.detail_canvas.yview)
        self.detail_canvas.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.pack(side="right", fill="y")
        self.detail_canvas.pack(fill="both", expand=True)

        self.detail_inner = tk.Frame(self.detail_canvas, bg=WHITE)
        self.detail_win   = self.detail_canvas.create_window(
            (0, 0), window=self.detail_inner, anchor="nw"
        )
        self.detail_inner.bind(
            "<Configure>",
            lambda e: self.detail_canvas.configure(scrollregion=self.detail_canvas.bbox("all"))
        )
        self.detail_canvas.bind(
            "<Configure>",
            lambda e: self.detail_canvas.itemconfig(self.detail_win, width=e.width)
        )

        # ── Status bar ────────────────────────────────────────────────────────
        self.cap_status = tk.Label(tab, text="", font=("Helvetica", 9, "italic"),
                                   bg=BG, fg=MUTED, anchor="w")
        self.cap_status.pack(fill="x", padx=14, pady=(0, 4))

        self._refresh_capstone_list()

    # ── Capstone list helpers ─────────────────────────────────────────────────

    def _refresh_capstone_list(self):
        q = self.cap_search_var.get().strip().lower()
        self.cap_listbox.delete(0, "end")
        for i, cap in enumerate(self.capstones):
            title = cap.get("title", "Untitled")
            badge = " ⭐" if cap.get("required") else ""
            if q and q not in title.lower() and q not in " ".join(cap.get("tags", [])).lower():
                continue
            self.cap_listbox.insert("end", f"  {badge}{title}")
        n = self.cap_listbox.size()
        self.cap_status.config(text=f"{n} of {len(self.capstones)} project(s) shown")

    def _on_capstone_select(self, _event=None):
        sel = self.cap_listbox.curselection()
        if not sel:
            return
        # Map listbox index back to capstone (filter may hide some)
        q      = self.cap_search_var.get().strip().lower()
        visible = [
            cap for cap in self.capstones
            if not q or q in cap.get("title", "").lower()
               or q in " ".join(cap.get("tags", [])).lower()
        ]
        idx = sel[0]
        if idx < len(visible):
            self._show_detail(visible[idx])

    def _show_detail(self, cap: dict):
        for w in self.detail_inner.winfo_children():
            w.destroy()

        pad = {"padx": 18, "pady": 4, "anchor": "w"}

        def lbl(text, bold=False, color=DARK, size=11):
            tk.Label(self.detail_inner, text=text,
                     font=("Helvetica", size, "bold" if bold else "normal"),
                     bg=WHITE, fg=color, wraplength=560, justify="left").pack(**pad)

        lbl(cap.get("title", "Untitled"), bold=True, size=14)

        if cap.get("required"):
            tk.Label(self.detail_inner, text="⭐  Required project",
                     font=("Helvetica", 10, "bold"),
                     bg="#fef9c3", fg="#92400e", padx=8, pady=3).pack(anchor="w", padx=18, pady=(0, 6))

        lbl("Contact / Sponsor:", bold=True, color=MUTED, size=10)
        lbl(cap.get("contact", "—"), color=BLUE)

        lbl("Eligible Majors:", bold=True, color=MUTED, size=10)
        lbl(", ".join(cap.get("majors", [])) or "—")

        lbl("Summary:", bold=True, color=MUTED, size=10)
        lbl(cap.get("summary", "No summary provided."), color="#374151")

        lbl("Related Courses:", bold=True, color=MUTED, size=10)
        courses_frame = tk.Frame(self.detail_inner, bg=WHITE)
        courses_frame.pack(anchor="w", padx=18, pady=2)
        for c in cap.get("related_courses", []):
            tk.Label(courses_frame, text=c, font=("Helvetica", 9),
                     bg="#dcfce7", fg="#166534", padx=6, pady=2, relief="flat").pack(side="left", padx=(0, 4), pady=2)

        lbl("Tags:", bold=True, color=MUTED, size=10)
        tags_frame = tk.Frame(self.detail_inner, bg=WHITE)
        tags_frame.pack(anchor="w", padx=18, pady=2)
        for t in cap.get("tags", []):
            tk.Label(tags_frame, text=f"#{t}", font=("Helvetica", 9),
                     bg="#ede9fe", fg="#4c1d95", padx=6, pady=2, relief="flat").pack(side="left", padx=(0, 4), pady=2)

    # ── Add / Edit dialog ─────────────────────────────────────────────────────

    def _capstone_dialog(self, title: str, prefill: dict | None = None) -> dict | None:
        """Modal dialog; returns filled dict or None if cancelled."""
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("680x700")
        dlg.configure(bg=BG)
        dlg.grab_set()
        dlg.resizable(True, True)

        canvas   = tk.Canvas(dlg, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dlg, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        inner = tk.Frame(canvas, bg=BG, padx=20, pady=16)
        win   = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))

        p = prefill or {}

        def field(label, var_or_widget, hint=""):
            tk.Label(inner, text=label, font=("Helvetica", 10, "bold"),
                     bg=BG, fg=DARK).pack(anchor="w", pady=(8, 0))
            if isinstance(var_or_widget, (tk.StringVar, tk.BooleanVar)):
                if isinstance(var_or_widget, tk.BooleanVar):
                    tk.Checkbutton(inner, text="Yes — mark as required (⭐)",
                                   variable=var_or_widget, bg=BG, font=("Helvetica", 10),
                                   cursor="hand2").pack(anchor="w")
                else:
                    ttk.Entry(inner, textvariable=var_or_widget,
                              font=("Helvetica", 10), width=60).pack(fill="x")
            else:
                var_or_widget.pack(fill="x")
            if hint:
                tk.Label(inner, text=hint, font=("Helvetica", 8, "italic"),
                         bg=BG, fg=MUTED).pack(anchor="w")

        v_title    = tk.StringVar(value=p.get("title", ""))
        v_contact  = tk.StringVar(value=p.get("contact", ""))
        v_majors   = tk.StringVar(value=", ".join(p.get("majors", [])))
        v_tags     = tk.StringVar(value=_tags_str(p.get("tags", [])))
        v_courses  = tk.StringVar(value=", ".join(p.get("related_courses", [])))
        v_required = tk.BooleanVar(value=p.get("required", False))

        field("Project Title *", v_title)
        field("Contact / Sponsor", v_contact)
        field("Eligible Majors", v_majors, "e.g.  CS, CpE, ME  — comma-separated abbreviations")
        field("Tags", v_tags, "e.g.  robotics, IoT, machine learning  — comma or semicolon separated")
        field("Related Courses", v_courses, "Course names matching the student tracker, comma-separated")

        tk.Label(inner, text="Summary *", font=("Helvetica", 10, "bold"),
                 bg=BG, fg=DARK).pack(anchor="w", pady=(8, 0))
        summary_box = tk.Text(inner, font=("Helvetica", 10), height=7,
                              wrap="word", relief="solid", bd=1)
        summary_box.insert("1.0", p.get("summary", ""))
        summary_box.pack(fill="x")

        field("Required Project", v_required)

        result: dict | None = None

        def on_save():
            nonlocal result
            t = v_title.get().strip()
            s = summary_box.get("1.0", "end").strip()
            if not t:
                messagebox.showwarning("Missing Field", "Project title is required.", parent=dlg)
                return
            if not s:
                messagebox.showwarning("Missing Field", "Summary is required.", parent=dlg)
                return
            result = {
                "title":           t,
                "summary":         s,
                "contact":         v_contact.get().strip(),
                "majors":          [m.strip() for m in v_majors.get().split(",") if m.strip()],
                "tags":            _parse_tags(v_tags.get()),
                "related_courses": [c.strip() for c in v_courses.get().split(",") if c.strip()],
                "required":        v_required.get(),
            }
            dlg.destroy()

        def on_cancel():
            dlg.destroy()

        btn_row = tk.Frame(inner, bg=BG)
        btn_row.pack(pady=16, anchor="w")
        tk.Button(btn_row, text="💾  Save", command=on_save,
                  bg=GREEN, fg="white", font=("Helvetica", 11, "bold"),
                  relief="flat", padx=16, pady=8, cursor="hand2").pack(side="left", padx=(0, 10))
        tk.Button(btn_row, text="Cancel", command=on_cancel,
                  bg="#e5e7eb", fg=DARK, font=("Helvetica", 10),
                  relief="flat", padx=12, pady=8, cursor="hand2").pack(side="left")

        dlg.wait_window()
        return result

    def _add_capstone(self):
        data = self._capstone_dialog("Add New Capstone Project")
        if data:
            self.capstones.append(data)
            save_capstones(self.capstones)
            self._refresh_capstone_list()
            messagebox.showinfo("Saved", f"'{data['title']}' added successfully.")

    def _edit_capstone(self):
        sel = self.cap_listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select a project to edit.")
            return
        q      = self.cap_search_var.get().strip().lower()
        visible = [
            (i, cap) for i, cap in enumerate(self.capstones)
            if not q or q in cap.get("title", "").lower()
               or q in " ".join(cap.get("tags", [])).lower()
        ]
        list_idx = sel[0]
        if list_idx >= len(visible):
            return
        orig_idx, cap = visible[list_idx]
        data = self._capstone_dialog("Edit Capstone Project", prefill=cap)
        if data:
            self.capstones[orig_idx] = data
            save_capstones(self.capstones)
            self._refresh_capstone_list()
            self._show_detail(data)

    def _delete_capstone(self):
        sel = self.cap_listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select a project to delete.")
            return
        q      = self.cap_search_var.get().strip().lower()
        visible = [
            (i, cap) for i, cap in enumerate(self.capstones)
            if not q or q in cap.get("title", "").lower()
               or q in " ".join(cap.get("tags", [])).lower()
        ]
        list_idx = sel[0]
        if list_idx >= len(visible):
            return
        orig_idx, cap = visible[list_idx]
        if messagebox.askyesno("Confirm Delete",
                               f"Delete '{cap.get('title')}'?\nThis cannot be undone."):
            self.capstones.pop(orig_idx)
            save_capstones(self.capstones)
            for w in self.detail_inner.winfo_children():
                w.destroy()
            self._refresh_capstone_list()

    # ── CSV Import / Export ───────────────────────────────────────────────────

    def _import_csv(self):
        path = filedialog.askopenfilename(
            title="Select Capstone CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        required_cols = {"title", "summary"}
        imported = 0
        skipped  = 0
        errors   = []

        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                cols = {c.strip().lower() for c in (reader.fieldnames or [])}
                if not required_cols.issubset(cols):
                    messagebox.showerror(
                        "Invalid CSV",
                        f"CSV must have at minimum these columns:\n  title, summary\n\n"
                        f"Found: {', '.join(sorted(cols)) or '(none)'}",
                    )
                    return

                existing_titles = {c.get("title", "").lower() for c in self.capstones}

                for row in reader:
                    r = {k.strip().lower(): v.strip() for k, v in row.items()}
                    title   = r.get("title", "").strip()
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
                    self.capstones.append(entry)
                    existing_titles.add(title.lower())
                    imported += 1

        except Exception as exc:
            messagebox.showerror("Import Error", str(exc))
            return

        save_capstones(self.capstones)
        self._refresh_capstone_list()
        messagebox.showinfo(
            "Import Complete",
            f"Imported:  {imported} project(s)\n"
            f"Skipped:   {skipped} (missing fields or duplicate title)\n\n"
            "Required CSV columns: title, summary\n"
            "Optional columns: contact, majors, tags, related_courses, required",
        )

    def _export_csv(self):
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            title="Export Capstones to CSV",
            defaultextension=".csv",
            initialfile=f"capstones_{ts}.csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return

        fieldnames = ["title", "summary", "contact", "majors", "tags", "related_courses", "required"]
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for cap in self.capstones:
                writer.writerow({
                    "title":           cap.get("title", ""),
                    "summary":         cap.get("summary", ""),
                    "contact":         cap.get("contact", ""),
                    "majors":          ", ".join(cap.get("majors", [])),
                    "tags":            ", ".join(cap.get("tags", [])),
                    "related_courses": ", ".join(cap.get("related_courses", [])),
                    "required":        "yes" if cap.get("required") else "no",
                })
        messagebox.showinfo("Export Complete", f"Exported {len(self.capstones)} project(s) to:\n{path}")

    # ══════════════════════════════════════════════════════════════════════════
    #  TAB 2 — Course Catalogue
    # ══════════════════════════════════════════════════════════════════════════

    def _build_courses_tab(self):
        tab = self.tab_courses

        info = tk.Frame(tab, bg="#eff6ff", pady=8, padx=14,
                        highlightbackground="#bfdbfe", highlightthickness=1)
        info.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(
            info,
            text=(
                "ℹ️   Changes here are saved to courses_data.json and picked up by student_tracker.py "
                "the next time it starts. Removed courses are shown with  ✖  in red."
            ),
            font=("Helvetica", 9), bg="#eff6ff", fg="#1e40af", wraplength=900, justify="left",
        ).pack(anchor="w")

        # Season selector
        sel_bar = tk.Frame(tab, bg=BG, pady=10)
        sel_bar.pack(fill="x", padx=12)
        tk.Label(sel_bar, text="Season:", font=("Helvetica", 11, "bold"),
                 bg=BG, fg=DARK).pack(side="left")
        self.season_var = tk.StringVar(value="Fall")
        for s, color in [("Fall", "#b45309"), ("Spring", "#15803d")]:
            tk.Radiobutton(
                sel_bar, text=f"  {s}  ", variable=self.season_var, value=s,
                command=self._refresh_course_panel,
                font=("Helvetica", 10, "bold"),
                bg=BG, fg=color, activebackground=BG, selectcolor=BG,
                indicatoron=False, relief="solid", borderwidth=1,
                cursor="hand2", padx=10, pady=4,
            ).pack(side="left", padx=6)

        # Major selector
        maj_bar = tk.Frame(tab, bg=BG)
        maj_bar.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(maj_bar, text="Major:", font=("Helvetica", 11, "bold"),
                 bg=BG, fg=DARK).pack(side="left")
        self.course_major_var = tk.StringVar(value=MAJORS[0])
        self.maj_menu = ttk.Combobox(
            maj_bar, textvariable=self.course_major_var,
            values=MAJORS, state="readonly", font=("Helvetica", 10), width=52,
        )
        self.maj_menu.pack(side="left", padx=8)
        self.maj_menu.bind("<<ComboboxSelected>>", lambda _: self._refresh_course_panel())

        # Paned: course list on left, add/remove controls on right
        pane = tk.PanedWindow(tab, orient="horizontal", bg=BG, sashwidth=6)
        pane.pack(fill="both", expand=True, padx=12, pady=4)

        # ── Left: active courses ──────────────────────────────────────────────
        left = tk.Frame(pane, bg=WHITE, highlightbackground="#d1d5db", highlightthickness=1)
        pane.add(left, minsize=340, stretch="always")

        tk.Label(left, text="Active Courses", font=("Helvetica", 11, "bold"),
                 bg=HEADER, fg="white", pady=8).pack(fill="x")

        self.course_listbox = tk.Listbox(
            left, font=("Helvetica", 10), selectbackground=BLUE,
            selectforeground="white", activestyle="none",
            relief="flat", bd=0, highlightthickness=0, selectmode="extended",
        )
        cl_scroll = ttk.Scrollbar(left, orient="vertical", command=self.course_listbox.yview)
        self.course_listbox.configure(yscrollcommand=cl_scroll.set)
        cl_scroll.pack(side="right", fill="y")
        self.course_listbox.pack(fill="both", expand=True, padx=4, pady=4)

        rm_btn = tk.Button(
            left, text="🗑  Remove Selected Course(s)",
            command=self._remove_courses,
            bg=RED, fg="white", font=("Helvetica", 10, "bold"),
            relief="flat", padx=12, pady=8, cursor="hand2",
            activebackground="#dc2626", activeforeground="white",
        )
        rm_btn.pack(fill="x", padx=8, pady=(0, 8))

        restore_btn = tk.Button(
            left, text="↩  Restore All Defaults for This Major",
            command=self._restore_defaults,
            bg="#64748b", fg="white", font=("Helvetica", 9),
            relief="flat", padx=12, pady=6, cursor="hand2",
        )
        restore_btn.pack(fill="x", padx=8, pady=(0, 10))

        # ── Right: add new course ─────────────────────────────────────────────
        right = tk.Frame(pane, bg=WHITE, highlightbackground="#d1d5db", highlightthickness=1)
        pane.add(right, minsize=280, stretch="never")

        tk.Label(right, text="Add New Course", font=("Helvetica", 11, "bold"),
                 bg=HEADER, fg="white", pady=8).pack(fill="x")

        add_body = tk.Frame(right, bg=WHITE, padx=14, pady=14)
        add_body.pack(fill="both", expand=True)

        tk.Label(add_body, text="Course Name *", font=("Helvetica", 10, "bold"),
                 bg=WHITE, fg=DARK).pack(anchor="w", pady=(0, 4))
        self.new_course_var = tk.StringVar()
        ttk.Entry(add_body, textvariable=self.new_course_var,
                  font=("Helvetica", 10), width=34).pack(fill="x")

        tk.Label(add_body,
                 text="Will be added to the currently selected\nseason and major.",
                 font=("Helvetica", 9, "italic"), bg=WHITE, fg=MUTED).pack(anchor="w", pady=(6, 14))

        tk.Button(
            add_body, text="＋  Add Course",
            command=self._add_course,
            bg=GREEN, fg="white", font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=8, cursor="hand2",
            activebackground="#059669", activeforeground="white",
        ).pack(anchor="w")

        ttk.Separator(add_body, orient="horizontal").pack(fill="x", pady=18)

        tk.Label(add_body, text="Bulk Import Courses",
                 font=("Helvetica", 10, "bold"), bg=WHITE, fg=DARK).pack(anchor="w")
        tk.Label(add_body,
                 text="One course name per line.\nAdds to currently selected season & major.",
                 font=("Helvetica", 9, "italic"), bg=WHITE, fg=MUTED).pack(anchor="w", pady=(4, 6))
        self.bulk_text = tk.Text(add_body, font=("Helvetica", 10), height=10,
                                 wrap="word", relief="solid", bd=1)
        self.bulk_text.pack(fill="x")
        tk.Button(
            add_body, text="📋  Add All Lines",
            command=self._bulk_add_courses,
            bg=BLUE, fg="white", font=("Helvetica", 10, "bold"),
            relief="flat", padx=14, pady=7, cursor="hand2",
            activebackground="#2563eb", activeforeground="white",
        ).pack(anchor="w", pady=(8, 0))

        # Status bar
        self.course_status = tk.Label(tab, text="", font=("Helvetica", 9, "italic"),
                                      bg=BG, fg=MUTED, anchor="w")
        self.course_status.pack(fill="x", padx=14, pady=4)

        self._refresh_course_panel()

    # ── Course panel helpers ──────────────────────────────────────────────────

    def _current_season_dict(self) -> dict[str, list[str]]:
        season = self.season_var.get().lower()
        return self.courses.setdefault(season, {})

    def _refresh_course_panel(self):
        major  = self.course_major_var.get()
        season = self.season_var.get().lower()
        active = self.courses.get(season, {}).get(major, [])
        default = (_DEFAULT_FALL if season == "fall" else _DEFAULT_SPRING).get(major, [])

        self.course_listbox.delete(0, "end")
        for c in sorted(active):
            removed_flag = "" if c in default else "  [custom]"
            self.course_listbox.insert("end", f"  {c}{removed_flag}")

        n = len(active)
        self.course_status.config(
            text=f"{n} course(s) in {major}  ·  {self.season_var.get()}"
        )

    def _add_course(self):
        name   = self.new_course_var.get().strip()
        major  = self.course_major_var.get()
        season = self.season_var.get().lower()

        if not name:
            messagebox.showwarning("Empty Name", "Please enter a course name.")
            return

        bucket = self.courses.setdefault(season, {}).setdefault(major, [])
        if name in bucket:
            messagebox.showinfo("Duplicate", f'"{name}" is already in this list.')
            return

        bucket.append(name)
        save_courses(self.courses)
        self._refresh_course_panel()
        self.new_course_var.set("")
        self.course_status.config(text=f'✔  Added "{name}" to {major}  ({self.season_var.get()})')

    def _bulk_add_courses(self):
        raw   = self.bulk_text.get("1.0", "end").strip()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        if not lines:
            messagebox.showinfo("Empty", "Nothing to add — text box is empty.")
            return

        major  = self.course_major_var.get()
        season = self.season_var.get().lower()
        bucket = self.courses.setdefault(season, {}).setdefault(major, [])
        added  = 0
        for name in lines:
            if name not in bucket:
                bucket.append(name)
                added += 1

        save_courses(self.courses)
        self._refresh_course_panel()
        self.bulk_text.delete("1.0", "end")
        messagebox.showinfo("Bulk Import",
                            f"Added {added} course(s)  ·  skipped {len(lines) - added} duplicate(s).")

    def _remove_courses(self):
        sel    = self.course_listbox.curselection()
        if not sel:
            messagebox.showinfo("No Selection", "Select one or more courses to remove.")
            return

        major  = self.course_major_var.get()
        season = self.season_var.get().lower()
        bucket = self.courses.get(season, {}).get(major, [])

        # Pull names from listbox labels (strip leading spaces and [custom] badge)
        names_to_remove = []
        for i in sel:
            raw = self.course_listbox.get(i).strip()
            name = raw.replace("  [custom]", "").strip()
            names_to_remove.append(name)

        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Remove {len(names_to_remove)} course(s) from {major} ({self.season_var.get()})?\n\n"
            + "\n".join(f"  • {n}" for n in names_to_remove)
            + "\n\nStudents who already selected these will retain their selection.",
        )
        if not confirm:
            return

        for name in names_to_remove:
            if name in bucket:
                bucket.remove(name)

        save_courses(self.courses)
        self._refresh_course_panel()

    def _restore_defaults(self):
        major  = self.course_major_var.get()
        season = self.season_var.get().lower()
        default = (_DEFAULT_FALL if season == "fall" else _DEFAULT_SPRING).get(major, [])

        if not messagebox.askyesno(
            "Restore Defaults",
            f"Reset {major} ({self.season_var.get()}) to the built-in course list?\n"
            "Any added or removed courses will be lost.",
        ):
            return

        self.courses.setdefault(season, {})[major] = list(default)
        save_courses(self.courses)
        self._refresh_course_panel()
        self.course_status.config(text=f"↩  Restored defaults for {major}  ({self.season_var.get()})")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TCombobox", padding=4)
    style.configure("TEntry",    padding=4)
    ProfessorApp(root)
    root.mainloop()