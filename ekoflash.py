import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog, ttk

# ==================== THEME COLORS - MODERN & PROFESSIONAL ====================
BG_MAIN = "#0A0A0A"           
BG_DARK = "#111111"           
BG_LIGHT = "#1A1A1A"          
ACCENT_BLUE = "#00BFFF"       
TEXT_BLUE = "#00CCFF"
FG_WHITE = "#EEEEEE"
BTN_ORANGE = "#FF9500"        
BTN_BLUE = "#00BFFF"          
BTN_RED = "#FF2D55"           
BTN_GREEN = "#00CC66"
BTN_DARK = "#222222"
SUCCESS_GREEN = "#00FF9D"
ODIN_BOX_BG = "#141414"

class EkoFlashGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EKO FLASH PRO v2.1")
        self.root.geometry("1080x850")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(False, False)
        
        # Variables
        self.part_vars = {}
        self.auto_reboot_var = tk.BooleanVar(value=True)
        self.odin_vars = {}
        self.odin_opts_vars = {}
        self.pit_var = tk.StringVar()
        self.current_mode = "FASTBOOT"

        # Modern Style for Tabs
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=BTN_DARK, foreground=FG_WHITE, 
                            font=("Consolas", 10, "bold"), padding=[16, 6])
        self.style.map("TNotebook.Tab", 
                      background=[("selected", ACCENT_BLUE)], 
                      foreground=[("selected", "#000000")])

        self.setup_layout()
        # Start device monitoring thread
        threading.Thread(target=self.monitor_device, daemon=True).start()

    def setup_layout(self):
        # ==================== HEADER ====================
        header = tk.Frame(self.root, bg=BG_MAIN, height=100)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=BG_MAIN)
        title_frame.pack(pady=15)

        tk.Label(title_frame, text="EKO FLASH PRO", bg=BG_MAIN, fg=ACCENT_BLUE, 
                 font=("Consolas", 32, "bold")).pack()
        tk.Label(title_frame, text="DEVELOPER: AHMED YOUNIS", bg=BG_MAIN, fg="#888888", 
                 font=("Consolas", 12, "bold")).pack(pady=(2,0))

        # ==================== MODE SWITCHER ====================
        mode_frame = tk.Frame(self.root, bg=BG_MAIN)
        mode_frame.pack(pady=(5, 15))

        self.btn_fastboot = tk.Button(mode_frame, text="FASTBOOT MODE", bg=BTN_BLUE, fg="#000000",
                                      font=("Consolas", 11, "bold"), width=25, height=2, relief="flat",
                                      command=lambda: self.switch_mode("FASTBOOT"))
        self.btn_fastboot.pack(side="left", padx=10)

        self.btn_odin = tk.Button(mode_frame, text="ODIN MODE", bg=BTN_DARK, fg=FG_WHITE,
                                  font=("Consolas", 11, "bold"), width=25, height=2, relief="flat",
                                  command=lambda: self.switch_mode("ODIN"))
        self.btn_odin.pack(side="left", padx=10)

        # ==================== MAIN CONTAINER ====================
        self.container = tk.Frame(self.root, bg=BG_MAIN)
        self.container.pack(fill="both", expand=True, padx=25, pady=10)

        self.fastboot_frame = tk.Frame(self.container, bg=BG_MAIN)
        self.odin_frame = tk.Frame(self.container, bg=BG_MAIN)

        self.build_fastboot_ui()
        self.build_odin_ui()

        self.fastboot_frame.pack(fill="both", expand=True)

    def build_fastboot_ui(self):
        main_frame = tk.Frame(self.fastboot_frame, bg=BG_MAIN)
        main_frame.pack(fill="both", expand=True)

        parts_title = tk.Label(main_frame, text="PARTITION FLASHING (FASTBOOT)", bg=BG_MAIN, fg=ACCENT_BLUE,
                              font=("Consolas", 14, "bold"))
        parts_title.pack(anchor="w", pady=(0, 8))

        # القائمة الكاملة للبارتيشنات
        parts = ["boot", "recovery", "system", "vendor", "product", "vbmeta", "vendor_boot", "userdata"]
        part_frame = tk.Frame(main_frame, bg=BG_DARK, relief="flat", bd=0)
        part_frame.pack(fill="x", pady=8)

        for p in parts:
            row = tk.Frame(part_frame, bg=BG_DARK, height=48)
            row.pack(fill="x", pady=1, padx=2)
            row.pack_propagate(False)

            tk.Label(row, text=f"{p.upper():<12}", bg=BG_DARK, fg=TEXT_BLUE, 
                     font=("Consolas", 10, "bold"), width=14, anchor="w").pack(side="left", padx=15)

            v = tk.StringVar()
            self.part_vars[p] = v

            ent = tk.Entry(row, textvariable=v, bg="#1F1F1F", fg=FG_WHITE, insertbackground=ACCENT_BLUE,
                           font=("Consolas", 9), relief="flat", bd=0, highlightthickness=2,
                           highlightbackground="#333", highlightcolor=ACCENT_BLUE, width=55)
            ent.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))

            self.create_btn(row, "BROWSE", lambda x=p: self.browse(x, "FASTBOOT"), 10, BTN_ORANGE, "#000000").pack(side="left", padx=4)
            self.create_btn(row, "FLASH", lambda x=p: self.flash_fastboot(x), 9, BTN_BLUE, "#000000").pack(side="left", padx=4)

        # Quick Actions
        quick_frame = tk.LabelFrame(main_frame, text=" QUICK ACTIONS ", bg=BG_MAIN, fg=ACCENT_BLUE,
                                   font=("Consolas", 11, "bold"), bd=1, relief="solid")
        quick_frame.pack(fill="x", pady=15)

        qf_inner = tk.Frame(quick_frame, bg=BG_MAIN)
        qf_inner.pack(pady=12, padx=15, fill="x")

        self.create_btn(qf_inner, "FLASH ALL", self.flash_all_fastboot, 18, BTN_ORANGE, "#000000").pack(side="left", padx=6)
        self.create_btn(qf_inner, "ERASE SYSTEM", lambda: self.erase_part("system"), 18, BTN_RED, FG_WHITE).pack(side="left", padx=6)
        self.create_btn(qf_inner, "WIPE DATA", self.wipe_data, 18, BTN_RED, FG_WHITE).pack(side="left", padx=6)
        self.create_btn(qf_inner, "REBOOT SYSTEM", self.reboot_device, 18, BTN_BLUE, "#000000").pack(side="left", padx=6)

        chk = tk.Checkbutton(qf_inner, text=" Auto Reboot After Flash", variable=self.auto_reboot_var,
                            bg=BG_MAIN, fg=TEXT_BLUE, selectcolor=BTN_GREEN, font=("Consolas", 10, "bold"), activebackground=BG_MAIN)
        chk.pack(side="right", padx=20)

        log_title = tk.Label(main_frame, text="OPERATION LOG", bg=BG_MAIN, fg=ACCENT_BLUE,
                            font=("Consolas", 12, "bold"), anchor="w")
        log_title.pack(anchor="w", pady=(10, 5))

        self.log_widget = tk.Text(main_frame, height=10, bg="#0A0A0A", fg=FG_WHITE, font=("Consolas", 9),
                                  relief="flat", bd=0, highlightthickness=2, highlightbackground="#222")
        self.log_widget.pack(fill="both", expand=True, pady=(0, 10), padx=2)

    def build_odin_ui(self):
        main = tk.Frame(self.odin_frame, bg=BG_MAIN)
        main.pack(fill="both", expand=True, padx=10, pady=5)

        # ID:COM Status
        top_com = tk.Frame(main, bg=BG_MAIN)
        top_com.pack(fill="x", pady=(0, 15))

        com_frame = tk.LabelFrame(top_com, text=" ID:COM ", bg=BG_DARK, fg=ACCENT_BLUE,
                                 font=("Consolas", 11, "bold"), bd=2, relief="solid")
        com_frame.pack(side="left", fill="y", padx=(0, 15))

        self.odin_com_label = tk.Label(com_frame, text="WAITING...", bg="#222222", fg="#FFAA00",
                                      font=("Consolas", 14, "bold"), width=20, height=2)
        self.odin_com_label.pack(padx=20, pady=12)

        pass_frame = tk.Frame(top_com, bg=BG_MAIN)
        pass_frame.pack(side="left", fill="y")
        self.pass_label = tk.Label(pass_frame, text="READY", bg=BTN_DARK, fg=FG_WHITE,
                                  font=("Consolas", 20, "bold"), width=12, height=2, relief="flat")
        self.pass_label.pack()

        # Split: Left (Log & Options) / Right (Files Selection)
        split = tk.Frame(main, bg=BG_MAIN)
        split.pack(fill="both", expand=True)

        left = tk.Frame(split, bg=BG_MAIN, width=400)
        left.pack(side="left", fill="y", padx=(0, 15))
        left.pack_propagate(False)

        notebook = ttk.Notebook(left)
        notebook.pack(fill="both", expand=True)

        # Tab 1: Log
        log_tab = tk.Frame(notebook, bg=ODIN_BOX_BG)
        notebook.add(log_tab, text="  LOG  ")
        self.odin_log = tk.Text(log_tab, bg=ODIN_BOX_BG, fg=FG_WHITE, font=("Consolas", 9), relief="flat")
        self.odin_log.pack(fill="both", expand=True, padx=8, pady=8)

        # Tab 2: Options
        opt_tab = tk.Frame(notebook, bg=ODIN_BOX_BG)
        notebook.add(opt_tab, text=" OPTIONS ")
        opts = [("Auto Reboot", True), ("Nand Erase", False), ("Re-Partition", False), ("F. Reset Time", True)]
        for name, val in opts:
            var = tk.BooleanVar(value=val)
            self.odin_opts_vars[name] = var
            tk.Checkbutton(opt_tab, text=name, variable=var, bg=ODIN_BOX_BG, fg=FG_WHITE,
                          selectcolor=BTN_GREEN, font=("Consolas", 10), anchor="w", activebackground=ODIN_BOX_BG).pack(anchor="w", padx=20, pady=8)

        # Tab 3: PIT
        pit_tab = tk.Frame(notebook, bg=ODIN_BOX_BG)
        notebook.add(pit_tab, text="  PIT  ")
        tk.Label(pit_tab, text="PIT Partition Table:", bg=ODIN_BOX_BG, fg=ACCENT_BLUE, font=("Consolas", 10)).pack(anchor="w", padx=20, pady=(20,5))
        tk.Entry(pit_tab, textvariable=self.pit_var, bg=BG_LIGHT, fg=FG_WHITE, font=("Consolas", 9),
                relief="flat", highlightthickness=1, highlightbackground="#444").pack(fill="x", padx=20, ipady=8)
        self.create_btn(pit_tab, "SELECT PIT FILE", lambda: self.browse("PIT", "ODIN"), 18, BTN_ORANGE, "#000").pack(pady=15, padx=20)

        # Right Side: Files Selection
        right = tk.Frame(split, bg=BG_MAIN)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="FLASH FILES SELECTION", bg=BG_MAIN, fg=ACCENT_BLUE,
                              font=("Consolas", 14, "bold")).pack(anchor="w", pady=(0, 10))

        files_frame = tk.Frame(right, bg=BG_DARK, relief="flat")
        files_frame.pack(fill="both", expand=True)

        odin_parts = ["BL", "AP", "CP", "CSC", "USERDATA"]
        for p in odin_parts:
            row = tk.Frame(files_frame, bg=BG_DARK, height=55)
            row.pack(fill="x", pady=2, padx=3)
            row.pack_propagate(False)

            c_var = tk.BooleanVar(value=False)
            p_var = tk.StringVar()
            self.odin_vars[p] = {"check": c_var, "path": p_var}

            tk.Checkbutton(row, variable=c_var, bg=BG_DARK, selectcolor=BTN_GREEN, activebackground=BG_DARK).pack(side="left", padx=15)
            self.create_btn(row, p, lambda x=p: self.browse(x, "ODIN"), 8, "#333333", FG_WHITE).pack(side="left", padx=(0,8))
            tk.Entry(row, textvariable=p_var, bg="#1F1F1F", fg=FG_WHITE, font=("Consolas", 9),
                          relief="flat", highlightthickness=1, highlightbackground="#444").pack(side="left", fill="x", expand=True, ipady=10, padx=5)

        control_frame = tk.Frame(right, bg=BG_MAIN)
        control_frame.pack(fill="x", pady=25)
        self.create_btn(control_frame, "START FLASHING", self.start_real_odin_flash, 25, BTN_GREEN, "#000000").pack(side="left", padx=8, fill="x", expand=True)
        self.create_btn(control_frame, "RESET ALL", self.odin_reset, 18, BTN_DARK, FG_WHITE).pack(side="left", padx=8)

    def create_btn(self, parent, txt, cmd, w, bg_color, fg_color):
        return tk.Button(parent, text=txt, command=cmd, width=w, bg=bg_color, fg=fg_color,
                         font=("Consolas", 9, "bold"), relief="flat", cursor="hand2")

    def write_log(self, msg, target="MAIN"):
        ts = time.strftime("%H:%M:%S")
        full_msg = f"[{ts}] {msg}\n"
        if target in ["MAIN", "BOTH"]:
            self.log_widget.insert(tk.END, full_msg)
            self.log_widget.see(tk.END)
        if target in ["ODIN", "BOTH"]:
            self.odin_log.insert(tk.END, full_msg)
            self.odin_log.see(tk.END)

    def switch_mode(self, mode):
        self.current_mode = mode
        if mode == "FASTBOOT":
            self.btn_fastboot.config(bg=BTN_BLUE, fg="#000000")
            self.btn_odin.config(bg=BTN_DARK, fg=FG_WHITE)
            self.odin_frame.pack_forget()
            self.fastboot_frame.pack(fill="both", expand=True)
        else:
            self.btn_fastboot.config(bg=BTN_DARK, fg=FG_WHITE)
            self.btn_odin.config(bg=BTN_BLUE, fg="#000000")
            self.fastboot_frame.pack_forget()
            self.odin_frame.pack(fill="both", expand=True)

    def browse(self, p, mode):
        # تصفية الملفات بناءً على الوضع
        if mode == "ODIN":
            types = [("Samsung Binaries", "*.tar;*.md5;*.pit"), ("All Files", "*.*")]
        else:
            types = [("Flash Images", "*.img;*.bin;*.zip"), ("All Files", "*.*")]
            
        f = filedialog.askopenfilename(filetypes=types)
        if f:
            if mode == "FASTBOOT":
                self.part_vars[p].set(f)
            else:
                if p == "PIT": self.pit_var.set(f)
                else:
                    self.odin_vars[p]["path"].set(f)
                    self.odin_vars[p]["check"].set(True)

    # ==================== CORE ENGINE LOGIC ====================
    
    def monitor_device(self):
        """مراقبة الأجهزة برمجياً وبشكل حي"""
        while True:
            cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            try:
                # Fastboot check
                res_f = subprocess.run(["fastboot", "devices"], capture_output=True, text=True, creationflags=cf)
                # Samsung check (via Heimdall)
                res_s = subprocess.run(["heimdall", "detect"], capture_output=True, text=True, creationflags=cf)
                
                if res_f.stdout.strip():
                    self.odin_com_label.config(text="FASTBOOT CONNECTED", bg=BTN_BLUE, fg="#000")
                elif "Device detected" in res_s.stdout:
                    self.odin_com_label.config(text="SAMSUNG CONNECTED", bg=SUCCESS_GREEN, fg="#000")
                else:
                    self.odin_com_label.config(text="WAITING...", bg="#222", fg="#FFAA00")
            except: pass
            time.sleep(3)

    def flash_fastboot(self, part):
        path = self.part_vars[part].get()
        if not path:
            self.write_log(f"Error: No file selected for {part}")
            return
        threading.Thread(target=self._exec_cmd, args=(["fastboot", "flash", part, path], f"Flashing {part}")).start()

    def start_real_odin_flash(self):
        """بدء عملية الفلاش الحقيقية لأجهزة سامسونج"""
        self.write_log("<OSM> Analysis Started...", "ODIN")
        self.pass_label.config(text="FLASHING", bg=BTN_ORANGE, fg="#000")
        
        # بناء أمر Heimdall الحقيقي
        cmd = ["heimdall", "flash"]
        if self.pit_var.get(): cmd += ["--pit", self.pit_var.get()]
        
        # خريطة أسماء البارتيشنات المتوقعة
        map_names = {"BL": "BOOTLOADER", "AP": "SYSTEM", "CP": "RADIO", "CSC": "HIDDEN"}
        
        has_files = False
        for p, data in self.odin_vars.items():
            if data["check"].get() and data["path"].get():
                has_files = True
                p_name = map_names.get(p, p)
                cmd += [f"--{p_name}", data["path"].get()]

        if not has_files:
            self.write_log("Error: No binary files selected!", "ODIN")
            self.pass_label.config(text="FAIL", bg=BTN_RED, fg="#FFF")
            return

        def run_flash():
            self._exec_cmd(cmd, "Odin Multi-Flash", "ODIN")
            if self.odin_opts_vars["Auto Reboot"].get():
                self.reboot_device()

        threading.Thread(target=run_flash, daemon=True).start()

    def _exec_cmd(self, cmd, title, target="MAIN"):
        self.write_log(f"Process: {title}", target)
        cf = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=cf)
            for line in proc.stdout:
                if line.strip(): self.write_log(f"  > {line.strip()}", target)
            proc.wait()
            
            if proc.returncode == 0:
                self.write_log(f"SUCCESS: {title} done.", target)
                if target == "ODIN": self.pass_label.config(text="PASS!", bg=SUCCESS_GREEN, fg="#000")
            else:
                self.write_log(f"ERROR: {title} failed (Code: {proc.returncode})", target)
                if target == "ODIN": self.pass_label.config(text="FAIL", bg=BTN_RED, fg="#FFF")
        except Exception as e:
            self.write_log(f"CRITICAL ERROR: {str(e)}", target)

    def flash_all_fastboot(self):
        for p, v in self.part_vars.items():
            if v.get(): self.flash_fastboot(p)

    def erase_part(self, p):
        threading.Thread(target=self._exec_cmd, args=(["fastboot", "erase", p], f"Erasing {p}")).start()

    def wipe_data(self):
        threading.Thread(target=self._exec_cmd, args=(["fastboot", "-w"], "Wiping Userdata")).start()

    def reboot_device(self):
        # محاولة ريبوت عبر فاست بوت أولاً ثم أندرويد
        subprocess.run(["fastboot", "reboot"], creationflags=0x08000000 if os.name == 'nt' else 0)
        self.write_log("Reboot command dispatched.")

    def odin_reset(self):
        for p in self.odin_vars:
            self.odin_vars[p]["check"].set(False)
            self.odin_vars[p]["path"].set("")
        self.pit_var.set("")
        self.odin_log.delete('1.0', tk.END)
        self.pass_label.config(text="READY", bg=BTN_DARK, fg=FG_WHITE)

if __name__ == "__main__":
    root = tk.Tk()
    app = EkoFlashGUI(root)
    root.mainloop()
