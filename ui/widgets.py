"""Reusable widgets used across multiple views."""

import customtkinter as ctk
from .theme import ACCENT, MUTED, SUCCESS, DANGER, WARNING, FONT_MONO


class TrialBanner(ctk.CTkFrame):
    """Top-of-window banner showing trial/license status."""

    def __init__(self, parent, license_manager, lang_fn, **kw):
        super().__init__(parent, height=32, corner_radius=0, **kw)
        self._lm = license_manager
        self._t = lang_fn
        self._label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11))
        self._label.pack(side="left", padx=12)
        self._btn = ctk.CTkButton(
            self, text="", height=22, width=110,
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=6,
        )
        self._btn.pack(side="right", padx=8, pady=4)
        self.refresh()

    def refresh(self):
        status = self._lm.status_line()
        plan = self._lm.plan()
        if plan in ("pro", "unlimited"):
            self._label.configure(text=f"  ✓  {status}", text_color=SUCCESS)
            self._btn.configure(text="", width=0)
        elif plan == "trial":
            days = self._lm.days_left_trial()
            color = SUCCESS if days > 7 else (WARNING if days > 2 else DANGER)
            self._label.configure(text=f"  ⏳  {status}", text_color=color)
            self._btn.configure(
                text=self._t("trial.activate"),
                fg_color=ACCENT,
                hover_color="#8B85FF",
            )
        else:
            self._label.configure(
                text=f"  ✗  {status}", text_color=DANGER
            )
            self._btn.configure(
                text=self._t("trial.buy_now"),
                fg_color=DANGER,
                hover_color="#F87171",
            )


class FolderRow(ctk.CTkFrame):
    """Label + path entry + Browse button."""

    def __init__(self, parent, label: str, browse_cb, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        ctk.CTkLabel(self, text=label, width=120, anchor="w",
                     font=ctk.CTkFont(size=12)).pack(side="left")
        self._var = ctk.StringVar()
        self._entry = ctk.CTkEntry(self, textvariable=self._var,
                                   height=32, font=ctk.CTkFont(size=12))
        self._entry.pack(side="left", fill="x", expand=True, padx=(4, 6))
        ctk.CTkButton(
            self, text="Browse", width=80, height=32,
            font=ctk.CTkFont(size=12),
            command=lambda: self._on_browse(browse_cb),
        ).pack(side="left")

    def _on_browse(self, cb):
        path = cb()
        if path:
            self._var.set(path)

    @property
    def path(self) -> str:
        return self._var.get()

    def set_path(self, p: str):
        self._var.set(p)


class ProgressCard(ctk.CTkFrame):
    """Processing progress card: title, file counter, progress bar, ETA."""

    def __init__(self, parent, title: str, **kw):
        super().__init__(parent, corner_radius=12, **kw)
        self.grid_columnconfigure(0, weight=1)
        self._title = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        )
        self._title.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))
        self._counter = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=11), text_color=MUTED, anchor="w"
        )
        self._counter.grid(row=1, column=0, sticky="w", padx=16)
        self._bar = ctk.CTkProgressBar(self, height=6, corner_radius=4)
        self._bar.set(0)
        self._bar.grid(row=2, column=0, sticky="ew", padx=16, pady=(6, 4))
        self._eta = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=10), text_color=MUTED, anchor="e"
        )
        self._eta.grid(row=3, column=0, sticky="e", padx=16, pady=(0, 12))

    def update(self, current: int, total: int, eta: str = ""):
        pct = current / total if total else 0
        self._bar.set(pct)
        self._counter.configure(text=f"{current} / {total}")
        self._eta.configure(text=f"ETA: {eta}" if eta else "")

    def set_title(self, text: str):
        self._title.configure(text=text)

    def done(self):
        self._bar.set(1)
        self._eta.configure(text="Done ✓", text_color=SUCCESS)


class StatsRow(ctk.CTkFrame):
    """Three stat boxes: selects / rejects / rate."""

    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self._boxes = {}
        for i, (key, label) in enumerate([
            ("selects", "Selects"), ("rejects", "Rejects"), ("rate", "Rate")
        ]):
            box = ctk.CTkFrame(self, corner_radius=10)
            box.grid(row=0, column=i, padx=6, sticky="ew")
            self.grid_columnconfigure(i, weight=1)
            val_lbl = ctk.CTkLabel(box, text="—",
                                   font=ctk.CTkFont(size=22, weight="bold"))
            val_lbl.pack(padx=18, pady=(10, 2))
            ctk.CTkLabel(box, text=label,
                         font=ctk.CTkFont(size=10), text_color=MUTED).pack(pady=(0, 10))
            self._boxes[key] = val_lbl

    def set(self, selects: int, rejects: int):
        total = selects + rejects
        rate = f"{selects / total * 100:.0f}%" if total else "—"
        self._boxes["selects"].configure(text=str(selects), text_color=SUCCESS)
        self._boxes["rejects"].configure(text=str(rejects), text_color=DANGER)
        self._boxes["rate"].configure(text=rate)


class LogBox(ctk.CTkTextbox):
    """Scrollable monospace log output."""

    def __init__(self, parent, **kw):
        super().__init__(parent, font=ctk.CTkFont(family="Consolas", size=11),
                         state="disabled", **kw)

    def append(self, line: str):
        self.configure(state="normal")
        self.insert("end", line + "\n")
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")
