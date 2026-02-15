#!/usr/bin/env python3
"""
VIRA AD BLOCKER - System-wide ad blocking for Linux and Termux (Android)
All rights reserved to Vira's team.
"""

import os
import sys
import time
import json
import signal
import subprocess
import urllib.request
from pathlib import Path

# ---------- ANIMATED SPLASH (متوافق مع البيئات المختلفة) ----------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_width():
    """يحصل على عرض الطرفية أو يرجع 80 إذا لم يمكن."""
    try:
        if hasattr(os, 'get_terminal_size'):
            return os.get_terminal_size().columns
    except Exception:
        pass
    return 80

def animated_splash(duration=3):
    frames = [
        "╔════════════════════════════╗",
        "║  VIRA AD BLOCKER  █        ║",
        "╚════════════════════════════╝",
        "╔════════════════════════════╗",
        "║  VIRA AD BLOCKER  ██       ║",
        "╚════════════════════════════╝",
        "╔════════════════════════════╗",
        "║  VIRA AD BLOCKER  ███      ║",
        "╚════════════════════════════╝",
        "╔════════════════════════════╗",
        "║  VIRA AD BLOCKER  ████     ║",
        "╚════════════════════════════╝",
        "╔════════════════════════════╗",
        "║  VIRA AD BLOCKER  █████    ║",
        "╚════════════════════════════╝",
        "╔════════════════════════════╗",
        "║  VIRA AD BLOCKER  ██████   ║",
        "╚════════════════════════════╝",
        "╔════════════════════════════╗",
        "║  VIRA AD BLOCKER  ███████  ║",
        "╚════════════════════════════╝",
        "╔════════════════════════════╗",
        "║  VIRA AD BLOCKER  ████████ ║",
        "╚════════════════════════════╝",
        "╔════════════════════════════╗",
        "║  VIRA AD BLOCKER  █████████║",
        "╚════════════════════════════╝",
    ]
    end_time = time.time() + duration
    width = get_terminal_width()
    while time.time() < end_time:
        for frame in frames:
            clear_screen()
            lines = frame.split('\n')
            print("\n" * 3)
            for line in lines:
                print(line.center(width))
            print("\n" * 2)
            time.sleep(0.1)
    clear_screen()

