"""License activation dialog / view."""

import customtkinter as ctk
from ui.theme import accent_button, ACCENT, SUCCESS, DANGER, MUTED


class ActivateDialog(ctk.CTkToplevel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, **kw)
        self._app = app
        self.title("Activate License — PhotoStudioHub")
        self.geometry("480x340")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="PhotoStudioHub",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, pady=(28, 4))

        ctk.CTkLabel(
            self,
            text=self._t("trial.enter_key"),
            font=ctk.CTkFont(size=13),
            text_color=MUTED,
        ).grid(row=1, column=0, pady=(0, 20))

        self._key_entry = ctk.CTkEntry(
            self,
            placeholder_text="pro|XXXXXXXXXXXXXXXX|2027-01-01|...",
            width=400,
            height=38,
            font=ctk.CTkFont(family="Consolas", size=11),
        )
        self._key_entry.grid(row=2, column=0, padx=40)

        self._status_lbl = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=11)
        )
        self._status_lbl.grid(row=3, column=0, pady=(10, 0))

        fp_text = f"Machine ID: {self._app.license_manager.fingerprint()}"
        ctk.CTkLabel(
            self, text=fp_text,
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=MUTED,
        ).grid(row=4, column=0, pady=(16, 0))

        ctk.CTkLabel(
            self,
            text="Send your Machine ID to support@photostudiohub.com to receive your key.",
            font=ctk.CTkFont(size=10),
            text_color=MUTED,
            wraplength=400,
        ).grid(row=5, column=0, pady=(4, 0))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, pady=24)
        accent_button(
            btn_frame,
            self._t("trial.activate"),
            command=self._activate,
            width=160,
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            btn_frame, text="Close", width=100, height=36,
            fg_color="transparent", border_width=1,
            command=self.destroy,
        ).pack(side="left", padx=8)

    def _activate(self):
        key = self._key_entry.get().strip()
        if not key:
            return
        result = self._app.license_manager.activate(key)
        if result["valid"]:
            self._status_lbl.configure(
                text=f"✓  {self._t('trial.key_valid')}  ({result['plan'].capitalize()})",
                text_color=SUCCESS,
            )
            self._app.refresh_trial_banner()
            self.after(1500, self.destroy)
        else:
            self._status_lbl.configure(
                text=f"✗  {self._t('trial.key_invalid')} — {result.get('error', '')}",
                text_color=DANGER,
            )

    def _t(self, key: str, **kw) -> str:
        return self._app.t(key, **kw)
