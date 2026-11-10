"""Build an interim Markdown report strictly from completed experiment outputs."""
import json
from pathlib import Path
import pandas as pd

root=Path(__file__).resolve().parents[1]
out=root/'results'
meta=json.loads((out/'metadata.json').read_text(encoding='utf-8'))
if meta['study_status']!='REAL_DATA':
    raise RuntimeError('Real data results required')
summary=pd.read_csv(out/'cv_summary.csv')
final=pd.read_csv(out/'final_untouched_test_results.csv')
def table(frame):
    return '| '+' | '.join(frame.columns)+' |\n|'+ '|'.join(['---']*len(frame.columns))+'|\n'+ '\n'.join('| '+' | '.join(str(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None))
display=pd.DataFrame({'Yöntem':summary.model})
for metric in ['ap','precision','recall','f1','roc_auc']:
    display[metric]=[f'{m:.4f} ± {s:.4f}' for m,s in zip(summary[metric+'_mean'],summary[metric+'_std'])]
text=f'''# Yedinci hafta ara raporu

**Aşırı Dengesiz Veride Kredi Kartı Dolandırıcılığı Tespiti: Örnekleme, Maliyet-Duyarlı Öğrenme ve Eşik Seçimi**

Tarih: 11 Kasım 2026. Durum: gerçek veride tamamlanmış karşılaştırma; öğrenci incelemesi gereken ara rapor taslağı.

## Amaç ve veri

Amaç, aşırı dengesiz kredi kartı işlemlerinde örnekleme, sınıf ağırlıkları ve karar eşiğinin etkisini karşılaştırmaktır. OpenML #1597 ham ARFF dosyası kullanılmıştır. İncelenen veri {meta['rows']} kayıt, {meta['fraud']} pozitif sınıf ve {meta['features']} model girdisi içerir. Pozitif oranı {meta['fraud_rate']:.6%} olarak hesaplanmıştır.

Kaynak: https://www.openml.org/d/1597 . Dosya SHA-256: `{meta['source_sha256']}`.

## Yöntem

V1–V28 ve Amount kullanılmıştır. Ham dosyadaki Time alanı tasarım gereği model girdilerinden çıkarılmıştır. Sonuçlar rastgele grup bölmeli karşılaştırmadır; gelecekteki işlemler üzerinde zaman sıralı başarıyı göstermez.

29 özelliği aynı olan kayıtlar aynı grupta tutulmuştur. Fazladan özdeş özellik satırı sayısı {meta['duplicates']}, farklı etiket içeren özdeş özellik grubu sayısı {meta['conflicting_label_groups']} olarak bulunmuştur. Bu gruplar kart/müşteri kimliği değildir; kart bazında bağımsızlık garanti edilmez. Sağlanan PCA dönüşümü ham özellikler olmadan yeniden öğrenilemez.

Test kümesi başlangıçta grup ayrımıyla ayrılmıştır. Geliştirme kümesinde beş farklı tohumla eğitim/doğrulama bölmesi oluşturulmuş, eğitim bölmesi ayrıca model öğrenme ve eşik kalibrasyonu için ayrılmıştır. StandardScaler ve SMOTE/undersampling yalnızca model öğrenme altkümesine uygulanmıştır. F1 eşiği yalnızca iç kalibrasyon kümesinde seçilmiştir. Modeller dış doğrulamada AP ile sıralanmış; AP eşitliğinde doğrulama F1 kullanılmıştır. Test sonuçları seçim sürecine katılmamıştır.

## Geliştirme sonuçları

Beş tekrarın ortalaması ± örneklem standart sapması aşağıdadır. AP, average precision olup trapez integralli PR alanıyla eş anlamlı kullanılmamalıdır.

{table(display)}

## Kilitlenmiş nihai değerlendirme

Geliştirmede seçilen yöntem: **{meta['selected_by_dev_cv_ap']}**. Test, seçilen yöntem ve önceden belirlenen LR baseline için final aşamasında değerlendirilmiştir. Test boyutu {meta['test_size']}, pozitif sayısı {meta['test_fraud']}.

{table(final[['model','ap','precision','recall','f1','tp','fp','fn','tn','threshold']].round(6))}

## İstatistiksel yorum ve sınırlılıklar

Tekrarlar örtüşen aynı veri kümesinden geldiği için bağımsız değildir. Standart sapma bölme duyarlılığını betimler; popülasyon güven aralığı değildir. Beş eşleştirilmiş fark için hesaplanan Wilcoxon değerleri yalnızca keşifseldir; doğrulayıcı anlamlılık veya üstünlük iddiası yapılmaz. Özdeş özellik gruplarını yeniden örnekleyen test bootstrap aralıkları da keşifseldir. Çoklu karşılaştırma ve model seçimi belirsizliği bulunmaktadır.

FP + 10×FN gerçek finansal kayıp değil, varsayımsal maliyet ölçüsüdür. Sınıf ağırlığı ve örnekleme sonrası olasılıkların kalibre olduğu varsayılmamıştır. Zaman değişimi, kart kimliği yokluğu, sağlanan PCA ve tek veri kaynağı genellenebilirliği sınırlar.

## Kalan çalışma ve yayın etiği

15 yayınlık doğrulama listesi `kaynak_dogrulama.md` dosyasındadır; öğrenci tam metinleri okuyup yöntemle ilişkilendirmelidir. On ikinci hafta için IEEE biçiminde 6–8 sayfalık metin hazırlanırken araştırma sorusu, bu protokol, gerçek sonuçlar, sınırlılıklar ve kaynakça birleştirilmelidir. Zaman sıralı duyarlılık analizi ayrı bir protokolle planlanmalı; burada görülen test sonuçları kullanılarak yeni model ayarı yapılmamalıdır.

Üretken yapay zekâ desteği: kod inceleme/düzeltme, çalıştırma düzeni ve taslak raporlama için kullanılmıştır. Bilimsel yorumların ve kaynakların son doğrulaması öğrenciye aittir; hocanın kullanım kuralları ayrıca kontrol edilmelidir.
'''
(root/'reports'/'7_hafta_ara_raporu.md').write_text(text,encoding='utf-8')
display.to_csv(root/'reports'/'sonuc_tablosu.csv',index=False,encoding='utf-8-sig')
print('Report created from REAL_DATA outputs')
