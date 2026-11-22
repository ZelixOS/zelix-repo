pkgname=zelix-cli
pkgver=1.3.0
pkgrel=1
pkgdesc="Unified command-line management tool for ZelixOS"
arch=('any')
options=('!debug' '!strip')
url="https://github.com/ZelixOS/zelix-cli"
license=('GPL')
depends=('bash' 'pacman' 'sudo')
optdepends=('zelix-hello: launch the welcome application with zelix hello'
            'flatpak: manage Flatpak applications'
            'rate-mirrors: optimize Arch mirrors'
            'fastfetch: detailed system information'
            'paru: update AUR packages'
            'yay: alternative AUR package helper')
source=('zelix')
sha256sums=('SKIP')

package() {
    install -Dm755 "$srcdir/zelix" "$pkgdir/usr/bin/zelix"
}
