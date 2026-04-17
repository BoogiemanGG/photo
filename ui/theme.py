"""
Shared design tokens for PhotoStudioHub GUI.
Inspired by Lovable / Linear aesthetic — clean, dark-first, strong accents.
"""

import customtkinter as ctk

ACCENT = "#6C63FF"          # purple accent
ACCENT_HOVER = "#8B85FF"
SUCCESS = "#22C55E"
WARNING = "#F59E0B"
DANGER = "#EF4444"
MUTED = "#6B7280"

FONT_HEADING = ("Inter", 18, "bold")
FONT_SUBHEADING = ("Inter", 13, "bold")
FONT_BODY = ("Inter", 12)
FONT_SMALL = ("Inter", 10)
FONT_MONO = ("Consolas", 11)

CORNER_RADIUS = 10
CARD_RADIUS = 12
BUTTON_HEIGHT = 36


def apply_theme(appearance: str = "dark") -> None:
    ctk.set_appearance_mode(appearance)
    ctk.set_default_color_theme("blue")


def accent_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=ACCENT,
        hover_color=ACCENT_HOVER,
        corner_radius=CORNER_RADIUS,
        height=BUTTON_HEIGHT,
        font=ctk.CTkFont(size=13, weight="bold"),
        **kw,
    )


def ghost_button(parent, text: str, command=None, **kw) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color="transparent",
        border_width=1,
        border_color=MUTED,
        text_color=("gray20", "gray80"),
        hover_color=("gray90", "gray20"),
        corner_radius=CORNER_RADIUS,
        height=BUTTON_HEIGHT,
        font=ctk.CTkFont(size=12),
        **kw,
    )


def card_frame(parent, **kw) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, corner_radius=CARD_RADIUS, **kw)


def section_label(parent, text: str, **kw) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=MUTED,
        **kw,
    )
