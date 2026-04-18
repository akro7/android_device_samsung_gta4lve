import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog

# --- AKRO-X ULTRA CYBER THEME ---
BG_MAIN = "#050505"       # Amoled Black
BG_PANEL = "#0A0A0A"      # Darker Grey
CYAN_ACCENT = "#00D2FF"   # Cyber Blue (Electric Blue)
ORANGE_HIGHLIGHT = "#FF8C00" # Orange for selection/buttons
LIME_GREEN = "#32FF00"    # Success Green
YELLOW_BRIGHT = "#FFFF00" # File Selection
PURPLE_SYSTEM = "#9D00FF" # Reboot Color
RED_DANGER = "#FF0000"    # Wipe/Error Color
GOLD_DEV = "#FFD700"      # Gold Branding
FG_WHITE = "#F0F0F0"

class EkoFlashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EKO FLASH PRO - AKRO-X ENGINE")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        
        # استدعاء الأيقونة
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        self.part_vars = {}
        self.setup_layout()
        
        # مراقب حالة الاتصال (Fastboot Monitor)
        threading.Thread(target=self.monitor_fastboot, daemon=True).start()

    def setup_layout(self):
        # --- HEADER SECTION ---
        header = tk.Frame(self.root, bg=BG_MAIN, height=100)
        header.pack(side="top", fill="x", padx=30, pady=(15, 10))
        
        title_box = tk.Frame(header, bg=BG_MAIN)
        title_box.pack(side="left")
        
        tk.Label(title_box, text="EKO FLASH PRO", bg=BG_MAIN, fg=CYAN_ACCENT, 
                 font=("Consolas", 26, "bold")).pack(anchor="w")
        
        dev_frame = tk.Frame(title_box, bg=GOLD_DEV, padx=2, pady=1)
        dev_frame.pack(anchor="w", pady=2)
        tk.Label(dev_frame, text=" DEVELOPER: AHMED YOUNIS ", bg=BG_MAIN, fg=GOLD_DEV, 
                 font=("Consolas", 9, "bold")).pack()
        
        self.status_canvas = tk.Canvas(header, width=30, height=30, bg=BG_MAIN, highlightthickness=0)
        self.status_canvas.pack(side="right", padx=10)
        self.status_dot = self.status_canvas.create_oval(5, 5, 25, 25, fill=RED_DANGER)

        # --- BODY CONTAINER ---
        container = tk.Frame(self.root, bg=BG_MAIN)
        container.pack(fill="both", expand=True, padx=30, pady=5)

        self.left_side = tk.Frame(container, bg=BG_PANEL, width=550, padx=15, pady=15)
        self.left_side.pack(side="left", fill="both", expand=True)

        self.right_side = tk.Frame(container, bg=BG_MAIN, width=380)
        self.right_side.pack(side="right", fill="both", padx=(20, 0))

        self.build_partition_ui()
        self.build_log_ui()
        self.build_footer_ui()

    def build_partition_ui(self):
        # تم ترتيب العناصر لضمان ظهور VENDOR_BOOT
        parts = ["system", "boot", "recovery", "product", "vendor", "vbmeta", "userdata", "vendor_boot"]
        for p in parts:
            row = tk.Frame(self.left_side, bg=BG_PANEL)
            row.pack(fill="x", pady=4) # تقليل الـ pady لزيادة المساحة
            
            tk.Label(row, text=p.upper(), bg=BG_PANEL, fg=CYAN_ACCENT, 
                     width=12, anchor="w", font=("Consolas", 9, "bold")).pack(side="left")
            
            v = tk.StringVar()
            self.part_vars[p] = v
            ent = tk.Entry(row, textvariable=v, bg="#000", fg=FG_WHITE, borderwidth=0,
                           font=("Consolas", 9), highlightthickness=1, highlightbackground="#222")
            ent.pack(side="left", fill="x", expand=True, padx=8, ipady=3)
            
            self.btn(row, "...", lambda x=p: self.browse(x), 3, YELLOW_BRIGHT).pack(side="left", padx=2)
            self.btn(row, "FLASH", lambda x=p: self.flash(x), 7, ORANGE_HIGHLIGHT).pack(side="left", padx=2)

    def build_log_ui(self):
        tk.Label(self.right_side, text="ENGINE LOG", bg=BG_MAIN, fg=CYAN_ACCENT, 
                 font=("Consolas", 10, "bold")).pack(anchor="w")
        
        self.log_widget = tk.Text(self.right_side, bg="#000", fg=FG_WHITE, font=("Consolas", 9),
                                  borderwidth=0, highlightthickness=1, highlightbackground="#111")
        self.log_widget.pack(fill="both", expand=True, pady=5)
        self.write_log("[SYSTEM] Engine Initialized.")

    def build_footer_ui(self):
        footer = tk.Frame(self.left_side, bg=BG_PANEL)
        footer.pack(side="bottom", fill="x", pady=(10, 0))
        self.btn(footer, "🗑️ WIPE DATA (FORMAT)", self.wipe, 22, RED_DANGER).pack(side="left", expand=True, padx=5)
        self.btn(footer, "🔄 REBOOT SYSTEM", self.reboot, 22, PURPLE_SYSTEM).pack(side="left", expand=True, padx=5)

    def btn(self, parent, txt, cmd, w, clr):
        b = tk.Button(parent, text=txt, command=cmd, width=w, bg=BG_MAIN, fg=clr,
                      activebackground=clr, activeforeground=BG_MAIN, font=("Consolas", 8, "bold"),
                      relief="flat", cursor="hand2", highlightthickness=1, highlightbackground=clr)
        b.bind("<Enter>", lambda e: b.config(bg=clr, fg=BG_MAIN))
        b.bind("<Leave>", lambda e: b.config(bg=BG_MAIN, fg=clr))
        return b

    def monitor_fastboot(self):
        last_serial = None
        while True:
            try:
                cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                res = subprocess.run(["fastboot", "devices"], capture_output=True, text=True, creationflags=cf)
                output = res.stdout.strip()
                
                if output:
                    current_serial = output.split()[0]
                    self.status_canvas.itemconfig(self.status_dot, fill=LIME_GREEN)
                    if current_serial != last_serial:
                        self.write_log(f"[STATUS] Device Connected: {current_serial}")
                        last_serial = current_serial
                else:
                    self.status_canvas.itemconfig(self.status_dot, fill=RED_DANGER)
                    if last_serial:
                        self.write_log("[STATUS] Device Disconnected.")
                        last_serial = None
            except:
                pass
            time.sleep(1.0)

    def write_log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_widget.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_widget.see(tk.END)

    def browse(self, p):
        f = filedialog.askopenfilename(filetypes=[("Image Files", "*.img"), ("All Files", "*.*")])
        if f:
            self.part_vars[p].set(f)
            self.write_log(f"[FILE] Selected {p}: {os.path.basename(f)}")

    def flash(self, p):
        path = self.part_vars[p].get()
        if not path:
            self.write_log(f"[ERROR] No file for {p}")
            return
        def task():
            self.write_log(f"[PROCESS] Flashing {p}...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            proc = subprocess.Popen(["fastboot", "flash", p, path], 
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=cf)
            for line in proc.stdout:
                if line.strip(): self.root.after(0, self.write_log, f"  > {line.strip()}")
            proc.wait()
            if proc.returncode == 0:
                self.write_log(f"[SUCCESS] {p} Flashed.")
            else:
                self.write_log(f"[FAILED] {p} Error.")
        threading.Thread(target=task, daemon=True).start()

    def wipe(self):
        def task():
            self.write_log("[PROCESS] Wiping Data...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(["fastboot", "-w"], creationflags=cf)
            self.write_log("[SUCCESS] Format Complete.")
        threading.Thread(target=task, daemon=True).start()

    def reboot(self):
        def task():
            self.write_log("[PROCESS] Rebooting...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(["fastboot", "reboot"], creationflags=cf)
            self.write_log("[SUCCESS] Done.")
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = EkoFlashGUI(root)
    root.mainloop()
