import streamlit as st
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
from fpdf import FPDF

# Set page title and icon
st.set_page_config(page_title="Invoice Generator", page_icon=":page_facing_up:")

# Load CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Create a dummy style.css file if it doesn't exist for the code to run without error
if not os.path.exists("style.css"):
    with open("style.css", "w") as f:
        f.write("") # Empty file for now

local_css("style.css")

# Main function
def main():
    st.title("Invoice Generator")
    st.markdown("Create and download professional invoices in PDF format.")

    # Company information
    with st.expander("Company Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name", "Your Company LLC")
            company_address = st.text_area("Company Address", "123 Business St\nCity, State 12345")
        with col2:
            company_phone = st.text_input("Phone", "(123) 456-7890")
            company_email = st.text_input("Email", "billing@company.com")

    # Client information
    with st.expander("Client Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Client Name", "Client Company Inc")
            client_address = st.text_area("Client Address", "456 Client Ave\nCity, State 67890")
        with col2:
            client_phone = st.text_input("Client Phone", "(987) 654-3210")
            client_email = st.text_input("Client Email", "accounts@client.com")

    # Invoice details
    with st.expander("Invoice Details", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            invoice_number = st.text_input("Invoice Number", "INV-0001")
        with col2:
            invoice_date = st.date_input("Invoice Date", datetime.today())
        with col3:
            due_date = st.date_input("Due Date", datetime.today())

    # Items
    st.subheader("Items/Services")
    items = []
    
    # Add item button
    if 'item_count' not in st.session_state:
        st.session_state.item_count = 1

    def add_item():
        st.session_state.item_count += 1

    # Item form
    for i in range(st.session_state.item_count):
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 2])
            with col1:
                description = st.text_input(f"Description {i+1}", key=f"desc_{i}", value=f"Service {i+1}")
            with col2:
                quantity = st.number_input(f"Qty {i+1}", min_value=1, value=1, key=f"qty_{i}")
            with col3:
                # Changed input label to remove Rupee symbol
                rate = st.number_input(f"Rate (INR) {i+1}", min_value=0.0, value=100.0, step=1.0, key=f"rate_{i}")
            
            amount = quantity * rate
            items.append({
                "description": description,
                "quantity": quantity,
                "rate": rate,
                "amount": amount
            })

    st.button("Add Another Item", on_click=add_item)

    # Tax rate
    tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)

    # Calculate totals
    subtotal = sum(item["amount"] for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount

    # Display totals
    st.subheader("Totals")
    col1, col2, col3 = st.columns(3)
    # Changed display to use "INR"
    col1.metric("Subtotal", f"INR {subtotal:,.2f}")
    col2.metric(f"Tax ({tax_rate}%)", f"INR {tax_amount:,.2f}")
    col3.metric("Total", f"INR {total:,.2f}", delta_color="off")

    # Generate PDF
    if st.button("Generate Invoice PDF"):
        try:
            # Create PDF object
            pdf = FPDF()
            pdf.add_page()
            
            # Set font and colors
            pdf.set_font("Arial", 'B', 16)
            pdf.set_text_color(74, 107, 175)  # Blue color for headings
            
            # Company information
            pdf.cell(0, 10, company_name, ln=1)
            pdf.set_font("Arial", '', 12)
            pdf.set_text_color(0, 0, 0)  # Black for regular text
            pdf.multi_cell(0, 6, company_address)
            pdf.cell(0, 6, company_phone, ln=1)
            pdf.cell(0, 6, company_email, ln=1)
            
            # Invoice header
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 14)
            pdf.set_text_color(74, 107, 175)
            pdf.cell(0, 10, "INVOICE", ln=1, align='R')
            pdf.set_font("Arial", '', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, f"Invoice #: {invoice_number}", ln=1, align='R')
            pdf.cell(0, 6, f"Date: {invoice_date.strftime('%B %d, %Y')}", ln=1, align='R')
            pdf.cell(0, 6, f"Due Date: {due_date.strftime('%B %d, %Y')}", ln=1, align='R')
            
            # Client information
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 6, "Bill To:", ln=1)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 6, client_name, ln=1)
            pdf.multi_cell(0, 6, client_address)
            pdf.cell(0, 6, client_phone, ln=1)
            pdf.cell(0, 6, client_email, ln=1)
            
            # Items table
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.set_fill_color(245, 245, 245)  # Light gray for header
            pdf.cell(100, 10, "Description", 1, 0, 'L', 1)
            pdf.cell(20, 10, "Qty", 1, 0, 'L', 1)
            pdf.cell(30, 10, "Rate", 1, 0, 'R', 1)
            pdf.cell(30, 10, "Amount", 1, 1, 'R', 1)
            
            pdf.set_font("Arial", '', 12)
            for item in items:
                pdf.cell(100, 10, item["description"], 1)
                pdf.cell(20, 10, str(item["quantity"]), 1)
                # Changed to use "INR" instead of "₹"
                pdf.cell(30, 10, f"INR {item['rate']:,.2f}", 1, 0, 'R')
                pdf.cell(30, 10, f"INR {item['amount']:,.2f}", 1, 1, 'R')
            # Totals
            pdf.ln(5)
            # Changed to use "INR" instead of "₹"
            pdf.cell(150, 10, "Subtotal:", 0, 0, 'R')
            pdf.cell(30, 10, f"INR {subtotal:,.2f}", 0, 1, 'R')
            if tax_rate > 0:
                pdf.cell(150, 10, f"Tax ({tax_rate}%):", 0, 0, 'R')
                pdf.cell(30, 10, f"INR {tax_amount:,.2f}", 0, 1, 'R')
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(150, 10, "Total:", 0, 0, 'R')
                pdf.cell(30, 10, f"INR {total:,.2f}", 0, 1, 'R')
            # Footer
            pdf.ln(20)
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(119, 119, 119)  # Gray color
            pdf.cell(0, 6, "Thank you for your business!", 0, 1, 'C')
            pdf.cell(0, 6, company_name, 0, 1, 'C')
            
            # Generate PDF bytes
            # Ensure the string is encoded with 'latin-1' before passing to output.
            # This is handled by FPDF internally, but removing the problematic character is key.
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            
            # Download button
            st.download_button(
                label="Download Invoice",
                data=pdf_bytes,
                file_name=f"Invoice_{invoice_number}.pdf",
                mime="application/pdf"
            )
            
            st.success("Invoice generated successfully!")
        except Exception as e:
            st.error(f"Error generating PDF: {e}")

if __name__ == "__main__":
    main()