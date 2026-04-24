import tkinter as tk
from tkinter import ttk, messagebox
import re
import copy

# ── Theme Colors ──────────────────────────────────────────────────────────────
BG       = "#f0f4f8"
DARK     = "#1a2332"
WHITE    = "#ffffff"
CARD_BG  = "#ffffff"
MID_DARK = "#2d3f55"
ACCENT   = "#3b82f6"
GREEN    = "#10b981"
PURPLE   = "#7c3aed"
AMBER    = "#f59e0b"
RED      = "#ef4444"
MUTED    = "#6b7280"
LIGHT_BG = "#f8fafc"

# ── Engineering Courses with Tags ─────────────────────────────────────────────
ENGINEERING_COURSES = [
    {
        "code": "ENGR 1001",
        "name": "Engineering Orientation",
        "tags": ["engineering", "design"],
    },
    {
        "code": "ENGR 1041",
        "name": "Foundations of Design 1",
        "tags": ["engineering", "design"],
    },
    {
        "code": "ENGR 1051",
        "name": "Foundations of Design 2",
        "tags": ["engineering", "design"],
    },
    {
        "code": "ECCS 1611",
        "name": "Programming 1",
        "tags": ["programming", "software"],
    },
    {
        "code": "ECCS 1621",
        "name": "Programming 2",
        "tags": ["programming", "software"],
    },
    {
        "code": "ECCS 1721",
        "name": "Digital Logic",
        "tags": ["electrical", "hardware"],
    },
    {
        "code": "ECCS 2311",
        "name": "Electric Circuits",
        "tags": ["electrical"],
    },
    {
        "code": "ECCS 2331",
        "name": "Digital Signal Processing",
        "tags": ["electrical", "signal_processing"],
    },
    {
        "code": "ECCS 2341",
        "name": "Electronics",
        "tags": ["electrical", "hardware"],
    },
    {
        "code": "ECCS 2381",
        "name": "Maker Engineering",
        "tags": ["robotics", "design", "embedded"],
    },
    {
        "code": "ECCS 2671",
        "name": "Data Structures & Algorithms 1",
        "tags": ["programming", "software"],
    },
    {
        "code": "ECCS 3241",
        "name": "Embedded Hardware-Software",
        "tags": ["embedded", "hardware", "programming"],
    },
    {
        "code": "ECCS 3351",
        "name": "Embedded Real-Time App",
        "tags": ["embedded", "programming", "robotics"],
    },
    {
        "code": "ECCS 3411",
        "name": "Computer Security",
        "tags": ["security", "programming", "networking"],
    },
    {
        "code": "ECCS 3611",
        "name": "Computer Architecture",
        "tags": ["hardware", "electrical"],
    },
    {
        "code": "ECCS 3631",
        "name": "Networks & Data Communications",
        "tags": ["networking", "software"],
    },
    {
        "code": "ECCS 3661",
        "name": "Operating Systems",
        "tags": ["software", "programming"],
    },
]

