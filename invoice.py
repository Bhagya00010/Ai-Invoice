
import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import os
import random
from dotenv import load_dotenv
from jinja2 import Template
import re

# Load environment variables
load_dotenv()
API_KEY = st.secrets["GOOGLE_API_KEY"]
if not API_KEY:
    st.error("API key not found. Please check your .env file.")
    st.stop()

genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Failed to load AI model: {str(e)}")
    st.stop()

# Extract invoice details using Gemini
def extract_invoice_details(text, gst_rate):
    prompt = f"""
    Extract invoice details from the following text. Return a JSON object with:
    - date: DD/MM/YYYY
    - customer_name
    - items: list of items with name and price
    - mobile
    - address
    - invoice_number
    - gst_number
    - gst_rate: {gst_rate}
    Text: {text}
    Format as a valid JSON object.
    """
    try:
        response = model.generate_content(prompt)
        json_str = response.text
        json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("No valid JSON found in AI response.")
    except Exception as e:
        st.error(f"Error extracting invoice details: {str(e)}")
        return None

# Generate invoice HTML
def generate_invoice_html(data):
    try:
        with open('invoice_template.html', 'r') as file:
            template = Template(file.read())

        processed_items = []
        subtotal, total_gst = 0, 0
        gst_rate = float(str(data.get('gst_rate', '18')).replace('%', ''))

        for idx, item in enumerate(data.get('items', [])):
            price = st.number_input(f"Price for {item['name']}", min_value=0.0, value=float(item['price']), key=f'price_{idx}')
            gst_amount = (price * gst_rate) / 100
            total = price + gst_amount
            processed_items.append({
                'name': item.get('name', '-'),
                'price': f"{price:.2f}",
                'gst_amount': f"{gst_amount:.2f}",
                'total': f"{total:.2f}"
            })
            subtotal += price
            total_gst += gst_amount

        invoice_id = data.get('invoice_number')
        if not invoice_id or invoice_id.strip() == "-":
            lower = st.session_state.invoice_range.get('lower', 100)
            upper = st.session_state.invoice_range.get('upper', 500)
            invoice_id = str(random.randint(lower, upper)) if upper > lower else datetime.now().strftime('%d%m%Y%H%M%S')

        grand_total = subtotal + total_gst

        return template.render({
            'company_details': st.session_state.company_details,
            'invoice_id': invoice_id,
            'date': data.get('date', datetime.now().strftime('%d/%m/%Y')),
            'customer_name': data.get('customer_name', '-'),
            'address': data.get('address', '-'),
            'mobile': data.get('mobile', '-'),
            'gst_number': data.get('gst_number', '-'),
            'items': processed_items,
            'subtotal': f"{subtotal:.2f}",
            'total_gst': f"{total_gst:.2f}",
            'grand_total': f"{grand_total:.2f}",
            'gst_rate': f"{gst_rate}%"
        })
    except Exception as e:
        st.error(f"Error generating invoice HTML: {str(e)}")
        return "<p>Error generating invoice</p>"

# Navbar Component
def navbar():
    st.markdown("""
        <style>
            .navbar {
                background-color: #0e1117;
                padding: 1rem;
                color: white;
                font-size: 1.2rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .nav-links a {
                margin-left: 1.5rem;
                color: white;
                text-decoration: none;
            }
            .nav-links a:hover {
                text-decoration: underline;
            }
        </style>
        <div class="navbar">
            <div><b>📦 AI Invoice Generator</b></div>
        </div>
    """, unsafe_allow_html=True)

