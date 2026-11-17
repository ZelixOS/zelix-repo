# Zelix Hello

ZelixOS için Python ve PyQt6 ile yazılmış karşılama ve sistem yönetimi uygulaması.

## Özellikler

- Sistem bilgileri ve proje bağlantıları.
- Arch, Flatpak ve AUR kaynaklarından uygulama yönetimi.
- Güncelleme, ayna ve bakım araçlarına erişim.
- Sistem servisleri ve masaüstü ayarları.
- Donanım algılama ve sürücü önerileri.
- Türkçe ve İngilizce arayüz.

## Kurulum

Zelix deposunun yapılandırıldığı bir sistemde:

```bash
sudo pacman -Syu zelix-hello
zelix-hello
```

## Kaynaktan çalıştırma

Python, `python-pyqt6`, `qt6-svg` ve `polkit` gereklidir. Depo dizininde:

```bash
python main.py
```

Flatpak, AUR ve ayna işlemleri ilgili ek araçları gerektirir. Yetki isteyen işlemler masaüstü kimlik doğrulama aracını kullanır.

## Kaynak düzeni

`tabs/` uygulama sayfalarını, `ui/` ana pencereyi ve stili, `utils/` yardımcı işlevleri ve çevirileri, `assets/` görselleri içerir.

Paket tarifi [zelix-repo](https://github.com/ZelixOS/zelix-repo/tree/main/zelix-hello) deposundadır.