# ── Default Capstone Projects (instructor-editable) ───────────────────────────
DEFAULT_CAPSTONES = [
    {
        "name": "Smart Home Automation System",
        "description": (
            "Design and build an IoT-based home automation system using embedded "
            "microcontrollers, wireless networking protocols, and a web dashboard "
            "for real-time monitoring and control."
        ),
        "tags": ["embedded", "electrical", "programming", "networking"],
    },
    {
        "name": "Cybersecurity Intrusion Detection Platform",
        "description": (
            "Develop a network intrusion detection system using traffic analysis, "
            "anomaly detection algorithms, and real-time alerting. Includes firewall "
            "rule management and security event logging."
        ),
        "tags": ["security", "networking", "programming", "software"],
    },
    {
        "name": "Autonomous Robotics Platform",
        "description": (
            "Build a mobile autonomous robot featuring real-time sensor fusion, "
            "PID motor control, obstacle avoidance, and path planning — all running "
            "on a custom embedded real-time operating system."
        ),
        "tags": ["robotics", "embedded", "programming", "hardware"],
    },
    {
        "name": "FPGA-Based Signal Processing System",
        "description": (
            "Implement DSP algorithms (FFT, filtering, modulation) on reconfigurable "
            "FPGA hardware in HDL, targeting real-time audio processing or RF "
            "communication applications."
        ),
        "tags": ["electrical", "signal_processing", "hardware"],
    },
    {
        "name": "Enterprise Network Infrastructure Design",
        "description": (
            "Design, simulate, and deploy a scalable enterprise network with VLANs, "
            "routing protocols, QoS policies, and integrated security monitoring "
            "across multiple sites."
        ),
        "tags": ["networking", "software", "security"],
    },
    {
        "name": "Embedded Medical Monitoring Device",
        "description": (
            "Prototype a wearable patient monitoring system with low-power embedded "
            "hardware, real-time biosignal acquisition, Bluetooth telemetry, and a "
            "companion mobile dashboard."
        ),
        "tags": ["embedded", "electrical", "hardware", "programming"],
    },
    {
        "name": "Custom RISC Processor Design",
        "description": (
            "Design and simulate a pipelined RISC processor from scratch using HDL, "
            "covering ALU design, instruction set architecture, cache hierarchy, and "
            "performance benchmarking."
        ),
        "tags": ["hardware", "electrical", "engineering"],
    },
    {
        "name": "Full-Stack IoT Engineering Platform",
        "description": (
            "Build a full-stack platform that ingests real-time sensor data from "
            "embedded edge devices, stores it in a cloud database, and visualizes "
            "it through an interactive web dashboard."
        ),
        "tags": ["programming", "software", "networking", "embedded"],
    },
    {
        "name": "Software-Defined Radio Communications",
        "description": (
            "Develop a software-defined radio system capable of transmitting and "
            "receiving modulated signals, including a GUI for real-time spectrum "
            "visualization and demodulation."
        ),
        "tags": ["electrical", "signal_processing", "programming"],
    },
    {
        "name": "Secure Embedded Firmware Framework",
        "description": (
            "Create a security-hardened firmware framework for embedded devices, "
            "incorporating secure boot, encrypted OTA updates, and runtime anomaly "
            "detection with minimal overhead."
        ),
        "tags": ["embedded", "security", "programming", "hardware"],
    },
]

# ── Tag → display-color mapping ───────────────────────────────────────────────
TAG_COLORS = {
    "programming":       ("#dbeafe", "#1d4ed8"),
    "software":          ("#e0f2fe", "#0369a1"),
    "electrical":        ("#fef9c3", "#854d0e"),
    "hardware":          ("#ffedd5", "#9a3412"),
    "embedded":          ("#f3e8ff", "#6b21a8"),
    "robotics":          ("#dcfce7", "#166534"),
    "networking":        ("#e0f2fe", "#075985"),
    "security":          ("#fee2e2", "#991b1b"),
    "signal_processing": ("#fef3c7", "#92400e"),
    "design":            ("#fce7f3", "#9d174d"),
    "engineering":       ("#f1f5f9", "#334155"),
}
DEFAULT_TAG_COLOR = ("#e5e7eb", "#374151")


def tag_colors(tag):
    return TAG_COLORS.get(tag, DEFAULT_TAG_COLOR)


def parse_tags(tag_string: str) -> list[str]:
    """Extract tags from <tag1> <tag2> ... format."""
    return [t.strip().lower() for t in re.findall(r"<([^>]+)>", tag_string)]


def compute_score(capstone: dict, taken_data: list[dict]) -> float:
    """
    Score a capstone (0.0–1.0) based on courses taken and enjoyment ratings.

    Algorithm per capstone tag T:
      - coverage  = (# courses with T the student took) / (# total courses with T)
      - avg_enjoy = mean enjoyment (0–5) of those taken courses
      - interest  = 0.4 + avg_enjoy / 8.33   → maps 0–5 into 0.4–1.0
      - tag_score = coverage × interest
    Final score = mean(tag_scores) across all capstone tags that have
    at least one matching course in the curriculum.
    """
    if not capstone["tags"]:
        return 0.0

    tag_scores = []
    for tag in capstone["tags"]:
        courses_with_tag = [c for c in ENGINEERING_COURSES if tag in c["tags"]]
        if not courses_with_tag:
            continue
        taken_with_tag = [t for t in taken_data if tag in t["course"]["tags"]]
        if not taken_with_tag:
            tag_scores.append(0.0)
            continue
        coverage = len(taken_with_tag) / len(courses_with_tag)
        avg_enjoy = sum(t["rating"] for t in taken_with_tag) / len(taken_with_tag)
        interest = 0.4 + avg_enjoy / (5 / 0.6)  # 0.4 → 1.0 across 0–5
        tag_scores.append(coverage * interest)

    return sum(tag_scores) / len(tag_scores) if tag_scores else 0.0


