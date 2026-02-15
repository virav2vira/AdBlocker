# VIRA AdBlocker

**VIRA AdBlocker** is a system-wide ad blocking tool for Linux and Termux (Android). It blocks ads in browsers, apps, and even YouTube without requiring root on Android.

---

## ✨ Features

- Blocks web ads (banners, pop-ups, video ads)
- Blocks in-app ads on Android (via local VPN)
- Works with YouTube (web and app)
- No root required on Android
- Lightweight and automated
- Regularly updated blocklists

---

## 📦 Installation

### On Termux (Android)

1. Install Termux from [F-Droid](https://f-droid.org/en/packages/com.termux/).
2. Install Termux:API from [F-Droid](https://f-droid.org/en/packages/com.termux.api/).
3. Open Termux and run:

```bash
pkg update && pkg upgrade
pkg install git python
git clone https://github.com/virav2vira/AdBlocker.git
cd AdBlocker
chmod +x install.sh
./install.sh


start the tool:
python AdBlocker.py


On linux
git clone https://github.com/virav2vira/AdBlocker.git
cd AdBlocker
chmod +x install.sh
sudo ./install.sh   # requires sudo for hosts file modification
python3 AdBlocker.py
Run the tool
python AdBlocker.py

Then choose from the menu:

· [1] Start blocking – enables ad blocking.
· [2] Stop blocking – disables ad blocking.
· [3] Check status – shows if blocking is active.
· [4] Exit – closes the tool.

⚙️ How It Works

· On Linux: Uses /etc/hosts file to redirect ad domains to 0.0.0.0.
· On Termux: Uses sing-box to create a local VPN that filters ad domains.
