import os
import subprocess
import time
import sys
import platform

# --- AKRO-X PRESET (Neon Aesthetics) ---
class Colors:
    BLUE = '\033[1;34m'
    CYAN = '\033[1;36m'
    WHITE = '\033[1;37m'
    GOLD = '\033[0;33m'
    ORANGE = '\033[38;5;208m'
    RED = '\033[1;31m'
    RESET = '\033[0m'

# --- Multi-Platform Logic ---
OS_NAME = platform.system()
IS_WINDOWS = OS_NAME == "Windows"
FASTBOOT_BIN = "fastboot" if IS_WINDOWS else "termux-fastboot"
CLEAR_CMD = "cls" if IS_WINDOWS else "clear"

LOGO = f"""
{Colors.BLUE}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃{Colors.WHITE}             ✨ {Colors.CYAN}EKO FLASH PRO{Colors.WHITE} ✨              {Colors.BLUE}┃
┃{Colors.GOLD}                 v2.0 STABLE                  {Colors.BLUE}┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{Colors.RESET}"""

FOOTER = f"""
{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 {Colors.GOLD}👤 Lead Developer :{Colors.WHITE} Ahmed Younis (AKRO) 🐼
 {Colors.GOLD}⚡ Engine         :{Colors.CYAN} AKRO-X ULTRA-CORE
 {Colors.GOLD}🌐 Platform       :{Colors.WHITE} {OS_NAME} Mode
{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}"""

# --- Core Engine ---
class FlashEngine:
    def __init__(self):
        # تحديد مسار الملفات تلقائياً بناءً على النظام
        if IS_WINDOWS:
            self.download_path = os.getcwd() # في ويندوز يفضل وضع الملفات بجانب الأداة
        else:
            self.download_path = "/sdcard/Download/"

        # خيارات التفليش الموسعة
        self.partitions = {
            "1": ("system", "system.img"),
            "2": ("boot", "boot.img"),
            "3": ("recovery", "recovery.img"),
            "4": ("product", "product.img"),
            "5": ("vendor", "vendor.img"),
            "6": ("vbmeta", "vbmeta.img"),
            "7": ("userdata", "userdata.img"),
            "8": ("vendor_boot", "vendor_boot.img")
        }

    def run_cmd(self, command, label):
        print(f"{Colors.CYAN}⚡ [EXECUTING]: {Colors.WHITE}{label}...{Colors.RESET}")
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"{Colors.BLUE}✅ Success!{Colors.RESET}\n")
            return True
        except subprocess.CalledProcessError:
            print(f"{Colors.RED}❌ Error during: {label}{Colors.RESET}\n")
            return False

    def flash_partition(self, part_name, img_name):
        img_path = os.path.join(self.download_path, img_name)
        if os.path.exists(img_path):
            cmd = f"{FASTBOOT_BIN} flash {part_name} \"{img_path}\""
            self.run_cmd(cmd, f"Flashing {part_name.upper()}")
        else:
            print(f"{Colors.RED}📂 File Not Found: {img_name}{Colors.RESET}")

    def clear(self):
        os.system(CLEAR_CMD)
        print(LOGO)

    def show_menu(self):
        self.clear()
        print(f"{Colors.GOLD}  --- CORE PARTITIONS ---{Colors.RESET}")
        
        # تنظيم الخيارات في صفين لشكل أرقى
        keys = list(self.partitions.keys())
        for i in range(0, len(keys), 2):
            k1 = keys[i]
            v1 = self.partitions[k1][0].capitalize()
            line = f"  {Colors.ORANGE}[{k1}]{Colors.RESET} {Colors.WHITE}{v1.ljust(15)}"
            if i + 1 < len(keys):
                k2 = keys[i+1]
                v2 = self.partitions[k2][0].capitalize()
                line += f"{Colors.ORANGE}[{k2}]{Colors.RESET} {Colors.WHITE}{v2}"
            print(line)
        
        print(f"\n{Colors.GOLD}  --- SPECIAL OPERATIONS ---{Colors.RESET}")
        print(f"  {Colors.ORANGE}[A]{Colors.RESET} {Colors.CYAN}Flash All Images     {Colors.ORANGE}[W]{Colors.RESET} {Colors.RED}Wipe Data (-w)")
        print(f"  {Colors.ORANGE}[R]{Colors.RESET} {Colors.WHITE}Reboot System        {Colors.ORANGE}[Q]{Colors.RESET} {Colors.RED}Exit")
        print(FOOTER)

    def start(self):
        while True:
            self.show_menu()
            choice = input(f"{Colors.GOLD}➤ AKRO_COMMAND: {Colors.WHITE}").upper()

            if choice in self.partitions:
                part, img = self.partitions[choice]
                self.flash_partition(part, img)
                input(f"\n{Colors.BLUE}Press Enter to continue...{Colors.RESET}")
            
            elif choice == 'A':
                print(f"{Colors.ORANGE}🚀 Initializing Full Flash Sequence...{Colors.RESET}")
                for key in self.partitions:
                    part, img = self.partitions[key]
                    self.flash_partition(part, img)
                print(f"{Colors.BLUE}✨ Sequence Completed.{Colors.RESET}")
                time.sleep(2)

            elif choice == 'W':
                self.run_cmd(f"{FASTBOOT_BIN} -w", "Wiping Userdata")
                time.sleep(2)

            elif choice == 'R':
                self.run_cmd(f"{FASTBOOT_BIN} reboot", "Rebooting Device")
                sys.exit()
            
            elif choice == 'Q':
                print(f"{Colors.RED}👋 AKRO-X Terminated.{Colors.RESET}")
                sys.exit()
            
            else:
                print(f"{Colors.RED}❌ Unknown Command!{Colors.RESET}")
                time.sleep(1)

if __name__ == "__main__":
    # تهيئة المسارات في تيرمكس
    if not IS_WINDOWS and not os.path.exists("/sdcard/Download"):
        os.system("termux-setup-storage")
    
    engine = FlashEngine()
    engine.start()
