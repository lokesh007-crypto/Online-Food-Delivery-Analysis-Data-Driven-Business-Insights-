import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# 1. Page creation

st.set_page_config(page_title="Food Delivery Dashboard", layout="wide")
st.title("🍔 Online Food Delivery Analysis Dashboard")

# 2. Load data

df = pd.read_csv("Cleaned_food_delivery_data.csv")
df["Order_Date"] = pd.to_datetime(df["Order_Date"])

# 3. Sidebar filters

st.sidebar.header("Filters")

city_filter = st.sidebar.multiselect("Select City", options=df["City"].unique(), default=df["City"].unique())
cuisine_filter = st.sidebar.multiselect("Select Cuisine", options=df["Cuisine_Type"].unique(), default=df["Cuisine_Type"].unique())
status_filter = st.sidebar.multiselect("Order Status", options=df["Order_Status"].unique(), default=df["Order_Status"].unique())

df_filtered = df[
    (df["City"].isin(city_filter)) &
    (df["Cuisine_Type"].isin(cuisine_filter)) &
    (df["Order_Status"].isin(status_filter))
].copy()

# 4. metrics

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Orders", f"{df_filtered['Order_ID'].count():,}")
col2.metric("Total Revenue", f"₹{df_filtered['Final_Amount'].sum():,.0f}")
col3.metric("Avg Order Value", f"₹{df_filtered['Order_Value'].mean():,.2f}")
col4.metric("Cancellation Rate", f"{(df_filtered['Order_Status']=='Cancelled').mean()*100:.1f}%")

col5, col6 = st.columns(2)
col5.metric("Avg Delivery Time", f"{df_filtered['Delivery_Time_Min'].mean():.1f} min")
col6.metric("Avg Delivery Rating", f"{df_filtered['Delivery_Rating'].mean():.2f} ⭐")

st.markdown("---")

# 5. Correlation heatmap

st.subheader("Correlation Heatmap")
num_column = df_filtered.select_dtypes(include="number").columns.tolist()
corr_info = df_filtered[num_column].corr()
fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(corr_info, annot=True, fmt='.2f', cmap="coolwarm", ax=ax)
st.pyplot(fig)

st.markdown("---")


# 6. Top 10 spending customers

st.subheader("1. Top 10 Spending Customers")

top_spending_customer = ( df_filtered.groupby("Customer_ID")["Final_Amount"].sum().sort_values(ascending=False).head(10))

fig, ax = plt.subplots(figsize=(7, 5))
top_spending_customer.sort_values().plot(kind="barh", ax=ax)

ax.set_title("Top 10 Spending Customers")
ax.set_xlabel("Total Spending")
ax.set_ylabel("Customer ID")

st.pyplot(fig)
st.caption("A few customers contribute significantly to total revenue compared to other customers.")


# 7. Age group vs order value

st.subheader("2. Age Group vs Order Value")

age_vs_order_value = df_filtered.groupby("Age_Group")["Order_Value"].sum()

fig, ax = plt.subplots(figsize=(5, 5))
ax.pie( age_vs_order_value, labels=age_vs_order_value.index, autopct="%1.1f%%", startangle=90)

ax.set_title("Age Group Share of Order Value")
st.pyplot(fig)

st.caption("Most revenue comes from adults compared to seniors and younger adults.")

# 8. Weekend vs weekday order patterns

st.subheader("3. Weekend vs Weekday Order Patterns")

order_pattern = df_filtered["Order_Day"].value_counts()

fig, ax = plt.subplots(figsize=(5, 5))
order_pattern.plot(kind="bar", ax=ax)

ax.set_title("Weekend vs Weekday Order Patterns")
ax.set_xlabel("Order Day")
ax.set_ylabel("Order Count")

st.pyplot(fig)
st.caption("Most orders happen on weekdays compared to weekends.")

# 9. Monthly revenue

st.subheader("4. Monthly Revenue")

df_filtered["Order_Date"] = pd.to_datetime(df_filtered["Order_Date"])

month = df_filtered["Order_Date"].dt.to_period("M")
monthly_revenue = df_filtered.groupby(month)["Final_Amount"].sum()

fig, ax = plt.subplots(figsize=(8, 5))
monthly_revenue.plot(kind="line", marker="o", ax=ax)

