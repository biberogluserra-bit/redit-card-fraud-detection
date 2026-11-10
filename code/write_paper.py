"""Build the Turkish conference manuscript from the archived experiment outputs."""
from pathlib import Path
import csv
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root = Path(__file__).resolve().parents[1]
out = root / 'reports'
def records(filename):
    with (root/'results'/filename).open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))
raw = records('cv_repeated_results.csv')
summary = records('cv_summary.csv')
final = records('final_untouched_test_results.csv')
def num(val, digits=3):
    return f'{float(val):.{digits}f}'.replace('.', ',')
def ms(r, k):
    return num(r[k+'_mean'])+' ± '+num(r[k+'_std'])
names = {'LR_base':'LR', 'LR_threshold_F1':'LR + eşik', 'LR_weighted':'LR + ağırlık', 'LR_SMOTE_0.10':'LR + SMOTE', 'LR_RUS_0.10':'LR + RUS', 'RF_balanced':'RF + ağırlık'}
d = Document()
s=d.sections[0]
s.page_width=Inches(8.5); s.page_height=Inches(11)
s.left_margin=s.right_margin=Inches(.68); s.top_margin=Inches(.70); s.bottom_margin=Inches(.7)
normal=d.styles['Normal']; normal.font.name='Times New Roman'; normal.font.size=Pt(10)
pf=normal.paragraph_format; pf.space_after=Pt(4); pf.line_spacing=1.04
pf.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
footer=s.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
def section(n, new=False):
    s=d.add_section(WD_SECTION.NEW_PAGE if new else WD_SECTION.CONTINUOUS)
    cols=s._sectPr.find(qn('w:cols'));cols.set(qn('w:num'),str(n));cols.set(qn('w:space'),'320')
def p(t):
    return d.add_paragraph(t)
def center(t, size=11, bold=False):
    z=d.add_paragraph(); z.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=z.add_run(t);r.bold=bold;r.font.size=Pt(size)
def head(t):
    z=d.add_paragraph();z.paragraph_format.keep_with_next=True;z.paragraph_format.space_before=Pt(5);z.alignment=WD_ALIGN_PARAGRAPH.CENTER
    z.add_run(t).bold=True
def tab(title,headers,rows):
    center(title,9,True)
    tbl=d.add_table(rows=0,cols=len(headers));tbl.style='Light Shading Accent 1'
    for row in [headers]+list(rows):
        for cell,v in zip(tbl.add_row().cells,row):
            para=cell.paragraphs[0];para.alignment=WD_ALIGN_PARAGRAPH.LEFT
            para.paragraph_format.space_after=Pt(3);para.paragraph_format.space_before=Pt(3)
            run=para.add_run(str(v));run.font.size=Pt(9)
def image(name,width):
    a=d.add_paragraph();a.alignment=WD_ALIGN_PARAGRAPH.CENTER
    a.add_run().add_picture(str(root/'results'/name),width=Inches(width))
