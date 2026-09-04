#!/bin/bash

# Python'dan gelecek olan parametreleri alıyoruz
ROOT_PART=$1
DEPS_PATH=$2

if [ -z "$ROOT_PART" ] || [ -z "$DEPS_PATH" ]; then
    echo "Hata: Hedef disk veya deps klasörü belirtilmedi!"
    exit 1
fi

echo "Hedef Disk: $ROOT_PART dizinine bağlanılıyor..."
mkdir -p /mnt/zelix_target
mount "$ROOT_PART" /mnt/zelix_target

echo "ZelixOS Aurora özel dosyaları (duvar kağıtları, ikonlar vb.) kopyalanıyor..."
# Bu komut zelixdeps hiyerarşisini hedef sisteme birebir aktarır
cp -ar "$DEPS_PATH"/* /mnt/zelix_target/

echo "Masaüstü teması ve arka plan ayarlanıyor (Breeze Dark / Zelix Aurora)..."
for userdir in /mnt/zelix_target/home/*; do
    if [ -d "$userdir" ]; then
        username=$(basename "$userdir")
        mkdir -p "$userdir/.config"
        cp -rn /mnt/zelix_target/etc/skel/.config/* "$userdir/.config/" 2>/dev/null || true
        arch-chroot /mnt/zelix_target chown -R "$username:$username" "/home/$username" 2>/dev/null || true
    fi
done
mkdir -p /mnt/zelix_target/root/.config
cp -rn /mnt/zelix_target/etc/skel/.config/* /mnt/zelix_target/root/.config/ 2>/dev/null || true

# =================================================================
# ZELIX REPO YAPILANDIRMASI
# =================================================================
echo "ZelixOS deposu pacman.conf'a ekleniyor..."
if ! grep -q "\[zelixrepo\]" /mnt/zelix_target/etc/pacman.conf; then
    cat <<EOF >> /mnt/zelix_target/etc/pacman.conf

[zelixrepo]
SigLevel = Optional TrustAll
Server = https://raw.githubusercontent.com/ZelixOS/zelix-repo/main/x86_64
EOF
fi

echo "ZelixOS uygulamaları (zelix-hello, zelix-updater) pacman ile kuruluyor..."
if command -v arch-chroot &> /dev/null; then
    arch-chroot /mnt/zelix_target pacman -Sy --noconfirm || true
    arch-chroot /mnt/zelix_target pacman -S zelix-hello zelix-updater --noconfirm || true
fi

# =================================================================
# ZELIX OS KİMLİK (IDENTITY) ENJEKSİYONU
# =================================================================
echo "İşletim sistemi kimliği (os-release) oluşturuluyor..."

# 1. /etc/os-release dosyasını tamamen ZelixOS olarak eziyoruz
cat <<EOF > /mnt/zelix_target/etc/os-release
NAME="ZelixOS"
PRETTY_NAME="ZelixOS Aurora"
ID=zelixos
ID_LIKE=arch
BUILD_ID=rolling
ANSI_COLOR="0;34"
HOME_URL="https://zelixos.com"
DOCUMENTATION_URL="https://docs.zelixos.com"
SUPPORT_URL="https://zelixos.com/support"
BUG_REPORT_URL="https://zelixos.com/br.html"
LOGO=/usr/share/zelix/zelix-icon.png
EOF

# 2. /etc/issue (TTY terminali açıldığında üstte yazan Hoş Geldiniz yazısı)
echo -e "\e[1;35mZelixOS Linux\e[0m \r (\l)\n" > /mnt/zelix_target/etc/issue

# 3. LSB Release uyumluluğu
cat <<EOF > /mnt/zelix_target/etc/lsb-release
LSB_VERSION=1.4
DISTRIB_ID=ZelixOS 
DISTRIB_RELEASE=rolling
DISTRIB_DESCRIPTION="ZelixOS Aurora"
EOF

# =================================================================
# ZELIX OS GRUB THEME (activation only — files already copied above)
# =================================================================
echo "GRUB teması etkinleştiriliyor..."

GRUB_THEME_PATH="/boot/grub/themes/zelix-aurora/theme.txt"

if [ -f "/mnt/zelix_target${GRUB_THEME_PATH}" ]; then
    # Set GRUB_THEME in /etc/default/grub (add or replace the line)
    if grep -q "^GRUB_THEME=" /mnt/zelix_target/etc/default/grub 2>/dev/null; then
        sed -i "s|^GRUB_THEME=.*|GRUB_THEME=\"${GRUB_THEME_PATH}\"|" /mnt/zelix_target/etc/default/grub
    else
        echo "GRUB_THEME=\"${GRUB_THEME_PATH}\"" >> /mnt/zelix_target/etc/default/grub
    fi

    # gfxterm is required for themes to render at all
    if ! grep -q "^GRUB_GFXMODE=" /mnt/zelix_target/etc/default/grub 2>/dev/null; then
        echo "GRUB_GFXMODE=1920x1080,auto" >> /mnt/zelix_target/etc/default/grub
    fi
    if grep -q "^GRUB_TERMINAL_OUTPUT=" /mnt/zelix_target/etc/default/grub 2>/dev/null; then
        sed -i "s|^GRUB_TERMINAL_OUTPUT=.*|GRUB_TERMINAL_OUTPUT=gfxterm|" /mnt/zelix_target/etc/default/grub
    else
        echo "GRUB_TERMINAL_OUTPUT=gfxterm" >> /mnt/zelix_target/etc/default/grub
    fi

    # Bake it into grub.cfg
    if command -v arch-chroot &> /dev/null; then
        arch-chroot /mnt/zelix_target grub-mkconfig -o /boot/grub/grub.cfg || true
    fi
else
    echo "UYARI: Tema dosyası bulunamadı: /mnt/zelix_target${GRUB_THEME_PATH}"
fi

# =================================================================
# ZELIX OS SDDM THEME
# =================================================================
echo "Display manager kontrol ediliyor..."

SDDM_THEME_NAME="zelix-aurora"
SDDM_THEME_PATH="/usr/share/sddm/themes/${SDDM_THEME_NAME}"

# Detect currently enabled display manager inside the target
ENABLED_DM=""
for dm in sddm gdm lightdm lxdm; do
    if arch-chroot /mnt/zelix_target systemctl is-enabled "${dm}.service" &>/dev/null; then
        ENABLED_DM="$dm"
        break
    fi
done

if [ -z "$ENABLED_DM" ]; then
    echo "UYARI: Etkin bir display manager bulunamadı. SDDM teması atlanıyor."
elif [ "$ENABLED_DM" != "sddm" ]; then
    echo "UYARI: Sistemde '$ENABLED_DM' etkin, sddm değil. SDDM teması uygulanmayacak."
    echo "       (Zorla sddm'e geçmek isterseniz script'i düzenleyip FORCE_SDDM=1 yapın.)"
else
    echo "SDDM etkin, tema uygulanıyor..."
    if [ -d "/mnt/zelix_target${SDDM_THEME_PATH}" ]; then
        mkdir -p /mnt/zelix_target/etc/sddm.conf.d

        cat <<EOF > /mnt/zelix_target/etc/sddm.conf.d/zelix-theme.conf
[Theme]
Current=${SDDM_THEME_NAME}
EOF
        echo "SDDM teması başarıyla ayarlandı: ${SDDM_THEME_NAME}"
    else
        echo "UYARI: SDDM tema klasörü bulunamadı: /mnt/zelix_target${SDDM_THEME_PATH}"
    fi
fi

# İşlemler tamam, diski ayır
echo "Sistem temizleniyor ve disk ayrılıyor..."
umount /mnt/zelix_target
echo "ZelixOS Aurora yapılandırması başarıyla tamamlandı!"