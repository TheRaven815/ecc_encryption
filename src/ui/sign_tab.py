import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import datetime

BG_DEEP    = "#0a0c10"
BG_SURFACE = "#0f1117"
BG_CARD    = "#161b27"
BG_CARD2   = "#1c2133"
BORDER     = "#252d42"
BORDER_HI  = "#2e3a57"

ACCENT_BLUE   = "#4f8ef7"
ACCENT_ORANGE = "#fb923c"
ACCENT_GREEN  = "#34d399"
TEXT_PRIMARY  = "#e2e8f0"
TEXT_MUTED    = "#64748b"

FONT_MONO = "Consolas"
FONT_UI   = "Segoe UI"


def make_card(parent, **kwargs):
    return ctk.CTkFrame(parent,
                        fg_color=BG_CARD,
                        corner_radius=14,
                        border_width=1,
                        border_color=BORDER,
                        **kwargs)


class SignTab(ctk.CTkFrame):
    def __init__(self, master, engine, on_signature_generated=None, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.on_signature_generated = on_signature_generated
        self.configure(fg_color="transparent")
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Left: Message input card ──────────────────────────────────────────
        left = make_card(self)
        left.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        # Top accent strip
        ctk.CTkFrame(left, fg_color=ACCENT_ORANGE, height=3, corner_radius=0).grid(
            row=0, column=0, sticky="ew")

        # Header
        hdr = ctk.CTkFrame(left, fg_color="transparent")
        hdr.grid(row=1, column=0, sticky="ew", padx=18, pady=(14, 8))
        ctk.CTkLabel(hdr, text="✍  MESSAGE TO SIGN",
                     font=ctk.CTkFont(family=FONT_UI, size=13, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        self._char_count = ctk.CTkLabel(hdr, text="0 chars",
                                         font=ctk.CTkFont(family=FONT_UI, size=10),
                                         text_color=TEXT_MUTED)
        self._char_count.pack(side="right")

        # Message textbox
        self._msg_text = ctk.CTkTextbox(left, fg_color=BG_DEEP,
                                          border_color=BORDER, border_width=1,
                                          font=(FONT_UI, 13),
                                          text_color=TEXT_PRIMARY,
                                          corner_radius=10)
        self._msg_text.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self._msg_text.bind("<KeyRelease>", self._update_char_count)
        self._msg_text.bind("<FocusIn>", lambda _: self._msg_text.configure(border_color=ACCENT_ORANGE))
        self._msg_text.bind("<FocusOut>", lambda _: self._msg_text.configure(border_color=BORDER))

        # Helper hint
        ctk.CTkLabel(left,
                      text="💡 Type or paste any text you want to sign cryptographically.",
                      font=ctk.CTkFont(family=FONT_UI, size=10),
                      text_color=TEXT_MUTED, anchor="w").grid(
            row=3, column=0, sticky="ew", padx=18, pady=(0, 14))

        # ── Right: action + output ────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, padx=(0, 0), pady=0, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        # Sign button (large, prominent)
        self._sign_btn = ctk.CTkButton(
            right,
            text="  ✍  GENERATE SIGNATURE",
            command=self._sign_message,
            font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
            fg_color=ACCENT_ORANGE,
            hover_color="#e07828",
            corner_radius=12,
            height=52)
        self._sign_btn.grid(row=0, column=0, pady=(0, 12), sticky="ew")

        # Signature output card
        sig_card = make_card(right)
        sig_card.grid(row=1, column=0, sticky="nsew")
        sig_card.grid_columnconfigure(0, weight=1)
        sig_card.grid_rowconfigure(2, weight=1)  # textbox row grows

        ctk.CTkFrame(sig_card, fg_color=ACCENT_GREEN, height=3, corner_radius=0).grid(
            row=0, column=0, sticky="ew")

        sig_hdr = ctk.CTkFrame(sig_card, fg_color="transparent")
        sig_hdr.grid(row=1, column=0, sticky="ew", padx=18, pady=(10, 4))
        ctk.CTkLabel(sig_hdr, text="🟢  RESULTING SIGNATURE",
                     font=ctk.CTkFont(family=FONT_UI, size=12, weight="bold"),
                     text_color=ACCENT_GREEN).pack(side="left")
        ctk.CTkButton(sig_hdr, text="Copy", command=self._copy_signature,
                      width=56, height=24,
                      font=ctk.CTkFont(family=FONT_UI, size=10),
                      fg_color=BG_CARD2, hover_color=BORDER_HI,
                      corner_radius=8).pack(side="right")

        self._sig_text = ctk.CTkTextbox(
            sig_card, fg_color=BG_DEEP,
            border_color=BORDER, border_width=1,
            font=(FONT_MONO, 11), text_color="#94a3b8",
            corner_radius=10)
        self._sig_text.grid(row=2, column=0, padx=18, pady=(0, 8), sticky="nsew")
        self._sig_text.bind("<FocusIn>", lambda _: self._sig_text.configure(border_color=ACCENT_GREEN))
        self._sig_text.bind("<FocusOut>", lambda _: self._sig_text.configure(border_color=BORDER))

        # Status label – inside sig_card so it doesn't steal height from the card
        self._status_lbl = ctk.CTkLabel(
            sig_card, text="Awaiting input…",
            font=ctk.CTkFont(family=FONT_UI, size=10),
            text_color=TEXT_MUTED, anchor="w")
        self._status_lbl.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 10))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _update_char_count(self, _=None):
        n = len(self._msg_text.get("0.0", "end").strip())
        self._char_count.configure(text=f"{n} chars")

    def _copy_signature(self):
        sig = self._sig_text.get("0.0", "end").strip()
        if sig:
            self.clipboard_clear()
            self.clipboard_append(sig)
            self._status_lbl.configure(text="✓ Signature copied to clipboard", text_color=ACCENT_GREEN)
            self.after(2500, lambda: self._status_lbl.configure(
                text="Awaiting input…", text_color=TEXT_MUTED))

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _sign_message(self):
        msg = self._msg_text.get("0.0", "end").strip()
        if not msg:
            self._status_lbl.configure(text="⚠  No message provided", text_color="#fb923c")
            return
        try:
            self._sign_btn.configure(text="  ⏳  Signing…", state="disabled")
            self.update_idletasks()
            signature = self.engine.sign_message(msg)
            self._sig_text.delete("0.0", "end")
            self._sig_text.insert("0.0", signature)
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            self._status_lbl.configure(text=f"✓  Signature generated at {ts}", text_color=ACCENT_GREEN)
            self._sign_btn.configure(text="  ✓  SIGNED!", fg_color=ACCENT_GREEN, state="normal")
            self.after(2000, lambda: self._sign_btn.configure(
                text="  ✍  GENERATE SIGNATURE", fg_color=ACCENT_ORANGE))
            if self.on_signature_generated:
                self.on_signature_generated(msg, signature)
        except Exception as e:
            self._sign_btn.configure(text="  ✍  GENERATE SIGNATURE", fg_color=ACCENT_ORANGE, state="normal")
            messagebox.showerror("Signing Error", str(e))
