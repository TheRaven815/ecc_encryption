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
ACCENT_CYAN   = "#22d3ee"
ACCENT_GREEN  = "#34d399"
ACCENT_RED    = "#f87171"
ACCENT_PURPLE = "#a78bfa"
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


class VerifyTab(ctk.CTkFrame):
    def __init__(self, master, engine, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.configure(fg_color="transparent")
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Left: inputs (message + signature) ───────────────────────────────
        left = make_card(self)
        left.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=2)
        left.grid_rowconfigure(3, weight=1)

        ctk.CTkFrame(left, fg_color=ACCENT_BLUE, height=3, corner_radius=0).grid(
            row=0, column=0, sticky="ew")

        ctk.CTkLabel(left, text="📄  ORIGINAL MESSAGE",
                     font=ctk.CTkFont(family=FONT_UI, size=12, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=18, pady=(14, 6))

        self._msg_text = ctk.CTkTextbox(
            left, fg_color=BG_DEEP, border_color=BORDER, border_width=1,
            font=(FONT_UI, 12), text_color=TEXT_PRIMARY, corner_radius=10, height=100)
        self._msg_text.grid(row=2, column=0, padx=18, pady=(0, 8), sticky="nsew")

        ctk.CTkFrame(left, fg_color=BORDER, height=1).grid(row=3, column=0, sticky="ew", padx=18, pady=4)

        ctk.CTkLabel(left, text="🔏  SIGNATURE",
                     font=ctk.CTkFont(family=FONT_UI, size=12, weight="bold"),
                     text_color=ACCENT_PURPLE).grid(row=4, column=0, sticky="w", padx=18, pady=(6, 6))

        self._sig_text = ctk.CTkTextbox(
            left, fg_color=BG_DEEP, border_color=BORDER, border_width=1,
            font=(FONT_MONO, 11), text_color="#94a3b8", corner_radius=10)
        self._sig_text.grid(row=5, column=0, padx=18, pady=(0, 18), sticky="nsew")
        left.grid_rowconfigure(5, weight=2)

        # ── Right: action + result ────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, padx=(0, 0), pady=0, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        # Verify button
        self._verify_btn = ctk.CTkButton(
            right,
            text="  🛡  RUN VERIFICATION",
            command=self._verify_signature,
            font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
            fg_color=ACCENT_PURPLE,
            hover_color="#8b6fe8",
            corner_radius=12,
            height=52)
        self._verify_btn.grid(row=0, column=0, pady=(0, 12), sticky="ew")

        # Result panel card
        result_card = make_card(right)
        result_card.grid(row=1, column=0, sticky="nsew")
        result_card.grid_columnconfigure(0, weight=1)
        result_card.grid_rowconfigure(2, weight=1)

        ctk.CTkFrame(result_card, fg_color=ACCENT_PURPLE, height=3, corner_radius=0).grid(
            row=0, column=0, sticky="ew")

        ctk.CTkLabel(result_card, text="📋  VERIFICATION LOG",
                     font=ctk.CTkFont(family=FONT_UI, size=12, weight="bold"),
                     text_color=TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=18, pady=(12, 6))

        # Big visual result indicator
        self._result_indicator = ctk.CTkLabel(
            result_card,
            text="—",
            font=ctk.CTkFont(family=FONT_UI, size=40, weight="bold"),
            text_color=TEXT_MUTED)
        self._result_indicator.grid(row=2, column=0, pady=(10, 5))

        self._result_label = ctk.CTkLabel(
            result_card,
            text="Awaiting verification…",
            font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
            text_color=TEXT_MUTED)
        self._result_label.grid(row=3, column=0, pady=(0, 10))

        # Log textbox
        ctk.CTkFrame(result_card, fg_color=BORDER, height=1).grid(
            row=4, column=0, sticky="ew", padx=18, pady=(0, 8))

        self._log_text = ctk.CTkTextbox(
            result_card, fg_color=BG_DEEP,
            border_color=BORDER, border_width=1,
            font=(FONT_MONO, 10), text_color=TEXT_MUTED,
            corner_radius=10, height=120)
        self._log_text.grid(row=5, column=0, padx=18, pady=(0, 18), sticky="nsew")
        result_card.grid_rowconfigure(5, weight=1)
        self._log_text.insert("0.0", "[ ECC Verification Engine ready ]\n> Awaiting input…")

    # ── API ───────────────────────────────────────────────────────────────────

    def set_data(self, message: str, signature: str):
        self._msg_text.delete("0.0", "end")
        self._msg_text.insert("0.0", message)
        self._sig_text.delete("0.0", "end")
        self._sig_text.insert("0.0", signature)

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _verify_signature(self):
        msg = self._msg_text.get("0.0", "end").strip()
        sig = self._sig_text.get("0.0", "end").strip()
        if not msg or not sig:
            self._result_indicator.configure(text="⚠", text_color="#fb923c")
            self._result_label.configure(text="Missing message or signature", text_color="#fb923c")
            return

        try:
            self._verify_btn.configure(text="  ⏳  Verifying…", state="disabled")
            self.update_idletasks()
            is_valid = self.engine.verify_signature(msg, sig)
            ts = datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

            if is_valid:
                icon, lbl_text, color = "✅", "SIGNATURE VALID", ACCENT_GREEN
            else:
                icon, lbl_text, color = "❌", "INVALID SIGNATURE", ACCENT_RED

            self._result_indicator.configure(text=icon, text_color=color)
            self._result_label.configure(text=lbl_text, text_color=color)

            log_entry = (
                f"─── Verification @ {ts} ───\n"
                f"Status  : {lbl_text}\n"
                f"Message : {msg[:60]}{'…' if len(msg) > 60 else ''}\n"
                f"Sig     : {sig[:40]}…\n"
            )
            self._log_text.delete("0.0", "end")
            self._log_text.insert("0.0", log_entry)

            self._verify_btn.configure(
                text=f"  {'✅' if is_valid else '❌'}  {'VALID' if is_valid else 'INVALID'}",
                fg_color=color,
                state="normal")
            self.after(2500, lambda: self._verify_btn.configure(
                text="  🛡  RUN VERIFICATION", fg_color=ACCENT_PURPLE))

        except Exception as e:
            self._result_indicator.configure(text="⚠", text_color=ACCENT_RED)
            self._result_label.configure(text="Verification error", text_color=ACCENT_RED)
            self._verify_btn.configure(text="  🛡  RUN VERIFICATION",
                                         fg_color=ACCENT_PURPLE, state="normal")
            messagebox.showerror("Verification Error", str(e))
