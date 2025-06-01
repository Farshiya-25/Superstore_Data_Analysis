import pandas as pd
import mysql.connector
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os

# database connection function

def get_connection():
    conn = mysql.connector.connect(host = "localhost",
                                user = "root",
                                password ="Farshi@25",
                                database = "Superstore")
    
    return conn


def run_query(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    return pd.DataFrame(rows, columns=columns)

# Total number of orders, sales, profit 

def total_orders():
    df = run_query("SELECT COUNT(DISTINCT Order_ID) AS total_orders FROM Orders")
    st.metric("Total Orders", value= f"${df['total_orders'][0]:,.2f}")

def total_profit():
    df = run_query("SELECT ROUND(SUM(Profit), 2) AS total_profit FROM Orders")
    st.metric("Total profit", value=f"${df['total_profit'][0]:,.2f}")

def total_sales():
    df = run_query("SELECT ROUND(SUM(Sales), 2) AS total_sales FROM Orders")
    st.metric("Total Sales", value=f"${df['total_sales'][0]:,.2f}")

# Orders by Country

def orders_by_state():
    df = run_query("""SELECT State,
                   COUNT(DISTINCT Order_ID) AS total_orders 
                   FROM Orders
                   GROUP BY State
                   ORDER BY total_orders DESC
                   LIMIT 10""")
    fig = px.bar(df,x='State',y='total_orders')
    st.plotly_chart(fig)

# sales & profit trend over time(year)

def sales_profit_trend():
    df = run_query("""
        SELECT 
            YEAR(Order_Date) AS year,
            ROUND(SUM(Sales), 2) AS total_sales,
            ROUND(SUM(Profit), 2) AS total_profit
        FROM orders
        GROUP BY year
        ORDER BY year
    """)

    df_melted = df.melt(id_vars='year', value_vars=['total_sales', 'total_profit'],
                        var_name='Metric', value_name='Amount')
    
    fig = px.bar(df_melted,
                 x='year',
                 y='Amount',
                 color='Metric',
                 barmode='group',
                 text='Amount')
    
    st.plotly_chart(fig)

# Monthly patterns by Total orders

def monthwise_total_orders():
    df = run_query("""SELECT 
                MONTHNAME(Order_Date) AS order_month,
                MONTH(Order_Date) AS order_number,
                COUNT(DISTINCT Order_ID) AS total_orders
                FROM Orders
                GROUP BY order_month,order_number
                ORDER BY order_number""")
    st.plotly_chart(px.line(df,x='order_month', y='total_orders'))

# Sales by sub_category

def sub_category_sales():
        df_sub_cat = run_query("SELECT Sub_Category, SUM(Sales) AS total_sales FROM Orders GROUP BY Sub_Category")
        st.plotly_chart(px.bar(df_sub_cat,x='Sub_Category',y='total_sales',title='Sales by Sub_category'))

# Sale by category

def category_sales():
    df_cat = run_query("SELECT Category, SUM(Sales) AS total_sales FROM Orders GROUP BY Category")
    st.plotly_chart(px.pie(df_cat,names='Category',values='total_sales',title='Sales by Category'))

# Profitability at different discount levels

def avg_profit_by_dicount():
    df = run_query("""SELECT 
                CASE
                    WHEN Discount = 0 THEN "No Discount"
                    WHEN Discount BETWEEN 0.01 AND 0.2 THEN "Low discount"
                    WHEN Discount BETWEEN 0.21 AND 0.4 THEN "Medium discount"
                    ELSE "High discount"
                END AS discount_levels,
                ROUND(AVG(Profit), 2) AS avg_profit
                FROM Orders
                GROUP BY discount_levels
                ORDER BY avg_profit""")
    st.plotly_chart(px.line(df,x='discount_levels',y='avg_profit',markers=True))

# Top 10 products

def top_10_products():
    df = run_query("""SELECT
            Product_Name,
            ROUND(SUM(Sales) ,2) AS total_sales
            FROM Orders
            GROUP BY Product_Name
            ORDER BY total_sales DESC
            LIMIT 10
            """)
    st.plotly_chart(px.bar(df,y='Product_Name',x='total_sales',orientation='h'))

# Top 10 customers by quantity

def top_10_customers():
    df = run_query("""SELECT
            Customer_Name,
            SUM(Quantity) AS total_quantity
            FROM Orders
            GROUP BY Customer_Name
            ORDER BY total_quantity DESC
            LIMIT 10
            """)
    st.plotly_chart(px.bar(df,x='Customer_Name',y='total_quantity'))

def negative_profit_products():
    df = run_query("""SELECT Product_Name,
                    ROUND(SUM(Profit), 2) AS total_profit
                    FROM Orders
                    GROUP BY Product_Name
                    HAVING total_profit < 0
                    ORDER BY total_profit ASC
                   LIMIT 10
                    """)
    st.plotly_chart(px.bar(df,x='Product_Name',y='total_profit'))

st.set_page_config(layout="wide")

st.header(":violet[SUPERSTORE DATA ANALYSIS]", divider='rainbow')

page1,page2 = st.tabs([":blue[ANALYSIS]",":blue[INSIGHTS]"])

with page1:
    col1,col2 = st.columns(2)
    with col1:
        st.subheader('Total Orders')
        total_orders()

        st.subheader('Total Sales')
        total_sales()

        st.subheader('Total Profit')
        total_profit()

    with col2:
        st.subheader('Total Orders by State')
        orders_by_state()

    col1,col2 = st.columns(2)
    with col1:
        st.subheader('Sales & Profit trends over Time')
        sales_profit_trend()

    with col2:
        st.subheader('Total Orders by Months')
        monthwise_total_orders()    


    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Sales by Category")
        category_sales()

    with col2:
        st.subheader("Sales by Sub_category")
        sub_category_sales()

    
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 products by Sales")
        top_10_products()

    with col2:
        st.subheader("Top 10 customers by Total purchase")
        top_10_customers()

    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Profitability at different discount levels")
        avg_profit_by_dicount()

    with col2:
        st.subheader("Products with negative profit")
        negative_profit_products()

with page2:
    st.header("Summarized Insights")
    st.write("1. Total orders show good customer engagement across the business")
    st.write("2. Sales are high, especsially in Technology category")
    st.write("3. California, New York, Texas have the most orders")
    st.write("4. Increasing Sales and Profit from 2014 to 2017")
    st.write("5. Orders increase during the end of the year (like November and December due to holidays)")
    st.write("6. Phones, Chairs, Copiers are the top performing sub-categories")
    st.write("7. A few top customers spend much more than the others")
    st.write("8. Giving too much discounts(20% and more) often leads to losses")
    st.write("9. To grow profit, avoid over discounting and focus on best selling profitable products")
    st.write("10. Tables, Bookcases, Binders are the under performing sub-categories")
    