"""
Cull Review dialog — post-culling modal that lets the photographer browse
thumbnails of selects and rejects, override decisions, and confirm before
editing / retouching begins.
"""

from pathlib import Path

import customtkinter as ctk
from PIL import Image

from ui.theme import ACCENT, MUTED, SUCCESS, DANGER, card_frame, section_label
from ui.theme import accent_button, ghost_button


_THUMB_W = 180
_THUMB_H = 120
_COLS = 4


class CullReviewDialog(ctk.CTkToplevel):
    def __init__(self, parent, selects: list, rejects: list, on_done):
        super().__init__(parent)
        self.title("Review culling results")
        self.geometry("900x640")
        self.minsize(760, 520)
        self._on_done = on_done

        # Merge and annotate: each entry becomes {result, selected: bool}
        self._entries: list[dict] = []
        for r in selects:
            self._entries.append({"result": r, "selected": True})
        for r in rejects:
            self._entries.append({"result": r, "selected": False})

        self._tiles: list[_Tile] = []
        self._cancelled = False

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 6))
        ctk.CTkLabel(
            header, text="Review Culling Results",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")
        self._count_lbl = ctk.CTkLabel(
            header, text="", font=ctk.CTkFont(size=12), text_color=MUTED,
        )
        self._count_lbl.pack(side="right")

        ctk.CTkLabel(
            self,
            text="Click a thumbnail to toggle select/reject. "
                 "Green = keep, red = discard.",
            font=ctk.CTkFont(size=11), text_color=MUTED,
        ).grid(row=0, column=0, sticky="sw", padx=16, pady=(0, 0))

        # Scrollable grid of tiles
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        for c in range(_COLS):
            self._scroll.grid_columnconfigure(c, weight=1)

        for i, entry in enumerate(self._entries):
            tile = _Tile(
                self._scroll, entry,
                on_toggle=lambda t=None: self._update_count(),
            )
            tile.grid(row=i // _COLS, column=i % _COLS,
                      padx=6, pady=6, sticky="nsew")
            self._tiles.append(tile)

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=16, pady=12)
        footer.grid_columnconfigure(1, weight=1)

        ghost_button(footer, "Select all", command=self._select_all, width=110)\
            .grid(row=0, column=0, padx=(0, 6))
        ghost_button(footer, "Reject all", command=self._reject_all, width=110)\
            .grid(row=0, column=1, sticky="w")

        ghost_button(footer, "Cancel", command=self._on_cancel, width=100)\
            .grid(row=0, column=2, padx=(0, 8))
        accent_button(footer, "Continue",
                      command=self._on_continue, width=140)\
            .grid(row=0, column=3)

        self._update_count()

    def _update_count(self):
        n_sel = sum(1 for e in self._entries if e["selected"])
        n_rej = len(self._entries) - n_sel
        self._count_lbl.configure(text=f"{n_sel} selects / {n_rej} rejects")

    def _select_all(self):
        for t in self._tiles:
            t.set_selected(True)
        self._update_count()

    def _reject_all(self):
        for t in self._tiles:
            t.set_selected(False)
        self._update_count()

    def _on_continue(self):
        selects = [e["result"] for e in self._entries if e["selected"]]
        rejects = [e["result"] for e in self._entries if not e["selected"]]
        self._on_done(selects, rejects, False)
        self.destroy()

    def _on_cancel(self):
        self._cancelled = True
        self._on_done([], [], True)
        self.destroy()


class _Tile(ctk.CTkFrame):
    def __init__(self, parent, entry: dict, on_toggle):
        super().__init__(parent, corner_radius=8, border_width=2)
        self._entry = entry
        self._on_toggle = on_toggle
        self.grid_columnconfigure(0, weight=1)

        self._img_lbl = ctk.CTkLabel(self, text="", cursor="hand2")
        self._img_lbl.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 2))

        path = self._result_path()
        name = Path(path).name if path else "?"
        self._name_lbl = ctk.CTkLabel(
            self, text=name, font=ctk.CTkFont(size=10),
            anchor="w", wraplength=_THUMB_W,
        )
        self._name_lbl.grid(row=1, column=0, sticky="w", padx=6)

        meta = self._meta_text(entry["result"])
        self._meta_lbl = ctk.CTkLabel(
            self, text=meta, font=ctk.CTkFont(size=10),
            text_color=MUTED, anchor="w", wraplength=_THUMB_W,
        )
        self._meta_lbl.grid(row=2, column=0, sticky="w", padx=6, pady=(0, 4))

        self._load_thumb()
        self._refresh_border()
        self._img_lbl.bind("<Button-1>", lambda _e: self._toggle())
        self.bind("<Button-1>", lambda _e: self._toggle())
        self._name_lbl.bind("<Button-1>", lambda _e: self._toggle())
        self._meta_lbl.bind("<Button-1>", lambda _e: self._toggle())

    def _result_path(self) -> str:
        r = self._entry["result"]
        if isinstance(r, dict):
            return r.get("path", "")
        return str(r)

    def _meta_text(self, r) -> str:
        if not isinstance(r, dict):
            return ""
        bits = []
        if "score" in r:
            bits.append(f"score {r['score']}")
        reasons = _reject_reasons(r)
        if reasons:
            bits.append("• " + ", ".join(reasons))
        return "  ".join(bits)

    def _load_thumb(self):
        path = self._result_path()
        try:
            img = Image.open(path)
            img.thumbnail((_THUMB_W, _THUMB_H))
            w, h = img.size
            self._ctk_img = ctk.CTkImage(light_image=img, dark_image=img,
                                         size=(w, h))
            self._img_lbl.configure(image=self._ctk_img, text="")
        except Exception:
            self._img_lbl.configure(
                text="(no preview)", text_color=MUTED,
                height=_THUMB_H, width=_THUMB_W,
            )

    def set_selected(self, selected: bool):
        self._entry["selected"] = selected
        self._refresh_border()

    def _toggle(self):
        self._entry["selected"] = not self._entry["selected"]
        self._refresh_border()
        self._on_toggle()

    def _refresh_border(self):
        color = SUCCESS if self._entry["selected"] else DANGER
        self.configure(border_color=color)


def _reject_reasons(r: dict) -> list[str]:
    reasons: list[str] = []
    sh = r.get("sharpness")
    if isinstance(sh, dict) and sh.get("passed") is False:
        reasons.append("blurry")
    exp = r.get("exposure")
    if isinstance(exp, dict) and exp.get("passed") is False:
        reasons.append(exp.get("reason", "exposure"))
    nz = r.get("noise")
    if isinstance(nz, dict) and nz.get("passed") is False:
        reasons.append("noisy")
    mb = r.get("motion_blur")
    if isinstance(mb, dict) and mb.get("passed") is False:
        reasons.append("motion blur")
    eyes = r.get("eyes")
    if isinstance(eyes, dict) and eyes.get("all_eyes_open") is False:
        reasons.append("eyes closed")
    expr = r.get("expression")
    if isinstance(expr, dict) and expr.get("passed") is False:
        reasons.append("expression")
    return reasons
