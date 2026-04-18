import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, scrolledtext

# --- AKRO-X PREMIUM THEME ---
BG_MAIN = "#050505"       # Amoled Black
BG_SECONDARY = "#0D0D0D"  # Dark Grey
CYAN_ACCENT = "#00D2FF"   # Cyber Blue
YELLOW_FILE = "#FFFF00"   # Yellow for Browsing
RED_DANGER = "#FF0000"    # Red for Wipe/Errors
GREEN_OK = "#00FF00"      # Green for Success
FG_WHITE = "#F0F0F0"      # Off White

class EkoFlashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EKO FLASH PRO - AKRO-X ENGINE")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        
        self.part_vars = {}
        self.setup_layout()
        
        # مراقب حالة الجهاز في الخلفية
        threading.Thread(target=self.monitor_fastboot, daemon=True).start()

    def setup_layout(self):
        # --- HEADER SECTION ---
        header = tk.Frame(self.root, bg=BG_MAIN, height=100)
        header.pack(side="top", fill="x", padx=25, pady=15)
        
        # Title & Developer Info
        title_frame = tk.Frame(header, bg=BG_MAIN)
        title_frame.pack(side="left")
        
        tk.Label(title_frame, text="EKO FLASH PRO", bg=BG_MAIN, fg=CYAN_ACCENT, 
                 font=("Consolas", 26, "bold")).pack(anchor="w")
        
        tk.Label(title_frame, text="DEVELOPER: AHMED YOUNIS (AKRO)", bg=BG_MAIN, fg=FG_WHITE, 
                 font=("Consolas", 12, "bold")).pack(anchor="w", pady=2)
        
        # Status Light (The Dot)
        self.status_canvas = tk.Canvas(header, width=40, height=40, bg=BG_MAIN, highlightthickness=0)
        self.status_canvas.pack(side="right", padx=10)
        self.status_dot = self.status_canvas.create_oval(10, 10, 30, 30, fill=RED_DANGER)

        # --- MAIN BODY ---
        main_container = tk.Frame(self.root, bg=BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=25, pady=5)

        # Left: Controls (Partitions)
        self.left_frame = tk.Frame(main_container, bg=BG_SECONDARY, width=580, padx=20, pady=20)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Right: Logs
        self.right_frame = tk.Frame(main_container, bg=BG_MAIN, width=380)
        self.right_frame.pack(side="right", fill="both", padx=(20, 0))

        self.create_partition_rows()
        self.create_log_area()
        self.create_bottom_actions()

    def create_partition_rows(self):
        partitions = ["system", "boot", "recovery", "product", "vendor", "vbmeta", "userdata", "vendor_boot"]
        
        for part in partitions:
            row = tk.Frame(self.left_frame, bg=BG_SECONDARY)
            row.pack(fill="x", pady=6)
            
            tk.Label(row, text=part.upper(), bg=BG_SECONDARY, fg=CYAN_ACCENT, 
                     width=12, anchor="w", font=("Consolas", 10, "bold")).pack(side="left")
            
            var = tk.StringVar()
            self.part_vars[part] = var
            entry = tk.Entry(row, textvariable=var, bg="#000", fg=FG_WHITE, 
                             insertbackground=FG_WHITE, relief="flat", font=("Consolas", 9))
            entry.pack(side="left", fill="x", expand=True, padx=8, ipady=4)
            
            # أزرار بجانب كل خيار (تصفح وتفليش)
            self.create_btn(row, "...", lambda p=part: self.browse_file(p), 4, YELLOW_FILE).pack(side="left", padx=2)
            self.create_btn(row, "FLASH", lambda p=part: self.flash_single(p), 8, CYAN_ACCENT).pack(side="left", padx=2)

    def create_bottom_actions(self):
        btn_container = tk.Frame(self.left_frame, bg=BG_SECONDARY)
        btn_container.pack(side="bottom", fill="x", pady=(20, 0))
        
        # Wipe Data (Format)
        self.create_btn(btn_container, "WIPE DATA (FORMAT)", self.wipe_data, 22, RED_DANGER).pack(side="left", expand=True, padx=5)
        
        # Reboot System
        self.create_btn(btn_container, "REBOOT SYSTEM", self.reboot_sys, 22, CYAN_ACCENT).pack(side="left", expand=True, padx=5)

    def create_log_area(self):
        tk.Label(self.right_frame, text="LOG", bg=BG_MAIN, fg=CYAN_ACCENT, 
                 font=("Consolas", 11, "bold")).pack(anchor="w")
        
        self.log_area = scrolledtext.ScrolledText(self.right_frame, bg="#000", fg=FG_WHITE, 
                                                  font=("Consolas", 9), borderwidth=1, relief="solid")
        self.log_area.pack(fill="both", expand=True, pady=5)
        self.log(">>> AKRO-X Engine Initialized...")

    def create_btn(self, parent, text, cmd, w, color):
        btn = tk.Button(parent, text=text, command=cmd, width=w, 
                        bg=BG_MAIN, fg=color, activebackground=color, activeforeground=BG_MAIN,
                        font=("Consolas", 9, "bold"), relief="flat", cursor="hand2", 
                        highlightthickness=1, highlightbackground=color)
        
        # تأثير عند تمرير الماوس
        btn.bind("<Enter>", lambda e: btn.config(bg=color, fg=BG_MAIN))
        btn.bind("<Leave>", lambda e: btn.config(bg=BG_MAIN, fg=color))
        return btn

    # --- CORE LOGIC ---
    def monitor_fastboot(self):
        while True:
            try:
                cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                res = subprocess.run(["fastboot", "devices"], capture_output=True, text=True, creationflags=cf)
                if res.stdout.strip():
                    self.status_canvas.itemconfig(self.status_dot, fill=GREEN_OK)
                else:
                    self.status_canvas.itemconfig(self.status_dot, fill=RED_DANGER)
            except:
                self.status_canvas.itemconfig(self.status_dot, fill=RED_DANGER)
            time.sleep(2)

    def log(self, msg):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)

    def browse_file(self, part):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.img"), ("All Files", "*.*")])
        if path:
            self.part_vars[part].set(path)
            self.log(f"[SELECTED] {part.upper()} -> {os.path.basename(path)}")

    def flash_single(self, part):
        img_path = self.part_vars[part].get()
        if not img_path:
            self.log(f"![ERROR] No file selected for {part}")
            return
        
        def run():
            self.log(f"\n[FLASH] Starting {part.upper()}...")
            try:
                cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                # استخدام قائمة لضمان التعامل مع المسارات الطويلة والمسافات
                proc = subprocess.Popen(["fastboot", "flash", part, img_path], 
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=cf)
                for line in proc.stdout:
                    self.root.after(0, self.log, line.strip())
                proc.wait()
                
                if proc.returncode == 0:
                    self.root.after(0, self.log, f"✅ {part.upper()} Flash Success!")
                else:
                    self.root.after(0, self.log, f"❌ {part.upper()} Flash Failed!")
            except Exception as e:
                self.root.after(0, self.log, f"❌ Execution Error: {str(e)}")

        threading.Thread(target=run, daemon=True).start()

    def wipe_data(self):
        def run():
            self.log("\n[ACTION] Wiping Userdata (Formatting)...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            res = subprocess.run(["fastboot", "-w"], capture_output=True, text=True, creationflags=cf)
            self.log(res.stdout if res.stdout else "✅ Wipe operation sent.")
            self.log(">>> Format Complete.")
        threading.Thread(target=run, daemon=True).start()

    def reboot_sys(self):
        def run():
            self.log("\n[ACTION] Rebooting to System...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(["fastboot", "reboot"], creationflags=cf)
            self.log(">>> Reboot command sent.")
        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = EkoFlashGUI(root)
    root.mainloop()
