import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

df_= pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.head()

### Veri setimizi inceleyelim ###
df.shape
df.describe().T

### Eksik Verileri çıkaralım ###
df.isnull().sum()
df.dropna(inplace=True)
df.shape

### İade edilen ürünleri veri setinden çıkaralım ###

df = df[~ df["Invoice"].str.contains("C",na=False)]

### Müşterilerin harcadığı toplam harcamayı veri setimize ekleyelim ###
df["TotalPrice"] = df["Quantity"] * df["Price"]

### RFM Metriklerinin oluşturulması ###

df["InvoiceDate"].max()
today_date = dt.datetime(2011,12,11)


rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda x: (today_date - x.max()).days,
                                    "Invoice": lambda y: y.nunique(),
                                    "TotalPrice": lambda z: z.sum()})

rfm.columns = ["recency","frequency","monetary"]
rfm = rfm[rfm["monetary"]>0]

### RFM Skorlarının Oluşturulması ###

#pd.options.mode.chained_assignment = None

rfm["recency_score"] = pd.qcut(rfm["recency"], 5 , labels=[5,4,3,2,1])

rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"),5, labels=[1,2,3,4,5])

rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1,2,3,4,5])

rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str)+rfm["frequency_score"].astype(str))
rfm.head()

### RFM Skorlarıyla Segmentlerin Oluşturulması ###

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

rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)

### Segmentasyon tamamlandı. Segmentleri analiz ederek pazarlama stratejimizi oluşturabiliriz ###

rfm.groupby("segment").agg(["mean", "count"])

