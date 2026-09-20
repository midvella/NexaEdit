# NexaEdit

CustomTkinter arayüzü, `rembg[cpu]` ve Pillow ile yerel arka plan kaldırma.
Görsel seç → Arka planı kaldır → Şeffaf PNG kaydet.

## Kaynaktan çalıştırma

Python **3.14 x64** gereklidir.

```sh
python -m venv venv
```

Windows:

```bat
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

Linux / macOS:

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Linux Python kurulumunda Tk desteği gerekir (Debian/Ubuntu: `python3-tk`).
CustomTkinter, Tk altyapısını kullanır. Masaüstü oturumu olmadan arayüz açılamaz.

## Kurulum / kaldırma

Linux/macOS: `./install.sh` kurar, `./uninstall.sh` sanal ortamı ve uygulama menüsü kısayolunu kaldırır.
Windows: `install.bat` kurar, `uninstall.bat` sanal ortamı kaldırır. Kaynak dosyaları silmezler.
Kaynaktan ilk arka plan kaldırma işleminde U²-Net modeli (~176 MB) indirilir;
sonraki kullanımlar çevrimdışıdır. Görseller hiçbir sunucuya gönderilmez.

## Derleme

Windows `.exe` için **Windows üzerinde** Python 3.14 x64 kurup
`build_windows.bat` dosyasını çalıştırın. Python kurulumunda Tcl/Tk ve Python
Launcher seçenekleri etkin olmalıdır.

Diğer sistemlerde, yukarıdaki sanal ortamın Python komutuyla:

```sh
python -m pip install -r requirements-build.txt
python build.py
```

`build.py` modeli indirir/doğrular, CustomTkinter tema/fontlarını ve modeli
PyInstaller paketine ekler. Ardından **derlenmiş programda gerçek CPU çıkarımı,
PNG kaydı ve arayüz açılış testi** çalıştırır. Bir adım başarısız olursa komut
başarısız çıkar; ZIP yalnızca bu testlerden sonra oluşturulur. Derleme sırasında
masaüstü erişimi gerekir.

Çıktılar:

- Windows: `dist/NexaEdit/NexaEdit.exe`
- Linux: `dist/NexaEdit/NexaEdit`
- Dağıtım: `dist/NexaEdit-<platform>.zip`

**NexaEdit klasörünün tamamını paylaşın.** EXE tek başına çalışmaz; `_internal`
klasörü gerekli kütüphaneleri ve modeli içerir. Derlenmiş uygulamada ilk kullanımda
internet gerekmez. Her işletim sisteminin paketi o sistemde derlenmelidir.
Linux paketini hedeflediğiniz en eski Linux dağıtımı üzerinde derleyin.

## Davranış ve sınırlar

- PNG, JPEG, WEBP, BMP ve TIFF; en fazla 25 megapiksel.
- EXIF yönü düzeltilir; animasyonlarda ilk kare kullanılır.
- Çıktı orijinal piksel boyutunda RGBA PNG'dir; önizleme yalnızca ekranda küçültülür.
- Aynı anda tek işlem yapılır. Model yükleme, işleme ve dosya işlemleri arka plandadır.
- Kaynak görselin aynı yoluna kaydetme engellenir. Kayıt hatasında mevcut hedef korunur.
- CPU kullanılır; CUDA/GPU kurulumu gerekmez. İşleme süresi ve maske kalitesi görsele/donanıma bağlıdır.
- Uygulamayı işlem sırasında kapatmak devam eden işi sonlandırır.

## Kontroller

Sanal ortamın Python komutuyla:

```sh
python -m unittest discover -s tests -v
python main.py --self-test
python main.py --smoke-gui
```

`--self-test` gerçek model ile çalışır; kaynak kullanımında model indirmesi gerekebilir.
`--smoke-gui` arayüzü kısa süre açıp kapatır.

Paketleme yaklaşımı: [CustomTkinter resmî paketleme belgesi](https://customtkinter.tomschimansky.com/documentation/packaging/).
