import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog

# --- AKRO-X ULTRA CYBER THEME ---
BG_MAIN = "#050505"       # Amoled Black
BG_PANEL = "#0A0A0A"      # Darker Grey
CYAN_ACCENT = "#00D2FF"   # Cyber Blue
MAGENTA_BTN = "#FF00FF"   # Neon Pink
LIME_GREEN = "#32FF00"    # Success Green
YELLOW_BRIGHT = "#FFFF00" # Warning/File
PURPLE_SYSTEM = "#9D00FF" # Reboot Color
RED_DANGER = "#FF0000"    # Wipe Color
GOLD_DEV = "#FFD700"      # Gold for Ahmed Younis
FG_WHITE = "#F0F0F0"

class EkoFlashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EKO FLASH PRO - AKRO-X ENGINE")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        
        self.part_vars = {}
        self.setup_layout()
        
        # مراقب حالة الاتصال
        threading.Thread(target=self.monitor_fastboot, daemon=True).start()

    def setup_layout(self):
        # --- HEADER ---
        header = tk.Frame(self.root, bg=BG_MAIN, height=110)
        header.pack(side="top", fill="x", padx=30, pady=20)
        
        # Title
        title_box = tk.Frame(header, bg=BG_MAIN)
        title_box.pack(side="left")
        
        tk.Label(title_box, text="EKO FLASH PRO", bg=BG_MAIN, fg=CYAN_ACCENT, 
                 font=("Consolas", 28, "bold")).pack(anchor="w")
        
        # Developer Branding (The "Dala'a" part)
        dev_frame = tk.Frame(title_box, bg=GOLD_DEV, padx=2, pady=2)
        dev_frame.pack(anchor="w", pady=5)
        tk.Label(dev_frame, text=" DEVELOPER: AHMED YOUNIS (AKRO) ", bg=BG_MAIN, fg=GOLD_DEV, 
                 font=("Consolas", 11, "bold")).pack()
        
        # Status Light
        self.status_canvas = tk.Canvas(header, width=40, height=40, bg=BG_MAIN, highlightthickness=0)
        self.status_canvas.pack(side="right", padx=10)
        self.status_dot = self.status_canvas.create_oval(10, 10, 30, 30, fill=RED_DANGER)

        # --- BODY ---
        container = tk.Frame(self.root, bg=BG_MAIN)
        container.pack(fill="both", expand=True, padx=30)

        # Left Side (Partition Controls)
        self.left_side = tk.Frame(container, bg=BG_PANEL, width=550, padx=20, pady=20)
        self.left_side.pack(side="left", fill="both", expand=True)

        # Right Side (Pure Log - No scrollbar)
        self.right_side = tk.Frame(container, bg=BG_MAIN, width=380)
        self.right_side.pack(side="right", fill="both", padx=(25, 0))

        self.build_partition_ui()
        self.build_log_ui()
        self.build_footer_ui()

    def build_partition_ui(self):
        parts = ["system", "boot", "recovery", "product", "vendor", "vbmeta", "userdata", "vendor_boot"]
        
        for p in parts:
            row = tk.Frame(self.left_side, bg=BG_PANEL)
            row.pack(fill="x", pady=6)
            
            tk.Label(row, text=p.upper(), bg=BG_PANEL, fg=CYAN_ACCENT, 
                     width=11, anchor="w", font=("Consolas", 10, "bold")).pack(side="left")
            
            v = tk.StringVar()
            self.part_vars[p] = v
            ent = tk.Entry(row, textvariable=v, bg="#000", fg=FG_WHITE, borderwidth=0,
                           insertbackground=FG_WHITE, font=("Consolas", 9), highlightthickness=1, 
                           highlightbackground="#222")
            ent.pack(side="left", fill="x", expand=True, padx=10, ipady=4)
            
            self.btn(row, "...", lambda x=p: self.browse(x), 4, YELLOW_BRIGHT).pack(side="left", padx=2)
            self.btn(row, "FLASH", lambda x=p: self.flash(x), 8, MAGENTA_BTN).pack(side="left", padx=2)

    def build_log_ui(self):
        tk.Label(self.right_side, text="ENGINE LOG", bg=BG_MAIN, fg=CYAN_ACCENT, 
                 font=("Consolas", 11, "bold")).pack(anchor="w")
        
        # استخدام Text عادي بدلاً من ScrolledText لإخفاء الشريط الأبيض تماماً
        self.log_widget = tk.Text(self.right_side, bg="#000", fg=FG_WHITE, font=("Consolas", 9),
                                  borderwidth=0, highlightthickness=1, highlightbackground=CYAN_ACCENT)
        self.log_widget.pack(fill="both", expand=True, pady=5)
        self.write_log(">>> AKRO-X System: Active & Ready.")

    def build_footer_ui(self):
        footer = tk.Frame(self.left_side, bg=BG_PANEL)
        footer.pack(side="bottom", fill="x", pady=(20, 0))
        
        self.btn(footer, "🗑️ WIPE DATA (FORMAT)", self.wipe, 25, RED_DANGER).pack(side="left", expand=True, padx=5)
        self.btn(footer, "🔄 REBOOT SYSTEM", self.reboot, 25, PURPLE_SYSTEM).pack(side="left", expand=True, padx=5)

    def btn(self, parent, txt, cmd, w, clr):
        b = tk.Button(parent, text=txt, command=cmd, width=w, bg=BG_MAIN, fg=clr,
                      activebackground=clr, activeforeground=BG_MAIN, font=("Consolas", 9, "bold"),
                      relief="flat", cursor="hand2", highlightthickness=1, highlightbackground=clr)
        b.bind("<Enter>", lambda e: b.config(bg=clr, fg=BG_MAIN))
        b.bind("<Leave>", lambda e: b.config(bg=BG_MAIN, fg=clr))
        return b

    # --- FUNCTIONALITY ---
    def monitor_fastboot(self):
        while True:
            try:
                cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                res = subprocess.run(["fastboot", "devices"], capture_output=True, text=True, creationflags=cf)
                self.status_canvas.itemconfig(self.status_dot, fill=LIME_GREEN if res.stdout.strip() else RED_DANGER)
            except:
                self.status_canvas.itemconfig(self.status_dot, fill=RED_DANGER)
            time.sleep(1.5)

    def write_log(self, msg):
        self.log_widget.insert(tk.END, msg + "\n")
        self.log_widget.see(tk.END) # النزول التلقائي

    def browse(self, p):
        f = filedialog.askopenfilename(filetypes=[("Image Files", "*.img"), ("All Files", "*.*")])
        if f:
            self.part_vars[p].set(f)
            self.write_log(f"[FILE] {p.upper()} Loaded.")

    def flash(self, p):
        path = self.part_vars[p].get()
        if not path:
            self.write_log("! ERROR: No file selected.")
            return
        
        def task():
            self.write_log(f"\n[EXEC] Flashing {p.upper()}...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            proc = subprocess.Popen(["fastboot", "flash", p, path], 
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=cf)
            for line in proc.stdout:
                self.root.after(0, self.write_log, line.strip())
            proc.wait()
            self.root.after(0, self.write_log, "✅ Process Finished." if proc.returncode == 0 else "❌ Process Failed.")

        threading.Thread(target=task, daemon=True).start()

    def wipe(self):
        def task():
            self.write_log("\n[ACTION] Formatting Device Data...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(["fastboot", "-w"], creationflags=cf)
            self.write_log("✅ Wipe Data Successful.")
        threading.Thread(target=task, daemon=True).start()

    def reboot(self):
        def task():
            self.write_log("\n[ACTION] Rebooting to OS...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(["fastboot", "reboot"], creationflags=cf)
            self.write_log("✅ Reboot Command Sent.")
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = EkoFlashGUI(root)
    root.mainloop()
