"""
Main pipeline view — input/output folder selection, profile picker,
start/stop, live progress cards, stats row, and log.
"""

import shutil
import threading
import time
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from ui.theme import accent_button, ghost_button, card_frame, section_label, ACCENT, MUTED
from ui.widgets import FolderRow, ProgressCard, StatsRow, LogBox


PROFILES = [
    "natural_warm", "light_airy", "moody_dark", "classic_bw",
    "faded_matte", "golden_hour", "cool_editorial", "vibrant", "film_vintage",
]
PROFILE_LABELS = {
    "natural_warm":   "Natural Warm",
    "light_airy":     "Light & Airy",
    "moody_dark":     "Moody Dark",
    "classic_bw":     "Classic B&W",
    "faded_matte":    "Faded Matte",
    "golden_hour":    "Golden Hour",
    "cool_editorial": "Cool Editorial",
    "vibrant":        "Vibrant",
    "film_vintage":   "Film Vintage",
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
        self._profile_var = ctk.StringVar(value=PROFILE_LABELS["natural_warm"])
        ctk.CTkOptionMenu(
            opts_frame,
            values=list(PROFILE_LABELS.values()),
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

        # --- Retouch options (checklist) ---
        rt_card = card_frame(self)
        rt_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        rt_card.grid_columnconfigure((0, 1, 2, 3), weight=1)
        section_label(rt_card, "RETOUCH STEPS").grid(
            row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(12, 4)
        )
        self._retouch_vars: dict[str, ctk.BooleanVar] = {}
        _rt_opts = [
            ("do_blemish",      "Blemish removal",   True),
            ("do_skin_smooth",  "Skin smoothing",    True),
            ("do_dark_circles", "Dark circles",      True),
            ("do_eye_bright",   "Eye brightening",   True),
            ("do_teeth",        "Teeth whitening",   True),
            ("do_shine",        "Shine reduction",   True),
            ("do_red_eye",      "Red-eye removal",   True),
            ("do_dust",         "Dust spot removal", True),
        ]
        for idx, (key, label, default) in enumerate(_rt_opts):
            var = ctk.BooleanVar(value=default)
            self._retouch_vars[key] = var
            ctk.CTkCheckBox(
                rt_card, text=label, variable=var,
                font=ctk.CTkFont(size=11), height=22,
            ).grid(row=1 + idx // 4, column=idx % 4, sticky="w", padx=16, pady=4)
        # pad bottom
        ctk.CTkFrame(rt_card, fg_color="transparent", height=8).grid(
            row=3, column=0, columnspan=4, sticky="ew"
        )

        # --- Output options: batch rename + review ---
        out_card = card_frame(self)
        out_card.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        out_card.grid_columnconfigure(2, weight=1)
        section_label(out_card, "OUTPUT OPTIONS").grid(
            row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(12, 4)
        )
        self._rename_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            out_card, text="Batch rename output",
            variable=self._rename_var,
            font=ctk.CTkFont(size=12), height=22,
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(4, 10))
        self._rename_prefix_var = ctk.StringVar(value="Session")
        ctk.CTkLabel(out_card, text="Prefix:", font=ctk.CTkFont(size=11)).grid(
            row=1, column=1, sticky="e", padx=(0, 4)
        )
        ctk.CTkEntry(
            out_card, textvariable=self._rename_prefix_var,
            width=160, height=28, font=ctk.CTkFont(size=12),
        ).grid(row=1, column=2, sticky="w", padx=(0, 16))
        self._review_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            out_card, text="Review culls before editing",
            variable=self._review_var,
            font=ctk.CTkFont(size=12), height=22,
        ).grid(row=1, column=3, sticky="e", padx=16)

        # --- Start / Stop buttons ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="w", pady=(0, 16))
        self._start_btn = accent_button(btn_frame, self._t("pipeline.start"),
                                        command=self._on_start, width=140)
        self._start_btn.pack(side="left", padx=(0, 10))
        self._stop_btn = ghost_button(btn_frame, self._t("pipeline.stop"),
                                      command=self._on_stop, width=100)
        self._stop_btn.pack(side="left")
        self._stop_btn.configure(state="disabled")

        # --- Progress cards ---
        prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        prog_frame.grid(row=5, column=0, sticky="ew", pady=(0, 12))
        prog_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._cull_card = ProgressCard(prog_frame, "Culling")
        self._cull_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        self._edit_card = ProgressCard(prog_frame, "Editing")
        self._edit_card.grid(row=0, column=1, sticky="nsew", padx=6)
        self._retouch_card = ProgressCard(prog_frame, "Retouching")
        self._retouch_card.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        # --- Stats row ---
        self._stats = StatsRow(self)
        self._stats.grid(row=6, column=0, sticky="ew", pady=(0, 12))

        # --- Log ---
        section_label(self, "LOG").grid(row=7, column=0, sticky="w", pady=(0, 4))
        self._log = LogBox(self, height=160)
        self._log.grid(row=8, column=0, sticky="nsew")
        self.grid_rowconfigure(8, weight=1)

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
        _label_to_key = {v: k for k, v in PROFILE_LABELS.items()}
        profile = _label_to_key.get(self._profile_var.get(), "natural_warm")

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
        import sys
        sys.path.insert(0, str(Path(__file__).parents[2]))

        try:
            total = len(photos)
            t0 = time.time()
            selects: list = []
            rejects: list = []
            rename = self._rename_var.get()
            prefix = (self._rename_prefix_var.get() or "Session").strip() or "Session"
            retouch_opts = {k: v.get() for k, v in self._retouch_vars.items()}

            if mode in ("cull", "full"):
                from core.culling.pipeline import run_culling_pipeline
                self._log_ui(f"[CULL] Starting culling on {total} photos…")
                cull_result = run_culling_pipeline([str(p) for p in photos])
                selects = cull_result["selects"]
                rejects = cull_result["rejects"]
                for i in range(1, total + 1):
                    if not self._running:
                        break
                    self.after(0, self._cull_card.update, i, total, "")
                self.after(0, self._cull_card.done)
                self.after(0, self._stats.set, len(selects), len(rejects))
                self._log_ui(f"[CULL] Done — {len(selects)} selects, {len(rejects)} rejects")

                # Copy originals into selects/ + rejects/ subfolders
                selects_dir = Path(output_path) / "selects"
                rejects_dir = Path(output_path) / "rejects"
                selects_dir.mkdir(parents=True, exist_ok=True)
                rejects_dir.mkdir(parents=True, exist_ok=True)
                for r in rejects:
                    src = r["path"] if isinstance(r, dict) else r
                    try:
                        shutil.copy2(src, rejects_dir / Path(src).name)
                    except Exception as e:
                        self._log_ui(f"[CULL] Copy reject failed {Path(src).name}: {e}")
                for r in selects:
                    src = r["path"] if isinstance(r, dict) else r
                    try:
                        shutil.copy2(src, selects_dir / Path(src).name)
                    except Exception as e:
                        self._log_ui(f"[CULL] Copy select failed {Path(src).name}: {e}")
                self._log_ui(
                    f"[CULL] Copied originals → selects/ ({len(selects)}), "
                    f"rejects/ ({len(rejects)})"
                )

                # Optional interactive review — only in full mode
                if mode == "full" and self._review_var.get() and self._running:
                    reviewed = self._review_culls(selects, rejects)
                    if reviewed is None:
                        self._log_ui("[CULL] Review cancelled — stopping")
                        self._running = False
                    else:
                        selects, rejects = reviewed
                        self.after(0, self._stats.set, len(selects), len(rejects))
                        self._log_ui(
                            f"[CULL] After review — {len(selects)} selects, "
                            f"{len(rejects)} rejects"
                        )

            if mode in ("edit", "full") and self._running:
                from core.editing.pipeline import edit_single
                import config as _cfg
                _ext = {"JPEG": ".jpg", "PNG": ".png", "TIFF": ".tiff"}.get(
                    _cfg.OUTPUT_FORMAT, ".jpg")
                edit_photos = selects if mode == "full" else list(range(total))
                n = len(edit_photos)
                pad = max(3, len(str(n)))
                self._log_ui(f"[EDIT] Editing {n} photos…")
                for i, r in enumerate(edit_photos, 1):
                    if not self._running:
                        break
                    src = r["path"] if isinstance(r, dict) else photos[r]
                    stem = (f"{prefix}_{i:0{pad}d}" if rename
                            else Path(src).stem)
                    out = Path(output_path) / (stem + _ext)
                    try:
                        edit_single(str(src), str(out), profile=profile)
                    except Exception as e:
                        self._log_ui(f"[EDIT] Error on {Path(src).name}: {e}")
                    elapsed = time.time() - t0
                    eta = f"{(elapsed / i) * (n - i):.0f}s"
                    self.after(0, self._edit_card.update, i, n, eta)
                self.after(0, self._edit_card.done)
                self._log_ui("[EDIT] Done")

            if mode in ("retouch", "full") and self._running:
                from core.retouching.pipeline import retouch_single
                retouch_photos = selects if mode == "full" else list(range(total))
                n = len(retouch_photos)
                pad = max(3, len(str(n)))
                self._log_ui(f"[RETOUCH] Retouching {n} photos…")
                for i, r in enumerate(retouch_photos, 1):
                    if not self._running:
                        break
                    src = r["path"] if isinstance(r, dict) else photos[r]
                    if rename:
                        out_name = Path(output_path) / (
                            f"{prefix}_{i:0{pad}d}_rt" + Path(src).suffix
                        )
                    else:
                        out_name = Path(output_path) / ("rt_" + Path(src).name)
                    try:
                        retouch_single(str(src), str(out_name), **retouch_opts)
                    except Exception as e:
                        self._log_ui(f"[RETOUCH] Error on {Path(src).name}: {e}")
                    elapsed = time.time() - t0
                    eta = f"{(elapsed / i) * (n - i):.0f}s"
                    self.after(0, self._retouch_card.update, i, n, eta)
                self.after(0, self._retouch_card.done)
                self._log_ui("[RETOUCH] Done")

            total_elapsed = time.time() - t0
            self._log_ui(f"[INFO] Pipeline finished in {total_elapsed:.1f}s")

        except Exception as e:
            self._log_ui(f"[ERROR] {self._t('errors.generic', msg=str(e))}")
        finally:
            self.after(0, self._finish)

    def _review_culls(self, selects: list, rejects: list):
        """Show modal CullReviewDialog, block pipeline thread until user decides.
        Returns (selects, rejects) after user overrides, or None if cancelled.
        """
        from ui.views.cull_review_view import CullReviewDialog
        done_evt = threading.Event()
        result: dict = {"selects": selects, "rejects": rejects, "cancelled": False}

        def _open():
            dlg = CullReviewDialog(self, selects, rejects, on_done=_on_done)
            dlg.grab_set()

        def _on_done(new_selects, new_rejects, cancelled):
            result["selects"] = new_selects
            result["rejects"] = new_rejects
            result["cancelled"] = cancelled
            done_evt.set()

        self.after(0, _open)
        done_evt.wait()
        if result["cancelled"]:
            return None
        return result["selects"], result["rejects"]

    def _log_ui(self, msg: str):
        self.after(0, self._log.append, msg)

    def _finish(self):
        self._running = False
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")

    def _t(self, key: str, **kw) -> str:
        return self._app.t(key, **kw)
