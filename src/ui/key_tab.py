import customtkinter as ctk
import tkinter as tk
from src.utils.helpers import save_to_file, load_from_file
from tkinter import messagebox

# ─── Tokens (imported from app palette) ───────────────────────────────────────
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
TEXT_PRIMARY  = "#e2e8f0"
TEXT_MUTED    = "#64748b"

FONT_MONO = "Consolas"
FONT_UI   = "Segoe UI"


def make_section_header(parent, text, accent=ACCENT_BLUE):
    """Horizontal rule + label used as a section divider."""
    f = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(f, text=text, font=ctk.CTkFont(family=FONT_UI, size=11, weight="bold"),
                 text_color=accent).pack(side="left")
    ctk.CTkFrame(f, height=1, fg_color=BORDER).pack(side="left", fill="x", expand=True, padx=(10, 0))
    return f


def make_card(parent, **kwargs):
    """Standard dark card frame."""
    return ctk.CTkFrame(parent,
                        fg_color=BG_CARD,
                        corner_radius=14,
                        border_width=1,
                        border_color=BORDER,
                        **kwargs)


def accent_button(parent, text, command, accent=ACCENT_BLUE, **kwargs):
    """Consistent CTA button."""
    return ctk.CTkButton(
        parent, text=text, command=command,
        font=ctk.CTkFont(family=FONT_UI, size=12, weight="bold"),
        fg_color=accent, hover_color=accent,
        corner_radius=10, height=40,
        **kwargs
    )