center('Aşırı Dengesiz Veride Kredi Kartı Dolandırıcılığı Tespiti',21)
center('Örnekleme, Maliyet-Duyarlı Öğrenme ve Eşik Seçimi',15)
center('Sevim Serra Biberoğlu')
center('Yapay Zekâ ve Veri Mühendisliği Tezli Yüksek Lisans Programı',10)
center('Bilimsel Araştırma Teknikleri ve Yayın Etiği',10)
section(2)
p('Özet—Kredi kartı dolandırıcılığı tespitinde bir yöntemin değeri, kaç dolandırıcılığı yakaladığı kadar inceleme gerektiren yanlış alarmlara da bağlıdır. Bu çalışmada 284.807 işlemlik anonim veri üzerinde lojistik regresyon, sınıf ağırlıkları, SMOTE, rastgele alt örnekleme, karar eşiği seçimi ve Random Forest karşılaştırıldı. Aynı 29 model girdisine sahip işlemler bölme sırasında birlikte tutuldu. Beş geliştirme tekrarında sınıf ağırlıklı Random Forest ortalama 0,796 ± 0,017 Average Precision elde etti. Temel lojistik regresyonun karşılığı 0,737 ± 0,047 oldu. Önceden ayrılan 57.034 işlemde Random Forest 98 dolandırıcılığın 79’unu, lojistik regresyon ise 59’unu saptadı. İki model de 13 yanlış alarm üretti. Bulgular, gözlenen iki günlük işlem dağılımında, grup ayrımı ve doğrulama ile belirlenen protokol koşullarında geçerlidir.')
p('Anahtar sözcükler—Dolandırıcılık tespiti, sınıf dengesizliği, Average Precision, SMOTE, eşik seçimi.')
head('I. GİRİŞ')
p('Bir işlem incelemeye gönderildiğinde iki tür hata ortaya çıkabilir. Normal bir işlemin işaretlenmesi inceleme yükünü artırır. Dolandırıcılığın gözden kaçması ise müdahale fırsatını ortadan kaldırır. İncelenen veride tüm işlemleri normal kabul eden bir kural yaklaşık %99,83 doğruluğa ulaşır ve 492 dolandırıcılığın tamamını kaçırır. Bu nedenle çalışmanın birincil ölçütü dolandırıcılığı listenin üst sıralarına taşıma başarısını değerlendiren Average Precision’dır (AP). Karar eşiğine bağlı sonuçlar ayrıca raporlanır.')
p('Araştırmada üç soru ele alındı. İlk soru, azınlık sınıfını sentetik işlemlerle çoğaltmanın veya çoğunluk sınıfını azaltmanın sıralama başarısına etkisidir. İkinci soru, sınıf ağırlıkları kullanıldığında duyarlılık artışına eşlik eden yanlış alarm yüküdür. Üçüncü soru, aynı lojistik regresyon skorlarından hareketle yalnızca karar eşiği değiştirildiğinde kesinlik ve duyarlılığın nasıl değiştiğidir. Her koşul aynı işlemler üzerinde değerlendirildiği için bir tekrar içindeki farklar doğrudan karşılaştırılabilir.')
p('Random Forest karşılaştırması, doğrusal bir karar fonksiyonuyla açıklanamayan ilişkileri öğrenebilen bir yöntem ekler. Ağaç topluluğu ile sınıf ağırlığı birlikte kullanıldığı için bu deney, olası kazancın ne kadarının ağaçlardan ve ne kadarının ağırlıklardan geldiğini ayrı ayrı ölçmez. Çalışmanın katkısı, aynı veri bölmelerinde altı somut karar yönteminin performansını ve bunların alarm sayılarına yansımasını birlikte göstermesidir.')
section(2,True)
head('II. İLGİLİ ÇALIŞMALAR')
p('Chawla ve arkadaşlarının SMOTE yöntemi, azınlık sınıfındaki komşular arasında sentetik örnek üretir [1]. Komşuluk geometrisi girdi ölçeklerinden etkilendiği için bu deneyde sentetik örnek üretiminden önce eğitim verisi standartlaştırıldı. Fernández ve arkadaşları, SMOTE ailesinin gelişimini ve sınıf sınırlarına yakın örnekleri işlemenin güçlüklerini ele alır [2]. Dolandırıcılık olarak etiketli iki işlemin özellikleri arasında yer alan bir sentetik noktanın gerçek dünyada gerçekleşebilir bir işlem olduğu bu veriden doğrulanamaz.')
p('He ve Garcia [14], sınıf dengesizliği altında veri düzeyinde ve algoritma düzeyinde müdahaleleri karşılaştırır. Alt örnekleme, eğitimde görülen normal işlem çeşitliliğini azaltabilir. Dal Pozzolo ve arkadaşları örneklemenin sınıf öncüllerini ve olasılık yorumunu nasıl etkilediğini inceler [10]. Bu nedenle bir yöntemin 0,5 eşiğinde daha sık alarm vermesi ile dolandırıcılığı üst sıralara taşıması ayrı sorular olarak değerlendirildi. Elkan’ın maliyet çerçevesinde [13] hata türlerinin ağırlıkları uygulama kararına bağlıdır. Bu çalışmada kullanılan hata puanı yalnızca açıkça belirtilen varsayımsal bir senaryoyu temsil eder.')
p('Davis ve Goadrich [12], ROC ve kesinlik–duyarlılık uzayları arasındaki ilişkiyi gösterir. Saito ve Rehmsmeier [9], pozitif sınıf seyrek olduğunda yanlış pozitiflerin kesinlik üzerindeki etkisinin PR gösteriminde görünür olduğunu vurgular. Dolayısıyla küçük bir yanlış pozitif oranı, inceleme ekibinin az sayıda hatalı alarm alacağı anlamına gelmeyebilir. Lipton ve arkadaşlarının analizi [15], F1 için uygun eşiğin skor dağılımıyla bağlantısını açıklar. Çalışmamızda eşik her tekrarda ayrı bir iç doğrulama altkümesinde seçildi.')
p('Breiman’ın Random Forest yaklaşımı ağaçların tahminlerini birleştirir [8]. Dolandırıcılık gibi zamanla değişebilen bir süreçte çevrimdışı değerlendirme ile gerçek kullanım arasında ek bir ayrım vardır. Dal Pozzolo ve arkadaşları [11] akış halinde gelen işlemlere ve gecikmeli etiketlere dikkat çeker. Buradaki rastgele grup bölmesi aynı işlem dağılımını örnekler. Daha sonraki bir dönemde kullanılacak modeli sınamak için ileri zamanlı ve ayrı bir protokol gerekir.')
head('III. VERİ VE KAYIT BÜTÜNLÜĞÜ')
p('Kullanıcının sağladığı arşivden çıkarılan creditcard.csv, Eylül 2013’te Avrupalı kart sahiplerinden toplanan iki günlük işlemlerin açık veri sürümüdür [10]. ZIP bütünlük kontrolü geçti. Dosyada Time, V1–V28, Amount ve Class olmak üzere 31 sütun vardır. Class hedef etikettir. V1–V28 yayımlayıcı tarafından dönüştürülmüş sayısal bileşenlerdir. Amount işlem tutarını, Time ilk işlemden beri geçen süreyi gösterir. Model için V1–V28 ve Amount seçildi. Time dosyada mevcut olmakla birlikte karşılaştırma tasarımında girdi olarak kullanılmadı.')
p('284.315 normal ve 492 dolandırıcılık işlemi saptandı. Eksik değer bulunmadı. Bütün sütunlar aynı olduğunda ilk satır dışındaki tekrar sayısı 1.081’dir. Modelin gördüğü 29 girdi karşılaştırıldığında sayı 9.144’e çıkar. İkinci sayı, zamanları farklı olsa bile model açısından ayırt edilemeyen işlemleri kapsar. Bu grupların hiçbirinde hedef etiketi çelişmedi. Satırlar silinmedi. Aynı gruptaki işlemler bölmenin aynı tarafına konularak gözlenen işlem sıklıkları korundu.')
section(2,True)
head('IV. DENEY TASARIMI')
p('İlk ayrım tüm ön işleme adımlarından önce yapıldı. Sabit 42 tohumuyla oluşturulan tabakalı grup bölmesinde 227.773 işlem geliştirmeye, 57.034 işlem nihai teste ayrıldı. Geliştirme verisinde 394, test verisinde 98 dolandırıcılık vardı. Grup, kart numarası veya müşteri kimliğine dayanmaz. Bir grup aynı 29 özelliğin sayısal izini taşıyan kayıtlardan oluşur. Her tekrarda model öğrenme, eşik belirleme, dış doğrulama ve test bölmelerinin bütün satırları kapsadığı ve aralarında ortak özellik grubu bulunmadığı denetlendi.')
p('Geliştirme bölümünde 11, 23, 37, 53 ve 71 tohumlarıyla beş ayrı eğitim–doğrulama ayrımı üretildi. Her ayrımda beş parçalı tabakalı grup bölücüsünün ilk dış parçası doğrulamaya ayrıldı. Kalan kayıtlar yeniden ayrılarak model öğrenme ve iç eşik seçimi kümeleri oluşturuldu. Bu işlem beş katın tamamında sırayla test edilen çapraz doğrulamadan farklıdır. Doğrulama kümeleri tekrarlar arasında örtüşebilir. Karşılaştırmayı adil tutmak için her tekrarda aynı öğrenme işlemleri bütün yöntemlere sunuldu.')
p('Temel lojistik regresyonda standartlaştırma parametreleri yalnızca öğrenme altkümesinde hesaplandı. Lojistik regresyon L-BFGS ile en çok 1.200 yinelemede uyarlandı. Ağırlıklı sürümde sınıf sıklığıyla ters orantılı ağırlıklar kullanıldı. SMOTE için beş komşu ve azınlık/çoğunluk hedef oranı 0,10 seçildi. Rastgele alt örneklemede (RUS) aynı hedef oran korundu. Ölçekleme ve örnekleme, scikit-learn [6] ve imbalanced-learn [7] iş akışlarının eğitim adımları içinde uygulandı. Doğrulama ve test verisi doğal sınıf dağılımını korudu.')
p('Eşik deneyinde temel lojistik regresyonun ürettiği skorlar yeniden kullanıldı. İç doğrulamada F1’i en yüksek yapan değer seçildi. Eşitlikte en yüksek eşik alındı. Dış doğrulama etiketleri bu karara katılmadı. Diğer yöntemlerde 0,5 eşiği kullanıldı. Random Forest 70 ağaç, en çok 12 derinlik, yaprak başına en az iki örnek ve her bootstrap örnekleminde dengelenmiş sınıf ağırlıkları ile eğitildi.')
head('V. ÖLÇÜTLER VE MODEL SEÇİMİ')
p('Kesinlik, doğru dolandırıcılık alarmlarının bütün alarmlara oranıdır. Duyarlılık, yakalanan dolandırıcılıkların bütün dolandırıcılıklara oranıdır. F1 bu iki oranın harmonik ortalamasıdır. AP, skor eşiği değiştikçe oluşan duyarlılık artışlarını ilgili kesinlik değerleriyle ağırlıklandırır. PR eğrisinin doğrusal ara değerlerle hesaplanan trapez alanından farklı bir niceliktir [9], [12]. ROC-AUC ise rastgele bir pozitifin rastgele bir negatiften daha yüksek puanlanmasına ilişkin sıralama ölçüsüdür.')
p('Seçim ölçütü beş dış doğrulamanın ortalama AP değeriydi. Eşitlikte doğrulama F1 ortalaması kullanıldı. Model seçimindeki iyimserlik riskini azaltmak üzere [4] son test yalnızca seçilen yöntem ve başlangıçta belirlenen temel model için kullanıldı. Nihai modeller, geliştirme verisinin sabit 2026 tohumlu öğrenme kısmında yeniden eğitildi. Her iki nihai karar kuralının eşiği 0,5 idi. Testteki hata sayıları modelin sonraki bir sürümünü ayarlamak için kullanılmadı.')
section(1,True)
head('VI. GELİŞTİRME BULGULARI')
tab('TABLO I. Beş dış doğrulamada ortalama ± örneklem standart sapması',['Yöntem','AP','Kesinlik','Duyarlılık','F1','ROC-AUC'],[[names[r['model']]]+[ms(r,k) for k in ['ap','precision','recall','f1','roc_auc']] for r in summary])
p('Tablo I’de yöntemler ortalama AP’ye göre sıralanmıştır. Eşik seçimi yalnızca ikili kararları değiştirdiği için temel lojistik regresyon ve eşik seçilmiş sürüm aynı AP ve ROC-AUC değerlerine sahiptir. “Ağırlık” sınıf sıklığına dayalı eğitim ağırlığını, RUS rastgele alt örneklemeyi gösterir.')
seeds=sorted({int(r['seed']) for r in raw});lookup={(int(r['seed']),r['model']):r for r in raw}
tab('TABLO II. Bölme bazında doğrulama sonuçları',['Tohum','Doğrulama n','Pozitif n','LR AP','RF AP','RF − LR AP','LR F1 eşiği'],[[s,lookup[s,'LR_base']['validation_n'],lookup[s,'LR_base']['validation_frauds'],num(lookup[s,'LR_base']['ap']),num(lookup[s,'RF_balanced']['ap']),num(float(lookup[s,'RF_balanced']['ap'])-float(lookup[s,'LR_base']['ap'])),num(lookup[s,'LR_threshold_F1']['threshold'])] for s in seeds])
section(2)
p('Örnekleme yöntemleri, 0,5 eşiğinde temelden daha yüksek duyarlılık üretti. SMOTE ile ortalama duyarlılık 0,819’a yükselirken kesinlik 0,339’a düştü. Alt örneklemede duyarlılık 0,833, kesinlik 0,240 oldu. İki yöntemin ortalama AP değeri temel lojistik regresyonun altında kaldı. Dolayısıyla daha çok dolandırıcılığın yakalanması burada sıralamanın bütünüyle iyileştiğini göstermiyor. Sentetik veri miktarı veya alt örnekleme oranı için yalnızca tek ayar sınandığından çıkarım bu iki uygulamayla sınırlıdır.')
p('Sınıf ağırlıklı lojistik regresyon 0,892 ile en yüksek ortalama duyarlılığı verdi. Kesinliği 0,054 oldu. Bu sonuç, incelemeye gönderilen işlemlerin büyük bölümünün normal olduğu bir çalışma noktasına karşılık gelir. Önerideki sabit yanlış alarm düzeyinde duyarlılık sorusu için modellerin dış doğrulamada aynı alarm bütçesine getirilmesi gerekirdi. Mevcut sonuçlar uygulanan eşiklerde alarm yüküyle birlikte yorumlanabilir.')
p('Yalnızca lojistik regresyon eşiğinin değiştirilmesi ortalama duyarlılığı 0,616’dan 0,716’ya çıkardı. Kesinlik 0,887’den 0,781’e inerken F1 ortalaması 0,725’ten 0,742’ye yükseldi. Tablo II’deki eşikler bağımsız iç doğrulamalarda seçildi. Bir işletme eşiği için F1 dışında günlük inceleme kapasitesi ve işlem başına hata maliyeti de gereklidir.')
p('Random Forest beş tekrarın her birinde temel modelden daha yüksek AP elde etti. Eşleştirilmiş AP farkının ortalaması 0,0582, standart sapması 0,0444 oldu. Beş tekrarlı iki taraflı keşifsel Wilcoxon değerinin 0,0625 olması, küçük örneklem ve örtüşen bölmeler ışığında yorumlanmalıdır. Aynı veri kümesinden türetilen bölmeleri ayrı veri kümeleri gibi saymak bağımsızlık varsayımını zedeler [3], [5].')
section(1,True)
head('VII. NİHAİ TEST VE TARTIŞMA')
tab('TABLO III. 57.034 işlemde son test, eşik 0,5',['Yöntem','TP','FP','FN','TN','AP','Kesinlik','Duyarlılık','F1'],[[names[r['model']]]+[r[k] for k in ['tp','fp','fn','tn']]+[num(r[k]) for k in ['ap','precision','recall','f1']] for r in final])
section(2)
image('pr_test_LR_base.png',3.28)
p('Şekil 1. Temel lojistik regresyonun son testteki kesinlik–duyarlılık eğrisi. Eğri, karar eşiği boyunca kesinliğin nasıl değiştiğini gösterir.')
image('pr_test_RF_balanced.png',3.28)
p('Şekil 2. Sınıf ağırlıklı Random Forest için aynı test kümesindeki kesinlik–duyarlılık eğrisi. İki grafikte de eksenler 0–1 ölçeğindedir.')
p('Temel modelin 72 alarmının 59’u doğruydu. Random Forest 92 alarm verdi ve bunların 79’u doğruydu. İki modelin de 56.936 normal işlem içindeki yanlış pozitif sayısı 13’tür. Gözlenen yanlış pozitif oranı iki yöntemde de yaklaşık %0,0228 oldu. Random Forest bu çalışma noktasında 20 ek dolandırıcılık yakaladı. Alarm sayıları ayrı ayrı sayıldığı için iki modelin aynı 13 normal işlemi işaretlediği çıkarılamaz.')
p('Random Forest için test AP değeri 0,8594, temel model için 0,7755’tir. ROC-AUC sırası tersine döner. Temel modelin değeri 0,9802, Random Forest’ın değeri 0,9701’dir. Bu sıralama farkı önemlidir. Nadir pozitiflerin üst sıralardaki yoğunluğuna odaklanan AP, ROC-AUC ile aynı değerlendirme sorusunu yanıtlamaz. Model karşılaştırması için hangi ölçütün kullanılacağı test sonuçları görülmeden belirlenmiştir.')
p('Özdeş özellik grupları üzerinden 200 yeniden örneklemenin AP için %2,5 ve %97,5 yüzdelikleri temel modelde 0,662–0,870, Random Forest’ta 0,770–0,930 oldu. Aralıklar eldeki test örneğindeki oynaklığı betimler. Bankalar veya dönemler arası değişimi kapsamaz. İki ayrı aralığın örtüşmesine bakarak modeller arasındaki farkın istatistiksel anlamlılığı belirlenemez.')
p('Kaçırılan dolandırıcılığa on, yanlış alarma bir birim verilen varsayımsal puan temel modelde 403, Random Forest’ta 203 oldu. İki modelin yanlış alarmları eşit olduğundan aradaki fark 20 kaçırılmış işleme verilen ağırlıktan kaynaklanır. Tutar, geri kazanım, müşteri etkisi ve inceleme maliyeti gözlenmediği için bu puan parasal tasarruf olarak yorumlanamaz.')
section(2,True)
head('VIII. SONUÇ VE GEÇERLİK SINIRLARI')
p('Bu veri ve protokol altında AP ile seçilen sınıf ağırlıklı Random Forest, son testte temel lojistik regresyondan daha yüksek duyarlılık ve F1 elde etti. Lojistik regresyon içinde en açık ayrım, eşik seçiminin skorlara müdahale etmeden kesinlik ile duyarlılık arasındaki dengeyi değiştirmesiydi. Örnekleme ve sınıf ağırlığı ise seçilen ayarlarda duyarlılığı artırırken yanlış alarm yükünü yükseltti. Bir yöntem seçilirken sıralama başarısı ile uygulanacak karar kuralı birlikte belirtilmelidir.')
p('İki günlük örneklem, sonraki dönemlerin dolandırıcılık örüntülerini temsil etmeyebilir. Kart ve müşteri kimliği gözlenmediği için aynı kişinin birbirinden farklı işlemleri farklı bölmelere düşmüş olabilir. Sağlanan PCA bileşenleri ham girdiler olmadan her eğitim bölmesinde yeniden hesaplanamaz. Random Forest için ağırlıksız bir kol ve tüm modellerde tüm örnekleme kombinasyonları çalışılmadı. Sonuçlar yalnızca uygulanan altı yöntemi karşılaştırır. Gelecekte ileri zamanlı bir test ve önceden tanımlanmış inceleme bütçesiyle aynı sorular yeniden sınanabilir.')
head('YENİDEN ÜRETİLEBİLİRLİK VE ETİK')
p('Deneylerde NumPy 2.3.5, pandas 2.3.3, scikit-learn 1.7.2 ve imbalanced-learn 0.14.0 kullanıldı. Bölme indeksleri, veri özeti, yöntem başına tekrar sonuçları ve final karışıklık matrisleri çalışma dosyalarında saklanmıştır. Verinin kaynağı ULB/Worldline açık kredi kartı dolandırıcılığı veri kümesidir. Çıktılar toplulaştırılmıştır. Üretken yapay zekâ kod düzeltme, deney yürütme, kaynak tarama ve bildiri metninin hazırlanmasında kullanılmıştır.')
head('KAYNAKLAR')
refs=[
'N. V. Chawla, K. W. Bowyer, L. O. Hall ve W. P. Kegelmeyer, “SMOTE: Synthetic Minority Over-sampling Technique,” JAIR, c. 16, ss. 321–357, 2002.',
'A. Fernández, S. García, F. Herrera ve N. V. Chawla, “SMOTE for Learning from Imbalanced Data: Progress and Challenges, Marking the 15-year Anniversary,” JAIR, c. 61, ss. 863–905, 2018.',
'J. Demšar, “Statistical Comparisons of Classifiers over Multiple Data Sets,” JMLR, c. 7, ss. 1–30, 2006.',
'G. C. Cawley ve N. L. C. Talbot, “On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation,” JMLR, c. 11, ss. 2079–2107, 2010.',
'Y. Bengio ve Y. Grandvalet, “No Unbiased Estimator of the Variance of K-Fold Cross-Validation,” JMLR, c. 5, ss. 1089–1105, 2004.',
'F. Pedregosa vd., “Scikit-learn: Machine Learning in Python,” JMLR, c. 12, ss. 2825–2830, 2011.',
'G. Lemaître, F. Nogueira ve C. K. Aridas, “Imbalanced-learn: A Python Toolbox to Tackle the Curse of Imbalanced Datasets in Machine Learning,” JMLR, c. 18, no. 17, ss. 1–5, 2017.',
'L. Breiman, “Random Forests,” Machine Learning, c. 45, ss. 5–32, 2001.',
'T. Saito ve M. Rehmsmeier, “The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets,” PLOS ONE, c. 10, e0118432, 2015.',
'A. Dal Pozzolo, O. Caelen, R. A. Johnson ve G. Bontempi, “Calibrating Probability with Undersampling for Unbalanced Classification,” IEEE SSCI, ss. 159–166, 2015.',
'A. Dal Pozzolo, G. Boracchi, O. Caelen, C. Alippi ve G. Bontempi, “Credit Card Fraud Detection: A Realistic Modeling and a Novel Learning Strategy,” IEEE TNNLS, c. 29, ss. 3784–3797, 2018.',
'J. Davis ve M. Goadrich, “The Relationship Between Precision-Recall and ROC Curves,” ICML, ss. 233–240, 2006.',
'C. Elkan, “The Foundations of Cost-Sensitive Learning,” IJCAI, ss. 973–978, 2001.',
'H. He ve E. A. Garcia, “Learning from Imbalanced Data,” IEEE TKDE, c. 21, ss. 1263–1284, 2009.',
'Z. C. Lipton, C. Elkan ve B. Naryanaswamy, “Optimal Thresholding of Classifiers to Maximize F1 Measure,” ECML PKDD, ss. 225–239, 2014.']
for i,t in enumerate(refs,1):
    z=d.add_paragraph(); z.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT;z.paragraph_format.space_after=Pt(2)
    z.add_run(f'[{i}] {t}').font.size=Pt(8.5)
