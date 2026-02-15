bash
#!/bin/bash
# VIRA AdBlocker Installation Script

echo "=============================="
echo "   VIRA AdBlocker Installer   "
echo "=============================="

# تحديد نظام التشغيل
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [[ -n "$PREFIX" && "$PREFIX" == *"com.termux"* ]]; then
        # Termux
        echo "Detected Termux (Android)"
        pkg update -y
        pkg install -y python clang git sing-box termux-api
    else
        # Linux
        echo "Detected Linux"
        # التحقق من وجود sudo
        if command -v sudo &> /dev/null; then
            sudo apt update
            sudo apt install -y python3 python3-pip curl
        else
            echo "Please install sudo or run as root."
            exit 1
        fi
    fi
else
    echo "Unsupported OS."
    exit 1
fi

echo "Making script executable..."
chmod +x AdBlocker.py

echo "=============================="
echo "Installation complete!"
echo "You can now run: python AdBlocker.py"
echo "=============================="
```
