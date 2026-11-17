# Zelix Updater

ZelixOS için Python ve PyQt6 ile yazılmış sistem güncelleme uygulaması. Yapılandırılmış pacman depolarındaki güncellemeleri kontrol eder ve işlem çıktısını arayüzde gösterir.

## Kurulum

Zelix deposunun yapılandırıldığı bir sistemde:

```bash
sudo pacman -Syu zelix-updater
zelix-updater
```

## Kullanım

Güncellemeleri kontrol edin, ardından sistem güncellemesini başlatın. Güncelleme işlemi `pkexec` üzerinden yönetici yetkisi ister ve `pacman -Syu --noconfirm` çalıştırır. Pacman sorularında varsayılan yanıtlar kullanılır.

AUR ve Flatpak güncellemeleri bu uygulamanın kapsamı dışındadır.

## Kaynaktan çalıştırma

Python, `python-pyqt6`, `polkit`, `pacman-contrib` ve `fakeroot` gereklidir. Grafik oturumda bir Polkit kimlik doğrulama aracının çalışması gerekir.

```bash
python main.py
```

Güncelleme kontrolü `checkupdates` aracını kullanır. Uygulama simgesi ve masaüstü girdisi kaynak dizininde bulunur.

Paket tarifi [zelix-repo](https://github.com/ZelixOS/zelix-repo/tree/main/zelix-updater) deposundadır.