# ═════════════════════════════════════════════════════════════════════════════
class CapstoneAdvisorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Engineering Capstone Advisor")
        self.root.geometry("860x720")
        self.root.configure(bg=DARK)
        self.root.resizable(True, True)
        self.root.minsize(680, 500)

        self.capstones: list[dict] = copy.deepcopy(DEFAULT_CAPSTONES)
        self.course_data: list[dict] = []  # {course, taken: BoolVar, rating: IntVar}

        self._build_ui()

    # ── Top-level layout ──────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TEntry", padding=5)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background="#243447",
            foreground="#94a3b8",
            padding=[20, 9],
            font=("Helvetica", 10, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", BG)],
            foreground=[("selected", DARK)],
        )
        style.configure("TSeparator", background="#e5e7eb")

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True)

        stud_tab = tk.Frame(nb, bg=BG)
        inst_tab = tk.Frame(nb, bg=BG)
        nb.add(stud_tab, text="  👤  Student View  ")
        nb.add(inst_tab, text="  🔧  Instructor Panel  ")

        self._build_student_tab(stud_tab)
        self._build_instructor_tab(inst_tab)

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=DARK, pady=18)
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text="🎓  Engineering Capstone Advisor",
            font=("Helvetica", 20, "bold"),
            fg=WHITE, bg=DARK,
        ).pack()
        tk.Label(
            hdr,
            text="Track your coursework · Rate your interests · Get your perfect capstone match",
            font=("Helvetica", 9),
            fg="#64748b", bg=DARK,
        ).pack(pady=(3, 0))

    # ── Reusable helpers ──────────────────────────────────────────────────────

    def _scrollable(self, parent) -> tuple:
        """Return (canvas, inner_frame) with scroll support."""
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(win_id, width=e.width),
        )

        def _scroll(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _scroll))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        return canvas, inner

    def _card(self, parent, title, accent=DARK, emoji="") -> tk.Frame:
        wrapper = tk.Frame(parent, bg=BG, pady=7, padx=14)
        wrapper.pack(fill="x")
        outer = tk.Frame(
            wrapper, bg=WHITE,
            highlightbackground="#dde3ec", highlightthickness=1,
        )
        outer.pack(fill="x")

        # Left accent stripe
        stripe = tk.Frame(outer, bg=accent, width=5)
        stripe.pack(side="left", fill="y")

        right = tk.Frame(outer, bg=WHITE)
        right.pack(side="left", fill="both", expand=True)

        title_bar = tk.Frame(right, bg="#f8fafc", pady=9, padx=14)
        title_bar.pack(fill="x")
        title_text = f"{emoji}  {title}" if emoji else title
        tk.Label(
            title_bar,
            text=title_text,
            font=("Helvetica", 11, "bold"),
            fg=accent, bg="#f8fafc",
        ).pack(anchor="w")
        ttk.Separator(right, orient="horizontal").pack(fill="x")

        body = tk.Frame(right, bg=WHITE, padx=14, pady=12)
        body.pack(fill="x")
        return body

    def _tag_pill(self, parent, tag: str) -> tk.Label:
        bg, fg = tag_colors(tag)
        lbl = tk.Label(
            parent,
            text=f"‹{tag}›",
            font=("Courier", 8, "bold"),
            bg=bg, fg=fg,
            padx=5, pady=2,
        )
        return lbl

    # ── Student Tab ───────────────────────────────────────────────────────────

    def _build_student_tab(self, parent):
        _, inner = self._scrollable(parent)

        # Student name
        name_body = self._card(inner, "Student Information", ACCENT, "👤")
        tk.Label(
            name_body,
            text="Full Name:",
            font=("Helvetica", 10, "bold"),
            bg=WHITE, fg="#374151",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.name_var = tk.StringVar()
        ttk.Entry(
            name_body,
            textvariable=self.name_var,
            font=("Helvetica", 11),
            width=44,
        ).grid(row=1, column=0, sticky="ew")
        name_body.columnconfigure(0, weight=1)

        # Courses
        self._build_courses_section(inner)

        # Recommend button
        btn_wrapper = tk.Frame(inner, bg=BG, padx=14, pady=4)
        btn_wrapper.pack(fill="x")
        tk.Button(
            btn_wrapper,
            text="🔍   Generate Capstone Recommendations",
            command=self._generate_recommendations,
            bg=PURPLE, fg=WHITE,
            font=("Helvetica", 12, "bold"),
            relief="flat", padx=0, pady=11, cursor="hand2",
            activebackground="#6d28d9", activeforeground=WHITE,
        ).pack(fill="x")

        # Results area (populated on demand)
        self.results_area = tk.Frame(inner, bg=BG)
        self.results_area.pack(fill="x")

    def _build_courses_section(self, parent):
        body = self._card(parent, "Engineering Courses Taken", MID_DARK, "📚")

        tk.Label(
            body,
            text="Check every course you have completed, then rate how much you enjoyed it (0 = disliked → 5 = loved).",
            font=("Helvetica", 9, "italic"),
            bg=WHITE, fg=MUTED, wraplength=740, justify="left",
        ).pack(anchor="w", pady=(0, 10))

        # Column headers
        hdr = tk.Frame(body, bg="#f1f5f9", pady=4, padx=8)
        hdr.pack(fill="x")
        tk.Label(hdr, text="✓", font=("Helvetica", 9, "bold"), bg="#f1f5f9", fg=MUTED, width=3).pack(side="left")
        tk.Label(hdr, text="Code", font=("Helvetica", 9, "bold"), bg="#f1f5f9", fg=MUTED, width=11, anchor="w").pack(side="left")
        tk.Label(hdr, text="Course Name", font=("Helvetica", 9, "bold"), bg="#f1f5f9", fg=MUTED).pack(side="left")
        tk.Label(hdr, text="Enjoyment Rating  (0 ──────── 5)", font=("Helvetica", 9, "bold"), bg="#f1f5f9", fg=MUTED).pack(side="right", padx=(0, 4))

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=(4, 0))

        self.course_data = []
        for i, course in enumerate(ENGINEERING_COURSES):
            row_bg = LIGHT_BG if i % 2 == 0 else WHITE
            row = tk.Frame(body, bg=row_bg, pady=5, padx=8)
            row.pack(fill="x")

            taken_var  = tk.BooleanVar(value=False)
            rating_var = tk.IntVar(value=3)

            cb = tk.Checkbutton(
                row, variable=taken_var,
                bg=row_bg, activebackground=row_bg,
                cursor="hand2",
            )
            cb.pack(side="left")

            tk.Label(
                row, text=course["code"],
                font=("Courier", 9, "bold"),
                bg=row_bg, fg="#475569", width=11, anchor="w",
            ).pack(side="left")

            tk.Label(
                row, text=course["name"],
                font=("Helvetica", 10),
                bg=row_bg, fg="#111827", anchor="w",
            ).pack(side="left", padx=(2, 0))

            # Rating widget (right-aligned)
            rating_frame = tk.Frame(row, bg=row_bg)
            rating_frame.pack(side="right")

            tk.Label(rating_frame, text="0", font=("Helvetica", 8), bg=row_bg, fg="#9ca3af").pack(side="left")

            scale = tk.Scale(
                rating_frame,
                variable=rating_var,
                from_=0, to=5,
                orient="horizontal",
                length=130,
                bg=row_bg,
                highlightthickness=0,
                troughcolor="#e2e8f0",
                sliderrelief="flat",
                width=12,
                showvalue=False,
            )
            scale.pack(side="left", padx=2)

            tk.Label(rating_frame, text="5", font=("Helvetica", 8), bg=row_bg, fg="#9ca3af").pack(side="left")

            stars_lbl = tk.Label(
                rating_frame, text="",
                font=("Helvetica", 10),
                bg=row_bg, fg=AMBER, width=6,
            )
            stars_lbl.pack(side="left", padx=(6, 0))

            # Closures ─────────────────────────────────────────────
            def _make_callbacks(t_var, r_var, sc, sl, rbg):
                def update_stars(*_):
                    v = r_var.get()
                    sl.config(text="★" * v + "☆" * (5 - v))

                def toggle(*_):
                    if t_var.get():
                        sc.config(state="normal")
                        sl.config(fg=AMBER)
                    else:
                        sc.config(state="disabled")
                        sl.config(fg="#d1d5db")
                    update_stars()

                return update_stars, toggle

            update_stars, toggle = _make_callbacks(
                taken_var, rating_var, scale, stars_lbl, row_bg
            )
            rating_var.trace_add("write", lambda *a, u=update_stars: u())
            taken_var.trace_add("write", lambda *a, t=toggle: t())
            toggle()  # apply initial (unchecked) state

            self.course_data.append(
                {"course": course, "taken": taken_var, "rating": rating_var}
            )

    # ── Recommendation Engine ─────────────────────────────────────────────────

    def _generate_recommendations(self):
        name = self.name_var.get().strip()

        taken_data = [
            {"course": d["course"], "rating": d["rating"].get()}
            for d in self.course_data
            if d["taken"].get()
        ]

        if not taken_data:
            messagebox.showwarning(
                "No Courses Selected",
                "Please check at least one course you have completed.",
            )
            return

        # Clear previous results
        for w in self.results_area.winfo_children():
            w.destroy()

        # Score every capstone
        scored = sorted(
            [(compute_score(cap, taken_data), cap) for cap in self.capstones],
            key=lambda x: x[0],
            reverse=True,
        )

        body = self._card(self.results_area, "Capstone Recommendations", PURPLE, "🏆")

        greeting = f"Top matches for {name}:" if name else "Your top capstone matches:"
        tk.Label(
            body,
            text=greeting,
            font=("Helvetica", 10, "italic"),
            bg=WHITE, fg=MUTED,
        ).pack(anchor="w", pady=(0, 10))

        medal_emojis  = ["🥇", "🥈", "🥉"]
        bar_colors    = [GREEN, ACCENT, AMBER]
        border_colors = ["#10b981", "#3b82f6", "#f59e0b"]

        shown = 0
        for rank, (score, cap) in enumerate(scored):
            if score < 0.01:
                continue
            if shown >= 3:
                break

            pct = min(int(score * 100), 99)
            bc  = border_colors[shown]
            bar = bar_colors[shown]

            result_card = tk.Frame(
                body, bg=LIGHT_BG,
                highlightbackground=bc,
                highlightthickness=2,
                pady=10, padx=14,
            )
            result_card.pack(fill="x", pady=(0, 10))

            # Title row
            top = tk.Frame(result_card, bg=LIGHT_BG)
            top.pack(fill="x")
            tk.Label(
                top,
                text=f"{medal_emojis[shown]}  {cap['name']}",
                font=("Helvetica", 12, "bold"),
                bg=LIGHT_BG, fg="#111827",
            ).pack(side="left")
            match_badge = tk.Label(
                top,
                text=f"  {pct}% match  ",
                font=("Helvetica", 10, "bold"),
                bg=bar, fg=WHITE,
                padx=2, pady=3,
            )
            match_badge.pack(side="right")

            # Progress bar
            bar_outer = tk.Frame(result_card, bg="#e5e7eb", height=6)
            bar_outer.pack(fill="x", pady=(6, 8))
            bar_outer.pack_propagate(False)
            bar_inner = tk.Frame(bar_outer, bg=bar, height=6)
            bar_inner.place(relwidth=score, relheight=1)

            # Description
            tk.Label(
                result_card,
                text=cap["description"],
                font=("Helvetica", 10),
                bg=LIGHT_BG, fg="#374151",
                wraplength=660, justify="left",
            ).pack(anchor="w", pady=(0, 6))

            # Tag pills
            pill_row = tk.Frame(result_card, bg=LIGHT_BG)
            pill_row.pack(anchor="w")
            tk.Label(
                pill_row,
                text="Topics:",
                font=("Helvetica", 8, "bold"),
                bg=LIGHT_BG, fg=MUTED,
            ).pack(side="left", padx=(0, 6))
            for tag in cap["tags"]:
                pill = self._tag_pill(pill_row, tag)
                pill.pack(side="left", padx=2)

            shown += 1

        if shown == 0:
            tk.Label(
                body,
                text="⚠️  No strong matches found. Try completing more courses or adjusting ratings.",
                font=("Helvetica", 10),
                bg=WHITE, fg=RED,
            ).pack(anchor="w")

    # ── Instructor Tab ────────────────────────────────────────────────────────

    def _build_instructor_tab(self, parent):
        _, inner = self._scrollable(parent)

        intro_body = self._card(inner, "Capstone Project Manager", "#1e40af", "🔧")
        tk.Label(
            intro_body,
            text=(
                "Add, edit, or remove capstone projects. Use <tag> notation to link "
                "projects to course topics. The recommendation engine uses these tags "
                "to match students based on their coursework and enjoyment ratings."
            ),
            font=("Helvetica", 9, "italic"),
            bg=WHITE, fg=MUTED, wraplength=720, justify="left",
        ).pack(anchor="w", pady=(0, 10))

        # Available tags reference
        ref_row = tk.Frame(intro_body, bg=WHITE)
        ref_row.pack(anchor="w", pady=(0, 4))
        tk.Label(
            ref_row,
            text="Available tags:",
            font=("Helvetica", 9, "bold"),
            bg=WHITE, fg="#374151",
        ).pack(side="left", padx=(0, 8))
        for tag in TAG_COLORS:
            pill = self._tag_pill(ref_row, tag)
            pill.pack(side="left", padx=2)

        # Capstone list
        list_body = self._card(inner, "Current Capstone Projects", MID_DARK, "📋")
        self.cap_list_frame = tk.Frame(list_body, bg=WHITE)
        self.cap_list_frame.pack(fill="x")
        self._refresh_capstone_list()

        # Add new capstone form
        form_body = self._card(inner, "Add New Capstone Project", GREEN, "➕")

        fields = tk.Frame(form_body, bg=WHITE)
        fields.pack(fill="x")
        fields.columnconfigure(1, weight=1)

        def _lbl(text, row):
            tk.Label(
                fields, text=text,
                font=("Helvetica", 10, "bold"),
                bg=WHITE, fg="#374151",
            ).grid(row=row, column=0, sticky="nw", pady=(6, 2), padx=(0, 12))

        _lbl("Project Name:", 0)
        self.new_name_var = tk.StringVar()
        ttk.Entry(fields, textvariable=self.new_name_var, font=("Helvetica", 10), width=55).grid(
            row=0, column=1, sticky="ew", pady=(6, 2)
        )

        _lbl("Description:", 1)
        desc_frame = tk.Frame(fields, bg=WHITE, highlightbackground="#d1d5db", highlightthickness=1)
        desc_frame.grid(row=1, column=1, sticky="ew", pady=(6, 2))
        self.new_desc_text = tk.Text(
            desc_frame, height=3, width=55,
            font=("Helvetica", 10),
            relief="flat", bd=4, bg=WHITE,
            wrap="word",
        )
        self.new_desc_text.pack(fill="x")

        _lbl("Tags:", 2)
        self.new_tags_var = tk.StringVar()
        ttk.Entry(fields, textvariable=self.new_tags_var, font=("Courier", 10), width=55).grid(
            row=2, column=1, sticky="ew", pady=(6, 2)
        )
        tk.Label(
            fields,
            text="Format:  <electrical>  <programming>  <robotics>  <embedded>  <networking>  <security>  etc.",
            font=("Helvetica", 8, "italic"),
            bg=WHITE, fg="#9ca3af",
        ).grid(row=3, column=1, sticky="w", pady=(0, 6))

        # Live tag preview
        preview_row = tk.Frame(fields, bg=WHITE)
        preview_row.grid(row=4, column=1, sticky="w", pady=(0, 8))
        tk.Label(preview_row, text="Preview:", font=("Helvetica", 8, "bold"),
                 bg=WHITE, fg=MUTED).pack(side="left", padx=(0, 6))
        self.preview_pills_frame = tk.Frame(preview_row, bg=WHITE)
        self.preview_pills_frame.pack(side="left")

        def _update_preview(*_):
            for w in self.preview_pills_frame.winfo_children():
                w.destroy()
            tags = parse_tags(self.new_tags_var.get())
            for t in tags:
                self._tag_pill(self.preview_pills_frame, t).pack(side="left", padx=2)

        self.new_tags_var.trace_add("write", _update_preview)

        tk.Button(
            form_body,
            text="➕  Add Capstone Project",
            command=self._add_capstone,
            bg=GREEN, fg=WHITE,
            font=("Helvetica", 11, "bold"),
            relief="flat", padx=18, pady=9, cursor="hand2",
            activebackground="#059669", activeforeground=WHITE,
        ).pack(anchor="w", pady=(4, 0))

    def _refresh_capstone_list(self):
        for w in self.cap_list_frame.winfo_children():
            w.destroy()

        if not self.capstones:
            tk.Label(
                self.cap_list_frame,
                text="No capstone projects defined yet.",
                font=("Helvetica", 10, "italic"),
                bg=WHITE, fg=MUTED,
            ).pack(anchor="w", pady=6)
            return

        for i, cap in enumerate(self.capstones):
            row_bg = LIGHT_BG if i % 2 == 0 else WHITE
            row = tk.Frame(self.cap_list_frame, bg=row_bg, pady=7, padx=8)
            row.pack(fill="x")

            info = tk.Frame(row, bg=row_bg)
            info.pack(side="left", fill="x", expand=True)

            tk.Label(
                info,
                text=cap["name"],
                font=("Helvetica", 10, "bold"),
                bg=row_bg, fg="#111827",
                anchor="w",
            ).pack(anchor="w")

            pill_row = tk.Frame(info, bg=row_bg)
            pill_row.pack(anchor="w", pady=(2, 0))
            for tag in cap["tags"]:
                pill = self._tag_pill(pill_row, tag)
                pill.pack(side="left", padx=2)

            tk.Button(
                row,
                text="✕  Remove",
                command=lambda idx=i: self._delete_capstone(idx),
                bg=RED, fg=WHITE,
                font=("Helvetica", 8, "bold"),
                relief="flat", padx=8, pady=3, cursor="hand2",
                activebackground="#dc2626", activeforeground=WHITE,
            ).pack(side="right", padx=(8, 0))

    def _add_capstone(self):
        name = self.new_name_var.get().strip()
        desc = self.new_desc_text.get("1.0", "end").strip()
        tags = parse_tags(self.new_tags_var.get())

        if not name:
            messagebox.showwarning("Missing Name", "Please enter a project name.")
            return
        if not tags:
            messagebox.showwarning(
                "Missing Tags",
                "Please enter at least one tag using <tag> format.\n\n"
                "Example:  <programming>  <electrical>  <robotics>",
            )
            return

        self.capstones.append({"name": name, "description": desc, "tags": tags})
        self._refresh_capstone_list()

        # Clear form
        self.new_name_var.set("")
        self.new_desc_text.delete("1.0", "end")
        self.new_tags_var.set("")

        messagebox.showinfo("Capstone Added", f'"{name}" has been added successfully.')

    def _delete_capstone(self, idx: int):
        name = self.capstones[idx]["name"]
        if messagebox.askyesno("Confirm Delete", f'Remove "{name}" from the capstone list?'):
            self.capstones.pop(idx)
            self._refresh_capstone_list()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TEntry", padding=5)
    style.configure("TScrollbar", troughcolor=BG, background="#94a3b8")

    app = CapstoneAdvisorApp(root)
    root.mainloop()