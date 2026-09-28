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

city_filter = st.sidebar.multiselect(
    "Select City", options=df["City"].unique(), default=df["City"].unique()
)
cuisine_filter = st.sidebar.multiselect(
    "Select Cuisine", options=df["Cuisine_Type"].unique(), default=df["Cuisine_Type"].unique()
)
status_filter = st.sidebar.multiselect(
    "Order Status", options=df["Order_Status"].unique(), default=df["Order_Status"].unique()
)

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

# 6. Top 10 spending customers

st.subheader("1. Top 10 Spending Customers")
top_spending_customer = (
    df_filtered.groupby("Customer_ID")["Final_Amount"].sum().sort_values(ascending=False)
).head(10)
fig, ax = plt.subplots(figsize=(10, 5))
top_spending_customer.plot(kind="bar", ax=ax)
ax.set_title("Top 10 spending customer")
ax.set_xlabel("Customer_ID")
ax.set_ylabel("Total_Spending")
st.pyplot(fig)
st.caption("A few customers contribute significantly to total revenue compared to others.")

# 7. Age group vs order value

st.subheader("2. Age Group vs Order Value")
age_vs_order_value = df_filtered.groupby("Age_Group")["Order_Value"].sum()
fig, ax = plt.subplots(figsize=(5, 5))
age_vs_order_value.plot(kind="bar", ax=ax)
ax.set_title("Age group vs order value")
ax.set_xlabel("Age_Group")
ax.set_ylabel("Order_Value")
st.pyplot(fig)
st.caption("Most revenue comes from the Adult group compared to Senior and Younger_Adult.")

# 8. Weekend vs weekday order patterns

st.subheader("3. Weekend vs Weekday Order Patterns")
order_pattern = df_filtered["Order_Day"].value_counts()
fig, ax = plt.subplots(figsize=(5, 5))
order_pattern.plot(kind="bar", ax=ax)
ax.set_title("weekend vs weekday Order_pattern")
ax.set_xlabel("Order_Day")
ax.set_ylabel("Order_count")
st.pyplot(fig)
st.caption("Most orders happen on weekdays compared to weekends.")

# 9. Monthly revenue

st.subheader("4. Monthly Revenue Trend")
month = df_filtered["Order_Date"].dt.to_period("M")
monthly_revenue = df_filtered.groupby(month)["Final_Amount"].sum()
fig, ax = plt.subplots(figsize=(10, 5))
monthly_revenue.plot(kind="line", ax=ax)
ax.set_title("Monthly Revenue")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue")
st.pyplot(fig)
st.caption("July has the highest revenue; February has the lowest.")

# 10. Impact of discounts on profit

st.subheader("5. Impact of Discounts on Profit")
impact = df_filtered.groupby("Discount_Applied")["Profit_Margin"].mean()
fig, ax = plt.subplots(figsize=(6, 5))
impact.plot(kind="bar", ax=ax)
ax.set_title("Impact of Discounts on Profit Margin")
ax.set_xlabel("Discount_Applied")
ax.set_ylabel("Average Profit Margin")
st.pyplot(fig)
st.caption("Shows how average profit margin changes across discount tiers.")

# 11. High-revenue cities and cuisines

st.subheader("6. High-Revenue Cities and Cuisines")

city_amount = df_filtered[df_filtered["City"] != "unknown"].groupby("City")["Final_Amount"].sum()
fig, ax = plt.subplots(figsize=(8, 5))
city_amount.plot(kind="bar", ax=ax)
ax.set_title("City-wise Revenue")
ax.set_xlabel("City")
ax.set_ylabel("Revenue")
ax.tick_params(axis='x', rotation=0)
st.pyplot(fig)

cusine_amount = df_filtered.groupby("Cuisine_Type")["Final_Amount"].sum()
fig, ax = plt.subplots(figsize=(8, 5))
cusine_amount.plot(kind="bar", ax=ax)
ax.set_title("Cuisine-wise Revenue")
ax.set_xlabel("Cuisine_Type")
ax.set_ylabel("Revenue")
ax.tick_params(axis='x', rotation=0)
st.pyplot(fig)

city_cuisine_revenue = df_filtered.groupby(["City", "Cuisine_Type"])["Final_Amount"].sum().reset_index()
fig, ax = plt.subplots(figsize=(15, 6))
sns.barplot(data=city_cuisine_revenue, x="City", y="Final_Amount", hue="Cuisine_Type", ax=ax)
for container in ax.containers:
    ax.bar_label(container, fmt='%d', rotation=90, padding=5)
st.pyplot(fig)
st.caption("Bangalore has the highest city revenue and Indian cuisine generates the highest revenue.")

# 12. Average delivery time by city

st.subheader("7. Average Delivery Time by City")
avg_time = df_filtered.groupby("City")["Delivery_Time_Min"].mean()
fig, ax = plt.subplots(figsize=(8, 5))
avg_time.plot(kind="bar", ax=ax)
ax.set_title("Average delivery time by city")
ax.set_xlabel("City")
ax.set_ylabel("Delivery_time")
ax.tick_params(axis='x', rotation=0)
st.pyplot(fig)
st.caption("Average delivery time is similar across cities, around 124-126 minutes.")

# 13. Distance vs delivery delay

st.subheader("8. Distance vs Delivery Delay")

def group_distance(x):
    if x <= 5: return "1-5"
    elif x <= 10: return "6-10"
    elif x <= 15: return "11-15"
    elif x <= 20: return "16-20"
    elif x <= 25: return "21-25"
    elif x <= 30: return "26-30"
    elif x <= 35: return "31-35"
    elif x <= 40: return "36-40"