class KeyManagementTab(ctk.CTkFrame):
    def __init__(self, master, engine, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.configure(fg_color="transparent")
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ── Left column: config card ──────────────────────────────────────────
        left = make_card(self)
        left.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        # Card title
        title_strip = ctk.CTkFrame(left, fg_color=ACCENT_BLUE, height=3, corner_radius=0)
        title_strip.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 0))
        ctk.CTkLabel(left, text="⚙  CONFIGURATION",
                     font=ctk.CTkFont(family=FONT_UI, size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=20, pady=(16, 20))

        # Curve selector
        ctk.CTkLabel(left, text="ECC CURVE TYPE",
                     font=ctk.CTkFont(family=FONT_UI, size=10, weight="bold"),
                     text_color=TEXT_MUTED).grid(row=2, column=0, sticky="w", padx=20)

        self._curves = ["SECP256R1 (P-256)", "SECP384R1 (P-384)", "SECP521R1 (P-521)",
                        "Ed25519 (Signatures)", "X25519 (Key Exchange)"]
        self._curve_var = ctk.StringVar(value=self._curves[0])
        self._curve_menu = ctk.CTkOptionMenu(
            left, values=self._curves, variable=self._curve_var,
            font=ctk.CTkFont(family=FONT_UI, size=12),
            fg_color=BG_CARD2, button_color=ACCENT_BLUE,
            button_hover_color="#3a7ed8",
            dropdown_fg_color=BG_CARD2, corner_radius=10,
            dynamic_resizing=False)
        self._curve_menu.grid(row=3, column=0, sticky="ew", padx=20, pady=(6, 18))

        # Password
        ctk.CTkLabel(left, text="SECURITY PASSWORD",
                     font=ctk.CTkFont(family=FONT_UI, size=10, weight="bold"),
                     text_color=TEXT_MUTED).grid(row=4, column=0, sticky="w", padx=20)

        pw_frame = ctk.CTkFrame(left, fg_color=BG_CARD2, corner_radius=10, border_width=1, border_color=BORDER)
        pw_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(6, 6))
        pw_frame.grid_columnconfigure(0, weight=1)
        self._pw_entry = ctk.CTkEntry(pw_frame, placeholder_text="Optional passphrase…",
                                       show="*", border_width=0,
                                       fg_color="transparent",
                                       font=ctk.CTkFont(family=FONT_UI, size=12),
                                       text_color=TEXT_PRIMARY)
        self._pw_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=6)
        self._show_pw = ctk.CTkCheckBox(left, text="Show password",
                                         font=ctk.CTkFont(family=FONT_UI, size=11),
                                         text_color=TEXT_MUTED,
                                         fg_color=ACCENT_BLUE, hover_color="#3a7ed8",
                                         command=self._toggle_pw)
        self._show_pw.grid(row=6, column=0, sticky="w", padx=22, pady=(2, 20))

        # Spacer
        ctk.CTkFrame(left, fg_color=BORDER, height=1).grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Generate button
        self._gen_btn = ctk.CTkButton(
            left, text="  🔑  GENERATE KEYS",
            command=self._generate_keys,
            font=ctk.CTkFont(family=FONT_UI, size=13, weight="bold"),
            fg_color=ACCENT_BLUE, hover_color="#3a7ed8",
            corner_radius=10, height=46)
        self._gen_btn.grid(row=8, column=0, sticky="ew", padx=20, pady=(0, 20))

        # ── Right column: key displays ────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, padx=(0, 0), pady=0, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)

        # Private Key
        pk_card = self._make_key_card(right, "🔴  PRIVATE KEY",
                                       ACCENT_RED, row=0,
                                       save_cmd=self._save_priv,
                                       load_cmd=self._load_priv,
                                       text_attr="_priv_text")
        # divider
        ctk.CTkFrame(right, fg_color=BORDER, height=1).grid(row=1, column=0, sticky="ew", pady=6)

        # Public Key
        pub_card = self._make_key_card(right, "🟢  PUBLIC KEY",
                                        ACCENT_GREEN, row=2,
                                        save_cmd=self._save_pub,
                                        load_cmd=self._load_pub,
                                        text_attr="_pub_text")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_key_card(self, parent, title, accent, row, save_cmd, load_cmd, text_attr):
        card = make_card(parent)
        card.grid(row=row, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        # Header bar
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        ctk.CTkLabel(hdr, text=title,
                     font=ctk.CTkFont(family=FONT_UI, size=12, weight="bold"),
                     text_color=accent).pack(side="left")

        btn_f = ctk.CTkFrame(hdr, fg_color="transparent")
        btn_f.pack(side="right")
        for lbl, cmd in [("  ↑  Save", save_cmd), ("  ↓  Load", load_cmd)]:
            ctk.CTkButton(btn_f, text=lbl, command=cmd, width=72, height=26,
                          font=ctk.CTkFont(family=FONT_UI, size=10, weight="bold"),
                          fg_color=BG_CARD2, hover_color=BORDER_HI,
                          corner_radius=8, border_width=1, border_color=BORDER).pack(side="left", padx=3)

        tb = ctk.CTkTextbox(card, fg_color=BG_DEEP, border_color=BORDER, border_width=1,
                             font=(FONT_MONO, 11), text_color="#94a3b8", corner_radius=10)
        tb.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="nsew")
        setattr(self, text_attr, tb)
        return card

    def _toggle_pw(self):
        self._pw_entry.configure(show="" if self._show_pw.get() else "*")

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _generate_keys(self):
        curve = self._curve_var.get()
        pw = self._pw_entry.get().encode() or None
        try:
            priv, pub = self.engine.generate_keys(curve, pw)
            self._update_textboxes(priv, pub)
            self._gen_btn.configure(text="  ✓  KEYS GENERATED", fg_color=ACCENT_GREEN)
            self.after(2000, lambda: self._gen_btn.configure(text="  🔑  GENERATE KEYS",
                                                              fg_color=ACCENT_BLUE))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _update_textboxes(self, priv=None, pub=None):
        if priv is not None:
            self._priv_text.delete("0.0", "end")
            self._priv_text.insert("0.0", priv)
        if pub is not None:
            self._pub_text.delete("0.0", "end")
            self._pub_text.insert("0.0", pub)

    def _save_priv(self): save_to_file(self._priv_text.get("0.0", "end"), "private_key.pem")
    def _save_pub(self):  save_to_file(self._pub_text.get("0.0", "end"),  "public_key.pem")

    def _load_priv(self):
        data, _ = load_from_file()
        if data:
            try:
                priv, pub = self.engine.load_private_key(data, self._pw_entry.get().encode() or None)
                self._update_textboxes(priv, pub)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _load_pub(self):
        data, _ = load_from_file()
        if data:
            try:
                pub = self.engine.load_public_key(data)
                self._update_textboxes(pub=pub)
            except Exception as e:
                messagebox.showerror("Error", str(e))
