# Yedinci hafta ara raporu

**Aşırı Dengesiz Veride Kredi Kartı Dolandırıcılığı Tespiti: Örnekleme, Maliyet-Duyarlı Öğrenme ve Eşik Seçimi**

Tarih: 11 Kasım 2026. Durum: gerçek veride tamamlanmış karşılaştırma; öğrenci incelemesi gereken ara rapor taslağı.

## Amaç ve veri

Amaç, aşırı dengesiz kredi kartı işlemlerinde örnekleme, sınıf ağırlıkları ve karar eşiğinin etkisini karşılaştırmaktır. Deney girdisi olarak data/creditcard.csv kullanılmıştır. İncelenen veri 284807 kayıt, 492 pozitif sınıf ve 29 model girdisi içerir. Pozitif oranı 0.172749% olarak hesaplanmıştır.

Veri seti kaydı: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud . Dosya SHA-256: `76274b691b16a6c49d3f159c883398e03ccd6d1ee12d9d8ee38f4b4b98551a89`.

## Yöntem

V1–V28 ve Amount kullanılmıştır. Ham dosyadaki Time alanı tasarım gereği model girdilerinden çıkarılmıştır. Sonuçlar rastgele grup bölmeli karşılaştırmadır; gelecekteki işlemler üzerinde zaman sıralı başarıyı göstermez.

29 özelliği aynı olan kayıtlar aynı grupta tutulmuştur. Fazladan özdeş özellik satırı sayısı 9144, farklı etiket içeren özdeş özellik grubu sayısı 0 olarak bulunmuştur. Bu gruplar kart/müşteri kimliği değildir; kart bazında bağımsızlık garanti edilmez. Sağlanan PCA dönüşümü ham özellikler olmadan yeniden öğrenilemez.

Test kümesi başlangıçta grup ayrımıyla ayrılmıştır. Geliştirme kümesinde beş farklı tohumla eğitim/doğrulama bölmesi oluşturulmuş, eğitim bölmesi ayrıca model öğrenme ve eşik kalibrasyonu için ayrılmıştır. StandardScaler ve SMOTE/undersampling yalnızca model öğrenme altkümesine uygulanmıştır. F1 eşiği yalnızca iç kalibrasyon kümesinde seçilmiştir. Modeller dış doğrulamada AP ile sıralanmış; AP eşitliğinde doğrulama F1 kullanılmıştır. Test sonuçları seçim sürecine katılmamıştır.

## Geliştirme sonuçları

Beş tekrarın ortalaması ± örneklem standart sapması aşağıdadır. AP, average precision olup trapez integralli PR alanıyla eş anlamlı kullanılmamalıdır.

| Yöntem | ap | precision | recall | f1 | roc_auc |
|---|---|---|---|---|---|
| RF_balanced | 0.7957 ± 0.0175 | 0.8854 ± 0.0416 | 0.7544 ± 0.0228 | 0.8139 ± 0.0160 | 0.9515 ± 0.0304 |
| LR_base | 0.7375 ± 0.0468 | 0.8865 ± 0.0477 | 0.6158 ± 0.0473 | 0.7247 ± 0.0258 | 0.9753 ± 0.0095 |
| LR_threshold_F1 | 0.7375 ± 0.0468 | 0.7806 ± 0.0818 | 0.7156 ± 0.0567 | 0.7420 ± 0.0114 | 0.9753 ± 0.0095 |
| LR_SMOTE_0.10 | 0.7300 ± 0.0586 | 0.3392 ± 0.0533 | 0.8185 ± 0.0241 | 0.4779 ± 0.0547 | 0.9718 ± 0.0058 |
| LR_weighted | 0.7154 ± 0.0592 | 0.0536 ± 0.0046 | 0.8922 ± 0.0196 | 0.1011 ± 0.0082 | 0.9721 ± 0.0068 |
| LR_RUS_0.10 | 0.6839 ± 0.0811 | 0.2395 ± 0.0544 | 0.8330 ± 0.0272 | 0.3689 ± 0.0631 | 0.9736 ± 0.0066 |

LR için eşik 0,5 iken ortalama F1 0.7247, iç doğrulamada seçilen eşikle 0.7420 bulundu. İki yöntemin aynı olasılık sıralamasını kullanması nedeniyle AP değerleri eşittir. Sınıf ağırlıklı LR'nin ortalama duyarlılığı 0.8922 ve kesinliği 0.0536 oldu. SMOTE ile ortalama AP 0.7300, rastgele alt örnekleme ile 0.6839 elde edildi.

## Kilitlenmiş nihai değerlendirme

Geliştirmede seçilen yöntem: **RF_balanced**. Test, seçilen yöntem ve önceden belirlenen LR baseline için final aşamasında değerlendirilmiştir. Test boyutu 57034, pozitif sayısı 98.

| model | ap | precision | recall | f1 | tp | fp | fn | tn | threshold |
|---|---|---|---|---|---|---|---|---|---|
| LR_base | 0.775493 | 0.819444 | 0.602041 | 0.694118 | 59 | 13 | 39 | 56923 | 0.5 |
| RF_balanced | 0.859395 | 0.858696 | 0.806122 | 0.831579 | 79 | 13 | 19 | 56923 | 0.5 |

Seçilen yöntem bu test bölmesinde 79 dolandırıcılık işlemini yakaladı, 19 işlemi kaçırdı ve 13 normal işlem için yanlış alarm verdi.

Test AP değeri için özdeş kayıt gruplarına dayalı bootstrap yüzdelikleri:

| model | ci_low_2_5 | ci_high_97_5 | replicates |
|---|---|---|---|
| LR_base | 0.6624 | 0.8695 | 200 |
| RF_balanced | 0.7699 | 0.9297 | 200 |

## İstatistiksel yorum ve sınırlılıklar

Tekrarlar örtüşen aynı veri kümesinden geldiği için bağımsız değildir. Standart sapma bölme duyarlılığını betimler; popülasyon güven aralığı değildir. Beş eşleştirilmiş fark için hesaplanan Wilcoxon değerleri yalnızca keşifseldir; doğrulayıcı anlamlılık veya üstünlük iddiası yapılmaz. Özdeş özellik gruplarını yeniden örnekleyen test bootstrap aralıkları da keşifseldir. Çoklu karşılaştırma ve model seçimi belirsizliği bulunmaktadır.

FP + 10×FN gerçek finansal kayıp değil, varsayımsal maliyet ölçüsüdür. Sınıf ağırlığı ve örnekleme sonrası olasılıkların kalibre olduğu varsayılmamıştır. Zaman değişimi, kart kimliği yokluğu, sağlanan PCA ve tek veri kaynağı genellenebilirliği sınırlar.

## Kalan çalışma ve yayın etiği

15 yayınlık doğrulama listesi `kaynak_dogrulama.md` dosyasındadır; öğrenci tam metinleri okuyup yöntemle ilişkilendirmelidir. On ikinci hafta için IEEE biçiminde 6–8 sayfalık metin hazırlanırken araştırma sorusu, bu protokol, gerçek sonuçlar, sınırlılıklar ve kaynakça birleştirilmelidir. Zaman sıralı duyarlılık analizi ayrı bir protokolle planlanmalı; burada görülen test sonuçları kullanılarak yeni model ayarı yapılmamalıdır.

Üretken yapay zekâ desteği: kod inceleme/düzeltme, çalıştırma düzeni ve taslak raporlama için kullanılmıştır. Bilimsel yorumların ve kaynakların son doğrulaması öğrenciye aittir; hocanın kullanım kuralları ayrıca kontrol edilmelidir.
