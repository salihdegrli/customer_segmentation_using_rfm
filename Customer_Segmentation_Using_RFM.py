# Columns:
# 0-Invoice – Fatura Numarası (Eğer bu kod C ile başlıyorsa işlemin iptal edildiğini ifade eder.)
# 1-StockCode – Ürün kodu (Her bir ürün için eşsiz numara.)
# 2-Description – Ürün ismi
# 3-Quantity – Ürün adedi (Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.)
# 4-InvoiceDate – Fatura tarihi
# 5-Price – Fatura fiyatı (Sterlin)
# 6-Customer ID – Eşsiz müşteri numarası
# 7-Country – Ülke ismi

import datetime as dt
import pandas as pd

pd.set_option('display.max_columns', None)  # bütün sütunları göster
pd.set_option('display.max_rows', None)  # bütün satırları göster
pd.set_option('display.float_format', lambda x: '%.2f' % x)  # virgülden sonra 2 basamak göster

"""GOREV1:"""
# 1. Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.
# 2. Veri setinin betimsel istatistiklerini inceleyiniz
# 3. Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
online_retail_II = pd.read_excel("hafta3/odev1/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = online_retail_II.copy()


def check_df(dataframe):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### info #####################")
    print(dataframe.info())
    print("##################### Head #####################")
    print(dataframe.head())
    print("##################### Tail #####################")
    print(dataframe.tail())
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### total canceled transaction #####################")
    print(dataframe.loc[df["Invoice"].astype(str).str.contains("C", na=False)].count()["Invoice"])
    print("##################### Quantiles #####################")
    print(dataframe.quantile([0, 0.05, 0.50, 0.95, 0.99, 1]).T)
    print("##################### Describe #####################")
    print(dataframe.describe().T)
    print("##################### nunique #####################")
    print(dataframe.nunique())


check_df(df)

print("##################### Total Invoice #####################")
print(df["Invoice"].nunique())

# 4. Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
df.dropna(inplace=True)

# 5.
print("##################### Eşsiz ürün sayısı kaçtır? #####################")
df["Description"].nunique()

# 6.
print("##################### Hangi üründen kaçar tane vardır? #####################")
df["Description"].value_counts().head()

# 7.En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.
print("######### en cok sipariş edilen 5 ürün ##########")
df.groupby("Description", as_index=False).agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

# 8. Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
print("##################### iptal edilen işlemleri çıkar #####################")
df = df[~df["Invoice"].astype(str).str.contains("C", na=False)]
check_df(df)

# 9. Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
print("##################### total price oluştur #####################")
df["TotalPrice"] = df["Price"] * df["Quantity"]
df.head()

"""
GOREV2: RFM metriklerinin hesaplanması
1-Recency, Frequency ve Monetary tanımlarını yapınız
2-Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile hesaplayınız.
3-Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.
4-Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.
"""

"""
Task
--------------
**Recency (yenilik): müşterinin en son satın aldığı tarihtir. 
Bugünden en son alışveriş yaptığı tarih çıkarılarak sonuç güne(duruma göre haftaya) çevriliri. 
Elde edilen metrik gün ya da hafta cinsindendir.
Bu dataset için bugünü temsit eden bir date oluşturularak ve InvoiceDate değişkeni kullanılarak elde edilir.

**Frequency (Sıklık): müşterinin satın alma sıklığıdır. 
elde edilen metriğin birimi adettir
Bu dataset için unique Invoice'ların  saydırılmasıyla elde edilir.

**Monetary (Parasal Değer): Müşterinin satın alma neticesinde bıraktığı parasal karşılık. 
Bu veri setinde TotalPrice değişkeni ile hesaplanır

example:
---------------
Customer         R          F       M
cust_1          40        250     5600

Recency = cust_1 40 gün önce alışveriş yapmış
frequency = cust_1 toplamda 250 adet alışveriş yapmış
monetary = cust_1 toplamda 5600 (£,$,TL) para bırakmış 
"""

today_date = df["InvoiceDate"].max() + dt.timedelta(days=2)  # iki gün sonrası garanti olması açısından seçildi

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                     'Invoice': lambda num: num.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
# 'InvoiceDate': lambda date: (today_date - date.max())
# burada ifade edilen "ilgili müşterinin son alışveriş tarihinden bugünü çıkar"
# max methodunun kullanım amacı bu

rfm.columns = ["Recency", "Frequency", "Monetary"]
rfm.head(20)

rfm.drop(rfm[rfm["Monetary"] == 0].index, inplace=True)
print(rfm[rfm["Monetary"] == 0])

print(rfm.describe().T)
"""
Görev 3: RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi

1-Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
2-Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.
3-Oluşan 2 farklı değişkenin değerini tek bir değişken olarak ifade ediniz ve RFM_SCORE olarak kaydediniz.
"""

# RECENCY değeri müşterinin yeniliğini ifade ettiği için diğer metriklerin aksine en yeni 5 en eski 1 olcak şekilde skorlara ayrılmıştır
rfm["recency_score"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['Frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))
rfm.head()
print(rfm.describe().T)

rfm[rfm["RF_SCORE"] == "51"].head()  # new_customers
rfm[rfm["RF_SCORE"] == "33"].head()  # need_attention

"""
GOREV4: RFM skorlarının segment olarak tanımlanması
1-Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlamaları yapınız.
2-Aşağıdaki seg_map yardımı ile skorları segmentlere çeviriniz.
"""

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)
rfm.head()

"""OREV5: Aksiyon zamanı!
1-Önemli bulduğunuz 3 segmenti seçiniz. Bu üç segmenti;
2-Hem aksiyon kararları açısından,
3-Hem de segmentlerin yapısı açısından (ortalama RFM değerleri) yorumlayınız.
4-'Loyal Customers' sınıfına ait customer ID'leri seçerek excel çıktısını alınız.
"""
rfm[["segment", "Recency", "Frequency", "Monetary"]].groupby("segment").agg(["count", "mean"])

# Dikkat gerektiren sınıfların id'lerini aldık. çünkü indexlerde id'ler vardı.
new_df = pd.DataFrame()
new_df["cant_loose_id"] = rfm[rfm["segment"] == "cant_loose"].index
new_df.head()
print(new_df.describe().T)
new_df.to_excel("hafta3/odev1/cant_loose.xlsx")
