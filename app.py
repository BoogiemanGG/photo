"""
PhotoStudioHub — main GUI entry point.
Run:  python app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk

from i18n import t as _t, set_lang, get_lang
from license.manager import LicenseManager
from ui.theme import apply_theme, ACCENT, MUTED
from ui.widgets import TrialBanner


class PhotoStudioHub(ctk.CTk):

    APP_TITLE = "PhotoStudioHub"
    GEOMETRY = "1080x720"
    MIN_SIZE = (860, 580)

    def __init__(self):
        super().__init__()

        self.license_manager = LicenseManager()
        self.lang = get_lang()
        self.theme = "dark"

        apply_theme(self.theme)
        self.title(self.APP_TITLE)
        self.geometry(self.GEOMETRY)
        self.minsize(*self.MIN_SIZE)

        self._check_access()
        self._build_ui()

    # ------------------------------------------------------------------ #
    # Access guard                                                         #
    # ------------------------------------------------------------------ #

    def _check_access(self):
        if not self.license_manager.can_run():
            self._show_expired_screen()

    def _show_expired_screen(self):
        from ui.views.activate_view import ActivateDialog
        ActivateDialog(self, self)
        # App still opens — users can see the interface but pipeline is gated

    # ------------------------------------------------------------------ #
    # UI build                                                             #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Trial banner (full width, row 0) ---
        self._banner = TrialBanner(self, self.license_manager, self.t)
        self._banner.grid(row=0, column=0, columnspan=2, sticky="ew")
        if self.license_manager.plan() in ("pro", "unlimited"):
            self._banner.grid_remove()

        # --- Sidebar (row 1, col 0) ---
        self._sidebar = self._build_sidebar()
        self._sidebar.grid(row=1, column=0, sticky="nsew")

        # --- Content area (row 1, col 1) ---
        self._content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self._content.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self._content.grid_rowconfigure(0, weight=1)
        self._content.grid_columnconfigure(0, weight=1)

        # Load default view
        self._views = {}
        self._active_view = None
        self._show_view("pipeline")

    def _build_sidebar(self) -> ctk.CTkFrame:
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(10, weight=1)

        # Logo
        ctk.CTkLabel(
            sidebar,
            text="PhotoStudio\nHub",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ACCENT,
            justify="center",
        ).grid(row=0, column=0, pady=(24, 8), padx=20, sticky="ew")

        ctk.CTkLabel(
            sidebar,
            text="AI Photo Processing",
            font=ctk.CTkFont(size=10),
            text_color=MUTED,
        ).grid(row=1, column=0, pady=(0, 20), padx=20, sticky="ew")

        # Navigation
        nav_items = [
            ("pipeline", self.t("nav.full_pipeline"), "🚀"),
            ("cull", self.t("nav.cull"), "✂"),
            ("edit", self.t("nav.edit"), "🎨"),
            ("retouch", self.t("nav.retouch"), "✨"),
            ("settings", self.t("nav.settings"), "⚙"),
            ("about", self.t("nav.about"), "ℹ"),
        ]
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for i, (key, label, icon) in enumerate(nav_items, 2):
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                height=40,
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                text_color=("gray20", "gray80"),
                corner_radius=8,
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self._show_view(k),
            )
            btn.grid(row=i, column=0, padx=8, pady=2, sticky="ew")
            self._nav_buttons[key] = btn

        # Activate button at bottom
        from ui.theme import accent_button
        act_btn = accent_button(
            sidebar,
            self.t("trial.activate") if not self.license_manager.is_licensed()
            else "✓ " + (self.license_manager.plan() or "").capitalize(),
            command=self._open_activate,
            width=160,
        )
        act_btn.grid(row=11, column=0, padx=20, pady=(0, 20), sticky="ew")
        self._activate_btn = act_btn

        return sidebar

    def _show_view(self, name: str):
        if self._active_view:
            self._views[self._active_view].grid_forget()

        # Highlight active nav button
        for k, btn in self._nav_buttons.items():
            btn.configure(
                fg_color=ACCENT if k == name else "transparent"
            )

        if name not in self._views:
            self._views[name] = self._create_view(name)

        self._views[name].grid(row=0, column=0, sticky="nsew")
        self._active_view = name

    def _create_view(self, name: str) -> ctk.CTkFrame:
        if name == "pipeline":
            from ui.views.pipeline_view import PipelineView
            return PipelineView(self._content, app=self)
        if name in ("cull", "edit", "retouch"):
            from ui.views.pipeline_view import PipelineView
            v = PipelineView(self._content, app=self)
            v._mode_var.set(name)
            return v
        if name == "settings":
            from ui.views.settings_view import SettingsView
            return SettingsView(self._content, app=self)
        if name == "about":
            return self._about_view()
        return ctk.CTkFrame(self._content, fg_color="transparent")

    def _about_view(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self._content, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(frame, text=self.t("about.title"),
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, pady=(20, 8)
        )
        ctk.CTkLabel(frame, text=self.t("about.desc"),
                     font=ctk.CTkFont(size=13)).grid(row=1, column=0, pady=4)
        ctk.CTkLabel(frame, text=self.t("about.offline"),
                     font=ctk.CTkFont(size=12), text_color=MUTED).grid(row=2, column=0, pady=4)
        ctk.CTkLabel(frame, text=self.t("about.credits"),
                     font=ctk.CTkFont(size=11), text_color=MUTED).grid(row=3, column=0, pady=16)
        fp = self.license_manager.fingerprint()
        ctk.CTkLabel(frame, text=f"Machine ID: {fp}",
                     font=ctk.CTkFont(family="Consolas", size=11),
                     text_color=MUTED).grid(row=4, column=0)
        return frame

    def _open_activate(self):
        from ui.views.activate_view import ActivateDialog
        ActivateDialog(self, self)

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def t(self, key: str, **kw) -> str:
        return _t(key, lang=self.lang, **kw)

    def set_lang(self, lang: str):
        set_lang(lang)
        self.lang = lang

    def refresh_trial_banner(self):
        self._banner.refresh()
        if self.license_manager.plan() in ("pro", "unlimited"):
            self._banner.grid_remove()
            if self._activate_btn.winfo_exists():
                plan = self.license_manager.plan() or ""
                self._activate_btn.configure(text=f"✓ {plan.capitalize()}")


def main():
    app = PhotoStudioHub()
    app.mainloop()


if __name__ == "__main__":
    main()
