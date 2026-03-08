import customtkinter as ctk
import tkinter as tk
from src.core.crypto_engine import ECCEngine
from src.ui.key_tab import KeyManagementTab
from src.ui.sign_tab import SignTab
from src.ui.verify_tab import VerifyTab
import time
import threading

# ─── Design Tokens ────────────────────────────────────────────────────────────
BG_DEEP    = "#0a0c10"
BG_SURFACE = "#0f1117"
BG_CARD    = "#161b27"
BG_CARD2   = "#1c2133"
BORDER     = "#252d42"
BORDER_HI  = "#2e3a57"

ACCENT_BLUE   = "#4f8ef7"
ACCENT_CYAN   = "#22d3ee"
ACCENT_GREEN  = "#34d399"
ACCENT_RED    = "#f87171"
ACCENT_PURPLE = "#a78bfa"
ACCENT_ORANGE = "#fb923c"
TEXT_PRIMARY  = "#e2e8f0"
TEXT_MUTED    = "#64748b"
TEXT_SUBTLE   = "#334155"

FONT_MONO = "Consolas"
FONT_UI   = "Segoe UI"

NAV_ITEMS = [
    ("key_management", "🔑", "Key\nManagement"),
    ("sign",           "✍",  "Sign\nMessage"),
    ("verify",         "🛡",  "Verify\nSignature"),
]


class AnimatedButton(ctk.CTkButton):
    """Button that pulses on hover via colour interpolation."""

    def __init__(self, master, base_color, hover_color, **kwargs):
        super().__init__(master, fg_color=base_color, hover_color=hover_color, **kwargs)
        self._base = base_color
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _=None):
        self.configure(fg_color=self._hover_color)

    def _on_leave(self, _=None):
        self.configure(fg_color=self._base)


class GlowLabel(ctk.CTkLabel):
    """Label whose text_color pulses between two values."""

    def __init__(self, master, color_a, color_b, speed=1800, **kwargs):
        super().__init__(master, **kwargs)
        self._ca, self._cb, self._speed = color_a, color_b, speed
        self._step = 0
        self._pulse()

    def _pulse(self):
        t = (1 + __import__("math").sin(self._step * 3.14159 / self._speed)) / 2
        r = int(int(self._ca[1:3], 16) * t + int(self._cb[1:3], 16) * (1 - t))
        g = int(int(self._ca[3:5], 16) * t + int(self._cb[3:5], 16) * (1 - t))
        b = int(int(self._ca[5:7], 16) * t + int(self._cb[5:7], 16) * (1 - t))
        self.configure(text_color=f"#{r:02x}{g:02x}{b:02x}")
        self._step += 30
        self.after(30, self._pulse)


class NavButton(ctk.CTkFrame):
    """Sidebar icon + label navigation button with selection highlight."""

    def __init__(self, master, icon, label_text, key, on_select, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=12, **kwargs)
        self._key = key
        self._on_select = on_select
        self._selected = False

        self._bg_canvas = tk.Canvas(self, bg=BG_SURFACE, highlightthickness=0, width=82, height=88)
        self._bg_canvas.pack(fill="both", expand=True)

        self._icon_lbl = tk.Label(self._bg_canvas, text=icon, font=(FONT_UI, 20),
                                  bg=BG_SURFACE, fg=TEXT_MUTED)
        self._icon_lbl.place(relx=0.5, rely=0.36, anchor="center")

        self._text_lbl = tk.Label(self._bg_canvas, text=label_text, font=(FONT_UI, 9),
                                   bg=BG_SURFACE, fg=TEXT_MUTED, justify="center", wraplength=76)
        self._text_lbl.place(relx=0.5, rely=0.74, anchor="center")

        self._bg_canvas.bind("<Button-1>", self._click)
        self._icon_lbl.bind("<Button-1>", self._click)
        self._text_lbl.bind("<Button-1>", self._click)
        self._bg_canvas.bind("<Enter>", self._hover_on)
        self._bg_canvas.bind("<Leave>", self._hover_off)
        self._icon_lbl.bind("<Enter>", self._hover_on)
        self._icon_lbl.bind("<Leave>", self._hover_off)

    def _click(self, _=None):
        self._on_select(self._key)

    def _hover_on(self, _=None):
        if not self._selected:
            self._set_colors(BG_CARD, TEXT_PRIMARY, ACCENT_BLUE)

    def _hover_off(self, _=None):
        if not self._selected:
            self._set_colors(BG_SURFACE, TEXT_MUTED, TEXT_MUTED)

    def _set_colors(self, bg, fg_icon, fg_text):
        self._bg_canvas.configure(bg=bg)
        self._icon_lbl.configure(bg=bg, fg=fg_icon)
        self._text_lbl.configure(bg=bg, fg=fg_text)

    def select(self):
        self._selected = True
        self._set_colors(BG_CARD2, ACCENT_CYAN, ACCENT_CYAN)

    def deselect(self):
        self._selected = False
        self._set_colors(BG_SURFACE, TEXT_MUTED, TEXT_MUTED)


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, height=28, fg_color=BG_SURFACE,
                         corner_radius=0, **kwargs)
        self.pack_propagate(False)

        self._dot = ctk.CTkLabel(self, text="●", text_color=ACCENT_GREEN,
                                  font=ctk.CTkFont(size=10))
        self._dot.pack(side="left", padx=(12, 4))

        self._msg = ctk.CTkLabel(self, text="System ready  •  ECC Engine initialised",
                                  text_color=TEXT_MUTED,
                                  font=ctk.CTkFont(family=FONT_UI, size=11))
        self._msg.pack(side="left")

        self._clock = ctk.CTkLabel(self, text="", text_color=TEXT_SUBTLE,
                                    font=ctk.CTkFont(family=FONT_MONO, size=10))
        self._clock.pack(side="right", padx=12)
        self._tick()

    def set(self, text, color=ACCENT_GREEN):
        self._dot.configure(text_color=color)
        self._msg.configure(text=text)

    def _tick(self):
        self._clock.configure(text=time.strftime("%H:%M:%S"))
        self.after(1000, self._tick)


class ModernECCApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ECC Encryption")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=BG_DEEP)

        self.engine = ECCEngine()
        self._current_tab = None
        self._tab_frames: dict[str, ctk.CTkFrame] = {}
        self._nav_btns: dict[str, NavButton] = {}

        self._build_ui()
        self._switch_tab("key_management")

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ─ taller so nothing clips ────────────────────────────────
        hdr = tk.Frame(self, bg=BG_SURFACE, height=70)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # Decorative left accent strip
        tk.Frame(hdr, bg=ACCENT_BLUE, width=4).pack(side="left", fill="y")

        tk.Label(hdr, text="⬡", font=(FONT_UI, 24, "bold"),
                 bg=BG_SURFACE, fg=ACCENT_CYAN).pack(side="left", padx=(14, 8))

        title_f = tk.Frame(hdr, bg=BG_SURFACE)
        title_f.pack(side="left")
        tk.Label(title_f, text="ECC ENCRYPTION", font=(FONT_UI, 16, "bold"),
                 bg=BG_SURFACE, fg=TEXT_PRIMARY).pack(anchor="w")
        tk.Label(title_f, text="Elliptic Curve Cryptography  •  v2.1.0",
                 font=(FONT_UI, 10), bg=BG_SURFACE, fg=TEXT_MUTED).pack(anchor="w")

        # Right-side badges
        badge_f = tk.Frame(hdr, bg=BG_SURFACE)
        badge_f.pack(side="right", padx=18)
        for txt, col in [("P-256/384/521", ACCENT_BLUE), ("Ed25519", ACCENT_PURPLE)]:
            tk.Label(badge_f, text=txt, font=(FONT_UI, 9, "bold"),
                     bg=col, fg="white",
                     padx=8, pady=3, relief="flat").pack(side="left", padx=4)

        # ── Separator ─────────────────────────────────────────────────────────
        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x")

        # ── Body: sidebar + content ────────────────────────────────────────────
        body = tk.Frame(self, bg=BG_DEEP)
        body.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(body, bg=BG_SURFACE, width=88)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Vertical accent line on sidebar right edge
        tk.Frame(sidebar, bg=BORDER, width=1).pack(side="right", fill="y")

        for key, icon, label in NAV_ITEMS:
            btn = NavButton(sidebar, icon, label, key, self._switch_tab)
            btn.pack(pady=(8, 2), padx=8)
            self._nav_btns[key] = btn

        # Content area
        self._content = tk.Frame(body, bg=BG_DEEP)
        self._content.pack(side="left", fill="both", expand=True)

        # Container for tabs to provide consistent margins (20px)
        # Tab frames will fill this container and switch via tkraise()
        self._tab_container = ctk.CTkFrame(self._content, fg_color="transparent")
        self._tab_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Pre-build tab frames and place them all in the same spot (stacked).
        self._tab_frames["key_management"] = KeyManagementTab(
            self._tab_container, self.engine, fg_color=BG_DEEP)
        self._tab_frames["sign"] = SignTab(
            self._tab_container, self.engine,
            on_signature_generated=self.sync_signature,
            fg_color=BG_DEEP)
        self._tab_frames["verify"] = VerifyTab(
            self._tab_container, self.engine, fg_color=BG_DEEP)

        # place() with relwidth/relheight=1 stacks frames inside the container
        for frame in self._tab_frames.values():
            frame.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        # ── Status bar ────────────────────────────────────────────────────────
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        self._status_bar = StatusBar(self)
        self._status_bar.pack(fill="x", side="bottom")

    # ── Navigation ────────────────────────────────────────────────────────────

    def _switch_tab(self, key: str):
        if self._current_tab == key:
            return
        # Bring the selected frame to the top – no pack/unpack → no flicker
        self._tab_frames[key].tkraise()
        for k, btn in self._nav_btns.items():
            btn.select() if k == key else btn.deselect()
        self._current_tab = key
        names = {"key_management": "Key Management", "sign": "Sign Message", "verify": "Verify Signature"}
        self._status_bar.set(f"Active view: {names.get(key, key)}", ACCENT_CYAN)

    # ── Cross-tab sync ────────────────────────────────────────────────────────

    def sync_signature(self, message: str, signature: str):
        self._tab_frames["verify"].set_data(message, signature)
        self._status_bar.set("Signature generated – synced to Verify tab ✓", ACCENT_GREEN)