ax.set_title("Monthly Revenue")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue")
ax.tick_params(axis="x", rotation=45)

st.pyplot(fig)
st.caption("July has the highest revenue , while February has the lowest ")


# 10. Impact of discounts

st.subheader("5. Impact of Discounts")

df_filtered["Price_Reduction"] = (df_filtered["Order_Value"] - df_filtered["Final_Amount"])

impact = df_filtered.groupby("Discount_Applied")["Price_Reduction"].mean()

fig, ax = plt.subplots(figsize=(6, 5))
impact.plot(kind="bar", ax=ax)

ax.set_title("Impact of Discounts")
ax.set_xlabel("Discount Applied")
ax.set_ylabel("Average Price Reduction")

st.pyplot(fig)
st.caption("Higher discounts directly increase the price reduction.")

# 11. High-revenue cities and cuisines

st.subheader("6. High-Revenue Cities and Cuisines")

city_cuisine_revenue = (df_filtered.groupby(["City", "Cuisine_Type"])["Final_Amount"].sum().reset_index())

fig, ax = plt.subplots(figsize=(10, 5))

sns.barplot( data=city_cuisine_revenue, x="City", y="Final_Amount",  hue="Cuisine_Type", ax=ax )

ax.set_title("Revenue by City and Cuisine")
ax.set_xlabel("City")
ax.set_ylabel("Revenue")
ax.tick_params(axis="x", rotation=30)

st.pyplot(fig)
st.caption("Bangalore has the highest city revenue, and Indian cuisine generates the highest revenue.")

# 12. Average delivery time by city

st.subheader("7. Average Delivery Time by City")

fig, ax = plt.subplots(figsize=(8, 5))

sns.violinplot( data=df_filtered, x="City", y="Delivery_Time_Min", cut=0, inner="quartile", ax=ax )

ax.set_title("Delivery Time Distribution by City")
ax.set_xlabel("City")
ax.set_ylabel("Delivery Time (Minutes)")
ax.tick_params(axis="x", rotation=30)

st.pyplot(fig)
st.caption("Average delivery time is similar across cities, around 124-126 minutes.")

# 13. Distance vs delivery delay

st.subheader("8. Distance vs Delivery Delay")

def group_distance(x):
    if x <= 5:
        return "1-5"
    elif x <= 10:
        return "6-10"
    elif x <= 15:
        return "11-15"
    elif x <= 20:
        return "16-20"
    elif x <= 25:
        return "21-25"
    elif x <= 30:
        return "26-30"
    elif x <= 35:
        return "31-35"
    elif x <= 40:
        return "36-40"

df_filtered["Distance_Group"] = df_filtered["Distance_km"].apply(group_distance)

delay = df_filtered.groupby("Distance_Group")["Delivery_Time_Min"].mean()

fig, ax = plt.subplots(figsize=(8, 5))
delay.plot(kind="bar", ax=ax)
ax.set_title("Distance vs delivery delay analysis")
ax.set_xlabel("Distance")
ax.set_ylabel("Delivery_time")
ax.tick_params(axis='x', rotation=0)
st.pyplot(fig)
plt.close(fig)

st.caption("There is no meaningful correlation between distance and delivery time.")

# 14. Delivery rating vs delivery time

st.subheader("9. Delivery Rating vs Delivery Time")

def group_min(x):
    if x <= 60:
        return "1-60"
    elif x <= 120:
        return "61-120"
    elif x <= 180:
        return "121-180"
    elif x <= 240:
        return "181-240"
    else:
        return "241-300"

df_filtered["group_delivery_time"] = df_filtered["Delivery_Time_Min"].apply(group_min)

rating_delivery_time = df_filtered.groupby(
    "group_delivery_time"
)["Delivery_Rating"].mean()

fig, ax = plt.subplots(figsize=(8, 5))

sns.violinplot( data=df_filtered, x="group_delivery_time", y="Delivery_Rating", cut=0, inner="quartile", ax=ax)

ax.set_title("Delivery Rating Distribution by Delivery Time")
ax.set_xlabel("Delivery Time (Minutes)")
ax.set_ylabel("Delivery Rating")

