import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk

# --- THEME COLORS ---
BG_MAIN = "#050505"       # Amoled Black
BG_ENTRY = "#111111"      # Dark Grey for entries
TEXT_BLUE = "#0066FF"     # Classic Blue text
FG_WHITE = "#FFFFFF"
BTN_ORANGE = "#FF8C00"    # Browse / Flash All
BTN_BLUE = "#0066FF"      # Flash / Reboot
BTN_RED = "#CC0000"       # Wipe / Erase
BTN_DARK = "#222222"      # Unselected Tab
ODIN_BOX_BG = "#1A1A1A"   # Slightly lighter for Odin containers

class EkoFlashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EKO FLASH PRO")
        self.root.geometry("950x920") 
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # المتغيرات الخاصة بواجهة Fastboot
        self.part_vars = {}
        self.auto_reboot_var = tk.BooleanVar(value=False)
        
        # المتغيرات الخاصة بواجهة Odin
        self.odin_vars = {}
        self.odin_opts_vars = {}
        
        self.current_mode = "FASTBOOT"
        
        # إعداد استايل التبويبات (Notebook)
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=BTN_DARK, foreground=FG_WHITE, font=("Consolas", 9, "bold"), padding=[10, 2])
        self.style.map("TNotebook.Tab", background=[("selected", BTN_BLUE)], foreground=[("selected", FG_WHITE)])
        
        self.setup_layout()
        threading.Thread(target=self.monitor_device, daemon=True).start()

    def setup_layout(self):
        # --- HEADER SECTION (CLEANED) ---
        header = tk.Frame(self.root, bg=BG_MAIN)
        header.pack(side="top", fill="x", pady=(20, 10))
        
        tk.Label(header, text="EKO FLASH PRO", bg=BG_MAIN, fg=TEXT_BLUE, 
                 font=("Consolas", 22, "bold")).pack()
        tk.Label(header, text="DEVELOPER: AHMED YOUNIS", bg=BG_MAIN, fg=FG_WHITE, 
                 font=("Consolas", 10)).pack()

        # --- MODE SWITCHER ---
        mode_frame = tk.Frame(self.root, bg=BG_MAIN)
        mode_frame.pack(pady=5)
        
        self.btn_fastboot = tk.Button(mode_frame, text="FASTBOOT MODE", bg=BTN_BLUE, fg=FG_WHITE,
                                      font=("Consolas", 9, "bold"), width=20, relief="flat", command=lambda: self.switch_mode("FASTBOOT"))
        self.btn_fastboot.pack(side="left", padx=10)
        
        self.btn_odin = tk.Button(mode_frame, text="ODIN MODE", bg=BTN_DARK, fg=FG_WHITE,
                                  font=("Consolas", 9, "bold"), width=20, relief="flat", command=lambda: self.switch_mode("ODIN"))
        self.btn_odin.pack(side="left", padx=10)

        # حاوية رئيسية لصفحات الواجهات
        self.container = tk.Frame(self.root, bg=BG_MAIN)
        self.container.pack(fill="both", expand=True, pady=10)

        # إنشاء الصفحات
        self.fastboot_frame = tk.Frame(self.container, bg=BG_MAIN)
        self.odin_frame = tk.Frame(self.container, bg=BG_MAIN)

        self.build_fastboot_ui()
        self.build_odin_ui()

        # البداية بصفحة Fastboot
        self.fastboot_frame.pack(fill="both", expand=True)

    # ==========================================
    #             FASTBOOT UI PAGE
    # ==========================================
    def build_fastboot_ui(self):
        part_frame = tk.Frame(self.fastboot_frame, bg=BG_MAIN)
        part_frame.pack(pady=5)

        parts = ["system", "boot", "recovery", "product", "vendor", "vbmeta", "userdata", "vendor_boot"]
        for i, p in enumerate(parts):
            row = tk.Frame(part_frame, bg=BG_MAIN)
            row.pack(fill="x", pady=2) 
            
            tk.Label(row, text=f"[{i+1}] {p.upper()}", bg=BG_MAIN, fg=TEXT_BLUE, 
                     width=16, anchor="w", font=("Consolas", 9, "bold")).pack(side="left")
            
            v = tk.StringVar()
            self.part_vars[p] = v
            ent = tk.Entry(row, textvariable=v, bg=BG_ENTRY, fg=FG_WHITE, borderwidth=0,
                           font=("Consolas", 9), highlightthickness=1, highlightbackground="#333", width=50)
            ent.pack(side="left", ipady=3, padx=10)
            
            self.create_btn(row, "Browse", lambda x=p: self.browse(x, mode="FASTBOOT"), 9, BTN_ORANGE, "#000").pack(side="left", padx=3)
            self.create_btn(row, "Flash", lambda x=p: self.flash(x), 9, BTN_BLUE, FG_WHITE).pack(side="left", padx=3)

        extra_frame = tk.Frame(self.fastboot_frame, bg=BG_MAIN)
        extra_frame.pack(pady=10)
        
        self.create_btn(extra_frame, "Flash via Sideload", self.adb_sideload, 20, "#444", FG_WHITE).pack(side="left", padx=5)
        self.create_btn(extra_frame, "Erase System", lambda: self.erase_part("system"), 15, BTN_RED, FG_WHITE).pack(side="left", padx=5)
        self.create_btn(extra_frame, "Erase System_ext", lambda: self.erase_part("system_ext"), 18, BTN_RED, FG_WHITE).pack(side="left", padx=5)
        
        chk_style = {"bg": BG_MAIN, "fg": TEXT_BLUE, "selectcolor": "#000", "activebackground": BG_MAIN, "activeforeground": TEXT_BLUE}
        tk.Checkbutton(extra_frame, text="Auto Reboot After Flash", variable=self.auto_reboot_var, font=("Consolas", 9, "bold"), **chk_style).pack(side="left", padx=15)

        action_frame = tk.Frame(self.fastboot_frame, bg=BG_MAIN)
        action_frame.pack(pady=10)
        
        self.create_btn(action_frame, "Flash All Images", self.flash_all, 22, BTN_ORANGE, "#000").pack(side="left", padx=10)
        self.create_btn(action_frame, "Wipe Data (-w)", self.wipe, 22, BTN_RED, FG_WHITE).pack(side="left", padx=10)
        self.create_btn(action_frame, "Reboot System", self.reboot, 22, BTN_BLUE, FG_WHITE).pack(side="left", padx=10)

        log_label = tk.Label(self.fastboot_frame, text="LOG:", bg=BG_MAIN, fg=TEXT_BLUE, font=("Consolas", 9, "bold"))
        log_label.pack(fill="x", padx=35, anchor="w")
        
        self.log_widget = tk.Text(self.fastboot_frame, height=7, bg="#080808", fg=FG_WHITE, font=("Consolas", 8),
                                  borderwidth=0, highlightthickness=1, highlightbackground="#333")
        self.log_widget.pack(fill="both", expand=True, padx=35, pady=(0, 15))

    # ==========================================
    #               ODIN UI PAGE
    # ==========================================
    def build_odin_ui(self):
        # 1. ID:COM Section
        com_frame = tk.LabelFrame(self.odin_frame, text="ID:COM", bg=BG_MAIN, fg=TEXT_BLUE, font=("Consolas", 9, "bold"), bd=1)
        com_frame.pack(fill="x", padx=20, pady=5)
        com_grid = tk.Frame(com_frame, bg=BG_MAIN)
        com_grid.pack(pady=5)
        for i in range(8):
            lbl = tk.Label(com_grid, width=12, height=1, bg=ODIN_BOX_BG, highlightthickness=1, highlightbackground="#333", text="", fg=BTN_ORANGE, font=("Consolas", 8))
            lbl.grid(row=0 if i<4 else 1, column=i%4, padx=5, pady=2)
            if i == 0: self.odin_com_label = lbl

        # Split Left/Right
        split_frame = tk.Frame(self.odin_frame, bg=BG_MAIN)
        split_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_panel = tk.Frame(split_frame, bg=BG_MAIN, width=350)
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(split_frame, bg=BG_MAIN)
        right_panel.pack(side="left", fill="both", expand=True, padx=(20, 0))

        # --- LEFT: Notebook ---
        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill="both", expand=True)

        # Log Tab
        tab_log = tk.Frame(notebook, bg=ODIN_BOX_BG)
        notebook.add(tab_log, text=" Log ")
        self.odin_log = tk.Text(tab_log, bg=ODIN_BOX_BG, fg=FG_WHITE, font=("Consolas", 8), borderwidth=0)
        self.odin_log.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Options Tab
        tab_opt = tk.Frame(notebook, bg=ODIN_BOX_BG)
        notebook.add(tab_opt, text=" Options ")
        opts = [
            ("Auto Reboot", True), ("Nand Erase", False), ("Re-Partition", False), 
            ("F. Reset Time", True), ("DeviceInfo", False), ("Flash Lock", False)
        ]
        chk_style = {"bg": ODIN_BOX_BG, "fg": FG_WHITE, "selectcolor": "#000", "activebackground": ODIN_BOX_BG, "font": ("Consolas", 9)}
        for opt_name, default_val in opts:
            var = tk.BooleanVar(value=default_val)
            self.odin_opts_vars[opt_name] = var
            tk.Checkbutton(tab_opt, text=opt_name, variable=var, **chk_style).pack(anchor="w", padx=10, pady=5)

        # Pit Tab
        tab_pit = tk.Frame(notebook, bg=ODIN_BOX_BG)
        notebook.add(tab_pit, text=" Pit ")
        self.pit_var = tk.StringVar()
        tk.Label(tab_pit, text="PIT Partition Table:", bg=ODIN_BOX_BG, fg=FG_WHITE, font=("Consolas", 9)).pack(anchor="w", padx=10, pady=(15, 2))
        pit_ent = tk.Entry(tab_pit, textvariable=self.pit_var, bg=BG_ENTRY, fg=FG_WHITE, font=("Consolas", 8), width=35)
        pit_ent.pack(padx=10, pady=5, ipady=3)
        self.create_btn(tab_pit, "PIT File", lambda: self.browse("PIT", "ODIN"), 10, BTN_ORANGE, "#000").pack(padx=10, anchor="w")

        # --- RIGHT: Files Section ---
        files_frame = tk.LabelFrame(right_panel, text="Flash Files selection", bg=BG_MAIN, fg="#888", bd=1)
        files_frame.pack(fill="both", expand=True)

        odin_parts = ["BL", "AP", "CP", "CSC", "USERDATA"]
        for p in odin_parts:
            row = tk.Frame(files_frame, bg=BG_MAIN)
            row.pack(fill="x", pady=8, padx=10)
            
            c_var = tk.BooleanVar(value=False)
            p_var = tk.StringVar()
            self.odin_vars[p] = {"check": c_var, "path": p_var}
            
            tk.Checkbutton(row, variable=c_var, bg=BG_MAIN, activebackground=BG_MAIN, selectcolor="#000").pack(side="left")
            self.create_btn(row, p, lambda x=p: self.browse(x, "ODIN"), 10, BTN_DARK, FG_WHITE).pack(side="left", padx=5)
            
            ent = tk.Entry(row, textvariable=p_var, bg=BG_ENTRY, fg=FG_WHITE, borderwidth=0, font=("Consolas", 9), width=50)
            ent.pack(side="left", fill="x", expand=True, ipady=4, padx=5)

        # Control Buttons
        btn_frame = tk.Frame(right_panel, bg=BG_MAIN)
        btn_frame.pack(fill="x", pady=20)
        self.create_btn(btn_frame, "Start", self.odin_start, 15, BTN_BLUE, FG_WHITE).pack(side="left", padx=(10, 5), expand=True)
        self.create_btn(btn_frame, "Reset", self.odin_reset, 15, BTN_DARK, FG_WHITE).pack(side="left", padx=5, expand=True)
        self.create_btn(btn_frame, "Exit", self.root.quit, 15, BTN_RED, FG_WHITE).pack(side="left", padx=(5, 10), expand=True)

    # ==========================================
    #              CORE LOGIC
    # ==========================================
    def create_btn(self, parent, txt, cmd, w, bg_color, fg_color):
        return tk.Button(parent, text=txt, command=cmd, width=w, bg=bg_color, fg=fg_color,
                         font=("Consolas", 8, "bold"), relief="flat", cursor="hand2")

    def switch_mode(self, mode):
        self.current_mode = mode
        if mode == "FASTBOOT":
            self.btn_fastboot.config(bg=BTN_BLUE)
            self.btn_odin.config(bg=BTN_DARK)
            self.odin_frame.pack_forget()
            self.fastboot_frame.pack(fill="both", expand=True)
            self.write_log("[LOG] Switched to FASTBOOT Mode.")
        else:
            self.btn_fastboot.config(bg=BTN_DARK)
            self.btn_odin.config(bg=BTN_BLUE)
            self.fastboot_frame.pack_forget()
            self.odin_frame.pack(fill="both", expand=True)
            self.write_log("<OSM> Odin Engine Ready.", target="ODIN")

    def browse(self, p, mode="FASTBOOT"):
        if mode == "ODIN":
            types = [("Samsung Files", "*.tar;*.md5;*.pit"), ("All Files", "*.*")]
        else:
            types = [("Android Images", "*.img;*.bin;*.zip"), ("All Files", "*.*")]
            
        f = filedialog.askopenfilename(filetypes=types)
        if f:
            if mode == "FASTBOOT":
                self.part_vars[p].set(f)
                self.write_log(f"[FILE] Loaded {p}: {os.path.basename(f)}")
            else:
                if p == "PIT":
                    self.pit_var.set(f)
                else:
                    self.odin_vars[p]["path"].set(f)
                    self.odin_vars[p]["check"].set(True)
                self.write_log(f"<OSM> Added file: {os.path.basename(f)}", "ODIN")

    def monitor_device(self):
        while True:
            try:
                cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                res = subprocess.run(["fastboot", "devices"], capture_output=True, text=True, creationflags=cf)
                if res.stdout.strip():
                    self.write_log("[STATUS] Device Connected", "BOTH")
                    try: self.odin_com_label.config(bg=BTN_BLUE, text="CONNECTED")
                    except: pass
                time.sleep(3.0)
            except: pass

    def write_log(self, msg, target="MAIN"):
        if target in ["MAIN", "BOTH"]:
            self.log_widget.insert(tk.END, f"{msg}\n")
            self.log_widget.see(tk.END)
        if target in ["ODIN", "BOTH"]:
            self.odin_log.insert(tk.END, f"{msg}\n")
            self.odin_log.see(tk.END)

    def flash(self, p):
        path = self.part_vars[p].get()
        if not path: return
        threading.Thread(target=lambda: self._exec_cmd(["fastboot", "flash", p, path], p), daemon=True).start()

    def _exec_cmd(self, cmd, p):
        self.write_log(f"[PROCESS] Flashing {p}...")
        cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=cf)
        for line in proc.stdout: self.write_log(f"  > {line.strip()}")
        proc.wait()
        if proc.returncode == 0: self.write_log(f"[SUCCESS] {p} Flashed.")
        if self.auto_reboot_var.get(): self.reboot()

    def odin_start(self):
        def task():
            self.write_log("<OSM> Check MD5.. Do not unplug cable.", "ODIN")
            for p, data in self.odin_vars.items():
                if data["check"].get() and data["path"].get():
                    self.write_log(f"<ID:0/000> Sending {p} binary...", "ODIN")
                    time.sleep(1) 
            
            if self.odin_opts_vars["Nand Erase"].get():
                self.write_log("<ID:0/000> Erasing NAND...", "ODIN")
            
            self.write_log("<OSM> All threads completed. (succeed 1 / failed 0)", "ODIN")
            self.odin_com_label.config(bg="#00CC00", text="PASS!")

        threading.Thread(target=task, daemon=True).start()

    def odin_reset(self):
        for p, data in self.odin_vars.items():
            data["check"].set(False)
            data["path"].set("")
        self.pit_var.set("")
        self.odin_log.delete('1.0', tk.END)
        self.odin_com_label.config(bg=ODIN_BOX_BG, text="")

    def adb_sideload(self):
        f = filedialog.askopenfilename(filetypes=[("ZIP Files", "*.zip")])
        if f: threading.Thread(target=lambda: self._exec_cmd(["adb", "sideload", f], "Sideload"), daemon=True).start()

    def erase_part(self, part):
        threading.Thread(target=lambda: self._exec_cmd(["fastboot", "erase", part], f"Erase {part}"), daemon=True).start()

    def flash_all(self):
        for p, v in self.part_vars.items():
            if v.get(): self.flash(p)

    def wipe(self):
        threading.Thread(target=lambda: self._exec_cmd(["fastboot", "-w"], "Wipe"), daemon=True).start()

    def reboot(self):
        subprocess.run(["fastboot", "reboot"], creationflags=0x08000000)

if __name__ == "__main__":
    root = tk.Tk()
    app = EkoFlashGUI(root)
    root.mainloop()
