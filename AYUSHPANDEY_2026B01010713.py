

import pandas as pd
import numpy as np

# ---------------------------------------------------------------
# STEP 1: Load the data
# ---------------------------------------------------------------
df = pd.read_csv(r"C:\Users\Ayush Pandey\Downloads\dirty_cafe_sales.csv")

print("Rows before cleaning:", len(df))
print("\nMissing values before cleaning:")
print(df.isna().sum())

# ---------------------------------------------------------------
# STEP 2: Tidy up the text
# Remove extra spaces from column names and from text values.
# ---------------------------------------------------------------
df.columns = df.columns.str.strip()

text_columns = ["Transaction ID", "Item", "Payment Method", "Location"]
for col in text_columns:
    df[col] = df[col].str.strip()

# ---------------------------------------------------------------
# STEP 3: Turn "bad" words into real missing values (NaN)
# The file uses "ERROR" and "UNKNOWN" instead of leaving cells empty.
# Pandas understands NaN much better, so we convert them.
# ---------------------------------------------------------------
df = df.replace(["ERROR", "UNKNOWN", ""], np.nan)

# ---------------------------------------------------------------
# STEP 4: Fix the data types
# Numbers were read as text because of the "ERROR"/"UNKNOWN" words.
# errors="coerce" means: if a value can't become a number, make it NaN.
# ---------------------------------------------------------------
number_columns = ["Quantity", "Price Per Unit", "Total Spent"]
for col in number_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], errors="coerce")

# ---------------------------------------------------------------
# STEP 5: Remove duplicate rows
# Every Transaction ID should appear only once.
# ---------------------------------------------------------------
df = df.drop_duplicates(subset="Transaction ID")

# ---------------------------------------------------------------
# STEP 6: Fill in missing prices using the menu
# Each item always has the same price, so we can learn the menu
# from the data itself (the most common price for each item).
# ---------------------------------------------------------------
menu = df.groupby("Item")["Price Per Unit"].agg(lambda prices: prices.mode().iloc[0])
print("\nMenu prices found in the data:")
print(menu)

# Look up each row's item in the menu, and use it only where price is missing.
df["Price Per Unit"] = df["Price Per Unit"].fillna(df["Item"].map(menu))

# ---------------------------------------------------------------
# STEP 7: Fill in missing item names using the price
# Only possible when ONE item has that price (e.g. 1.5 -> Tea).
# Prices like 3.0 belong to Cake AND Juice, so we leave those alone.
# ---------------------------------------------------------------
items_per_price = menu.reset_index().groupby("Price Per Unit")["Item"].agg(list)
unique_price_to_item = {
    price: items[0] for price, items in items_per_price.items() if len(items) == 1
}
df["Item"] = df["Item"].fillna(df["Price Per Unit"].map(unique_price_to_item))

# ---------------------------------------------------------------
# STEP 8: Use the formula  Total Spent = Quantity x Price Per Unit
# to fill whatever number is missing.
# ---------------------------------------------------------------
# Missing Total Spent  ->  Quantity * Price
df["Total Spent"] = df["Total Spent"].fillna(df["Quantity"] * df["Price Per Unit"])

# Missing Quantity  ->  Total / Price
df["Quantity"] = df["Quantity"].fillna(df["Total Spent"] / df["Price Per Unit"])

# Missing Price  ->  Total / Quantity
df["Price Per Unit"] = df["Price Per Unit"].fillna(df["Total Spent"] / df["Quantity"])

# ---------------------------------------------------------------
# STEP 9: Drop rows that still can't be fixed
# If we still don't know the quantity, price or total, the row
# isn't useful for sales analysis.
# ---------------------------------------------------------------
df = df.dropna(subset=["Quantity", "Price Per Unit", "Total Spent"])

# Quantity is a whole number (you can't buy 2.5 cookies).
df["Quantity"] = df["Quantity"].round().astype(int)

# ---------------------------------------------------------------
# STEP 10: Handle the remaining missing text and dates
# For categories, we label the gaps "Unknown" so we keep the rows.
# For dates, we leave them empty because guessing a date would be
# making up data.
# ---------------------------------------------------------------
for col in ["Item", "Payment Method", "Location"]:
    df[col] = df[col].fillna("Unknown")

# ---------------------------------------------------------------
# STEP 11: Final tidy up and save
# ---------------------------------------------------------------
df = df.reset_index(drop=True)
df.to_csv("cleaned_cafe_sales.csv", index=False)

print("\nRows after cleaning:", len(df))
print("\nMissing values after cleaning:")
print(df.isna().sum())
print("\nFirst 5 rows of the cleaned data:")
print(df.head())
print("\nSaved to cleaned_cafe_sales.csv")

df.to_csv(r"C:\Users\Ayush Pandey\Downloads\clean_cafe_sales.csv", index=False)