st.pyplot(fig)
st.caption("Delivery ratings are quite similar across delivery-time groups.")

# 15. Top-rated restaurants

st.subheader("10. Top 10 Rated Restaurants")

top_restaurant = (
    df_filtered.groupby("Restaurant_Name")["Restaurant_Rating"]
    .mean()
    .nlargest(10)
    .sort_values()
)

fig, ax = plt.subplots(figsize=(8, 5))

ax.scatter(
    top_restaurant.values,
    top_restaurant.index,
    s=80
)

ax.set_title("Top 10 Restaurants by Average Rating")
ax.set_xlabel("Average Restaurant Rating")
ax.set_ylabel("Restaurant Name")

st.pyplot(fig)
st.caption("Restaurant_101 has the highest average restaurant rating in analysis.")

# 16. Cancellation rate by restaurant

st.subheader("11. Cancellation Rate by Restaurant")

cancel_rate = (
    df_filtered.groupby("Restaurant_Name")["Cancellation_Reason"]
    .apply(lambda x: (x != "Not_Applicable").mean() * 100)
    .reset_index(name="Cancellation_Rate")
    .sort_values(by="Cancellation_Rate", ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(8, 5))

cancel_rate.set_index("Restaurant_Name")["Cancellation_Rate"].plot(
    kind="barh", ax=ax
)

ax.set_title("Cancellation Rate by Restaurant")
ax.set_xlabel("Cancellation Rate (%)")
ax.set_ylabel("Restaurant Name")

st.pyplot(fig)
st.caption("Restaurant_492 has the highest cancellation rate among the restaurants analyzed")

# 17. Cuisine-wise performance

st.subheader("12. Cuisine-Wise Performance")

cuisine_count = df_filtered["Cuisine_Type"].value_counts()

fig, ax = plt.subplots(figsize=(6, 6))

ax.pie(
    cuisine_count,
    labels=cuisine_count.index,
    autopct="%1.1f%%",
    startangle=90
)

ax.set_title("Cuisine-Wise Performance")

st.pyplot(fig)
st.caption("Indian cuisine performed the best in terms of revenue in the analysis.")

# 18. Peak hour demand

st.subheader("13. Peak Hour Demand Analysis")

peak_demand = df_filtered.groupby("Peak_Hour").size()

fig, ax = plt.subplots(figsize=(6, 5))

peak_demand.plot(kind="bar", ax=ax)

ax.set_title("Peak Hour Demand Analysis")
ax.set_xlabel("Peak Hour")
ax.set_ylabel("Order Count")
ax.set_xticklabels(["Non-Peak", "Peak"], rotation=0)

st.pyplot(fig)

st.caption("Non-peak hours have higher order volume than peak hours.")

# 19. Payment mode preferences

st.subheader("14. Payment Mode Preferences")

fig, ax = plt.subplots(figsize=(6, 6))
payment_counts = df_filtered["Payment_Mode"].value_counts()
ax.pie(
    payment_counts,
    labels=payment_counts.index,
    autopct="%1.1f%%"
)
ax.set_title("Payment Mode Preferences")
st.pyplot(fig)
plt.close(fig)


st.caption("Card is the most-used payment method, followed by Wallet, COD and UPI.")

# 20. Cancellation reason analysis

st.subheader("15. Cancellation Reason Analysis")

cancel_reason = df_filtered["Cancellation_Reason"].replace(
    "Not_Applicable", pd.NA
).dropna().value_counts()

if not cancel_reason.empty:

    fig, ax = plt.subplots(figsize=(8, 5))

    cancel_reason.plot(kind="bar", ax=ax)

    ax.set_xlabel("Cancellation Reason")
    ax.set_ylabel("Count")
    ax.set_title("Cancellation Reason Analysis")
    ax.tick_params(axis='x', rotation=0)

    st.pyplot(fig)
    plt.close(fig)

st.caption("Late Delivery, Customer Cancelled and Restaurant Issue are the main cancellation categories.")

st.markdown("---")

st.markdown(
    "**Overall Insight:** Adults generate the highest revenue, weekdays have more orders than weekends, and Bangalore leads in city revenue with Indian cuisine performing best. Card is the most preferred payment method, and late delivery is the most common cancellation reason."
)
