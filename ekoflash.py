import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext

# --- AKRO-X THEME (Windows Edition) ---
BG_COLOR = "#050505"      # Amoled Black
FG_WHITE = "#FFFFFF"      # Pure White
BLUE_ACCENT = "#0055FF"   # Electric Blue for Main Accents
ORANGE_HL = "#FF8800"     # Orange for Selections & Browse Buttons
RED_WARN = "#D32F2F"      # Red for Wipe/Danger

class EkoFlashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EKO FLASH PRO v2.0 - AKRO-X ENGINE")
        self.root.geometry("900x750")
        self.root.configure(bg=BG_COLOR)
        # منع تغيير حجم النافذة للحفاظ على التصميم
        self.root.resizable(False, False)
        
        self.part_vars = {}
        self.create_widgets()
        
    def create_widgets(self):
        # --- HEADER ---
        header_frame = tk.Frame(self.root, bg=BG_COLOR)
        header_frame.pack(pady=15)
        
        tk.Label(header_frame, text="✨ EKO FLASH PRO v2.0 ✨", bg=BG_COLOR, fg=BLUE_ACCENT, font=("Consolas", 18, "bold")).pack()
        tk.Label(header_frame, text="AKRO-X ULTRA-CORE", bg=BG_COLOR, fg=FG_WHITE, font=("Consolas", 12)).pack()
        
        # --- PARTITIONS GRID ---
        part_frame = tk.Frame(self.root, bg=BG_COLOR)
        part_frame.pack(pady=10, padx=20, fill="x")
        
        partitions = ["system", "boot", "recovery", "product", "vendor", "vbmeta", "userdata", "vendor_boot"]
        
        for i, part in enumerate(partitions):
            # اسم البارتيشن
            lbl = tk.Label(part_frame, text=f"[{i+1}] {part.upper()}", bg=BG_COLOR, fg=BLUE_ACCENT, width=15, anchor="w", font=("Consolas", 11, "bold"))
            lbl.grid(row=i, column=0, pady=8, padx=5)
            
            # مسار الملف المختار (نص برتقالي)
            var = tk.StringVar()
            self.part_vars[part] = var
            entry = tk.Entry(part_frame, textvariable=var, width=55, bg="#111111", fg=ORANGE_HL, font=("Consolas", 10), insertbackground=FG_WHITE, relief="solid", bd=1)
            entry.grid(row=i, column=1, pady=8, padx=5)
            
            # زر اختيار الملف (برتقالي)
            btn_browse = tk.Button(part_frame, text="Browse", bg=ORANGE_HL, fg=BG_COLOR, font=("Consolas", 10, "bold"), width=10, relief="flat", cursor="hand2",
                                   command=lambda p=part: self.browse_file(p))
            btn_browse.grid(row=i, column=2, pady=8, padx=5)
            
            # زر التفليش (أزرق)
            btn_flash = tk.Button(part_frame, text="Flash", bg=BLUE_ACCENT, fg=FG_WHITE, font=("Consolas", 10, "bold"), width=10, relief="flat", cursor="hand2",
                                  command=lambda p=part: self.flash_single(p))
            btn_flash.grid(row=i, column=3, pady=8, padx=5)

        # --- SPECIAL OPERATIONS ---
        ops_frame = tk.Frame(self.root, bg=BG_COLOR)
        ops_frame.pack(pady=20)
        
        tk.Button(ops_frame, text="⚡ Flash All Images", bg=ORANGE_HL, fg=BG_COLOR, font=("Consolas", 11, "bold"), width=20, relief="flat", cursor="hand2", command=self.flash_all).grid(row=0, column=0, padx=15)
        tk.Button(ops_frame, text="🗑️ Wipe Data (-w)", bg=RED_WARN, fg=FG_WHITE, font=("Consolas", 11, "bold"), width=20, relief="flat", cursor="hand2", command=self.wipe_data).grid(row=0, column=1, padx=15)
        tk.Button(ops_frame, text="🔄 Reboot System", bg=BLUE_ACCENT, fg=FG_WHITE, font=("Consolas", 11, "bold"), width=20, relief="flat", cursor="hand2", command=self.reboot).grid(row=0, column=2, padx=15)
        
        # --- TERMINAL LOG CONSOLE ---
        log_frame = tk.Frame(self.root, bg=BG_COLOR)
        log_frame.pack(fill="both", expand=True, padx=25, pady=5)
        
        tk.Label(log_frame, text="AKRO_COMMAND_LOGS:", bg=BG_COLOR, fg=BLUE_ACCENT, font=("Consolas", 10, "bold"), anchor="w").pack(fill="x")
        self.log_area = scrolledtext.ScrolledText(log_frame, bg="#0A0A0A", fg=FG_WHITE, font=("Consolas", 10), height=10, relief="solid", bd=1)
        self.log_area.pack(fill="both", expand=True, pady=5)
        self.log(">>> Engine Initialized. Waiting for commands...\n")
        
        # --- FOOTER ---
        footer = tk.Label(self.root, text="👤 Lead Developer: Ahmed Younis (AKRO) | 🌐 Platform: Windows Mode", bg=BG_COLOR, fg=BLUE_ACCENT, font=("Consolas", 9))
        footer.pack(side="bottom", pady=10)

    # --- FUNCTIONS ---
    def log(self, msg):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)

    def browse_file(self, part):
        filepath = filedialog.askopenfilename(title=f"Select {part}.img", filetypes=[("Image Files", "*.img"), ("All Files", "*.*")])
        if filepath:
            self.part_vars[part].set(filepath)
            self.log(f">>> Selected {part}: {filepath}")

    def run_fastboot(self, cmd_list, label):
        def task():
            self.log(f"\n[{label}] Executing: {' '.join(cmd_list)}")
            try:
                # إخفاء نافذة الـ CMD المزعجة في ويندوز
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=creationflags)
                
                for line in process.stdout:
                    self.root.after(0, self.log, line.strip())
                process.wait()
                
                if process.returncode == 0:
                    self.root.after(0, self.log, f"✅ [{label}] Success!")
                else:
                    self.root.after(0, self.log, f"❌ [{label}] Error (Code: {process.returncode})")
            except Exception as e:
                self.root.after(0, self.log, f"❌ Execution Failed: {str(e)}")
                
        # تشغيل الأمر في مسار منفصل عشان الواجهة ماتقفش
        threading.Thread(target=task, daemon=True).start()

    def flash_single(self, part):
        img_path = self.part_vars[part].get()
        if not img_path or not os.path.exists(img_path):
            self.log(f"⚠️ Error: No valid file selected for {part}")
            return
        self.run_fastboot(["fastboot", "flash", part, img_path], f"FLASH {part.upper()}")

    def flash_all(self):
        self.log("\n🚀 Initializing Full Flash Sequence...")
        def sequence():
            for part, var in self.part_vars.items():
                img_path = var.get()
                if img_path and os.path.exists(img_path):
                    self.log(f"\n--- Flashing {part.upper()} ---")
                    creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    process = subprocess.Popen(["fastboot", "flash", part, img_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=creationflags)
                    for line in process.stdout:
                        self.root.after(0, self.log, line.strip())
                    process.wait()
            self.root.after(0, self.log, "\n✨ Full Sequence Completed.")
            
        threading.Thread(target=sequence, daemon=True).start()

    def wipe_data(self):
        self.run_fastboot(["fastboot", "-w"], "WIPE DATA")

    def reboot(self):
        self.run_fastboot(["fastboot", "reboot"], "REBOOT")

if __name__ == "__main__":
    root = tk.Tk()
    app = EkoFlashGUI(root)
    root.mainloop()
