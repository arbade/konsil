# Discovery Plan — "Yüklenen MR/US'de kitle/kist boyut–konum ölçümü" yeteneği

**Tarih:** 2026-09-12 · **Ürün aşaması:** mevcut ürün (Konsil imaging) · **Yöntem:** 4 bağımsız lens (klinik-regülasyon, deterministik mühendislik, emsal-pazar, kullanıcı-değeri), ultracode çok-ajan keşfi

**Keşif sorusu:** Kullanıcı bir MR/US yüklediğinde sistem "radyolog gibi" inceleyip kitle/kistin boyutunu ve konumunu verebilir mi? Veremiyorsa bu ihtiyaç meşru yollarla nasıl karşılanır? ("Rapor tarif ettiği yeri neden modelde işaretlemiyor?" sorusu dahil.)

## Kısa cevap

**Hayır — ve bu bilinçli bir sınır.** Piksellerden lezyon tespit/ölçüm yapan her bileşen (VLM'e okutmak da, "deterministik görünümlü" nnU-Net/KiTS patoloji segmentasyonu da) tanımı gereği **CADe/CADx sınıfı regüle tıbbi cihazdır** (FDA 21 CFR 892.2060/2070; AB MDR Kural 11 → Sınıf IIa–IIb). Onaylı ürünler bile (Koios DS, Quantib Prostate, ClearRead CT) yalnızca **hekime adjunct** olarak satılır, hastaya değil. Genel VLM'lerin klinik görüntülerdeki ölçülü doğruluğu (%8–35) ve tek bir bariz yanlış işaretin araca güveni tamamen çökertmesi (asimetrik maliyet) bunu ürün açısından da öldürür. Boyut–konum bilgisinin tek meşru kaynağı **radyoloğun yazılı raporudur**; sistemin işi bunu pikselden yeniden üretmek değil, **kavratmaktır**.

Kullanıcı talebinin altındaki gerçek ihtiyaç üç katman: **(1) NEREDE?** (mekânsal yer görme) · **(2) NE KADAR büyük?** (mm'yi kavrama) · **(3) BÜYÜYOR mu?** (takipte değişim). Üçü de rapor-türevi veriyle, piksel okumadan karşılanabilir.

## Değerlendirilen seçenekler

| # | Seçenek | Piksel kuralı | Karar | Not |
|---|---|---|---|---|
| 1 | VLM'e görüntüyü "radyolog gibi" okutmak | **İHLAL** | ❌ yapma | Onaysız CADx; %8–35 doğruluk; halüsinasyon |
| 2 | Patoloji segmentasyon modeli (nnU-Net/KiTS, TS lezyon alt görevleri) | **İHLAL** | ❌ yapma | KiTS23 tümör Dice ≈0.75; non-commercial lisans; onaysız SaMD |
| 3 | **Rapor metni → yapı+bölge işaretçisi** (maskenin üst/orta/alt üçte-birliği, salt geometri) | uyumlu | ✅ **yapıldı (2026-09-12)** | `annotations.json marker` alanı; "~" ön eki + provenance notu zorunlu |
| 4 | Rapor alıntısı + yapı rozeti (mevcut annotations akışı) | uyumlu | ✅ mevcut, korunuyor | Emsal sınıf: PocketHealth/Scanslated "hasta-iletişim aracı" |
| 5 | Kullanıcı/radyolog güdümlü deterministik kaliper (2 nokta tıkla → voxel-spacing'den mm) | uyumlu | ⚠ koşullu | ABD'de 892.2050/MICAP sınırında; "sistem ölçer, karakterize etmez" diliyle, hukuki görüş sonrası |
| 6 | DICOM SR / US kaliperlerinin İNSAN transkripsiyonu | uyumlu | ⚠ koşullu | SR nesneleri hasta CD'lerinde nadir; varsa deterministik parse değerli |
| 7 | Rapordaki seri/kesit numarasından deterministik yerleşim | uyumlu | ⚠ koşullu | Rapor referans verirse ucuz ve kesin; US raporlarında yok |
| 8 | Takip (interval) değişim kartı — rapor-tabanlı boyut zaman çizgisi | uyumlu | ✅ sıradaki aday | case-update akışına; modaliteler-arası karşılaştırma uyarısıyla |
| 9 | Gerçek radyolog ikinci okuması paketleme | uyumlu | ✅ uzun vade | Sübtil bulgular için tek dürüst cevap; yorum lisanslı hekimde |

## Kritik varsayımlar (Impact × Uncertainty)

| # | Varsayım | Kategori | Etki | Belirsizlik | Test |
|---|---|---|---|---|---|
| A1 | Yaklaşık bölge işareti, "~" etiketiyle bile **kesin konum sanılmaz** | usability | yüksek | **yüksek** | 5 kullanıcıya işaretli sahne: "lezyon tam burada mı?" — yanlış-kesinlik >%20 ise görsel dil değişir (kesikli/geniş yarı saydam bölge) |
| A2 | Asıl ihtiyaç yeni ölçüm değil, **raporda yazanın 3B'de yerini görmek** | value | yüksek | orta | 5 vaka sahibiyle sesli-düşünme: "AI ölçseydi mi, raporun dediğini görmek mi?" |
| A3 | Raporlardaki konum ifadeleri küçük bir kural tablosuyla bölgeye eşlenebilir | feasibility | orta | orta | 20–30 rapor cümlesinde "yerleştirilebilir bulgu" oranını say |
| A4 | bbox Z-üçte-birliği radyoloğun "pol" kastıyla yeterince örtüşür (oblik organda PCA ekseni gerekebilir) | feasibility | orta | orta | kidney maskesinde bbox vs PCA bölmeyi yan yana render edip bir radyoloğa sor |
| A5 | Piksel-tabanlı her ölçüm özelliği Konsil'i onay gerektiren SaMD yapar | viability | yüksek | düşük | FDA CDS guidance + MDR Rule 11 ile özellik-bazlı sınıflandırma memosu |

## Karar çerçevesi

- A1 testi **geçerse** → bölge işaretçisi varsayılan kalır; geçmezse görsel dil "geniş yarı saydam bölge + zorunlu etiket"e döner.
- A3 ≥ ~%60 ise → annotation adımına konum-sözlüğü kural tablosu eklenir (üst/alt pol, anterior/posterior… → region).
- Kaliper (5) yalnızca hukuki görüş + "hekime-hitap" dili netleşirse yapılır.
- Piksel-yorumlu seçenekler (1, 2) **hiçbir koşulda** ürüne girmez; araştırma-only ROI deneyi (roadmap) ürün yüzeyine sızamaz.

## Bu keşiften çıkan uygulama (aynı gün yapıldı)

`annotations.json`'a isteğe bağlı `marker: {region, label}` alanı; viewer ⌖ odağında crosshair'i **raporun tarif ettiği bölgeye** (yapının kendi maskesinin üst/orta/alt üçte-birlik centroid'i — salt geometri) taşıyor ve "~" ön ekli 3D etiket çiziyor. Ayrıca render+MPR'da tutarlı **Yakınlaştır** kaydıracı eklendi. Sert kural ihlal edilmedi: hiçbir model piksel okumadı; bölge bilgisi yazılı rapor METNİNDEN, geometri deterministik segmentasyondan.
