import sqlite3
import pandas as pd 

#SET UP THE SQLITE DATABASE

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE sales_data (
        id INTEGER PRIMARY KEY,
        product TEXT NOT NULL,
        category TEXT NOT NULL, 
        unit_price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        quarter TEXT NOT NULL
    )
""")

sales_data = [
    ("Widget A", "Electronics", 29.99, 150, "2025-Q1"),
    ("Widget B", "Electronics", 49.99, 89, "2025-Q1"),
    ("Gadget X", "Accessories", 15.99, 300, "2025-Q1"),
    ("Widget A", "Electronics", 29.99, 200, "2025-Q2"),
    ("Gadget Y", "Accessories", 22.99, 175, "2025-Q2"),
    ("Widget C", "Electronics", 79.99, 50, "2025-Q2"),
    ("Gadget X", "Accessories", 15.99, 280, "2025-Q2"),
    ("Widget B", "Electronics", 49.99, 120, "2025-Q3"),
]

cursor.executemany("""
    INSERT INTO sales_data (product, category, unit_price, quantity, quarter)
    VALUES (?,?,?,?,?)
""",sales_data)
conn.commit()

#SET UP SAME DATA IN PANDAS DATAFRAME
df = pd.DataFrame(sales_data, columns=["product", "category", "unit_price", "quantity", "quarter" ])

print ("Data loaded in boht SQL and Pandas!\\n")

print ("\n==== TOTAL REVENUE PER PRODUCT - SQL DATABASE ====")
cursor.execute ("""
    SELECT product, SUM(unit_price * quantity) AS total_revenue
        
    FROM sales_data
    GROUP BY product
    ORDER BY total_revenue DESC 

""")

for row in cursor.fetchall():
    print(f"{row[0]}: ${row[1]:.2f}")

print ("\n==== TOTAL REVENUE PER PRODUCT - PANDAS DATAFRAME ====")
#Revenue per item 
df["revenue"] = df["unit_price"] * df["quantity"]

product_summary = (
    df.groupby ("product")
    .agg(total_revenue = ("revenue", "sum"))
    .sort_values("total_revenue", ascending= False) 
    .reset_index()  #takes current row index and converts it back into a standard column 
)
print(product_summary.to_string(index=False))

#Which quarter had the highest total quantity sold?
print ("\n==== QUARTER WITH THE HIGHEST TOTAL QUANTITY SOLD - SQL DATABASE ====")
cursor.execute("""
    SELECT quarter, SUM(quantity) AS total_sold, COUNT(quarter) AS highest_quarter
    FROM sales_data
    GROUP BY quarter
    ORDER BY highest_quarter DESC
    LIMIT 1

""")
for row in cursor.fetchall():
    print (f"The quarter with highest total quantity sold was {row[0]} with {row[1]} items sold!")

print ("\n==== QUARTER WITH THE HIGHEST TOTAL QUANTITY SOLD - PANDAS DATABASE ====")
highest_quarter = (
    df.groupby("quarter")
    .agg (highest_quarter = ("quantity", "sum"))
    .sort_values("highest_quarter", ascending= False)
    .head (1)
    .reset_index()
    )   
print (highest_quarter.to_string(index=False) )

#What is the average unit price per category?
print ("\n==== AVERAGE UNIT PRICE PER CATEGORY - SQL DATABASE ====")
cursor.execute("""
    SELECT category, ROUND(AVG(unit_price),0) AS avg_price
    FROM sales_data
    GROUP BY category
    ORDER BY avg_price DESC
""")
for row in cursor.fetchall():   

    print (f"Average Unit Price for {row[0]} - ${row[1]}")


print ("\n==== AVERAGE UNIT PRICE PER CATEGORY - PANDAS DATAFRAME ====")

avg_price= (
    df.groupby("category", as_index= False)["unit_price"]
    .mean()
    .round()
    .sort_values("unit_price", ascending= False)
    )
print (avg_price.to_string(index = False))

#Which products had total quantity over 200 across all quarters?

print ("\n==== PRODUCTS OVER 200 QUANTITY - SQL DATABASE ====")
cursor.execute ("""
    SELECT product, SUM(quantity) as total_quantity
    FROM sales_data
    GROUP BY product
    HAVING SUM(quantity) > 200
    ORDER BY total_quantity DESC
""")
for row in cursor.fetchall():
    print (f"{row[0]} {row[1]}")

print ("\n==== PRODUCTS OVER 200 QUANTITY- PANDAS DATAFRAME ====")

prod_stats = (
    df.groupby("product")
    .agg(total_quantity = ("quantity", "sum"))
    .query ("total_quantity > 200")
    .sort_values("total_quantity", ascending= False)
    
)
for prod, row in prod_stats.iterrows():

    print(f"{prod}: {row['total_quantity']}")

#BONUS: Use pd.read_sql() to run one of your SQL queries and get the result as a DataFrame.
print ("\n==== SQL TO DATAFRAME ====")
query = """
    SELECT product, SUM(unit_price * quantity) AS total_revenue
        
    FROM sales_data
    GROUP BY product
    ORDER BY total_revenue DESC 

"""
total_revenue = pd.read_sql(query, conn)
print(total_revenue.to_string(index=False))


"""RESULTS
(venv) noeliaquiroga@Noelias-MacBook-Pro dataframe_to_sql % python3 translation_challenge.py
Data loaded in boht SQL and Pandas!\n

==== TOTAL REVENUE PER PRODUCT - SQL DATABASE ====
Widget A: $10496.50
Widget B: $10447.91
Gadget X: $9274.20
Gadget Y: $4023.25
Widget C: $3999.50

==== TOTAL REVENUE PER PRODUCT - PANDAS DATAFRAME ====
 product  total_revenue
Widget A       10496.50
Widget B       10447.91
Gadget X        9274.20
Gadget Y        4023.25
Widget C        3999.50

==== QUARTER WITH THE HIGHEST TOTAL QUANTITY SOLD - SQL DATABASE ====
The quarter with highest total quantity sold was 2025-Q2 with 705 items sold!

==== QUARTER WITH THE HIGHEST TOTAL QUANTITY SOLD - PANDAS DATABASE ====
quarter  highest_quarter
2025-Q2              705

==== AVERAGE UNIT PRICE PER CATEGORY - SQL DATABASE ====
Average Unit Price for Electronics - $48.0
Average Unit Price for Accessories - $18.0

==== AVERAGE UNIT PRICE PER CATEGORY - PANDAS DATAFRAME ====
   category  unit_price
Electronics        48.0
Accessories        18.0

==== PRODUCTS OVER 200 QUANTITY - SQL DATABASE ====
Gadget X 580
Widget A 350
Widget B 209

==== PRODUCTS OVER 200 QUANTITY- PANDAS DATAFRAME ====
Gadget X: 580
Widget A: 350
Widget B: 209

==== SQL TO DATAFRAME ====
 product  total_revenue
Widget A       10496.50
Widget B       10447.91
Gadget X        9274.20
Gadget Y        4023.25
Widget C        3999.50
(venv) noeliaquiroga@Noelias-MacBook-Pro dataframe_to_sql % 



"""