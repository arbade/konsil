# Discovery Plan — OFF-PROTOCOL AI Görüntü Okuma Yolu ("bypass")

**Tarih:** 2026-09-12 · **Ürün aşaması:** mevcut ürün (Konsil imaging/board) · **Yöntem:** PM/Tasarımcı/Mühendis üçlü-lens fikir üretimi → seçim → varsayım haritası (Etki×Risk) → deney tasarımı. Otonom yürütüldü; tüm seçimler gerekçeli.

**Keşif sorusu:** Kullanıcı AÇIKÇA istediğinde ("bypass") devreye giren, varsayılan piksel-yasağını ZAYIFLATMAYAN bir AI görüntü okuma yolu nasıl ürünleştirilir? Emsal: shoulder-001'de elle yürütülen okuma (pydicom render → konsil-specialist'e sistematik gözlemsel okuma → `round1-goruntu-okuma-OFF-PROTOCOL.md`), görüntüdeki yanık "L" markerini bulup vaka dosyasındaki taraf boşluğunu kapattı.

## Kısa cevap ve konum

Bu yol **istisna kapısıdır, ürün yüzeyi değildir.** Bir önceki keşif ([discovery-lezyon-olcum-2026-09-12.md](discovery-lezyon-olcum-2026-09-12.md)) piksel-yorumun regülasyon ve doğruluk nedeniyle ürüne giremeyeceğini kayda geçirdi; o karar geçerli kalır. Buradaki fark: **kullanıcının açık, bilgilendirilmiş ve kayıt altına alınmış talebi** üzerine, resmi rapor gereksinimini ORTADAN KALDIRMADAN çalışan, çıktısı her zaman OFF-PROTOCOL etiketli bir okuma. Değer önerisi tanı değil: (1) resmi rapora erişilemeyen/gecikmiş durumda **geçici oryantasyon**, (2) rapor varken **ikinci-göz tutarlılık kontrolü**, (3) markerlar gibi **teknik-olgusal boşlukların** (taraf, projeksiyon, kalite) kapatılması.

## 1) Fikir üretimi (PM / Tasarımcı / Mühendis)

| # | Fikir | Lens | Boyut |
|---|---|---|---|
| F1 | Ayrı komut: `/konsil:okuma <case-id>` — imaging'e flag DEĞİL; deterministik hat dokunulmamış kalır, off-protocol yol fiziksel olarak ayrı skill/komut | PM | komut adı / mimari |
| F2 | Yazılı onay kapısı: komut önce riskleri sayar, kullanıcı tam cümleyi yazarak onaylar ("OFF-PROTOCOL OKUMAYI ONAYLIYORUM"); onay metni + zaman damgası board memlog'una işlenir | Tasarımcı | onay/bypass UX |
| F3 | Deterministik render ön-aşaması: `scripts/dicom_render.py` (pydicom `apply_voi_lut` + MONOCHROME1 inversiyonu + min-max normalizasyon) — emsaldeki elle akışın versiyonlanmış, tekrarlanabilir hali; AI'ya giden girdi sabitlenir | Mühendis | güvenlik bariyeri |
| F4 | Okuma protokollü ajan şablonu: konsil-specialist'ten türeyen "görüntü okuma üyesi" — bölge bölge sistematik tarama, her gözleme güven düzeyi, "bulgu uydurma; belirsizi belirsiz işaretle", literatür zorunluluğu yok (saf gözlemsel okuma) | Mühendis | kurul entegrasyonu |
| F5 | Makine-denetlenebilir çıktı şablonu: zorunlu ÜST başlık + zorunlu ALT disclaimer; board-report Reviewer Gate'e beşinci denetçi ("off-protocol uygunluk": disclaimer var mı, her gözlemde güven düzeyi var mı, dosya adı `*-OFF-PROTOCOL.md` mi) | Mühendis | güvenlik bariyeri |
| F6 | Kurul tutanağı entegrasyonu: okuma tutanakta ayrı, OFF-PROTOCOL etiketli bölümde; Missing Data Gate'teki "resmi radyoloji raporu eksik" bayrağını ASLA kapatmaz — boşluk açık kalır | PM | kurul entegrasyonu |
| F7 | Olgu/yorum ayrımı (two-track): "teknik olgu" (yanık marker, projeksiyon, ekspojur) ile "yorumsal bulgu" (kırık yok, lezyon yok) çıktıda ayrı bloklar; yalnızca teknik olgular vaka dosyası boşluklarını doldurabilir, o da provenance etiketiyle ("kaynak: OFF-PROTOCOL AI okuması") | PM | çıktı yerleşimi |
| F8 | Karşılaştırma modu: resmi rapor VARSA okuma köre yapılır, sonra rapor ile fark tablosu üretilir (ikinci-okuyucu QA) — tanı değil tutarlılık aracı | PM | değer genişletme |
| F9 | Görsel karantina: dosya adı zorunlu `-OFF-PROTOCOL` son eki, tutanakta bantlı uyarı bloğu, AI okumasından türetilen her PNG kırpıntısına "AI OKUMASI — RESMİ RAPOR DEĞİL" filigranı | Tasarımcı | çıktı yerleşimi |
| F10 | Kurumsal kill-switch: plugin ayarıyla yol tamamen kapatılabilir (`off_protocol_reading: disabled`); kurum/klinik dağıtımlarında varsayılan kapalı | PM | güvenlik bariyeri |
| F11 | Çift bağımsız okuma (ensemble): iki izole ajan aynı görüntüyü okur, uyuşmazlıklar "belirsiz"e düşürülür | Mühendis | güvenlik bariyeri |

