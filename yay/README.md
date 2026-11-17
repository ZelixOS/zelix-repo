# Yay paket tarifi

Yay, Arch Linux için Go ile yazılmış bir AUR yardımcısıdır. Bu dizin ZelixOS deposunda dağıtılan paketin PKGBUILD dosyasını içerir.

## Derleme

Arch Linux veya ZelixOS üzerinde `base-devel`, Go ve PKGBUILD dosyasında belirtilen bağımlılıklar gereklidir. Normal kullanıcıyla:

```bash
makepkg -s
```

Derleme kaynakları PKGBUILD dosyasındaki upstream adresinden alınır. Sürüm ve kaynak doğrulama değerleri aynı dosyada tutulur.

## Kullanım

Zelix deposunun yapılandırıldığı bir sistemde:

```bash
sudo pacman -Syu yay
yay --help
```

AUR paketlerinin tariflerini kurulumdan önce inceleyin.
