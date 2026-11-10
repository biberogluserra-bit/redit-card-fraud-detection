# Aşırı Dengesiz Veride Kredi Kartı Dolandırıcılığı Tespiti

**Deney durumu:** Kullanıcının sağladığı creditcard.csv ile altı yöntemin beş tekrarı ve final test değerlendirmesi tamamlandı. [7. hafta ara raporu](reports/7_hafta_ara_raporu.md), [sonuç tablosu](reports/sonuc_tablosu.csv) ve [kaynak listesi](reports/kaynak_dogrulama.md) hazırdır.

## Google Colab'de tek seferde çalıştırma
`Fraud_Project_Colab.ipynb` defterini Google Colab'e yükle, hücreleri sırayla çalıştır. Sistem OpenML #1597'yi indirir, deneyleri yürütür ve çıktıları zip olarak paketler.

## Bilgisayarda
```bash
pip install -r requirements.txt
python code/run_experiment.py --out results
# Alternatif: Kaggle kaynaklı CSV indirildiyse
python code/run_experiment.py --data data/creditcard.csv --out results
```

## Çıktılar
Tam resmî ARFF dosyasını `data/creditcard.arff` konumuna indirdikten sonra önce `python code/verify_source.py` ve ayrı klasörde sentetik test çalıştırılmalıdır. Ardından `python code/run_experiment.py --data data/creditcard.arff --out results` ve `python code/build_report.py` gerçek raporu üretir. Eksik dosyayı kullanmayın. Yeni çıktı klasörü, test setine bakılarak yeniden ayar yapılmasını bilimsel olarak meşrulaştırmaz.

Beş tekrar tam 5 katlı çapraz doğrulama değildir: beş farklı tohumla geliştirme bölmesi karşılaştırmasıdır. AP eşitliğinde model seçimi doğrulama F1 değerine dayanır.

- `results/metadata.json`: veri özeti ve yöntem beyanı
- `results/cv_repeated_results.csv`: 5 tekrarın her model için ölçümleri
- `results/cv_summary.csv`: ortalama / std, karşılaştırma tablosu
- `results/exploratory_paired_tests.csv`: 5 bağımlı bölüm üzerinden **keşifsel** Wilcoxon; bağımsızlık sınırlılığı
- `results/final_untouched_test_results.csv`: geliştirme verisine göre seçilen model ve önceden belirlenen baseline'ın en son test değerlendirmesi
- `results/pr_test_*.png`: nihai holdout Precision–Recall grafiği
- `results/test_bootstrap_confidence_intervals.csv`: holdout üzerinde özdeş özellik gruplarını yeniden örnekleyerek hesaplanmış **keşifsel** %95 AP aralıkları (evren güven aralığı değil)

## Yöntem güvenilirliği
- `Class` hedef; `V1..V28`, `Amount` girdi. OpenML sürümünde `Time` sütunu yoktur. Orijinal CSV dosyasında varsa **özelliklerden çıkarılır**, bu nedenle zaman bazlı ileriye dönük doğrulama yapılamaz.
- 29 özellikten türetilmiş özdeş satır grupları **aynı veri bölmesinde** tutulur. Birey, kart ve işlem ID'si bulunmadığından tam bağımsızlık garanti edilmez.
- Model seçiminde geliştirme bölmesinin 5 ayrı tekrarında PR-AUC (Average Precision) sıralaması kullanılır; **test kümesi yalnızca sonunda değerlendirilir**.
- Tüm ölçekleme ve yeniden örnekleme eğitim altkümesinde uygulanır. Eşik, iç kalibrasyon kümesinde F1 maksimize edilerek seçilir.
- `illustrative_cost = FP + 10 × FN` tamamen **varsayımsal bir maliyet fonksiyonudur**; veri setinde gerçek finansal kayıp yoktur.
- `--smoke-test` sadece sentetik veride kod çalışırlığını sınar; gerçek deney yerine geçmez.

## Bilimsel etik ve kullanım
Hoca yönergesindeki üretken yapay zekâ sınırlamasına uy. Hazırlanan metinler düzenlenebilir taslaktır; bilimsel yorumları, 15 tam metin makaleyi ve kodun sonuçlarını şahsen doğrula. Nihai rapora yapay zekâ kullanım beyanı ekle. Son bildiri, gerçek deney tabloları ve üretken yapay zekâ kullanım beyanı içerir.

## Kaynak ve atıf
OpenML #1597: https://www.openml.org/d/1597 . Orijinal veri: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud . Dataset citation: Dal Pozzolo et al. (2015), Calibrating Probability with Undersampling for Unbalanced Classification. Kaynak matrisi DOI bağlantılarını içerir.

## 12. hafta teslimi
[Altı sayfalık bildiri](reports/12_hafta_IEEE_bildiri.pdf), [düzenlenebilir Word dosyası](reports/12_hafta_IEEE_bildiri.docx), [sunum](reports/10_dakika_sunum.pptx) ve [literatür incelemesi](reports/literatur_inceleme.md).