d.core_properties.author='Sevim Serra Biberoğlu'
from docx.enum.text import WD_BREAK
import re
def anchor(prefix):
    return next(a for a in d.paragraphs if a.text.startswith(prefix))
def before(prefix, element):
    anchor(prefix)._p.addprevious(element)
def split(prefix):
    q=d.add_paragraph();q.paragraph_format.space_after=Pt(0);q.add_run().add_break(WD_BREAK.COLUMN)
    before(prefix,q._p)
def note(prefix, content):
    before(prefix,p(content)._p)
def plate(prefix,name,caption):
    q=d.add_paragraph();q.alignment=WD_ALIGN_PARAGRAPH.CENTER
    q.add_run().add_picture(str(out/name),width=Inches(3.28));before(prefix,q._p)
    note(prefix,caption)
split('I. GİRİŞ')
plate('I. GİRİŞ','ap_karsilastirma.png','Şekil 1. Beş geliştirme tekrarının özeti. Nokta ortalamayı, yatay çizgi bir örneklem standart sapmasını gösterir. Altı yöntemin aynı bölmelerde değerlendirilmesi eşleştirilmiş karşılaştırmayı mümkün kılar.')
split('III. VERİ VE KAYIT')
note('III. VERİ VE KAYIT','Literatürdeki farklı veri kümelerine ait performans değerleri bu deneyin karşılaştırma tablosuna taşınmadı. Sınıf oranı değiştiğinde aynı duyarlılık ve yanlış pozitif oranı farklı kesinlik değerleri verebilir. Bu nedenle karşılaştırmanın paydaları olarak dış doğrulamadaki pozitif sayıları ve son testteki toplam işlem sayısı ayrıca verildi.')
note('284.315 normal','Verinin bütünlüğünü izlemek için CSV dosyasının SHA-256 özeti kaydedildi. Bu işlem, sonraki bir çalıştırmada aynı girdi dosyasının kullanılıp kullanılmadığını kontrol etmeyi sağlar. Özellik gruplarının hesaplanması ise farklı bir soruyu, bir modelin görebileceği özdeş girdilerin bölme sınırını aşıp aşmadığını ele alır.')
note('284.315 normal','Özdeş girdilere sahip birden çok işlemi içeren 5.149 grup vardır. Bu gruplarda toplam 14.293 satır yer alır. En büyük grup 77 satır içerir. Grup içindeki ilk işlem saklanıp diğerleri sayıldığında aşağıda verilen 9.144 tekrar elde edilir. Grup düzeyindeki sayım, aynı işlem izini model öğrenirken ve değerlendirirken iki kez görme riskini görünür kılar.')
note('284.315 normal','İşlem tutarının normal sınıftaki ortancası 22,00, dolandırıcılık sınıfındaki ortancası 9,25’tir. Ortalamalar ise sırasıyla 88,29 ve 122,21’dir. Ortalamanın yönü ile ortancanın yönünün ayrılması, yalnızca “yüksek tutar” kuralına dayalı bir açıklamayı desteklemez. İşlem tutarı diğer 28 bileşenle birlikte kullanılmıştır.')
split('Eşik deneyinde')
note('Eşik deneyinde','Örneğin ilk tohumda model öğrenme altkümesi 145.809, iç doğrulama altkümesi 36.517 ve dış doğrulama altkümesi 45.447 işlem içerdi. Dış doğrulamada yalnızca 75 pozitif işlem vardı. Bir tek dolandırıcılığın yakalanması veya kaçırılması bu bölmede duyarlılığı yaklaşık 1,33 yüzde puan değiştirebilir. Bu yüzden tek koşudaki küçük farklara dayanarak model seçilmedi.')
split('Yalnızca lojistik')
plate('Random Forest beş','ap_tekrarlar.png','Şekil 2. Aynı beş doğrulama kümesinde AP. İki eğri arasındaki düşey uzaklık eşleştirilmiş farkı gösterir.')
note('Sınıf ağırlıklı lojistik','Temel lojistik regresyon dış doğrulama başına ortalama 6,0 yanlış alarm verirken bu sayı SMOTE ile 120,8 ve alt örnekleme ile 212,2 oldu. F1 eşiği seçilmiş lojistik regresyon ortalama 15,6 yanlış alarm üretti. Bunlar yaklaşık 45 bin işlem içeren dış doğrulama kümelerinin tekrar başına ortalamalarıdır.')
anchor('Şekil 1. Temel lojistik').text=anchor('Şekil 1. Temel lojistik').text.replace('Şekil 1.','Şekil 3.')
anchor('Şekil 2. Sınıf ağırlıklı').text=anchor('Şekil 2. Sınıf ağırlıklı').text.replace('Şekil 2.','Şekil 4.')
# Move interpretation beside the corresponding curves.
b=anchor('Şekil 4. Sınıf ağırlıklı')._p.getprevious()
b.addprevious(anchor('Temel modelin 72')._p)
b.addprevious(anchor('Random Forest için test AP')._p)
q=d.add_paragraph();q.add_run().add_break(WD_BREAK.COLUMN);b.addprevious(q._p)
split('KAYNAKLAR')
# IEEE references follow their first appearance in the paper.
order=[]
for a in d.paragraphs:
    if a.text=='KAYNAKLAR': break
    for digit in re.findall(r'\[(\d+)\]',a.text):
        if int(digit) not in order: order.append(int(digit))
assert set(order)==set(range(1,16))
for a in d.paragraphs:
    if a.text=='KAYNAKLAR':break
    for run in a.runs:
        if '[' in run.text:run.text=re.sub(r'\[(\d+)\]',lambda m:f'[{order.index(int(m[1]))+1}]',run.text)
for index,a in enumerate([a for a in d.paragraphs if re.match(r'^\[\d+\] ',a.text)]):
    a.runs[0].text=f'[{index+1}] '+refs[order[index]-1]
d.core_properties.title='Aşırı Dengesiz Veride Kredi Kartı Dolandırıcılığı Tespiti'
d.save(out/'12_hafta_IEEE_bildiri.docx')