# ---------- CORE AD BLOCKER CLASS ----------
class AdBlocker:
    def __init__(self):
        self.is_linux = sys.platform.startswith('linux')
        self.is_termux = 'com.termux' in os.environ.get('PREFIX', '')
        self.config_dir = Path.home() / '.vira_adblocker'
        self.config_dir.mkdir(exist_ok=True)
        self.pid_file = self.config_dir / 'daemon.pid'
        self.log_file = self.config_dir / 'adblocker.log'
        self.hosts_backup = self.config_dir / 'hosts.backup'
        self.blocklist = self.config_dir / 'blocklist.txt'

    def log(self, msg):
        with open(self.log_file, 'a') as f:
            f.write(f'{time.ctime()}: {msg}\n')

    def is_running(self):
        if self.pid_file.exists():
            with open(self.pid_file) as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                return True
            except ProcessLookupError:
                self.pid_file.unlink(missing_ok=True)
        return False

    def update_blocklists(self):
        """تحميل قوائم الإعلانات من عدة مصادر."""
        sources = [
            'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
            'https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/adservers.txt',
            'https://someonewhocares.org/hosts/zero/hosts'
        ]
        domains = set()
        for url in sources:
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    data = resp.read().decode('utf-8')
                    for line in data.splitlines():
                        line = line.strip()
                        if line and not line.startswith('#'):
                            parts = line.split()
                            if len(parts) >= 2 and parts[0] in ('0.0.0.0', '127.0.0.1'):
                                domains.add(parts[1])
                            elif '.' in line and ' ' not in line:
                                domains.add(line)
            except Exception as e:
                self.log(f'Failed to fetch {url}: {e}')
        with open(self.blocklist, 'w') as f:
            f.write('\n'.join(sorted(domains)))
        self.log(f'Blocklist updated: {len(domains)} entries')
        return len(domains)

    def start(self):
        if self.is_running():
            print("VIRA Ad Blocker is already running.")
            return
        print("Updating ad block lists...")
        count = self.update_blocklists()
        print(f"Loaded {count} ad domains.")
        if self.is_termux:
            self._start_termux()
        elif self.is_linux:
            self._start_linux()
        else:
            print("Unsupported platform.")
            sys.exit(1)

    def _start_linux(self):
        """Linux: استخدام ملف hosts (يحتاج صلاحيات root)."""
        if os.geteuid() != 0:
            print("Root privileges required. Please run with sudo.")
            return
        hosts = Path('/etc/hosts')
        # عمل نسخة احتياطية إذا لم تكن موجودة
        if not self.hosts_backup.exists():
            with open(hosts) as f:
                with open(self.hosts_backup, 'w') as b:
                    b.write(f.read())
        # قراءة القائمة
        with open(self.blocklist) as f:
            entries = [f'0.0.0.0 {line.strip()}' for line in f if line.strip()]
        # إضافة إلى ملف hosts
        with open(hosts, 'a') as f:
            f.write('\n# VIRA ADBLOCK START\n')
            f.write('\n'.join(entries))
            f.write('\n# VIRA ADBLOCK END\n')
        print("Ad blocking enabled via /etc/hosts.")
        self.log('Started on Linux')
        # إنشاء ملف PID وهمي
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))

    def _start_termux(self):
        """Termux: استخدام sing-box VPN (بدون روت)."""
        # التحقق من وجود sing-box
        if subprocess.run(['which', 'sing-box'], capture_output=True).returncode != 0:
            print("sing-box not found. Please install it: pkg install sing-box")
            return
        # إعداد الإعدادات
        config = {
            "log": {"level": "info", "output": str(self.log_file)},
            "dns": {
                "servers": [
                    {"tag": "dns_block", "address": "local"},
                    {"tag": "dns_regular", "address": "8.8.8.8"}
                ],
                "rules": [{"geosite": "adblock", "server": "dns_block"}],
                "final": "dns_regular"
            },
            "inbounds": [{
                "type": "tun",
                "interface_name": "tun0",
                "inet4_address": "172.19.0.1/30",
                "auto_route": True,
                "strict_route": True
            }],
            "outbounds": [{"type": "direct", "tag": "direct"}, {"type": "block", "tag": "block"}],
            "route": {
                "rules": [{"geosite": "adblock", "outbound": "block"}],
                "auto_detect_interface": True,
                "final": "direct"
            },
            "experimental": {
                "cache_file": {"enabled": True, "path": str(self.config_dir / 'cache.db')}
            }
        }
        # تحويل القائمة إلى صيغة geosite
        geosite_file = self.config_dir / 'geosite_adblock.txt'
        with open(self.blocklist) as f:
            domains = [f'domain:{line.strip()}' for line in f if line.strip()]
        with open(geosite_file, 'w') as f:
            f.write('\n'.join(domains))
        config['route']['rule_set'] = [{
            "type": "local",
            "tag": "adblock",
            "format": "binary",
            "path": str(geosite_file)
        }]
        config_path = self.config_dir / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        # طلب صلاحية VPN (Termux:API)
        subprocess.run(['termux-wifi-connectioninfo'], capture_output=True)
        # تشغيل sing-box في الخلفية
        proc = subprocess.Popen(
            ['sing-box', 'run', '-c', str(config_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        with open(self.pid_file, 'w') as f:
            f.write(str(proc.pid))
        print("Ad blocking enabled via sing-box VPN.")
        self.log('Started on Termux')

    def stop(self):
        if not self.is_running():
            print("VIRA Ad Blocker is not running.")
            return
        with open(self.pid_file) as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        self.pid_file.unlink(missing_ok=True)
        # على Linux، استعادة ملف hosts الأصلي
        if self.is_linux and not self.is_termux and self.hosts_backup.exists():
            with open(self.hosts_backup) as b:
                with open('/etc/hosts', 'w') as h:
                    h.write(b.read())
            print("Original hosts restored.")
        print("VIRA Ad Blocker stopped.")
        self.log('Stopped')

    def status(self):
        if self.is_running():
            print("VIRA Ad Blocker is RUNNING.")
        else:
            print("VIRA Ad Blocker is STOPPED.")

# ---------- MAIN MENU ----------
def main():
    # الشاشة الافتتاحية المتحركة
    animated_splash(duration=3)
    blocker = AdBlocker()
    while True:
        print("\n" + "="*60)
        print("                    VIRA AD BLOCKER")
        print("="*60)
        print("  [1] Start blocking")
        print("  [2] Stop blocking")
        print("  [3] Check status")
        print("  [4] Exit")
        print("="*60)
        choice = input("  Enter your choice (1-4): ").strip()
        if choice == '1':
            blocker.start()
        elif choice == '2':
            blocker.stop()
        elif choice == '3':
            blocker.status()
        elif choice == '4':
            print("\n  Thank you for using VIRA Ad Blocker. Goodbye!")
            break
        else:
            print("  Invalid choice. Please enter 1, 2, 3, or 4.")
        input("\n  Press Enter to continue...")
        clear_screen()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting...")
        sys.exit(0)