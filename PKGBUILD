# Maintainer: Moritz Bruder <muesli4 at gmail dot com>
pkgname=youtube-playlist-backup
pkgver=0.1
pkgrel=1
pkgdesc="Dumps all youtube playlists to stdout."
arch=(any)
url="https://github.com/muesli4/youtube-playlist-backup"
license=('GPL')
depends=('python' 'python-appdirs')
makedepends=()
checkdepends=()
optdepends=()
provides=('youtube-playlist-backup')
conflicts=()
source=("youtube-playlist-backup.py")
md5sums=(SKIP)

prepare() {
    #cd "$pkgname-$pkgver"
    echo
}

build() {
    #cd "$pkgname-$pkgver"
    echo
}

package() {
    install -m755 -D -T youtube-playlist-backup.py "$pkgdir/usr/bin/$pkgname"
}
