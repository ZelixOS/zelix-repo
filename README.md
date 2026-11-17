# ZelixOS Paket Deposu

ZelixOS uygulamalarının paket tarifleri, paketleme kaynakları ve pacman depo indeksleri.

## Paketler

| Dizin | İçerik |
| --- | --- |
| `zelix-hello/` | Karşılama ve sistem yönetimi uygulaması |
| `zelix-updater/` | Sistem güncelleme uygulaması |
| `zelixins/` | Grafik kurucu |
| `zelix-cli/` | Komut satırı yönetim aracı |
| `zelixpen/` | Ekran üzerinde çizim aracı |
| `paru/`, `yay/` | AUR yardımcılarının paket tarifleri |
| `x86_64/` | Depo veritabanı ve dosya indeksi |

## Kurulum

ZelixOS'ta `zelixrepo` deposu yapılandırılmışsa:

```bash
sudo pacman -Syu zelix-hello zelix-updater zelix-cli zelixpen
```

Paket arşivleri ve depo indeksleri [stable yayınından](https://github.com/ZelixOS/zelix-repo/releases/tag/stable) dağıtılır. Büyük paket dosyaları Git kaynak ağacı yerine yayın dosyalarında tutulur.

## Paket oluşturma

Arch Linux veya ZelixOS üzerinde `base-devel` ve ilgili PKGBUILD dosyasındaki bağımlılıklar gereklidir. İlgili paket dizininde normal kullanıcıyla çalıştırın:

```bash
makepkg -s
```

ZelixOS geliştirme çalışma alanında uygulama kaynakları ana dizinlerden eşitlenir. Kaynak değişikliklerini orada yapın; paket tariflerini bu depoda düzenleyin.

## İndeks ve yayın

`repo-add` ile yayınlanacak paketlerin indeksini oluşturun. Paket arşivlerini ve SHA256 dosyalarını önce yükleyin. İndekste belirtilen her paketin GitHub'da bulunduğunu ve SHA256 değerinin eşleştiğini doğruladıktan sonra şu dosyaları yayınlayın:

- `zelixrepo.db` ve `zelixrepo.db.tar.gz`
- `zelixrepo.files` ve `zelixrepo.files.tar.gz`

Depodaki `Publish Zelixins` GitHub Actions işi yalnızca kurucu paketini derlemek ve yayınlamak için elle başlatılabilir.
