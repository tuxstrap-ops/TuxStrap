#!/usr/bin/env bash
# ==============================================================================
# TuxStrap Installer & Setup Wizard (Linux)
# Supports both:
# 1. Local execution:   ./install.sh
# 2. Remote one-liner: curl -sSL https://.../install.sh | bash
# ==============================================================================

set -e

APP_NAME="tuxstrap"
DISPLAY_NAME="TuxStrap"
GITHUB_REPO="tuxstrap-ops/TuxStrap"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}${BOLD}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}${BOLD}[✓]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}${BOLD}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}${BOLD}[✗]${NC} $1"
}

# --- Uninstall routine ---
if [ "$1" == "--uninstall" ] || [ "$1" == "-u" ]; then
    echo -e "\n${BOLD}${CYAN}TuxStrap Kaldırılıyor (Uninstalling)...${NC}\n"
    rm -rf "$INSTALL_DIR"
    rm -f "$BIN_DIR/$APP_NAME"
    rm -f "$DESKTOP_DIR/tuxstrap.desktop"
    rm -f "$ICON_DIR/tuxstrap.svg"
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    print_success "TuxStrap sistemden başarıyla kaldırıldı."
    exit 0
fi

clear 2>/dev/null || true
echo -e "${CYAN}${BOLD}"
cat << "EOF"
  _______            _____ _                 
 |__   __|          / ____| |                
    | |_   ___  __ | (___ | |_ _ __ __ _ _ __  
    | | | | \ \/ /  \___ \| __| '__/ _` | '_ \ 
    | | |_| |>  <   ____) | |_| | | (_| | |_) |
    |_|\__,_/_/\_\ |_____/ \__|_|  \__,_| .__/ 
                                        | |    
   Linux Native Roblox Bootstrapper     |_|    
EOF
echo -e "${NC}"

# 1. Dependency Checks
print_step "Sistem gereksinimleri kontrol ediliyor..."
MISSING_PKGS=()

for cmd in python3 flatpak; do
    if ! command -v "$cmd" &> /dev/null; then
        MISSING_PKGS+=("$cmd")
    fi
done

if [ ${#MISSING_PKGS[@]} -ne 0 ]; then
    print_error "Eksik paketler: ${MISSING_PKGS[*]}"
    echo "Lütfen kurun: sudo apt install python3 flatpak"
    exit 1
fi

if ! python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" &> /dev/null; then
    print_warn "Python GTK3 eksik olabilir. Sorun yaşarsanız:"
    print_warn "sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0"
fi

# Sober check
if flatpak list --app | grep -qi "org.vinegarhq.Sober"; then
    print_success "Sober (Roblox Linux) kurulu."
else
    print_warn "Sober kurulu değil. Kurmak için:"
    echo -e "   ${BOLD}flatpak install --user https://sober.vinegarhq.org/sober.flatpakref${NC}\n"
fi

# 2. Dizinleri hazırla
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"

# 3. Dosyaları al (Yerel mi, Remote/curl mu?)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

if [ -f "$SCRIPT_DIR/main.py" ] && [ -d "$SCRIPT_DIR/core" ]; then
    print_step "Yerel dosyalardan kuruluyor..."
    cp -r "$SCRIPT_DIR/core" "$INSTALL_DIR/"
    cp -r "$SCRIPT_DIR/gui" "$INSTALL_DIR/"
    cp -r "$SCRIPT_DIR/bin" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/main.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/tuxstrap.desktop" "$DESKTOP_DIR/"
    cp "$SCRIPT_DIR/gui/assets/logo.svg" "$ICON_DIR/tuxstrap.svg"
else
    print_step "GitHub üzerinden son sürüm indiriliyor..."
    TMP_DIR=$(mktemp -d)
    TAR_URL="https://github.com/$GITHUB_REPO/archive/refs/heads/main.tar.gz"
    
    if curl -sSL -f "$TAR_URL" -o "$TMP_DIR/tuxstrap.tar.gz"; then
        tar -xzf "$TMP_DIR/tuxstrap.tar.gz" -C "$TMP_DIR"
        EXTRACTED_DIR=$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)
        cp -r "$EXTRACTED_DIR/core" "$INSTALL_DIR/"
        cp -r "$EXTRACTED_DIR/gui" "$INSTALL_DIR/"
        cp -r "$EXTRACTED_DIR/bin" "$INSTALL_DIR/"
        cp "$EXTRACTED_DIR/main.py" "$INSTALL_DIR/"
        cp "$EXTRACTED_DIR/tuxstrap.desktop" "$DESKTOP_DIR/"
        cp "$EXTRACTED_DIR/gui/assets/logo.svg" "$ICON_DIR/tuxstrap.svg"
        rm -rf "$TMP_DIR"
    else
        print_error "İndirme başarısız oldu. Lütfen internet bağlantınızı veya repo linkini kontrol edin."
        rm -rf "$TMP_DIR"
        exit 1
    fi
fi

# 4. Binary launcher oluştur
cat << 'EOF' > "$BIN_DIR/tuxstrap"
#!/usr/bin/env bash
INSTALL_DIR="$HOME/.local/share/tuxstrap"
export PYTHONPATH="$INSTALL_DIR:$PYTHONPATH"
exec python3 "$INSTALL_DIR/main.py" "$@"
EOF
chmod +x "$BIN_DIR/tuxstrap"
chmod +x "$INSTALL_DIR/bin/ciadpi" 2>/dev/null || true

# 5. Masaüstü menüsünü güncelle
print_step "Masaüstü kısayolları kaydediliyor..."
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo ""
print_success "TuxStrap başarıyla kuruldu!"
echo -e "${BOLD}Nasıl başlatabilirsiniz?${NC}"
echo -e "  1. Başlat Menüsünden: ${CYAN}TuxStrap${NC} ikonuna tıklayarak"
echo -e "  2. Terminalden:       ${CYAN}tuxstrap${NC}"
echo -e "  3. Kaldırmak için:    ${CYAN}tuxstrap --uninstall${NC} veya ${CYAN}$0 --uninstall${NC}"
echo ""
