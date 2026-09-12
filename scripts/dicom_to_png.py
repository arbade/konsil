#!/usr/bin/env python3
"""Konsil deterministic DICOM -> PNG renderer for the off-protocol AI read path.

DICOM -> pydicom read -> apply_voi_lut -> MONOCHROME1 inversion
-> min-max normalize to 8-bit -> PNG.

No AI touches pixels anywhere in this file. This render only FIXES the input
the off-protocol reading agent sees; it interprets nothing. The default
no-AI-on-pixels rule of imaging-3d is unaffected.

Usage:
  python dicom_to_png.py <in.dcm> <out.png> [--frame N]
"""
import argparse, sys
from pathlib import Path

# kritik importlar baştan: eksikse tek anlaşılır mesajla çık, yarıda iş bırakma
try:
    import numpy as np
    import pydicom
    from pydicom.pixel_data_handlers.util import apply_voi_lut
    from PIL import Image
except ImportError:
    sys.exit("pydicom/Pillow missing — run: bash scripts/setup_imaging.sh")

# Deterministiklik: rastgelelik yok, zaman damgası yok — aynı girdi her zaman
# aynı çıktı (test_commands'ta cmp ile doğrulanıyor).

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("in_dcm"); ap.add_argument("out_png")
    ap.add_argument("--frame", type=int, default=0, help="çok-kareli seride kare seçimi")
    a = ap.parse_args()

    # 1. DICOM oku
    ds = pydicom.dcmread(a.in_dcm)
    if "PixelData" not in ds:
        sys.exit(f"no pixel data in {a.in_dcm}")

    # 2. VOI LUT uygula — cihazın kendi pencere/LUT'u okumanın tanısal
    # penceresidir; yoksa ham veriye düş
    try:
        arr = apply_voi_lut(ds.pixel_array, ds)
    except Exception:
        arr = ds.pixel_array
        print("! no VOI LUT applied — raw pixel values used")

    # Çok-kareli seri: normalizasyon seçilen kare üzerinden yapılsın diye
    # kareyi ERKEN dilimle — tüm hacme göre pencere kareyi soldurur
    frames = int(getattr(ds, "NumberOfFrames", 1) or 1)
    if frames > 1:
        if not 0 <= a.frame < frames:
            sys.exit(f"--frame {a.frame} out of range (0..{frames - 1})")
        arr = arr[a.frame]
        print(f"! {frames} frames; rendering frame {a.frame}")

    # 3. MONOCHROME1 inversiyonu — LUT SONRASI yapılmalı, yoksa ters pencere
    if ds.get("PhotometricInterpretation", "") == "MONOCHROME1":
        arr = arr.max() - arr

    # 4. min-max normalizasyon -> uint8 — düz (tek değerli) görüntüde
    # sıfıra bölme koruması
    arr = arr.astype(np.float64)
    ptp = arr.max() - arr.min()
    if ptp == 0:
        print("! flat image — single-valued pixels, writing zeros")
        arr8 = np.zeros(arr.shape, dtype=np.uint8)
    else:
        arr8 = ((arr - arr.min()) / ptp * 255.0).astype(np.uint8)

    # 5. PNG yaz — provenance metadata'sı gömme YOK: PNG zlib çıktısı
    # deterministik kalsın diye sadece piksel yazılır
    out = Path(a.out_png)
    # ilk okumada renders/ henüz yok — üst dizini her zaman oluştur
    out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(arr8)
    img.save(out)
    print(f"-- wrote {out} ({img.width}x{img.height}, "
          f"{ds.get('PhotometricInterpretation', '?')}, "
          f"study {ds.get('StudyDate', '?') or '?'}, "
          f"modality {ds.get('Modality', '?') or '?'})")

if __name__ == "__main__":
    main()