# Footer Component
def footer():
    st.markdown("""
        <style>
            #footer {
                background-color: #0e1117;
                padding: 30px 0;
                color: white;
                font-family: 'Arial', sans-serif;
                position: relative;
                text-align: center;
                opacity: 0;
                animation: fadeIn 1s forwards;
            }
            #footer a {
                color: #00B8A9;
                text-decoration: none;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            #footer a:hover {
                color: #fff;
                text-decoration: underline;
            }
            #footer p {
                margin: 5px 0;
                font-size: 0.9rem;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        </style>
        <div id="footer">
            <p>Made with ❤️ by <b>Bhagya N. Patel</b> | 2025 ©</p>
            <p>
                <a href="https://www.linkedin.com/in/bhagyapatel" target="_blank">LinkedIn</a> | 
                <a href="https://bhagyapatel-portfolio.vercel.app" target="_blank">Portfolio</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

# About the Product Section
def about_section():
    with st.expander("ℹ️ About this Product", expanded=False):
        st.markdown("""
        **AI Invoice Generator** is a powerful Streamlit app that:
        - Uses **Google Gemini** to extract data from raw invoice text
        - Automatically calculates GST and totals
        - Generates a beautiful HTML invoice
        - Allows for manual price correction
        - Designed for freelancers, businesses, and automation

        **Features:**
        - 🧠 Gemini 1.5 Flash AI Integration
        - 📄 PDF-ready Invoice Template
        - 🔧 Custom GST rates and invoice numbers
        - 💼 Company branding

        **Security:**
        - Your data is processed securely
        - API keys are hidden using `.env`
        """)
def landing_page():
    # Set title
    st.title("Welcome to the AI Invoice Generator!")
        # Button for starting the process
    if st.button("Get Started"):
        st.session_state.page = 'company_details'
        st.rerun()

    # Simple, clean design layout
  st.markdown("""
    <div style="text-align: center; margin-top: 40px; background-color: black; padding: 20px; border-radius: 10px;">
        <h2 style="font-size: 28px; color: orange">Automate Your Invoice Generation Process</h2>
        <p style="font-size: 16px; color: white;">Easily generate invoices from raw customer input. Just paste the text, and let AI do the rest!</p>
        <h3 style="font-size: 20px; color: #4CAF50;">Key Features:</h3>
        <ul style="list-style-type: none; padding: 0; text-align: left; font-size: 16px; color: white; display: inline-block;">
            <li>✅ Automatically extracts customer details</li>
            <li>✅ Customize GST rates and invoice number</li>
            <li>✅ Generate professional invoices ready for download</li>
        </ul>
        <br/>
    </div>
    """, unsafe_allow_html=True)


   # How it Works: Simple layout with clean visuals
    st.markdown("""
    <div style="text-align: center; margin-top: 40px;">
        <h3 style="font-size: 22px; color: white;">How It Works</h3>
    </div>
    """, unsafe_allow_html=True)

    # How it Works: Simple layout with clean visuals
    st.markdown("""
    <div style="text-align: center; margin-top: 40px;">
        <h3 style="font-size: 22px; color: white;">How It Works</h3>
    </div>
    """, unsafe_allow_html=True)

    # First row: 3 images
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("static/1.jpg", caption="step-1", width=300)
    with col2:
        st.image("static/2.jpg", caption="step-2", width=300)
    with col3:
        st.image("static/3.jpg", caption="step-3", width=300)

    # Second row: 3 images
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("static/4.jpg", caption="step-4", width=300)
    with col2:
        st.image("static/5.jpg", caption="step-5", width=300)
    with col3:
        st.image("static/6.jpg", caption="step-6", width=300)

    


# Main Function
def main():
    st.set_page_config(layout="wide", page_title="AI Invoice Generator")

    if 'page' not in st.session_state:
        st.session_state.page = 'landing'

    if st.session_state.page == 'landing':
        landing_page()

    elif st.session_state.page == 'company_details':
        st.title("🏢 Company Details")

        with st.form("company_form"):
            name = st.text_input("Company Name *")
            logo = st.text_input("Company Logo URL *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone Number *")
            address = st.text_area("Address (Optional)")

            gst_options = ["5%", "12%", "18%", "28%", "Other"]
            gst_choice = st.selectbox("GST Rate", gst_options)
            gst_manual = st.text_input("Custom GST Rate (if Other)")

            invoice_lower = st.number_input("Invoice Number Lower Range", min_value=0, value=100)
            invoice_upper = st.number_input("Invoice Number Upper Range", min_value=0, value=500)

            submitted = st.form_submit_button("Next ➡")

            if submitted:
                if not all([name, logo, email, phone]):
                    st.warning("Please fill all required fields.")
                else:
                    final_gst = gst_manual if gst_choice == "Other" and gst_manual else gst_choice.replace("%", "")
                    st.session_state.company_details = {
                        "name": name,
                        "logo": logo,
                        "email": email,
                        "phone": phone,
                        "address": address,
                        "gst_rate": final_gst or "18"
                    }
                    st.session_state.gst_rate = final_gst or 18
                    st.session_state.invoice_range = {
                        "lower": invoice_lower,
                        "upper": invoice_upper
                    }
                    st.session_state.page = 'invoice_prompt'
                    st.rerun()

    elif st.session_state.page == 'invoice_prompt':
        st.title("🧾 Customer Invoice Prompt")

        if st.button("⬅ Back"):
            st.session_state.page = 'company_details'
            st.rerun()

        text_input = st.text_area("Paste raw invoice/customer text here:", height=120)

        if st.button("Generate Invoice"):
            if text_input:
                with st.spinner("Extracting and generating invoice..."):
                    invoice_data = extract_invoice_details(text_input, st.session_state.gst_rate)
                    if invoice_data:
                        st.session_state.invoice_data = invoice_data
                        st.session_state.invoice_html = generate_invoice_html(invoice_data)
                        st.session_state.page = 'invoice_result'
                        st.rerun()
            else:
                st.warning("Please enter some invoice details.")

    elif st.session_state.page == 'invoice_result':
        st.title("✅ Generated Invoice")

        if st.button("⬅ Back to Edit Prompt"):
            st.session_state.page = 'invoice_prompt'
            st.rerun()

        st.components.v1.html(st.session_state.invoice_html, height=900)

    footer()

if __name__ == "__main__":
    main()
