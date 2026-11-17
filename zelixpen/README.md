# ZelixPen

Python ve PyQt6 ile yazılmış ekran üzerinde çizim ve işaretleme aracı.

## Özellikler

- Serbest çizim, çizgi, ok, dikdörtgen ve daire araçları.
- Renk ve kalem kalınlığı seçimi.
- Geri alma, yineleme ve çizimleri temizleme.
- İmleç modunda alttaki uygulamalarla etkileşim.
- Çizimleri saydam arka planlı PNG olarak kaydetme.

## Kurulum

Zelix deposunun yapılandırıldığı bir sistemde:

```bash
sudo pacman -Syu zelixpen
zelixpen
```

## Kaynaktan çalıştırma

Python ve `python-pyqt6` gereklidir:

```bash
python main.py
```

Araç çubuğundan çizim aracını seçin. İmleç düğmesiyle masaüstüne geçin; çizime dönmek için bir çizim aracı seçin. Pencere katmanı ve imleç davranışı kullanılan masaüstü oturumuna bağlıdır.

Paket tarifi [zelix-repo](https://github.com/ZelixOS/zelix-repo/tree/main/zelixpen) deposundadır.
