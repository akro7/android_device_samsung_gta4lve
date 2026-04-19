import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk

# --- AKRO-X ULTRA CYBER THEME (CLASSIC & COMPACT) ---
BG_MAIN = "#050505"       # Amoled Black
BG_ENTRY = "#111111"      # Dark Grey for entries
TEXT_BLUE = "#0066FF"     # Classic Blue text
FG_WHITE = "#FFFFFF"
BTN_ORANGE = "#FF8C00"    # Browse / Flash All
BTN_BLUE = "#0066FF"      # Flash / Reboot
BTN_RED = "#CC0000"       # Wipe / Erase
BTN_DARK = "#222222"      # Unselected Tab

class EkoFlashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EKO FLASH PRO v2.1 - AKRO-X ENGINE")
        self.root.geometry("950x920") # ارتفاع مثالي لظهور كافة العناصر واللوج
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        self.part_vars = {}
        self.current_mode = "FASTBOOT"
        self.auto_reboot_var = tk.BooleanVar(value=False)
        
        self.setup_layout()
        threading.Thread(target=self.monitor_device, daemon=True).start()

    def setup_layout(self):
        # --- HEADER SECTION ---
        header = tk.Frame(self.root, bg=BG_MAIN)
        header.pack(side="top", fill="x", pady=(15, 5))
        
        tk.Label(header, text="☐ EKO FLASH PRO v2.1 ☐", bg=BG_MAIN, fg=TEXT_BLUE, 
                 font=("Consolas", 18, "bold")).pack()
        tk.Label(header, text="DEVELOPER: AHMED YOUNIS | AKRO-X ULTRA-CORE", bg=BG_MAIN, fg=FG_WHITE, 
                 font=("Consolas", 10)).pack()

        # --- MODE SWITCHER (ODIN vs FASTBOOT) ---
        mode_frame = tk.Frame(self.root, bg=BG_MAIN)
        mode_frame.pack(pady=5)
        
        self.btn_fastboot = tk.Button(mode_frame, text="FASTBOOT MODE", bg=BTN_BLUE, fg=FG_WHITE,
                                      font=("Consolas", 9, "bold"), width=20, relief="flat", command=lambda: self.switch_mode("FASTBOOT"))
        self.btn_fastboot.pack(side="left", padx=10)
        
        self.btn_odin = tk.Button(mode_frame, text="ODIN / HEIMDALL MODE", bg=BTN_DARK, fg=FG_WHITE,
                                  font=("Consolas", 9, "bold"), width=20, relief="flat", command=lambda: self.switch_mode("ODIN"))
        self.btn_odin.pack(side="left", padx=10)

        # --- PARTITIONS SECTION (OPTIMIZED SPACING) ---
        part_frame = tk.Frame(self.root, bg=BG_MAIN)
        part_frame.pack(pady=5)

        parts = ["system", "boot", "recovery", "product", "vendor", "vbmeta", "userdata", "vendor_boot"]
        for i, p in enumerate(parts):
            row = tk.Frame(part_frame, bg=BG_MAIN)
            row.pack(fill="x", pady=2) # مسافة عمودية دقيقة لضمان ظهور vendor_boot
            
            # Label
            tk.Label(row, text=f"[{i+1}] {p.upper()}", bg=BG_MAIN, fg=TEXT_BLUE, 
                     width=16, anchor="w", font=("Consolas", 9, "bold")).pack(side="left")
            
            # Text Entry
            v = tk.StringVar()
            self.part_vars[p] = v
            # تم تصحيح مكان الـ width ليكون داخل Entry وليس داخل pack
            ent = tk.Entry(row, textvariable=v, bg=BG_ENTRY, fg=FG_WHITE, borderwidth=0,
                           font=("Consolas", 9), highlightthickness=1, highlightbackground="#333", width=50)
            ent.pack(side="left", ipady=3, padx=10)
            
            # Buttons
            self.create_btn(row, "Browse", lambda x=p: self.browse(x), 9, BTN_ORANGE, "#000").pack(side="left", padx=3)
            self.create_btn(row, "Flash", lambda x=p: self.flash(x), 9, BTN_BLUE, FG_WHITE).pack(side="left", padx=3)

        # --- EXTRA DEVELOPER OPERATIONS ---
        extra_frame = tk.Frame(self.root, bg=BG_MAIN)
        extra_frame.pack(pady=10)
        
        self.create_btn(extra_frame, "Flash via Sideload", self.adb_sideload, 20, "#444", FG_WHITE).pack(side="left", padx=5)
        self.create_btn(extra_frame, "Erase System", lambda: self.erase_part("system"), 15, BTN_RED, FG_WHITE).pack(side="left", padx=5)
        self.create_btn(extra_frame, "Erase System_ext", lambda: self.erase_part("system_ext"), 18, BTN_RED, FG_WHITE).pack(side="left", padx=5)
        
        # Auto Reboot Checkbox
        chk_style = {"bg": BG_MAIN, "fg": TEXT_BLUE, "selectcolor": "#000", "activebackground": BG_MAIN, "activeforeground": TEXT_BLUE}
        tk.Checkbutton(extra_frame, text="Auto Reboot After Flash", variable=self.auto_reboot_var, font=("Consolas", 9, "bold"), **chk_style).pack(side="left", padx=15)

        # --- BOTTOM ACTIONS ---
        action_frame = tk.Frame(self.root, bg=BG_MAIN)
        action_frame.pack(pady=10)
        
        self.create_btn(action_frame, "☐ Flash All Images", self.flash_all, 22, BTN_ORANGE, "#000").pack(side="left", padx=10)
        self.create_btn(action_frame, "☐☐☐ Wipe Data (-w)", self.wipe, 22, BTN_RED, FG_WHITE).pack(side="left", padx=10)
        self.create_btn(action_frame, "☐☐ Reboot System", self.reboot, 22, BTN_BLUE, FG_WHITE).pack(side="left", padx=10)

        # --- LOG TERMINAL ---
        log_label = tk.Label(self.root, text="LOG:", bg=BG_MAIN, fg=TEXT_BLUE, font=("Consolas", 9, "bold"))
        log_label.pack(fill="x", padx=35, anchor="w")
        
        self.log_widget = tk.Text(self.root, height=7, bg="#080808", fg=FG_WHITE, font=("Consolas", 8),
                                  borderwidth=0, highlightthickness=1, highlightbackground="#333")
        self.log_widget.pack(fill="both", expand=True, padx=35, pady=(0, 15))
        self.write_log(">>> Engine Initialized. Waiting for commands...")

    def create_btn(self, parent, txt, cmd, w, bg_color, fg_color):
        return tk.Button(parent, text=txt, command=cmd, width=w, bg=bg_color, fg=fg_color,
                         font=("Consolas", 8, "bold"), relief="flat", cursor="hand2")

    def switch_mode(self, mode):
        self.current_mode = mode
        if mode == "FASTBOOT":
            self.btn_fastboot.config(bg=BTN_BLUE)
            self.btn_odin.config(bg=BTN_DARK)
            self.write_log("[ENGINE] Switched to FASTBOOT Mode.")
        else:
            self.btn_fastboot.config(bg=BTN_DARK)
            self.btn_odin.config(bg=BTN_BLUE)
            self.write_log("[ENGINE] Switched to ODIN/HEIMDALL Mode.")

    def monitor_device(self):
        last_status = None
        while True:
            try:
                cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                res = subprocess.run(["fastboot", "devices"], capture_output=True, text=True, creationflags=cf)
                if res.stdout.strip() and last_status != "connected":
                    self.write_log("[STATUS] Fastboot Device Detected.")
                    last_status = "connected"
                elif not res.stdout.strip() and last_status == "connected":
                    self.write_log("[STATUS] Device Disconnected.")
                    last_status = "disconnected"
            except:
                pass
            time.sleep(2.0)

    def write_log(self, msg):
        self.log_widget.insert(tk.END, f"{msg}\n")
        self.log_widget.see(tk.END)

    def browse(self, p):
        f = filedialog.askopenfilename(filetypes=[("Image Files", "*.img;*.tar;*.md5;*.lz4;*.bin"), ("All Files", "*.*")])
        if f:
            self.part_vars[p].set(f)
            self.write_log(f"[FILE] Loaded {p}: {os.path.basename(f)}")

    def flash(self, p):
        path = self.part_vars[p].get()
        if not path:
            self.write_log(f"[ERROR] No file selected for {p}")
            return
        
        def task():
            self.write_log(f"[PROCESS] Flashing {p} via {self.current_mode}...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            
            if self.current_mode == "FASTBOOT":
                cmd = ["fastboot", "flash", p, path]
            else:
                cmd = ["heimdall", "flash", f"--{p.upper()}", path]

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=cf)
            for line in proc.stdout:
                if line.strip(): self.root.after(0, self.write_log, f"  > {line.strip()}")
            proc.wait()
            
            if proc.returncode == 0:
                self.write_log(f"[SUCCESS] {p} flash complete.")
                if self.auto_reboot_var.get():
                    self.write_log("[SYSTEM] Auto Reboot Triggered...")
                    self.reboot()
            else:
                self.write_log(f"[FAILED] Error while flashing {p}.")

        threading.Thread(target=task, daemon=True).start()

    def adb_sideload(self):
        f = filedialog.askopenfilename(filetypes=[("ZIP Files", "*.zip")])
        if not f: return
        def task():
            self.write_log(f"[PROCESS] Sideloading via ADB: {os.path.basename(f)}...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            proc = subprocess.Popen(["adb", "sideload", f], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=cf)
            for line in proc.stdout:
                if line.strip(): self.root.after(0, self.write_log, f"  > {line.strip()}")
            proc.wait()
            if proc.returncode == 0:
                self.write_log("[SUCCESS] Sideload Complete.")
                if self.auto_reboot_var.get():
                    self.reboot()
            else:
                self.write_log("[FAILED] Sideload Error.")
        threading.Thread(target=task, daemon=True).start()

    def erase_part(self, part):
        def task():
            self.write_log(f"[PROCESS] Erasing {part}...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            proc = subprocess.run(["fastboot", "erase", part], capture_output=True, text=True, creationflags=cf)
            if proc.returncode == 0:
                self.write_log(f"[SUCCESS] Partition {part} erased successfully.")
            else:
                self.write_log(f"[FAILED] Failed to erase {part}.")
        threading.Thread(target=task, daemon=True).start()

    def flash_all(self):
        self.write_log("[INFO] Flash All feature triggered.")
        for p, var in self.part_vars.items():
            if var.get():
                self.flash(p)

    def wipe(self):
        def task():
            self.write_log("[PROCESS] Wiping user data (Format)...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            subprocess.run(["fastboot", "-w"], creationflags=cf)
            self.write_log("[SUCCESS] All data wiped.")
        threading.Thread(target=task, daemon=True).start()

    def reboot(self):
        def task():
            self.write_log("[PROCESS] Sending reboot command...")
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            if self.current_mode == "FASTBOOT":
                subprocess.run(["fastboot", "reboot"], creationflags=cf)
            else:
                 self.write_log("[WARNING] Reboot requested. Please force restart if using ODIN Mode.")
            self.write_log("[SUCCESS] Reboot initiated.")
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = EkoFlashGUI(root)
    root.mainloop()
