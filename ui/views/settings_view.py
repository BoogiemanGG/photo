"""Settings view — language, theme, thresholds, output format."""

import json
from pathlib import Path

import customtkinter as ctk
from ui.theme import accent_button, ghost_button, card_frame, section_label, MUTED
from config import OUTPUT_FORMAT, OUTPUT_QUALITY

_SETTINGS_FILE = Path.home() / ".photostudiohub" / "user_settings.json"

_DEFAULTS = {
    "lang": "en",
    "theme": "dark",
    "output_format": OUTPUT_FORMAT,
    "output_quality": OUTPUT_QUALITY,
    "xmp_export": True,
    "thresholds.sharpness_min": 27,
    "thresholds.noise_max": 45,
    "thresholds.exposure_low": 23,
    "thresholds.exposure_high": 88,
    "thresholds.duplicate_threshold": 33,
    "thresholds.motion_blur_threshold": 10,
}


def _load_settings() -> dict:
    try:
        return json.loads(_SETTINGS_FILE.read_text())
    except Exception:
        return {}


def _write_settings(data: dict):
    _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SETTINGS_FILE.write_text(json.dumps(data, indent=2))


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        self._app = app
        self._saved = {**_DEFAULTS, **_load_settings()}
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        s = self._saved

        # --- Appearance ---
        appear_card = card_frame(self)
        appear_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        appear_card.grid_columnconfigure(1, weight=1)
        appear_card.grid_columnconfigure(2, minsize=56)

        section_label(appear_card, self._t("settings.title")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 8)
        )

        ctk.CTkLabel(appear_card, text=self._t("settings.language"),
                     font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", padx=16, pady=4)
        from i18n import all_lang_options
        lang_codes = [c for c, _ in all_lang_options()]
        self._lang_var = ctk.StringVar(value=s["lang"])
        ctk.CTkOptionMenu(
            appear_card, values=lang_codes, variable=self._lang_var,
            width=160, height=30,
        ).grid(row=1, column=1, sticky="w", padx=16, pady=4)

        ctk.CTkLabel(appear_card, text=self._t("settings.theme"),
                     font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", padx=16, pady=4)
        self._theme_var = ctk.StringVar(value=s["theme"])
        ctk.CTkSegmentedButton(
            appear_card, values=["dark", "light", "system"],
            variable=self._theme_var, height=28,
        ).grid(row=2, column=1, sticky="w", padx=16, pady=4)

        ctk.CTkLabel(appear_card, text=self._t("settings.output_format"),
                     font=ctk.CTkFont(size=12)).grid(row=3, column=0, sticky="w", padx=16, pady=4)
        self._fmt_var = ctk.StringVar(value=s["output_format"])
        ctk.CTkSegmentedButton(
            appear_card, values=["JPEG", "PNG", "TIFF"],
            variable=self._fmt_var, height=28,
        ).grid(row=3, column=1, sticky="w", padx=16, pady=4)

        ctk.CTkLabel(appear_card, text=self._t("settings.output_quality"),
                     font=ctk.CTkFont(size=12)).grid(row=4, column=0, sticky="w", padx=16, pady=4)
        self._quality_var = ctk.IntVar(value=s["output_quality"])
        ctk.CTkSlider(appear_card, from_=60, to=100, variable=self._quality_var,
                      number_of_steps=40).grid(row=4, column=1, sticky="ew", padx=16, pady=4)
        ctk.CTkLabel(appear_card, textvariable=self._quality_var,
                     font=ctk.CTkFont(size=11), text_color=MUTED, width=40).grid(
            row=4, column=2, padx=(0, 16), pady=4)

        ctk.CTkLabel(appear_card, text=self._t("settings.xmp_export"),
                     font=ctk.CTkFont(size=12)).grid(row=5, column=0, sticky="w", padx=16, pady=(4, 14))
        self._xmp_var = ctk.BooleanVar(value=s["xmp_export"])
        ctk.CTkSwitch(appear_card, text="", variable=self._xmp_var).grid(
            row=5, column=1, sticky="w", padx=16, pady=(4, 14))

        # --- Culling thresholds ---
        thresh_card = card_frame(self)
        thresh_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        thresh_card.grid_columnconfigure(1, weight=1)
        thresh_card.grid_columnconfigure(2, minsize=56)

        section_label(thresh_card, self._t("thresholds.title")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(12, 8)
        )

        threshold_keys = [
            "thresholds.sharpness_min",
            "thresholds.noise_max",
            "thresholds.exposure_low",
            "thresholds.exposure_high",
            "thresholds.duplicate_threshold",
            "thresholds.motion_blur_threshold",
        ]
        self._threshold_vars = {}
        for i, key in enumerate(threshold_keys, 1):
            var = ctk.IntVar(value=s[key])
            self._threshold_vars[key] = var
            ctk.CTkLabel(thresh_card, text=self._t(key),
                         font=ctk.CTkFont(size=12)).grid(
                row=i, column=0, sticky="w", padx=16, pady=2)
            ctk.CTkSlider(thresh_card, from_=0, to=100,
                          number_of_steps=100, variable=var).grid(
                row=i, column=1, sticky="ew", padx=12, pady=2)
            ctk.CTkLabel(thresh_card, textvariable=var,
                         font=ctk.CTkFont(size=11), text_color=MUTED, width=40).grid(
                row=i, column=2, padx=(0, 16), pady=2)

        # --- Save / Reset ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="w", pady=(4, 0))
        accent_button(btn_frame, self._t("settings.save"),
                      command=self._save, width=120).pack(side="left", padx=(0, 10))
        ghost_button(btn_frame, self._t("settings.reset"),
                     command=self._reset, width=120).pack(side="left")

    def _save(self):
        import config
        data = {
            "lang": self._lang_var.get(),
            "theme": self._theme_var.get(),
            "output_format": self._fmt_var.get(),
            "output_quality": self._quality_var.get(),
            "xmp_export": self._xmp_var.get(),
        }
        for key, var in self._threshold_vars.items():
            data[key] = var.get()

        _write_settings(data)

        self._app.set_lang(data["lang"])
        ctk.set_appearance_mode(data["theme"])
        self._app.theme = data["theme"]
        config.OUTPUT_FORMAT = data["output_format"]
        config.OUTPUT_QUALITY = data["output_quality"]
        config.XMP_EXPORT = data["xmp_export"]

    def _reset(self):
        self._lang_var.set(_DEFAULTS["lang"])
        self._theme_var.set(_DEFAULTS["theme"])
        self._fmt_var.set(_DEFAULTS["output_format"])
        self._quality_var.set(_DEFAULTS["output_quality"])
        self._xmp_var.set(_DEFAULTS["xmp_export"])
        for key, var in self._threshold_vars.items():
            var.set(_DEFAULTS[key])

    def _t(self, key: str, **kw) -> str:
        return self._app.t(key, **kw)
