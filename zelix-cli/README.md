# Zelix CLI

ZelixOS için Bash ile yazılmış komut satırı yönetim aracı. Sistem güncellemesi, bakım ve yardımcı uygulamalara erişim sağlar.

## Kurulum

Zelix deposunun yapılandırıldığı bir sistemde:

```bash
sudo pacman -Syu zelix-cli
zelix help
```

## Komutlar

| Komut | İşlem |
| --- | --- |
| `zelix update` | Sistem, mevcut AUR yardımcısı ve Flatpak üzerinden güncelleme |
| `zelix mirrors` | Paket aynalarını düzenleme |
| `zelix clean` | Paket önbelleği ve sahipsiz paket bakımı |
| `zelix flathub` | Flathub desteğini yapılandırma |
| `zelix info` | Sistem bilgilerini gösterme |
| `zelix hello` | Zelix Hello uygulamasını açma |
| `zelix lang tr` | Arayüz dilini Türkçe yapma |
| `zelix lang en` | Arayüz dilini İngilizce yapma |

## Bağımlılıklar

Bash, pacman ve sudo gereklidir. Kullanılan komuta göre Flatpak, rate-mirrors, fastfetch, Paru, Yay veya Zelix Hello gerekir. Dil tercihi XDG yapılandırma dizinindeki `zelix/cli.conf` dosyasında tutulur; varsayılan konum `~/.config/zelix/cli.conf` olur.

## Kaynaktan kullanım

```bash
bash zelix help
```

Paketi oluşturmak için normal kullanıcıyla `makepkg -s` çalıştırın.
