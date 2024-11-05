import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set_theme(style='dark')

# Menyiapkan data yang dibutuhkan
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
        
    return daily_orders_df
    
def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({
        "payment_value": "sum"
    })
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={
        "payment_value": "total_spend"
    }, inplace=True)

    return sum_spend_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

    return sum_order_items_df

def review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)
    most_common_score = review_scores.idxmax()

    return review_scores, most_common_score

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

    return bystate_df, most_common_state

def create_order_status(df):
    order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
    most_common_status = order_status_df.idxmax()

    return order_status_df, most_common_status

# Title
st.header("E-Commerce Dashboard :convenience_store:")

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("https://raw.githubusercontent.com/ihsanuramdan/dicoding/refs/heads/main/all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

# Sidebar
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    # Title
    st.title("Ihsanu Ramdan M.")

    # Logo Image
    st.image("dashboard/logo.png")

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_spend_df = create_sum_spend_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
review_score, common_score = review_score_df(main_df)
state, most_common_state = create_bystate_df(main_df)
order_status, common_status = create_order_status(main_df)

# Introduction
st.markdown(
    '''
    Data yang digunakan adalah "E-Commerce Public Dataset" yang disediakan oleh Dicoding Indonesia
    '''
    )


# Daily Orders
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "BRL", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

with st.expander("Penjelasan Grafik"):
    st.write('''
            - Total jumlah pemesanan dalam rentang waktu September 2016 s.d. September 2018 adalah 99280 pesanan.
            - Tren jumlah pemesanan cenderung meningkat tiap harinya dengan ada lonjakan pada tanggal-tanggal tertentu.
             ''')

# Customer Spend Money
st.subheader("Customer Spend Money")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "BRL", locale="id_ID")
    st.markdown(f"Total Spend: **{total_spend}**")

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "BRL", locale="id_ID")
    st.markdown(f"Average Spend: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    sum_spend_df["order_approved_at"],
    sum_spend_df["total_spend"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

with st.expander("Penjelasan Grafik"):
    st.write('''
            - Total jumlah uang yang dibelanjakan di e-commerce dalam rentang waktu September 2016 s.d. September 2018 adalah R$20.542.122,89.
            - Tren jumlah uang yang dibelanjakan di e-commerce cenderung meningkat tiap harinya dengan ada lonjakan pada tanggal-tanggal tertentu.
             ''')

# Order Items

st.subheader("Order Items and Status")
tab1, tab2, tab3 = st.tabs(["Order Items", "Order Status","Deliver Status"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        total_items = sum_order_items_df["product_count"].sum()
        st.markdown(f"Total Items: **{total_items}**")

    with col2:
        avg_items = sum_order_items_df["product_count"].mean()
        st.markdown(f"Average Items: **{avg_items}**")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

    colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(10), palette=colors, hue="product_category_name_english", legend=False, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Number of Sales", fontsize=30)
    ax[0].set_title("Produk paling banyak terjual", loc="center", fontsize=50)
    ax[0].tick_params(axis ='y', labelsize=35)
    ax[0].tick_params(axis ='x', labelsize=30)

    sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(10), hue="product_category_name_english", palette=colors, legend=False, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Number of Sales", fontsize=30)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=50)
    ax[1].tick_params(axis='y', labelsize=35)
    ax[1].tick_params(axis='x', labelsize=30)

    st.pyplot(fig)

    with st.expander("Penjelasan Grafik"):
        st.write('''
                - Produk yang paling banyak terjual adalah dalam kategori **bed_bath_table**
                - Produk yang paling sedikit terjual adalah dalam kategori **security_and_services**
                ''')

with tab2:
    common_status_ = order_status.value_counts().index[0]
    st.markdown(f"Most Common Order Status: **{common_status_}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=order_status.index,
                y=order_status.values,
                order=order_status.index,
                hue=order_status.index,
                legend=False,
                palette=["#068DA9" if score == common_status else "#D3D3D3" for score in order_status.index]
                )
    
    plt.title("Order Status", fontsize=15)
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

    with st.expander("Penjelasan Grafik"):
        st.write('''
                - Hampir seluruh pemesanan telah di kirim. Sedikit diantaranya masih dalam proses pengiriman (Shipping)
                ''')

with tab3:
    deliverStatus_df = all_df.groupby(by="deliver_status").customer_id.nunique().sort_values(ascending=False).reset_index()
    deliveryTop2_df = deliverStatus_df[:2].copy()
    deliveryOthers_df = pd.DataFrame(data = {
        'deliver_status' : ['others'],
        'customer_id' : [deliverStatus_df['customer_id'][2:].sum()]
        })
    deliverStatus2_df = pd.concat([deliveryTop2_df, deliveryOthers_df]).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(12,6))
    
    plt.pie(
        x = deliverStatus2_df['customer_id'],
        labels = deliverStatus2_df['deliver_status'],
        autopct='%1.2f%%',
        explode= (0.1,0,0),
        )

    plt.title(
        label="Delivery Status Distribution", 
        fontdict={"fontsize":16},
        pad=10
        )
    
    st.pyplot(fig)    

    with st.expander("Penjelasan Grafik"):
        st.write('''
                - Pengiriman yang tepat waktu angkanya hampir mencapai 90%, sedangkan yang terlambat tidak sampai 8%
                ''')

# Review Score
st.subheader("Review Score")
col1,col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score}**")

with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index, 
            y=review_score.values, 
            order=review_score.index,
            hue_order=review_score.index,
            hue=review_score.index,
            legend= False,
            palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index]
            )

for i in range(len(review_score.index)):
        plt.text(i,review_score.values[i],review_score.values[i],ha='center')

plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)

with st.expander("Penjelasan Grafik"):
    st.write('''
            - Rata-rata penilaian dari seluruh toko di aplikasi e-commerce ini adalah 4.02
            - Customer yang memberikan rating 5 memiliki data terbanyak daripada rating yang lainnya. Namun demikian perlu juga untuk melihat review yang memiliki rating 1 dengan tujuan membuat perbaikan
             ''')

st.subheader("Customer Demographic")
tab1, tab2 = st.tabs(["State", "City"])

with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"Most Common State: **{most_common_state}**")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, 
                data=state,
                hue=state.customer_state.value_counts().index,
                legend=False,
                palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]
                    )
    
    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)

    with st.expander("Penjelasan Grafik"):
        st.write('''
                - Jumlah pembeli terbanyak berdasarkan negara bagiannya (state) adalah dari Negara Bagian Sao Paulo (Sao Paulo State - SP) sejumlah 41746 pembeli
                ''')

with tab2:
    customerCity_df = all_df.groupby(by="customer_city").customer_id.nunique().sort_values(ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12,6))

    topCity_df = customerCity_df.idxmax()
    most_common_city = customerCity_df.index[0]
    st.markdown(f"Most Common City: **{most_common_city}**")

    customerCity_df = customerCity_df.sort_values(ascending=False)

    sns.barplot(x=customerCity_df.index,
            y=customerCity_df.values,
            palette=["#068DA9" if city == topCity_df else "#D3D3D3" for city in customerCity_df.index],
            hue=customerCity_df.index,
            legend=False
            )


    plt.title("Number of Customers from Each City", fontsize=15)
    plt.xlabel("City")
    plt.ylabel("Number of Customers")
    plt.xticks(rotation=45, fontsize=10)
    st.pyplot(fig)

    with st.expander("Penjelasan Grafik"):
        st.write('''
                - Jumlah pembeli terbanyak berdasarkan kotanya adalah dari kota Sao Paulo sejumlah 15540 orang
                ''')

st.caption('Copyright (C) Ihsanu Ramdan M. 2024')