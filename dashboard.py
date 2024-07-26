#Mengimport library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')


#Menyiapkan dataframe
##Dataframe by daily rental
def create_daily_rental_df(df):
    daily_rental_df = df.resample(rule='D', on='dteday').agg({
        "instant": "nunique",
        "cnt": "sum"
    })
    daily_rental_df = daily_rental_df.reset_index()
    daily_rental_df.rename(columns={
        "instant": "records",
        "cnt": "count"
    }, inplace=True)
    
    return daily_rental_df

##Dataframe season_day_df
def create_season_day_df(df):
    season_day_df = df.groupby("season").cnt.sum().sort_values(ascending=False).reset_index()
    return season_day_df

##Dataframe by year
def create_yr_day_df(df):
    yr_day_df = df.groupby("yr").cnt.sum().sort_values(ascending=False).reset_index()
    return yr_day_df

##dataframe by work day
def create_work_day_df(df):
    work_day_df = df.groupby("workingday").cnt.sum().sort_values(ascending=False).reset_index()
    return work_day_df

#Dataframe rfm (recently, frequency, monetery)
def create_rfm_df(df):
    rfm_df = df.groupby(by="instant", as_index=False).agg({
    "dteday": "max",  # mengambil tanggal sewa terakhir
    "registered": "sum",  # menghitung total dari jumlah penyewa yang sudah registrasi
    "cnt": "sum"  # menghitung jumlah total sewa
    })
    rfm_df.columns = ["records", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"]).dt.date
    recent_date = pd.to_datetime(df["dteday"]).dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

#Memanggil dataframe
all_df = pd.read_csv("all_data.csv")
all_df

#Mengurutkan order data dan memastikan tipenya sudah bertipe datetime
datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

#Membuat komponen filter dg start date dan end date, membuat sidebar dan logo perusahaan
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()
 
with st.sidebar:
    image_path = ("img_106157_bg_shutterstock_609554810.png")
    st.image(image_path)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date])

#Menyimpan filter data   
main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]

#Menyiapkan berbagai dataframe
daily_rental_df = create_daily_rental_df(main_df)
season_day_df = create_season_day_df(main_df)
yr_day_df = create_yr_day_df(main_df)
work_day_df = create_work_day_df(main_df)
rfm_df = create_rfm_df(main_df)

#Melengkapi dashboard dengan visualisasi
st.header('Mobike Rental Cycles :sparkles:')
st.subheader('Daily Rental')

#Menampilkan total 
col1 = st.columns(1)[0]

with col1:
    total_rental = daily_rental_df['count'].sum()
    st.metric("Total rental", value=total_rental)


fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rental_df["dteday"],
    daily_rental_df["count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

#Demografi berdasarkan season, year, work day
st.subheader("Track Records of Rental Bike Demographics")
 
col1, col2 = st.columns(2)
 
with col1:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        y="cnt", 
        x="season",
        data=season_day_df.sort_values(by="cnt", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Total Rental Bikes by Season", loc="center", fontsize=15)
    ax.set_ylabel("Count")
    ax.set_xlabel("Season")
    ax.tick_params(axis='x', labelsize=12)
    st.pyplot(fig)
 
with col2:
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#D3D3D3", "#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        y="cnt", 
        x="yr",
        data=yr_day_df.sort_values(by="cnt", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Total Rental Bikes by Year (2011-2012)", loc="center", fontsize=15)
    ax.set_ylabel("Count")
    ax.set_xlabel("Year")
    ax.tick_params(axis='x', labelsize=12)
    st.pyplot(fig)
 
work_day_df = pd.DataFrame({
    'workingday': ['workingday', 'holiday'],
    'cnt': [2292410, 1000269]
})

workingday = work_day_df['workingday']
cnt = work_day_df['cnt']

colors = ['green', 'yellow']

fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(cnt, labels=workingday, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
ax.set_title("Number of Rental Bikes by Working Day and Holiday", fontsize=16)
st.pyplot(fig)

#Informasi RFM
st.subheader("Best Records of Rental Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = round(rfm_df.monetary.mean(), 3)
    st.metric("Average Count of Rental", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

# Recency plot
sns.barplot(y="recency", x="records", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel("Recency Days")
ax[0].set_xlabel("ID Records")
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)

# Frequency plot
sns.barplot(y="frequency", x="records", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel("Frequency Count of Registered Users")
ax[1].set_xlabel("ID Records")
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

# Monetary plot
sns.barplot(y="monetary", x="records", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel("Count Value")
ax[2].set_xlabel("ID Records")
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)

plt.suptitle("Best Records Day Based on RFM Parameters (instant)", fontsize=20)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Selly R 2024')