## 2) Seçilen fikirler (ilk sürüm kapsamı)

**F1 + F2 + F3 + F4/F5 + F7** — gerekçeler:

- **F1 (ayrı komut):** Bypass'ın imaging-3d'ye flag olarak eklenmesi (`/konsil:imaging --bypass`) sert kuralı taşıyan skill'in içine istisna sızdırır ve "kazara açma" riskini büyütür. Ayrı komut hem SKILL.md'deki sert kuralın metnini dokunulmamış bırakır hem de niyeti açık kılar. Komut adı önerisi: `/konsil:okuma` (Türkçe kullanıcı-yüzü ile uyumlu; açıklamasında "OFF-PROTOCOL" geçer).
- **F2 (yazılı onay):** "Açık komut/onay" gereksiniminin denetlenebilir hali. Tek tuş onayı otomasyon yanlılığını besler; tam cümle yazımı sürtünmeyi bilinçli olarak korur ve memlog kaydı emsal üretir.
- **F3 (deterministik render):** Emsalde elle yapılan pydicom akışı script'e dönmezse her çalıştırmada farklı pencere/normalizasyon → tekrarlanamaz okuma. Render deterministik, YORUM AI'da — sınır net.
- **F4+F5 (protokol + denetçi):** Emsal çıktının kalitesini (bölge bölge, güven düzeyli, "değerlendirilemedi" diyebilen) şablona bağlamak ve disclaimer'ı insan disiplinine değil Reviewer Gate denetçisine emanet etmek. Zorunlu gereksinim (a) ve (c) böyle mekanikleşir.
- **F7 (olgu/yorum ayrımı):** Emsalin en somut değeri "L" markeriydi — bu bir yorum değil gözlemsel olgu. Ayrım, değerin güvenli kısmının (teknik olgular) vaka dosyasına provenance'la akmasına izin verirken yorumsal bulguları karantinada tutar.

**Ertelenenler:** F8 (karşılaştırma modu) güçlü ama ikinci iterasyon — önce tekil okuma güvenli olsun. F11 (ensemble) maliyet/karmaşıklık; D1 deneyi gerekli gösterirse alınır. F9-F10 küçük ve büyük olasılıkla ilk sürümde "bedava" gelir (dosya adı kuralı + config anahtarı).

## 3) Varsayımlar

| # | Varsayım | Kategori |
|---|---|---|
| V1 | Kullanıcılar disclaimer'a rağmen "normal görünümde" cümlelerini resmi güvence gibi OKUMAZ; radyolog adımını atlamaz | GÜVENLİK — otomasyon yanlılığı / yanlış-negatif |
| V2 | Yazılı-onay sürtünmesi kullanıcıyı yıldırmaz; meşru ihtiyaçta yol gerçekten kullanılır | usability |
| V3 | Alt disclaimer okunur/etkilidir; banner körlüğüne kurban gitmez | GÜVENLİK — disclaimer'ın görmezden gelinmesi |
| V4 | Sistematik protokol + güven taksonomisi ile model "bulgu uydurma" yapmaz; belirsizi belirsiz bırakır (emsalde yaptı, genellenir mi?) | feasibility |
| V5 | Asıl değer teknik-olgusal boşluk kapatma + rapor-yokken oryantasyon; kullanıcılar bunu "AI tanısı" beklentisiyle karıştırmaz | value |
| V6 | "Yalnızca açık kullanıcı talebi + OFF-PROTOCOL etiket + resmi rapor gereksinimi korunur" çerçevesi projeyi CADx/SaMD sınıflandırmasının dışında (araştırma/kişisel araç konumunda) tutar | viability |
| V7 | Deterministik render (F3) tanısal açıdan yeterli görüntü üretir (VOI LUT kaybı, 8-bit indirgeme okumayı sistematik köreltmez) | feasibility |
| V8 | Reviewer Gate denetçisi disclaimer/etiket ihlallerini güvenilir yakalar (yanlış-geçirme ≈ 0) | GÜVENLİK — bariyer bütünlüğü |

## 4) Önceliklendirme (Etki × Risk)

