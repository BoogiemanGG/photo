"""
Main pipeline view — input/output folder selection, profile picker,
start/stop, live progress cards, stats row, and log.
"""

import threading
import time
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from ui.theme import accent_button, ghost_button, card_frame, section_label, ACCENT, MUTED
from ui.widgets import FolderRow, ProgressCard, StatsRow, LogBox


PROFILES = ["natural_warm", "light_airy", "moody_dark", "classic_bw"]
PROFILE_LABELS = {
    "natural_warm": "Natural Warm",
    "light_airy": "Light & Airy",
    "moody_dark": "Moody Dark",
    "classic_bw": "Classic B&W",
}


class PipelineView(ctk.CTkFrame):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self._app = app
        self._running = False
        self._thread: threading.Thread | None = None
        self._build()

    # ------------------------------------------------------------------ #
    # Layout                                                               #
    # ------------------------------------------------------------------ #

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        # --- Folder rows ---
        folder_card = card_frame(self)
        folder_card.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 12))
        folder_card.grid_columnconfigure(0, weight=1)

        section_label(folder_card, "INPUT / OUTPUT").grid(
            row=0, column=0, sticky="w", padx=16, pady=(12, 4)
        )

        self._input_row = FolderRow(
            folder_card,
            label=self._t("pipeline.select_input"),
            browse_cb=lambda: filedialog.askdirectory(title="Select Input Folder"),
        )
        self._input_row.grid(row=1, column=0, sticky="ew", padx=16, pady=4)

        self._output_row = FolderRow(
            folder_card,
            label=self._t("pipeline.select_output"),
            browse_cb=lambda: filedialog.askdirectory(title="Select Output Folder"),
        )
        self._output_row.grid(row=2, column=0, sticky="ew", padx=16, pady=(4, 14))

        # --- Profile + Mode row ---
        opts_frame = ctk.CTkFrame(self, fg_color="transparent")
        opts_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        opts_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(opts_frame, text=self._t("edit.profile"),
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 8))
        self._profile_var = ctk.StringVar(value="natural_warm")
        ctk.CTkOptionMenu(
            opts_frame,
            values=PROFILES,
            variable=self._profile_var,
            width=180,
            height=32,
            dynamic_resizing=False,
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(opts_frame, text="Mode", font=ctk.CTkFont(size=12)).grid(
            row=0, column=2, padx=(24, 8)
        )
        self._mode_var = ctk.StringVar(value="full")
        ctk.CTkSegmentedButton(
            opts_frame,
            values=["cull", "edit", "retouch", "full"],
            variable=self._mode_var,
            height=32,
        ).grid(row=0, column=3, sticky="w")

        # --- Start / Stop buttons ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="w", pady=(0, 16))
        self._start_btn = accent_button(btn_frame, self._t("pipeline.start"),
                                        command=self._on_start, width=140)
        self._start_btn.pack(side="left", padx=(0, 10))
        self._stop_btn = ghost_button(btn_frame, self._t("pipeline.stop"),
                                      command=self._on_stop, width=100)
        self._stop_btn.pack(side="left")
        self._stop_btn.configure(state="disabled")

        # --- Progress cards ---
        prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        prog_frame.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        prog_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._cull_card = ProgressCard(prog_frame, "Culling")
        self._cull_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._edit_card = ProgressCard(prog_frame, "Editing")
        self._edit_card.grid(row=0, column=1, sticky="nsew", padx=6)
        self._retouch_card = ProgressCard(prog_frame, "Retouching")
        self._retouch_card.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        # --- Stats row ---
        self._stats = StatsRow(self)
        self._stats.grid(row=4, column=0, sticky="ew", pady=(0, 12))

        # --- Log ---
        section_label(self, "LOG").grid(row=5, column=0, sticky="w", pady=(0, 4))
        self._log = LogBox(self, height=160)
        self._log.grid(row=6, column=0, sticky="nsew")
        self.grid_rowconfigure(6, weight=1)

    # ------------------------------------------------------------------ #
    # Event handlers                                                       #
    # ------------------------------------------------------------------ #

    def _on_start(self):
        input_path = self._input_row.path
        output_path = self._output_row.path
        if not input_path:
            self._log.append(f"[ERROR] {self._t('errors.no_input')}")
            return
        if not output_path:
            self._log.append(f"[ERROR] {self._t('errors.no_output')}")
            return
        photos = list(Path(input_path).glob("*"))
        photos = [p for p in photos if p.suffix.lower() in
                  {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".cr2", ".nef", ".arw", ".dng"}]
        if not photos:
            self._log.append(f"[ERROR] {self._t('errors.input_empty')}")
            return

        self._running = True
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._log.clear()
        self._log.append(f"[INFO] {self._t('pipeline.photos_found', n=len(photos))}")

        mode = self._mode_var.get()
        profile = self._profile_var.get()

        self._thread = threading.Thread(
            target=self._run_pipeline,
            args=(input_path, output_path, profile, mode, photos),
            daemon=True,
        )
        self._thread.start()

    def _on_stop(self):
        self._running = False
        self._log.append("[INFO] Stop requested — finishing current photo…")

    def _run_pipeline(self, input_path: str, output_path: str,
                      profile: str, mode: str, photos: list):
        import sys, os
        sys.path.insert(0, str(Path(__file__).parents[2]))

        try:
            total = len(photos)
            t0 = time.time()

            if mode in ("cull", "full"):
                from core.culling.pipeline import run_culling_pipeline
                self._log_ui(f"[CULL] Starting culling on {total} photos…")
                results = run_culling_pipeline([str(p) for p in photos])
                selects = [r for r in results if r.get("passed")]
                rejects = [r for r in results if not r.get("passed")]
                for i, r in enumerate(results, 1):
                    if not self._running:
                        break
                    self.after(0, self._cull_card.update, i, total, "")
                self.after(0, self._cull_card.done)
                self.after(0, self._stats.set, len(selects), len(rejects))
                self._log_ui(f"[CULL] Done — {len(selects)} selects, {len(rejects)} rejects")

            if mode in ("edit", "full") and self._running:
                from core.editing.pipeline import edit_single
                edit_photos = selects if mode == "full" else list(range(total))
                n = len(edit_photos)
                self._log_ui(f"[EDIT] Editing {n} photos…")
                for i, r in enumerate(edit_photos, 1):
                    if not self._running:
                        break
                    src = r["path"] if isinstance(r, dict) else photos[r]
                    out = Path(output_path) / Path(src).name
                    try:
                        edit_single(str(src), str(out), profile=profile)
                    except Exception as e:
                        self._log_ui(f"[EDIT] Error on {Path(src).name}: {e}")
                    elapsed = time.time() - t0
                    eta = f"{(elapsed / i) * (n - i):.0f}s"
                    self.after(0, self._edit_card.update, i, n, eta)
                self.after(0, self._edit_card.done)
                self._log_ui(f"[EDIT] Done")

            if mode in ("retouch", "full") and self._running:
                from core.retouching.pipeline import retouch_single
                retouch_photos = selects if mode == "full" else list(range(total))
                n = len(retouch_photos)
                self._log_ui(f"[RETOUCH] Retouching {n} photos…")
                for i, r in enumerate(retouch_photos, 1):
                    if not self._running:
                        break
                    src = r["path"] if isinstance(r, dict) else photos[r]
                    out_name = Path(output_path) / ("rt_" + Path(src).name)
                    try:
                        retouch_single(str(src), str(out_name))
                    except Exception as e:
                        self._log_ui(f"[RETOUCH] Error on {Path(src).name}: {e}")
                    elapsed = time.time() - t0
                    eta = f"{(elapsed / i) * (n - i):.0f}s"
                    self.after(0, self._retouch_card.update, i, n, eta)
                self.after(0, self._retouch_card.done)
                self._log_ui(f"[RETOUCH] Done")

            total_elapsed = time.time() - t0
            self._log_ui(f"[INFO] Pipeline finished in {total_elapsed:.1f}s")

        except Exception as e:
            self._log_ui(f"[ERROR] {self._t('errors.generic', msg=str(e))}")
        finally:
            self.after(0, self._finish)

    def _log_ui(self, msg: str):
        self.after(0, self._log.append, msg)

    def _finish(self):
        self._running = False
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")

    def _t(self, key: str, **kw) -> str:
        return self._app.t(key, **kw)
