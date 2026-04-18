import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, scrolledtext

# --- AKRO-X ADVANCED THEME ---
BG_MAIN = "#050505"       # Amoled Black
BG_SECONDARY = "#0D0D0D"  # Dark Grey for sections
CYAN_ACCENT = "#00D2FF"   # Cyber Blue
FG_WHITE = "#F0F0F0"      # Off White
RED_FAIL = "#FF0000"      # Status Red
GREEN_PASS = "#00FF00"    # Status Green

class EkoFlashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EKO FLASH PRO")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        
        self.part_vars = {}
        self.setup_layout()
        
        # تشغيل مراقب الحالة
        threading.Thread(target=self.monitor_fastboot, daemon=True).start()

    def setup_layout(self):
        # --- HEADER ---
        header = tk.Frame(self.root, bg=BG_MAIN, height=80)
        header.pack(side="top", fill="x", padx=20, pady=10)
        
        tk.Label(header, text="EKO FLASH PRO", bg=BG_MAIN, fg=CYAN_ACCENT, 
                 font=("Consolas", 22, "bold")).pack(side="left")
        
        # مؤشر الحالة (دائرة فقط)
        self.status_canvas = tk.Canvas(header, width=30, height=30, bg=BG_MAIN, highlightthickness=0)
        self.status_canvas.pack(side="right", padx=10)
        self.status_dot = self.status_canvas.create_oval(5, 5, 25, 25, fill=RED_FAIL)
        
        # اسم المطور تحت العنوان
        dev_info = tk.Label(self.root, text="Developer: Ahmed Younis", bg=BG_MAIN, fg=FG_WHITE, 
                            font=("Consolas", 10))
        dev_info.place(x=25, y=55)

        # --- MAIN CONTAINER ---
        main_container = tk.Frame(self.root, bg=BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Side: Controls
        self.left_frame = tk.Frame(main_container, bg=BG_SECONDARY, width=550, padx=15, pady=15)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Right Side: Logs
        self.right_frame = tk.Frame(main_container, bg=BG_MAIN, width=400)
        self.right_frame.pack(side="right", fill="both", padx=(15, 0))

        self.create_controls()
        self.create_log_area()

    def create_controls(self):
        partitions = ["system", "boot", "recovery", "product", "vendor", "vbmeta", "userdata", "vendor_boot"]
        
        for i, part in enumerate(partitions):
            row_frame = tk.Frame(self.left_frame, bg=BG_SECONDARY)
            row_frame.pack(fill="x", pady=5)
            
            tk.Label(row_frame, text=part.upper(), bg=BG_SECONDARY, fg=CYAN_ACCENT, 
                     width=12, anchor="w", font=("Consolas", 10, "bold")).pack(side="left")
            
            var = tk.StringVar()
            self.part_vars[part] = var
            entry = tk.Entry(row_frame, textvariable=var, bg="#000", fg=FG_WHITE, 
                             insertbackground=FG_WHITE, relief="flat", font=("Consolas", 9))
            entry.pack(side="left", fill="x", expand=True, padx=5, ipady=3)
            
            # أزرار احترافية مع تأثير Hover
            btn_b = self.create_custom_button(row_frame, "...", lambda p=part: self.browse_file(p), 4)
            btn_b.pack(side="left", padx=2)
            
            btn_f = self.create_custom_button(row_frame, "FLASH", lambda p=part: self.flash_single(p), 8)
            btn_f.pack(side="left", padx=2)

        # Special Buttons at bottom of left frame
        btn_box = tk.Frame(self.left_frame, bg=BG_SECONDARY)
        btn_box.pack(side="bottom", fill="x", pady=20)
        
        self.create_custom_button(btn_box, "⚡ FLASH ALL ROM", self.flash_all, 18, True).pack(side="left", expand=True, padx=5)
        self.create_custom_button(btn_box, "🗑️ WIPE DATA", self.wipe_data, 15).pack(side="left", expand=True, padx=5)
        self.create_custom_button(btn_box, "🔄 REBOOT", self.reboot, 15).pack(side="left", expand=True, padx=5)

    def create_log_area(self):
        tk.Label(self.right_frame, text="TERMINAL OUTPUT", bg=BG_MAIN, fg=CYAN_ACCENT, 
                 font=("Consolas", 10, "bold")).pack(anchor="w")
        self.log_area = scrolledtext.ScrolledText(self.right_frame, bg="#000", fg=FG_WHITE, 
                                                  font=("Consolas", 9), borderwidth=0)
        self.log_area.pack(fill="both", expand=True, pady=5)
        self.log(">>> Engine Ready. No device detected.")

    def create_custom_button(self, parent, text, command, width, primary=False):
        btn = tk.Button(parent, text=text, command=command, width=width, 
                        bg=CYAN_ACCENT if primary else BG_MAIN, 
                        fg=BG_MAIN if primary else CYAN_ACCENT,
                        activebackground=FG_WHITE, activeforeground=BG_MAIN,
                        font=("Consolas", 9, "bold"), relief="flat", cursor="hand2")
        
        # Hover Effect
        btn.bind("<Enter>", lambda e: btn.config(bg=FG_WHITE, fg=BG_MAIN))
        btn.bind("<Leave>", lambda e: btn.config(bg=CYAN_ACCENT if primary else BG_MAIN, 
                                                 fg=BG_MAIN if primary else CYAN_ACCENT))
        return btn

    # --- LOGIC ---
    def monitor_fastboot(self):
        while True:
            try:
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                result = subprocess.run(["fastboot", "devices"], capture_output=True, text=True, creationflags=creationflags)
                if result.stdout.strip():
                    self.status_canvas.itemconfig(self.status_dot, fill=GREEN_PASS)
                else:
                    self.status_canvas.itemconfig(self.status_dot, fill=RED_FAIL)
            except:
                self.status_canvas.itemconfig(self.status_dot, fill=RED_FAIL)
            time.sleep(1.5)

    def log(self, msg):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)

    def browse_file(self, part):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.img"), ("All Files", "*.*")])
        if path:
            self.part_vars[part].set(path)
            self.log(f"[FILE] {part} -> {os.path.basename(path)}")

    def flash_single(self, part):
        img = self.part_vars[part].get()
        if not img:
            self.log(f"![ERROR] No file for {part}")
            return
        threading.Thread(target=self._exec_flash, args=(part, img), daemon=True).start()

    def _exec_flash(self, part, path):
        self.log(f"\n[START] Flashing {part}...")
        try:
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            # إضافة علامات تنصيص لضمان عمل المسارات التي تحتوي على مسافات
            proc = subprocess.Popen(["fastboot", "flash", part, path], 
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=cf)
            for line in proc.stdout:
                self.root.after(0, self.log, line.strip())
            proc.wait()
            self.root.after(0, self.log, "✅ Finished." if proc.returncode == 0 else "❌ Failed.")
        except Exception as e:
            self.root.after(0, self.log, f"❌ Error: {str(e)}")

    def flash_all(self):
        def sequence():
            self.log("\n[SYSTEM] Full ROM Flash Sequence Started...")
            for part, var in self.part_vars.items():
                path = var.get()
                if path:
                    self._exec_flash(part, path)
            self.log("[SYSTEM] All operations completed.")
        threading.Thread(target=sequence, daemon=True).start()

    def wipe_data(self):
        threading.Thread(target=lambda: self._simple_cmd(["fastboot", "-w"], "WIPE"), daemon=True).start()

    def reboot(self):
        threading.Thread(target=lambda: self._simple_cmd(["fastboot", "reboot"], "REBOOT"), daemon=True).start()

    def _simple_cmd(self, cmd, label):
        self.log(f"\n[EXEC] {label}...")
        cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        subprocess.run(cmd, creationflags=cf)
        self.log(f"✅ {label} Done.")

if __name__ == "__main__":
    root = tk.Tk()
    app = EkoFlashGUI(root)
    root.mainloop()
