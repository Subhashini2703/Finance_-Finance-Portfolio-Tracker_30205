# frontend_fin.py

import streamlit as st
import pandas as pd
from datetime import date
from Backend import (
    create_asset, 
    create_transaction, 
    read_portfolio_summary, 
    read_all_transactions,
    update_asset_price,
    delete_transaction,
    get_business_insights
)

st.title('💰 Financial Portfolio Tracker - subhashini - 30205')
st.write("Welcome to your personal financial management dashboard.")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Manage Assets", "Transactions", "Business Insights"])

with tab1:
    st.header("Portfolio Summary")
    
    portfolio_data = read_portfolio_summary()
    
    if portfolio_data:
        df_portfolio = pd.DataFrame(portfolio_data, columns=['Ticker', 'Name', 'Class', 'Shares', 'Cost Basis', 'Current Price'])
        df_portfolio['Current Value'] = df_portfolio['Shares'] * df_portfolio['Current Price']
        df_portfolio['Gain/Loss'] = df_portfolio['Current Value'] - df_portfolio['Cost Basis']
        
        total_value = df_portfolio['Current Value'].sum()
        total_gain_loss = df_portfolio['Gain/Loss'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Portfolio Value", f"${total_value:,.2f}")
        with col2:
            st.metric("Total Gain/Loss", f"${total_gain_loss:,.2f}", delta=f"{total_gain_loss/total_value:.2%}" if total_value > 0 else "0.00%")

        st.subheader("Holdings Breakdown")
        st.dataframe(df_portfolio.style.format({
            'Shares': "{:,.4f}",
            'Cost Basis': "${:,.2f}",
            'Current Price': "${:,.2f}",
            'Current Value': "${:,.2f}",
            'Gain/Loss': "${:,.2f}"
        }), use_container_width=True)
        
        # Breakdown by Asset Class
        asset_class_breakdown = df_portfolio.groupby('Class')['Current Value'].sum().reset_index()
        st.subheader("Portfolio by Asset Class")
        st.bar_chart(asset_class_breakdown.set_index('Class'))
        
    else:
        st.info("No assets in your portfolio yet. Add some in the 'Manage Assets' tab.")

with tab2:
    st.header("Manage Assets")
    
    st.subheader("Add or Update Asset")
    with st.form("asset_form"):
        ticker = st.text_input("Ticker Symbol (e.g., AAPL)").upper()
        name = st.text_input("Asset Name (e.g., Apple Inc.)")
        asset_class = st.selectbox("Asset Class", ["Equity", "Fixed Income", "Crypto", "Commodity"])
        current_price = st.number_input("Current Price", min_value=0.01)
        
        submitted = st.form_submit_button("Save Asset")
        if submitted:
            if create_asset(ticker, name, asset_class, current_price):
                st.success(f"Asset '{ticker}' saved successfully!")
            else:
                st.error("Failed to save asset. Check your inputs and database connection.")
        
    st.subheader("Update Asset Price")
    assets = read_all_transactions()
    if assets:
        asset_options = [f"{a[0]} - {a[1]}" for a in assets]
        selected_asset = st.selectbox("Select Asset to Update Price", asset_options)
        
        if selected_asset:
            selected_ticker = selected_asset.split(" - ")[0]
            new_price = st.number_input(f"New Price for {selected_ticker}", min_value=0.01)
            
            if st.button("Update Price"):
                if update_asset_price(selected_ticker, new_price):
                    st.success(f"Price for {selected_ticker} updated successfully!")
                else:
                    st.error("Failed to update price.")
    else:
        st.info("No assets to update.")

with tab3:
    st.header("Log Transactions")
    
    st.subheader("Add New Transaction")
    with st.form("transaction_form"):
        ticker_options = [a[0] for a in read_all_transactions()]
        if not ticker_options:
            st.warning("Please add an asset in the 'Manage Assets' tab before logging a transaction.")
            st.stop()
            
        ticker = st.selectbox("Ticker Symbol", ticker_options)
        trans_date = st.date_input("Transaction Date", value=date.today())
        trans_type = st.selectbox("Transaction Type", ["buy", "sell", "dividend"])
        shares = st.number_input("Number of Shares", min_value=0.0001, format="%.4f")
        price_per_share = st.number_input("Price per Share", min_value=0.01)
        
        total_cost = shares * price_per_share
        st.write(f"Total Cost: ${total_cost:,.2f}")
        
        submitted = st.form_submit_button("Log Transaction")
        if submitted:
            if create_transaction(ticker, trans_date, trans_type, shares, price_per_share, total_cost):
                st.success(f"Transaction for {ticker} logged successfully!")
            else:
                st.error("Failed to log transaction. Ensure the asset ticker exists and inputs are valid.")
    
    st.subheader("Transaction History")
    transactions = read_all_transactions()
    if transactions:
        df_transactions = pd.DataFrame(transactions, columns=['ID', 'Ticker', 'Date', 'Type', 'Shares', 'Price', 'Total Cost'])
        st.dataframe(df_transactions.style.format({
            'Shares': "{:,.4f}",
            'Price': "${:,.2f}",
            'Total Cost': "${:,.2f}"
        }), use_container_width=True)
        
        st.subheader("Delete Transaction")
        transaction_id_to_delete = st.number_input("Enter Transaction ID to delete", min_value=0, step=1)
        if st.button("Delete Transaction"):
            if delete_transaction(transaction_id_to_delete):
                st.success(f"Transaction with ID {transaction_id_to_delete} deleted successfully!")
                st.rerun()
            else:
                st.error("Failed to delete transaction. Ensure the ID is correct.")

with tab4:
    st.header("Business Insights")
    st.info("This section provides key metrics on your financial data using aggregation functions.")
    
    insights = get_business_insights()
    
    if insights:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Unique Assets", insights.get('total_unique_assets', 0))
            st.metric("Total Transactions", insights.get('total_transactions', 0))
        with col2:
            st.metric("Total Buy Cost", f"${insights.get('total_buy_cost', 0.0):,.2f}")
            st.metric("Average Price per Share", f"${insights.get('avg_price_per_share', 0.0):,.2f}")
        with col3:
            st.metric("Max Transaction Cost", f"${insights.get('max_transaction_cost', 0.0):,.2f}")
            st.metric("Min Transaction Cost", f"${insights.get('min_transaction_cost', 0.0):,.2f}")
    else:
        st.warning("No insights available. Please add assets and transactions.")