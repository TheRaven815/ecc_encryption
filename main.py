import customtkinter as ctk
from src.ui.app import ModernECCApp

def main():
    # Set the appearance mode and color theme
    ctk.set_appearance_mode("Dark")  # Options: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Options: "blue" (standard), "green", "dark-blue"

    # Create and run the application
    app = ModernECCApp()
    app.mainloop()

if __name__ == "__main__":
    main()
