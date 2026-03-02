import customtkinter as ctk
from tkinter import filedialog, messagebox
import base64

from cryptography.hazmat.primitives.asymmetric import ec, ed25519, x25519
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature

# Modern UI Settings
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")

class AdvancedECCSuite(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Advanced ECC Cryptography Suite")
        self.geometry("900x700")
        self.minsize(900, 700)

        # Stored Key Objects (for signing/verifying)
        self.private_key_obj = None
        self.public_key_obj = None

        self.create_widgets()

    def create_widgets(self):
        # Header
        self.title_label = ctk.CTkLabel(self, text="Elliptic Curve Cryptography (ECC) Suite", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        # Tabview
        self.tabview = ctk.CTkTabview(self, width=850, height=600)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_keys = self.tabview.add("Key Management")
        self.tab_sign = self.tabview.add("Sign Message")
        self.tab_verify = self.tabview.add("Verify Signature")

        self.setup_key_management_tab()
        self.setup_sign_tab()
        self.setup_verify_tab()

    # ==========================================
    # TAB 1: KEY MANAGEMENT
    # ==========================================
    def setup_key_management_tab(self):
        # Settings Frame
        settings_frame = ctk.CTkFrame(self.tab_keys)
        settings_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(settings_frame, text="Select Curve:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.curves = ["SECP256R1 (P-256)", "SECP384R1 (P-384)", "SECP521R1 (P-521)", "Ed25519 (Signatures)", "X25519 (Key Exchange)"]
        self.curve_var = ctk.StringVar(value=self.curves[0])
        ctk.CTkOptionMenu(settings_frame, values=self.curves, variable=self.curve_var).grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(settings_frame, text="Private Key Password (Optional):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(settings_frame, placeholder_text="Leave blank for no password", show="*", width=200)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkButton(settings_frame, text="Generate New Keys", command=self.generate_keys, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, rowspan=2, padx=20, pady=10, sticky="nsew")

        # Textboxes Frame
        text_frame = ctk.CTkFrame(self.tab_keys)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_columnconfigure(1, weight=1)

        # Private Key UI
        ctk.CTkLabel(text_frame, text="Private Key (KEEP SECRET)", text_color="#ff6b6b", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(10,0))
        self.priv_text = ctk.CTkTextbox(text_frame, height=250)
        self.priv_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        priv_btn_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
        priv_btn_frame.grid(row=2, column=0, pady=(0,10))
        ctk.CTkButton(priv_btn_frame, text="Save to File", command=self.save_private_key, fg_color="#c0392b", hover_color="#e74c3c", width=120).pack(side="left", padx=5)
        ctk.CTkButton(priv_btn_frame, text="Load from File", command=self.load_private_key, fg_color="#d35400", hover_color="#e67e22", width=120).pack(side="left", padx=5)

        # Public Key UI
        ctk.CTkLabel(text_frame, text="Public Key (SHAREABLE)", text_color="#1dd1a1", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=(10,0))
        self.pub_text = ctk.CTkTextbox(text_frame, height=250)
        self.pub_text.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        pub_btn_frame = ctk.CTkFrame(text_frame, fg_color="transparent")
        pub_btn_frame.grid(row=2, column=1, pady=(0,10))
        ctk.CTkButton(pub_btn_frame, text="Save to File", command=self.save_public_key, fg_color="#16a085", hover_color="#1abc9c", width=120).pack(side="left", padx=5)
        ctk.CTkButton(pub_btn_frame, text="Load from File", command=self.load_public_key, fg_color="#27ae60", hover_color="#2ecc71", width=120).pack(side="left", padx=5)

    # ==========================================
    # TAB 2: SIGN MESSAGE
    # ==========================================
    def setup_sign_tab(self):
        self.tab_sign.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.tab_sign, text="Message to Sign:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(20,5), sticky="w")
        self.sign_msg_text = ctk.CTkTextbox(self.tab_sign, height=150)
        self.sign_msg_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        ctk.CTkButton(self.tab_sign, text="Sign Message with Private Key", command=self.sign_message, font=ctk.CTkFont(weight="bold"), height=40).grid(row=2, column=0, padx=10, pady=20)

        ctk.CTkLabel(self.tab_sign, text="Digital Signature (Base64):", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=10, pady=(5,5), sticky="w")
        self.signature_output = ctk.CTkTextbox(self.tab_sign, height=100)
        self.signature_output.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

    # ==========================================
    # TAB 3: VERIFY SIGNATURE
    # ==========================================
    def setup_verify_tab(self):
        self.tab_verify.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.tab_verify, text="Original Message:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=(20,5), sticky="w")
        self.verify_msg_text = ctk.CTkTextbox(self.tab_verify, height=100)
        self.verify_msg_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        ctk.CTkLabel(self.tab_verify, text="Signature (Base64):", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=(10,5), sticky="w")
        self.verify_sig_text = ctk.CTkTextbox(self.tab_verify, height=100)
        self.verify_sig_text.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        ctk.CTkButton(self.tab_verify, text="Verify Signature with Public Key", command=self.verify_signature, font=ctk.CTkFont(weight="bold"), height=40, fg_color="#8e44ad", hover_color="#9b59b6").grid(row=4, column=0, padx=10, pady=20)

    # ==========================================
    # LOGIC: KEY GENERATION & FILE I/O
    # ==========================================
    def generate_keys(self):
        selected_curve = self.curve_var.get()
        password = self.password_entry.get().encode()

        try:
            if "SECP256R1" in selected_curve: self.private_key_obj = ec.generate_private_key(ec.SECP256R1())
            elif "SECP384R1" in selected_curve: self.private_key_obj = ec.generate_private_key(ec.SECP384R1())
            elif "SECP521R1" in selected_curve: self.private_key_obj = ec.generate_private_key(ec.SECP521R1())
            elif "Ed25519" in selected_curve: self.private_key_obj = ed25519.Ed25519PrivateKey.generate()
            elif "X25519" in selected_curve: self.private_key_obj = x25519.X25519PrivateKey.generate()

            self.public_key_obj = self.private_key_obj.public_key()
            enc_alg = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()

            priv_pem = self.private_key_obj.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=enc_alg)
            pub_pem = self.public_key_obj.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

            self.priv_text.delete("0.0", "end")
            self.priv_text.insert("0.0", priv_pem.decode('utf-8'))
            self.pub_text.delete("0.0", "end")
            self.pub_text.insert("0.0", pub_pem.decode('utf-8'))

            messagebox.showinfo("Success", "Keys generated successfully! Ready for signing/verifying.")

        except Exception as e:
            messagebox.showerror("Error", f"Key generation failed:\n{str(e)}")

    def save_private_key(self):
        pem = self.priv_text.get("0.0", "end").strip()
        if not pem: return messagebox.showwarning("Warning", "No private key to save!")
        filepath = filedialog.asksaveasfilename(defaultextension=".pem", initialfile="private_key.pem", filetypes=[("PEM Files", "*.pem")])
        if filepath:
            with open(filepath, "w") as f: f.write(pem)
            messagebox.showinfo("Success", "Private key saved!")

    def save_public_key(self):
        pem = self.pub_text.get("0.0", "end").strip()
        if not pem: return messagebox.showwarning("Warning", "No public key to save!")
        filepath = filedialog.asksaveasfilename(defaultextension=".pem", initialfile="public_key.pem", filetypes=[("PEM Files", "*.pem")])
        if filepath:
            with open(filepath, "w") as f: f.write(pem)
            messagebox.showinfo("Success", "Public key saved!")

    def load_private_key(self):
        filepath = filedialog.askopenfilename(filetypes=[("PEM Files", "*.pem"), ("All Files", "*.*")])
        if not filepath: return
        
        password = self.password_entry.get().encode() or None
        try:
            with open(filepath, "rb") as f: pem_data = f.read()
            self.private_key_obj = serialization.load_pem_private_key(pem_data, password=password)
            self.priv_text.delete("0.0", "end")
            self.priv_text.insert("0.0", pem_data.decode('utf-8'))
            
            # Auto-derive public key if possible
            self.public_key_obj = self.private_key_obj.public_key()
            pub_pem = self.public_key_obj.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
            self.pub_text.delete("0.0", "end")
            self.pub_text.insert("0.0", pub_pem.decode('utf-8'))
            
            messagebox.showinfo("Success", "Private key loaded successfully!")
        except ValueError:
            messagebox.showerror("Error", "Incorrect password or invalid private key format.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load key:\n{str(e)}")

    def load_public_key(self):
        filepath = filedialog.askopenfilename(filetypes=[("PEM Files", "*.pem"), ("All Files", "*.*")])
        if not filepath: return
        try:
            with open(filepath, "rb") as f: pem_data = f.read()
            self.public_key_obj = serialization.load_pem_public_key(pem_data)
            self.pub_text.delete("0.0", "end")
            self.pub_text.insert("0.0", pem_data.decode('utf-8'))
            messagebox.showinfo("Success", "Public key loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load public key:\n{str(e)}")

    # ==========================================
    # LOGIC: SIGNING & VERIFYING
    # ==========================================
    def sign_message(self):
        if not self.private_key_obj:
            return messagebox.showwarning("Warning", "You must generate or load a Private Key first!")
        
        message = self.sign_msg_text.get("0.0", "end").strip().encode('utf-8')
        if not message:
            return messagebox.showwarning("Warning", "Please enter a message to sign.")

        try:
            if isinstance(self.private_key_obj, ec.EllipticCurvePrivateKey):
                signature = self.private_key_obj.sign(message, ec.ECDSA(hashes.SHA256()))
            elif isinstance(self.private_key_obj, ed25519.Ed25519PrivateKey):
                signature = self.private_key_obj.sign(message)
            elif isinstance(self.private_key_obj, x25519.X25519PrivateKey):
                return messagebox.showerror("Error", "X25519 is for Key Exchange, not Digital Signatures. Please use SECP or Ed25519.")
            else:
                return messagebox.showerror("Error", "Unsupported key type for signing.")

            sig_base64 = base64.b64encode(signature).decode('utf-8')
            self.signature_output.delete("0.0", "end")
            self.signature_output.insert("0.0", sig_base64)
            
            # Auto-fill verification tab for convenience
            self.verify_msg_text.delete("0.0", "end")
            self.verify_msg_text.insert("0.0", message.decode('utf-8'))
            self.verify_sig_text.delete("0.0", "end")
            self.verify_sig_text.insert("0.0", sig_base64)
            
            messagebox.showinfo("Success", "Message signed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Signing failed:\n{str(e)}")

    def verify_signature(self):
        if not self.public_key_obj:
            return messagebox.showwarning("Warning", "You must generate or load a Public Key first!")

        message = self.verify_msg_text.get("0.0", "end").strip().encode('utf-8')
        sig_base64 = self.verify_sig_text.get("0.0", "end").strip()

        if not message or not sig_base64:
            return messagebox.showwarning("Warning", "Please provide both the message and the signature.")

        try:
            signature = base64.b64decode(sig_base64)

            if isinstance(self.public_key_obj, ec.EllipticCurvePublicKey):
                self.public_key_obj.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            elif isinstance(self.public_key_obj, ed25519.Ed25519PublicKey):
                self.public_key_obj.verify(signature, message)
            else:
                return messagebox.showerror("Error", "Unsupported public key type for verification.")

            messagebox.showinfo("Verification Result", "✅ SIGNATURE IS VALID!\n\nThe message was indeed signed by the owner of the private key and has not been tampered with.")

        except InvalidSignature:
            messagebox.showerror("Verification Result", "❌ SIGNATURE IS INVALID!\n\nEither the message was altered, or the wrong key was used.")
        except Exception as e:
            messagebox.showerror("Error", f"Verification process failed:\n{str(e)}")

if __name__ == "__main__":
    app = AdvancedECCSuite()
    app.mainloop()