| # | Etki (yanlışsa hasar) | Risk (yanlış çıkma olasılığı) | Öncelik |
|---|---|---|---|
| V1 | **çok yüksek** — kaçırılmış patoloji + atlanmış radyolog | **yüksek** — otomasyon yanlılığı literatürde güçlü, akıcı/uzun metin güven yaratır | **P0** |
| V4 | **çok yüksek** — uydurulmuş bulgu tüm ürün güvenini çökertir (asimetrik maliyet) | orta — emsal iyi ama n=1, tek modalite | **P0** |
| V3 | yüksek | orta-yüksek — statik disclaimer'lar tipik olarak okunmaz | **P1** |
| V6 | yüksek — dağıtım/hukuk | orta — "kullanıcı talebiyle, adjunct, rapor-korumalı" konum savunulabilir ama gri | **P1** |
| V7 | orta — okuma kalitesi sistematik düşer | orta | P2 |
| V8 | orta — bariyer delinirse etiketa güven biter | düşük — mekanik kontrol | P2 |
| V5 | orta | düşük-orta | P2 |
| V2 | düşük — özellik az kullanılır, zarar yok | düşük | P3 |

## 5) Doğrulama deneyleri (kritik varsayımlar için)

**D1 — Tohumlu-bulgu yanlış-negatif testi (V4, kısmen V7):**
Kamuya açık, etiketli grafi setinden (örn. MURA / kırık-etiketli omuz-el bileği grafileri) 15–20 görüntü: ~yarısı bilinen bulgulu, yarısı normal. Her biri F3 render'ından geçirilip F4 protokolüyle köre okutulur. Ölçütler: **bariz bulguda yanlış-negatif oranı**, uydurulmuş-bulgu (yanlış-pozitif "kesin" iddia) sayısı, "belirsiz" etiketinin isabeti. **Eşik:** bariz bulgu kaçırma >%20 veya ≥1 yüksek-güvenli uydurma → yorumsal blok (F7'nin ikinci yolu) ilk sürümden çıkar, yalnız teknik-olgu okuması yayımlanır; ensemble (F11) yeniden değerlendirilir. Aynı setin bir alt kümesi orijinal DICOM penceresi vs F3 render'ı ile çift okutularak V7 ölçülür.

**D2 — Disclaimer/otomasyon-yanlılığı kullanım testi (V1, V3):**
5 kullanıcıya (vaka sahibi profili) shoulder-001 tarzı tamamlanmış bir OFF-PROTOCOL çıktısı gösterilir; senaryo sorusu: "Bu okumaya göre ne yaparsın? Radyoloğa götürür müsün? Bu belge nedir?" Ölçütler: çıktıyı "rapor" diye adlandırma oranı, "artık radyolog gerekmez" çıkarımı, alt disclaimer'ı fark etme. **Eşik:** ≥2/5 kullanıcı radyolog adımını gereksiz sayarsa → çıktı formatı sertleşir: her bölüm başına satır-içi uyarı, sonuç cümlesi yasağı ("normal" yerine "bu okumada saptanmadı"), komut sonunda kullanıcıya sesli teyit sorusu ("resmi rapor planın ne?" cevabı memlog'a).

V6 için deney değil masa çalışması: FDA CDS guidance + MDR Rule 11 üzerinden özellik-bazlı konumlandırma memosu (önceki keşfin A5 memosu genişletilir) — D1/D2 ile paralel yürür.

## 6) Karar çerçevesi

- D1 geçmeden yorumsal okuma bloğu (kırık/lezyon değerlendirmesi) hiçbir kurula girmez; teknik-olgu okuması (marker/projeksiyon/kalite) D1'den bağımsız erken çıkabilir — hasar yüzeyi minimal.
- D2 eşiği aşılırsa format sertleştirme ZORUNLU; disclaimer metni asla kısaltılamaz, yalnız güçlendirilebilir.
- Sert kural metni (SKILL.md) DEĞİŞMEZ; off-protocol komutun dokümantasyonu sert kurala atıf verir ve "bu yol o kuralın istisnası değil, kullanıcı-onaylı ayrı bir moddur; varsayılan davranışı etkilemez" der.
- Zorunlu değişmezler her sürümde: (a) çıktının ALTINDA atlanamaz disclaimer — "Bu bir yapay zekâ sonucudur; resmi radyoloji raporu değildir ve yerine geçmez; klinik korelasyon şarttır." (Reviewer Gate denetçisi doğrular); (b) yol yalnız açık kullanıcı onayıyla, onay memlog'da; (c) tutanakta OFF-PROTOCOL etiketi + Missing Data Gate'teki resmi-rapor bayrağı açık kalır; (d) `*-OFF-PROTOCOL.md` adlandırması.

## Emsal (bu keşfin tetiği)

shoulder-001, 2026-09-12: elle yürütülen okuma `cases/shoulder-001/board-2026-09-12/round1-goruntu-okuma-OFF-PROTOCOL.md`. Okuma bölge bölge, güven düzeyli ve "değerlendirilemedi" diyebilen formatta üretildi; yanık "L" markerini saptayarak vaka dosyasındaki taraf boşluğunu teknik-olgu düzeyinde kapattı. Bu emsal F3/F4/F5/F7'nin şablon kaynağıdır.
