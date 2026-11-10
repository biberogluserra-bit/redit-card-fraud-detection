# Yedinci hafta ara raporu — deney öncesi durum

**Proje:** Aşırı Dengesiz Veride Kredi Kartı Dolandırıcılığı Tespiti: Örnekleme, Maliyet-Duyarlı Öğrenme ve Eşik Seçimi

**Tarih:** 11 Kasım 2026. **Durum:** Deney sonuçları henüz yoktur; bu belge tamamlanmış sonuç raporu değildir.

## Tamamlanan inceleme

Özel GitHub deposundaki README, deney betiği, Colab defteri ve gereksinimler incelendi. Önceki çalışmalar korunarak yerel çalışma kopyası oluşturuldu. OpenML resmî metadata uç noktasına erişildi: https://www.openml.org/api/v1/json/data/1597 . Metadata 284807 işlem ve 492 dolandırıcılık bildirir; bunlar bu oturumda tamamlanmış veri denetiminin çıktısı değildir.

Ham ARFF başlığı Time alanını içerir. Önceki “OpenML verisinde Time yoktur” ifadesi düzeltildi. Time, bu karşılaştırmada model girdilerinden tasarım gereği çıkarılır. İleride zaman sıralı duyarlılık analizi yapılabilir.

## Veri erişimi ve engel

Resmî ARFF indirmesi 133916976 baytta kesildi. Dosyanın MD5 özeti dbd93a2c0591550490141f78f1c30fb7 olup resmî 178bcf9bb1f31a3dfe12d0e577884add değeriyle eşleşmedi. Bu eksik dosya kullanılmadı. Sunucu byte-range ile devam ettirmeyi desteklemedi. Resmî Parquet alternatifi de çok yavaş ilerledi. Bilimsel Python bağımlılıklarının indirilmesi tamamlanmadı. Verinin tamamının erişilebilir ve çalıştırılabilir olduğu doğrulanamadı.

## Kod düzeltmeleri

Yerel ARFF ve Parquet okuma eklendi. Hedef değişken tamsayıya dönüştürülmeden önce 0/1 kontrolü ve girdiler için sonlu sayı kontrolü eklendi. Her bölmede grup kesişimi olmaması denetlenir. Özdeş özellik gruplarında farklı etiketler sayılır. Veri SHA-256 özeti, kütüphane sürümleri ve yeniden üretim için bölme indeksleri kaydedilir. Çalışma sırasında geliştirme ölçümleri ara dosyaya yazılır. Mevcut final sonuç dosyalarının üzerine yeniden değerlendirme engellenir.

Mevcut düzen LR baseline, sınıf ağırlıklı LR, SMOTE LR, undersampling LR, iç doğrulamada F1 eşiği seçilmiş LR ve sınıf ağırlıklı Random Forest içerir. StandardScaler ve yeniden örnekleme yalnızca öğrenme altkümesindedir. Beş tekrarda model seçimi dış doğrulama AP ortalamasına dayanır; AP eşitliğinde doğrulama F1 kullanılır. Test yalnızca seçilmiş yöntem ve önceden belirlenmiş baseline için en sonda değerlendirilir.

## Sonuç tablosu

| Yöntem | Tekrar | AP ort. ± std | Precision / Recall / F1 | Durum |
|---|---|---|---|---|
| LR baseline | 0/5 | Hesaplanmadı | Hesaplanmadı | Gerçek deney bekliyor |
| Sınıf ağırlıklı LR | 0/5 | Hesaplanmadı | Hesaplanmadı | Gerçek deney bekliyor |
| SMOTE LR | 0/5 | Hesaplanmadı | Hesaplanmadı | Gerçek deney bekliyor |
| Undersampling LR | 0/5 | Hesaplanmadı | Hesaplanmadı | Gerçek deney bekliyor |
| F1 eşiği seçilmiş LR | 0/5 | Hesaplanmadı | Hesaplanmadı | Gerçek deney bekliyor |
| Random Forest | 0/5 | Hesaplanmadı | Hesaplanmadı | Gerçek deney bekliyor |

Test kümesi skorları ve gerçek tekrarlı kayıt sayısı hesaplanmamıştır. Sentetik test skorları bilimsel sonuç olarak kullanılmamıştır.

## Doğrulama ve sınırlılıklar

Deney betiğinin Python sözdizimi kontrolü geçti. Bağımlılıklar tamamlanamadığı için sentetik uçtan uca test ve gerçek deney henüz çalıştırılmadı. İstatistiksel raporlama, örtüşen tekrarlar nedeniyle betimsel ortalama ± örneklem standart sapması olarak yorumlanmalıdır. Keşifsel Wilcoxon ve bootstrap çıktıları doğrulayıcı anlamlılık iddiasına dönüştürülmemelidir. AP trapez PR alanından farklıdır. FP+10FN varsayımsal maliyettir. Kart kimliği ve PCA öncesi ham özellikler bulunmadığından tam bağımsızlık ve PCA kaynaklı ön işleme sızıntısının yokluğu garanti edilemez.

## Sonraki uygulama

1. Tam ARFF indirilip `code/verify_source.py` ile resmî MD5 karşılaştırılmalı; eksik dosya kullanılmamalıdır.
2. Gereksinimler kurulup önce ayrı klasörde sentetik uçtan uca test çalıştırılmalıdır.
3. Gerçek veride beş tekrar tamamlanmalı; grup ayrımı, sınıf sayıları, yakınsama uyarıları ve ara kayıtlar incelenmelidir.
4. Yöntemler geliştirme verisinden seçildikten sonra final test bir kez değerlendirilmelidir.
5. `code/build_report.py` gerçek sonuç dosyalarından ara rapor ve CSV tablo üretir; sentetik çıktıyı reddeder.
6. Kaynak doğrulama listesindeki 15 yayının tam metin incelemesi tamamlanmalı; 12. hafta IEEE 6–8 sayfalık bildiriye yöntem, gerçek sonuçlar ve sınırlılıklar aktarılmalıdır.

Üretken yapay zekâ kod inceleme, düzeltme ve taslak raporlama desteği sağlamıştır. Öğrenci bilimsel yorumları ve kaynakları doğrulamalı; hocanın yapay zekâ kullanım kurallarını ayrıca kontrol etmelidir.
