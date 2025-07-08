import streamlit as st
import pandas as pd

st.set_page_config(page_title="Inventory Management", layout="wide")
st.title("📦 Inventory Management Platform")

# Session state to store inventory
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=["Item", "Quantity", "Type"])

# --- Upload stock file ---
st.sidebar.header("Upload Stock File (.csv or .xlsx)")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        file_data = pd.read_csv(uploaded_file)
    else:
        file_data = pd.read_excel(uploaded_file)

    st.session_state.inventory = pd.concat([st.session_state.inventory, file_data], ignore_index=True)
    st.sidebar.success("✅ File uploaded and inventory updated!")

# --- Manual Entry ---
st.sidebar.header("Add Stock Manually")
with st.sidebar.form("manual_add_form"):
    item = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=1, value=1)
    stock_type = st.selectbox("Transaction Type", ["Bought", "Sold"])
    add = st.form_submit_button("Add Stock")

if add and item:
    new_row = {"Item": item, "Quantity": quantity, "Type": stock_type}
    st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_row])], ignore_index=True)
    st.sidebar.success("✅ Stock entry added!")

# --- Display Inventory ---
st.subheader("📊 Inventory Records")
st.dataframe(st.session_state.inventory, use_container_width=True)

# --- Calculate Remaining Stock ---
remaining_stock = st.session_state.inventory.groupby(["Item", "Type"])["Quantity"].sum().unstack(fill_value=0)
remaining_stock["Remaining"] = remaining_stock.get("Bought", 0) - remaining_stock.get("Sold", 0)
remaining_stock = remaining_stock.reset_index()

st.subheader("📦 Stock Summary")
st.dataframe(remaining_stock[["Item", "Bought", "Sold", "Remaining"]], use_container_width=True)

# --- Recommendation Section ---
st.subheader("🧠 Recommendations")
low_stock = remaining_stock[remaining_stock["Remaining"] <= 5]

if not low_stock.empty:
    for _, row in low_stock.iterrows():
        st.warning(f"🔔 Consider restocking: **{row['Item']}** (Remaining: {int(row['Remaining'])})")
else:
    st.success("✅ All items are sufficiently stocked.")