df_filtered["Distance_Group"] = df_filtered["Distance_km"].apply(group_distance)
delay = df_filtered.groupby("Distance_Group")["Delivery_Time_Min"].mean()
fig, ax = plt.subplots(figsize=(8, 5))
delay.plot(kind="bar", ax=ax)
ax.set_title("Distance vs delivery delay analysis")
ax.set_xlabel("Distance")
ax.set_ylabel("Delivery_time")
ax.tick_params(axis='x', rotation=0)
st.pyplot(fig)
st.caption("There is no meaningful correlation between distance and delivery time.")

# 14. Delivery rating vs delivery time

st.subheader("9. Delivery Rating vs Delivery Time")

def group_min(x):
    if x <= 60: return "1-60"
    elif x <= 120: return "61-120"
    elif x <= 180: return "121-180"
    elif x <= 240: return "181-240"
    else: return "241-300"

df_filtered["group_delivery_time"] = df_filtered["Delivery_Time_Min"].apply(group_min)
rating_delivery_time = df_filtered.groupby("group_delivery_time")["Delivery_Rating"].mean()
fig, ax = plt.subplots(figsize=(7, 6))
rating_delivery_time.plot(kind="bar", ax=ax)
ax.set_title("Delivery rating vs delivery time")
ax.set_xlabel("Delivery_time")
ax.set_ylabel("Delivery_rating")
st.pyplot(fig)
st.caption("Delivery ratings are quite similar across delivery-time groups.")

# 15. Top-rated restaurants

st.subheader("10. Top-Rated Restaurants")
top_restaurant = df_filtered.groupby("Restaurant_Name")["Restaurant_Rating"].mean().sort_values(ascending=False).head(10)
fig, ax = plt.subplots(figsize=(14, 5))
top_restaurant.plot(kind="bar", ax=ax)
ax.set_title("Top-rated restaurants")
ax.set_xlabel("Restaurant_Name")
ax.set_ylabel("Restaurant_Rating")
st.pyplot(fig)

# 16. Cancellation rate by restaurant

st.subheader("11. Cancellation Rate by Restaurant")
cancel_rate = (
    df_filtered.groupby("Restaurant_Name")["Cancellation_Reason"]
    .apply(lambda x: (x != "Not_Applicable").mean() * 100)
    .reset_index(name="Cancellation_Rate")
).sort_values(by="Cancellation_Rate", ascending=False).head(10)

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(cancel_rate["Restaurant_Name"], cancel_rate["Cancellation_Rate"])
ax.set_title("Cancellation rate by restaurant")
ax.set_xlabel("Restaurant_Name")
ax.set_ylabel("Cancellation_Rate")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# 17. Cuisine-wise performance

st.subheader("12. Cuisine-wise Performance")
fig, ax = plt.subplots(figsize=(6, 6))
cuisine_counts = df_filtered["Cuisine_Type"].value_counts()
ax.pie(cuisine_counts, labels=cuisine_counts.index, autopct="%1.1f%%")
ax.set_title("Cuisine-wise performance")
st.pyplot(fig)
st.caption("Indian cuisine performed the best in terms of revenue.")

# 18. Peak hour demand

st.subheader("13. Peak Hour Demand Analysis")
peak_demand = df_filtered.groupby("Peak_Hour").size()
fig, ax = plt.subplots(figsize=(8, 5))
peak_demand.plot(kind="bar", ax=ax)
ax.set_title("Peak hour demand analysis")
ax.set_xlabel("Peak_Hour")
ax.set_ylabel("Order_Count")
ax.set_xticklabels(["Non_peak(False)", "Peak(True)"], rotation=0)
st.pyplot(fig)
st.caption("Non-peak hours have higher order volume than peak hours.")

# 19. Payment mode preferences

st.subheader("14. Payment Mode Preferences")
fig, ax = plt.subplots(figsize=(6, 6))
payment_counts = df_filtered["Payment_Mode"].value_counts()
ax.pie(payment_counts, labels=payment_counts.index, autopct="%1.1f%%")
ax.set_title("Payment mode preferences")
st.pyplot(fig)

order_preferences = df_filtered.groupby("Payment_Mode")["Order_Value"].sum()
fig, ax = plt.subplots(figsize=(8, 5))
order_preferences.plot(kind="bar", ax=ax)
ax.set_title("payment_mode_preferences by order_value")
ax.set_xlabel("Payment_Mode")
ax.set_ylabel("Order_Value")
ax.tick_params(axis='x', rotation=0)
st.pyplot(fig)
st.caption("Card is the most-used payment method, followed by Wallet, COD and UPI.")

# 20. Cancellation reason analysis

st.subheader("15. Cancellation Reason Analysis")
cancel_reason = df_filtered["Cancellation_Reason"].apply(
    lambda x: x if x != "Not_Applicable" else None
).value_counts()
fig, ax = plt.subplots(figsize=(8, 5))
cancel_reason.plot(kind="bar", ax=ax)
ax.set_xlabel("Cancellation_Reason")
ax.set_ylabel("Count")
ax.set_title("Cancellation reason analysis")
ax.tick_params(axis='x', rotation=0)
st.pyplot(fig)
st.caption("Late Delivery, Customer Cancelled and Restaurant Issue are the main cancellation categories.")

st.markdown("---")
st.markdown(
    "**Overall Insight:** Adults generate the highest revenue, weekdays have more orders than weekends, and Bangalore leads in city revenue with Indian cuisine performing best. Card is the most preferred payment method, and late delivery is the most common cancellation reason."
)