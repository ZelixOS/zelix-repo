# Paru paket tarifi

Paru, Arch Linux için Rust ile yazılmış bir AUR yardımcısıdır. Bu dizin ZelixOS deposunda dağıtılan paketin PKGBUILD dosyasını içerir.

## Derleme

Arch Linux veya ZelixOS üzerinde `base-devel`, Cargo ve PKGBUILD dosyasında belirtilen bağımlılıklar gereklidir. Normal kullanıcıyla:

```bash
makepkg -s
```

Derleme kaynakları PKGBUILD dosyasındaki upstream adresinden alınır. Sürüm ve kaynak doğrulama değerleri aynı dosyada tutulur.

## Kullanım

Zelix deposunun yapılandırıldığı bir sistemde:

```bash
sudo pacman -Syu paru
paru --help
```

AUR paketlerinin tariflerini kurulumdan önce inceleyin.
