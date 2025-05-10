# import streamlit as st
# import google.generativeai as genai
# from datetime import datetime
# import json
# import os
# from dotenv import load_dotenv
# from jinja2 import Template
# import re

# # Load environment variables
# load_dotenv()

# # Configure Gemini API
# API_KEY = os.getenv("GOOGLE_API_KEY")
# if not API_KEY:
#     st.error("API key not found. Please check your .env file.")
#     st.stop()

# genai.configure(api_key=API_KEY)

# try:
#     model = genai.GenerativeModel('gemini-1.5-flash')
# except Exception as e:
#     st.error(f"Failed to load AI model: {str(e)}")
#     st.stop()

# def extract_invoice_details(text, gst_rate):
#     prompt = f"""
#     Extract invoice details from the following text. Return a JSON object with these fields:
#     - date: in DD/MM/YYYY format
#     - customer_name
#     - items: list of items with name and price
#     - mobile: phone number if present, else "-"
#     - address: if present, else "-"
#     - invoice_number: if present in text, else "-"
#     - gst_number: if present, else "-"
#     - gst_rate: {gst_rate} (apply this rate to all items)
#     Text: {text}
    
#     Format the response as a valid JSON object.
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         json_str = response.text
#         json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         else:
#             raise ValueError("No valid JSON found in AI response.")
#     except Exception as e:
#         st.error(f"Error extracting invoice details: {str(e)}")
#         return None

# def generate_invoice_html(data):
#     try:
#         with open('invoice_template.html', 'r') as file:
#             template = Template(file.read())
        
#         processed_items = []
#         subtotal = 0
#         total_gst = 0
        
#         gst_rate_str = str(data.get('gst_rate', '18')).replace('%', '')
#         gst_rate = float(gst_rate_str)  # Ensure gst_rate is numeric
        
#         for item in data.get('items', []):
#             price = float(item.get('price', 0))
#             gst_amount = (price * gst_rate) / 100  
#             total = price + gst_amount
#             processed_items.append({
#                 'name': item.get('name', '-'),
#                 'price': f"{price:.2f}",
#                 'gst_amount': f"{gst_amount:.2f}",
#                 'total': f"{total:.2f}"
#             })
#             subtotal += price
#             total_gst += gst_amount
        
#         grand_total = subtotal + total_gst
#         invoice_id = data.get('invoice_number', datetime.now().strftime('%d%m%Y%H%M%S'))
#         return template.render({
#             'company_details': st.session_state.company_details,
#             'invoice_id': invoice_id,
#             'date': data.get('date', datetime.now().strftime('%d/%m/%Y')),
#             'customer_name': data.get('customer_name', '-'),
#             'address': data.get('address', '-'),
#             'mobile': data.get('mobile', '-'),
#             'gst_number': data.get('gst_number', '-'),
#             'items': processed_items,
#             'subtotal': f"{subtotal:.2f}",
#             'total_gst': f"{total_gst:.2f}",
#             'grand_total': f"{grand_total:.2f}",
#             'gst_rate': f"{gst_rate}%"
#         })
#     except Exception as e:
#         st.error(f"Error generating invoice HTML: {str(e)}")
#         return "<p>Error generating invoice</p>"

# def main():
#     st.set_page_config(layout="wide")
    
#     if 'page' not in st.session_state:
#         st.session_state.page = 'company_details'
#     if 'company_details' not in st.session_state:
#         st.session_state.company_details = {}
#     if 'invoice_items' not in st.session_state:
#         st.session_state.invoice_items = []
#     if 'gst_rate' not in st.session_state:
#         st.session_state.gst_rate = 18  # Default GST Rate
    
#     if st.session_state.page == 'company_details':
#         st.title("Company Details")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             company_name = st.text_input("Company Name", st.session_state.company_details.get('name', ''))
#             company_address = st.text_area("Company Address", st.session_state.company_details.get('address', ''))
#             company_email = st.text_input("Company Email", st.session_state.company_details.get('email', ''))
#             gst_number = st.text_input("GST Number", st.session_state.company_details.get('gst_number', ''))
        
#         with col2:
#             company_phone = st.text_input("Company Phone", st.session_state.company_details.get('phone', ''))
#             company_logo = st.text_input("Company Logo URL", st.session_state.company_details.get('logo', ''))
#             gst_rate = st.slider("GST Rate (%)", 0, 28, st.session_state.gst_rate)
        
#         if st.button("Next"):
#             if company_name and company_address and company_email:
#                 st.session_state.company_details = {
#                     'name': company_name,
#                     'address': company_address,
#                     'email': company_email,
#                     'phone': company_phone,
#                     'logo': company_logo,
#                     'gst_number': gst_number
#                 }
#                 st.session_state.gst_rate = gst_rate
#                 st.session_state.page = 'invoice_generator'
#                 st.rerun()
#             else:
#                 st.error("Please fill in all required fields (Company Name, Address, and Email)")
    
#     elif st.session_state.page == 'invoice_generator':
#         st.title("💬 Invoice Generator")
#         if st.button("← Back to Company Details"):
#             st.session_state.page = 'company_details'
#             st.rerun()
        
#         text_input = st.text_area("Enter invoice details:", height=100)
        
#         if st.button("Generate Invoice"):
#             if text_input:
#                 with st.spinner("Generating invoice..."):
#                     invoice_data = extract_invoice_details(text_input, st.session_state.gst_rate)
#                     if invoice_data:
#                         st.session_state.invoice_data = invoice_data
#                         st.session_state.invoice_html = generate_invoice_html(invoice_data)
#             else:
#                 st.warning("Please enter invoice details.")
        
#         if "invoice_html" in st.session_state:
#             st.header("Generated Invoice")
#             st.components.v1.html(st.session_state.invoice_html, height=900)

# if __name__ == "__main__":
#     main()
# import os
# import json
# import re
# from datetime import datetime

# import streamlit as st
# from dotenv import load_dotenv
# from jinja2 import Template
# import google.generativeai as genai

# # ---------- Load Environment and Configure Gemini ----------
# load_dotenv()
# API_KEY = os.getenv("GOOGLE_API_KEY")

# if not API_KEY:
#     st.error("API key not found in .env file.")
#     st.stop()

# try:
#     genai.configure(api_key=API_KEY)
#     model = genai.GenerativeModel('gemini-1.5-flash')
# except Exception as e:
#     st.error(f"Failed to initialize Gemini model: {e}")
#     st.stop()


# # ---------- Extract Invoice Data from Text ----------
# def extract_invoice_details(text, gst_rate):
#     prompt = f"""
#     Extract invoice details from the following text and return a JSON object with:
#     - date (DD/MM/YYYY)
#     - customer_name
#     - items: list of {{ name, price }}
#     - mobile (or "-" if absent)
#     - address (or "-" if absent)
#     - invoice_number (or "-" if absent)
#     - gst_number (or "-" if absent)
#     - gst_rate: {gst_rate}

#     Text: {text}
#     """

#     try:
#         response = model.generate_content(prompt)
#         json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         raise ValueError("No valid JSON found in AI response.")
#     except Exception as e:
#         st.error(f"Failed to parse invoice: {e}")
#         return None


# # ---------- Generate Invoice HTML ----------
# def generate_invoice_html(data):
#     try:
#         with open('invoice_template.html', 'r') as file:
#             template = Template(file.read())

#         gst_rate = float(str(data.get('gst_rate', '18')).replace('%', ''))
#         subtotal, total_gst = 0.0, 0.0
#         processed_items = []

#         for idx, item in enumerate(data.get('items', [])):
#             name = item.get('name', '-')
#             price = st.number_input(f"Price for {name}", value=float(item['price']), min_value=0.0, key=f"item_{idx}")
#             gst_amount = price * gst_rate / 100
#             total = price + gst_amount

#             processed_items.append({
#                 'name': name,
#                 'price': f"{price:.2f}",
#                 'gst_amount': f"{gst_amount:.2f}",
#                 'total': f"{total:.2f}"
#             })

#             subtotal += price
#             total_gst += gst_amount

#         grand_total = subtotal + total_gst
#         invoice_id = data.get('invoice_number') or datetime.now().strftime('%d%m%Y%H%M%S')

#         return template.render({
#             'company_details': st.session_state.company_details,
#             'invoice_id': invoice_id,
#             'date': data.get('date', datetime.now().strftime('%d/%m/%Y')),
#             'customer_name': data.get('customer_name', '-'),
#             'address': data.get('address', '-'),
#             'mobile': data.get('mobile', '-'),
#             'gst_number': data.get('gst_number', '-'),
#             'items': processed_items,
#             'subtotal': f"{subtotal:.2f}",
#             'total_gst': f"{total_gst:.2f}",
#             'grand_total': f"{grand_total:.2f}",
#             'gst_rate': f"{gst_rate}%"
#         })

#     except Exception as e:
#         st.error(f"Error creating invoice HTML: {e}")
#         return "<p>Error generating invoice</p>"


# # ---------- Main App ----------
# def main():
#     st.set_page_config(layout="wide")
#     st.title("🧾 Smart Invoice Generator")

#     # Initialize session state
#     st.session_state.setdefault('company_details', {})
#     st.session_state.setdefault('gst_rate', 18)
#     st.session_state.setdefault('invoice_html', None)
#     st.session_state.setdefault('invoice_data', None)

#     # Text input
#     st.subheader("Step 1: Paste Your Invoice Text")
#     invoice_text = st.text_area("Invoice Details", height=150)

#     # GST Rate
#     st.session_state.gst_rate = st.slider("GST Rate (%)", min_value=0, max_value=28, value=st.session_state.gst_rate)

#     if st.button("Generate Invoice"):
#         if invoice_text.strip():
#             with st.spinner("Extracting and formatting invoice..."):
#                 data = extract_invoice_details(invoice_text, st.session_state.gst_rate)
#                 if data:
#                     st.session_state.invoice_data = data
#                     st.session_state.invoice_html = generate_invoice_html(data)
#         else:
#             st.warning("Please enter invoice text above.")

#     # Show invoice preview
#     if st.session_state.invoice_html:
#         st.subheader("📄 Invoice Preview")
#         if st.button("Regenerate Preview"):
#             st.session_state.invoice_html = generate_invoice_html(st.session_state.invoice_data)
#         st.components.v1.html(st.session_state.invoice_html, height=900)


# if __name__ == "__main__":
#     main()
# import streamlit as st
# import google.generativeai as genai
# from datetime import datetime
# import json
# import os
# from dotenv import load_dotenv
# from jinja2 import Template
# import re

# # Load environment variables
# load_dotenv()

# # Configure Gemini API
# API_KEY = os.getenv("GOOGLE_API_KEY")
# if not API_KEY:
#     st.error("API key not found. Please check your .env file.")
#     st.stop()

# genai.configure(api_key=API_KEY)

# try:
#     model = genai.GenerativeModel('gemini-1.5-flash')
# except Exception as e:
#     st.error(f"Failed to load AI model: {str(e)}")
#     st.stop()

# # Step 1: Extract invoice details using Gemini
# def extract_invoice_details(text, gst_rate):
#     prompt = f"""
#     Extract invoice details from the following text. Return a JSON object with these fields:
#     - date: in DD/MM/YYYY format
#     - customer_name
#     - items: list of items with name and price
#     - mobile: phone number if present, else "-"
#     - address: if present, else "-"
#     - invoice_number: if present in text, else "-"
#     - gst_number: if present, else "-"
#     - gst_rate: {gst_rate} (apply this rate to all items)
#     Text: {text}
#     Format the response as a valid JSON object.
#     """
#     try:
#         response = model.generate_content(prompt)
#         json_str = response.text
#         json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         else:
#             raise ValueError("No valid JSON found in AI response.")
#     except Exception as e:
#         st.error(f"Error extracting invoice details: {str(e)}")
#         return None

# # Step 2: Generate invoice HTML
# def generate_invoice_html(data):
#     try:
#         with open('invoice_template.html', 'r') as file:
#             template = Template(file.read())
        
#         processed_items = []
#         subtotal = 0
#         total_gst = 0
#         gst_rate = float(str(data.get('gst_rate', '18')).replace('%', ''))

#         for idx, item in enumerate(data.get('items', [])):
#             price = st.number_input(f"Price for {item['name']}", min_value=0.0, value=float(item['price']), key=f'price_{idx}')
#             gst_amount = (price * gst_rate) / 100
#             total = price + gst_amount
#             processed_items.append({
#                 'name': item.get('name', '-'),
#                 'price': f"{price:.2f}",
#                 'gst_amount': f"{gst_amount:.2f}",
#                 'total': f"{total:.2f}"
#             })
#             subtotal += price
#             total_gst += gst_amount

#         grand_total = subtotal + total_gst
#         invoice_id = data.get('invoice_number', datetime.now().strftime('%d%m%Y%H%M%S'))

#         return template.render({
#             'company_details': st.session_state.company_details,
#             'invoice_id': invoice_id,
#             'date': data.get('date', datetime.now().strftime('%d/%m/%Y')),
#             'customer_name': data.get('customer_name', '-'),
#             'address': data.get('address', '-'),
#             'mobile': data.get('mobile', '-'),
#             'gst_number': data.get('gst_number', '-'),
#             'items': processed_items,
#             'subtotal': f"{subtotal:.2f}",
#             'total_gst': f"{total_gst:.2f}",
#             'grand_total': f"{grand_total:.2f}",
#             'gst_rate': f"{gst_rate}%"
#         })
#     except Exception as e:
#         st.error(f"Error generating invoice HTML: {str(e)}")
#         return "<p>Error generating invoice</p>"

# # Main Function with Multi-Step Flow
# def main():
#     st.set_page_config(layout="wide")
    
#     if 'page' not in st.session_state:
#         st.session_state.page = 'company_details'

#     if st.session_state.page == 'company_details':
#         st.title("🏢 Company Details")

#         with st.form("company_form"):
#             name = st.text_input("Company Name *", value="", placeholder="e.g., XYZ Pvt Ltd")
#             logo = st.text_input("Company Logo URL *", value="", placeholder="URL of logo image")
#             email = st.text_input("Email *", value="", placeholder="e.g., contact@xyz.com")
#             phone = st.text_input("Phone Number *", value="", placeholder="e.g., +91 9876543210")
#             address = st.text_area("Address (Optional)", placeholder="Company address...")
            
#             gst_options = ["5%", "12%", "18%", "28%", "Other"]
#             gst_choice = st.selectbox("GST Rate", gst_options)
#             gst_manual = st.text_input("Custom GST Rate (only if 'Other')", placeholder="e.g., 15")

#             submitted = st.form_submit_button("Next ➡")

#             if submitted:
#                 if not all([name, logo, email, phone]):
#                     st.warning("Please fill all required fields.")
#                 else:
#                     final_gst = gst_manual if gst_choice == "Other" and gst_manual else gst_choice.replace("%", "")
#                     st.session_state.company_details = {
#                         "name": name,
#                         "logo": logo,
#                         "email": email,
#                         "phone": phone,
#                         "address": address,
#                         "gst_rate": final_gst or "18"
#                     }
#                     st.session_state.gst_rate = final_gst or 18
#                     st.session_state.page = 'invoice_prompt'
#                     st.rerun()

#     elif st.session_state.page == 'invoice_prompt':
#         st.title("🧾 Customer Invoice Prompt")

#         if st.button("⬅ Back"):
#             st.session_state.page = 'company_details'
#             st.rerun()

#         text_input = st.text_area("Paste raw invoice/customer text here:", height=120)

#         if st.button("Generate Invoice"):
#             if text_input:
#                 with st.spinner("Extracting and generating invoice..."):
#                     invoice_data = extract_invoice_details(text_input, st.session_state.gst_rate)
#                     if invoice_data:
#                         st.session_state.invoice_data = invoice_data
#                         st.session_state.invoice_html = generate_invoice_html(invoice_data)
#                         st.session_state.page = 'invoice_result'
#                         st.rerun()
#             else:
#                 st.warning("Please enter some invoice details.")

#     elif st.session_state.page == 'invoice_result':
#         st.title("✅ Generated Invoice")
        
#         if st.button("🔁 Regenerate Invoice"):
#             st.session_state.invoice_html = generate_invoice_html(st.session_state.invoice_data)

#         if st.button("⬅ Back to Edit Prompt"):
#             st.session_state.page = 'invoice_prompt'
#             st.rerun()

#         st.components.v1.html(st.session_state.invoice_html, height=900)

# if __name__ == "__main__":
#     main()
# import streamlit as st
# import google.generativeai as genai
# from datetime import datetime
# import json
# import os
# from dotenv import load_dotenv
# from jinja2 import Template
# import re

# # Load environment variables
# load_dotenv()

# # Configure Gemini API
# API_KEY = os.getenv("GOOGLE_API_KEY")
# if not API_KEY:
#     st.error("API key not found. Please check your .env file.")
#     st.stop()

# genai.configure(api_key=API_KEY)

# try:
#     model = genai.GenerativeModel('gemini-1.5-flash')
# except Exception as e:
#     st.error(f"Failed to load AI model: {str(e)}")
#     st.stop()

# # Step 1: Extract invoice details using Gemini
# def extract_invoice_details(text, gst_rate):
#     prompt = f"""
#     Extract invoice details from the following text. Return a JSON object with these fields:
#     - date: in DD/MM/YYYY format
#     - customer_name
#     - items: list of items with name and price
#     - mobile: phone number if present, else "-"
#     - address: if present, else "-"
#     - invoice_number: if present in text, else "-"
#     - gst_number: if present, else "-"
#     - gst_rate: {gst_rate} (apply this rate to all items)
#     Text: {text}
#     Format the response as a valid JSON object.
#     """
#     try:
#         response = model.generate_content(prompt)
#         json_str = response.text
#         json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         else:
#             raise ValueError("No valid JSON found in AI response.")
#     except Exception as e:
#         st.error(f"Error extracting invoice details: {str(e)}")
#         return None

# # Step 2: Generate invoice HTML
# def generate_invoice_html(data):
#     try:
#         with open('invoice_template.html', 'r') as file:
#             template = Template(file.read())
        
#         processed_items = []
#         subtotal = 0
#         total_gst = 0
#         gst_rate = float(str(data.get('gst_rate', '18')).replace('%', ''))

#         for idx, item in enumerate(data.get('items', [])):
#             price = st.number_input(f"Price for {item['name']}", min_value=0.0, value=float(item['price']), key=f'price_{idx}')
#             gst_amount = (price * gst_rate) / 100
#             total = price + gst_amount
#             processed_items.append({
#                 'name': item.get('name', '-'),
#                 'price': f"{price:.2f}",
#                 'gst_amount': f"{gst_amount:.2f}",
#                 'total': f"{total:.2f}"
#             })
#             subtotal += price
#             total_gst += gst_amount

#         grand_total = subtotal + total_gst
#         invoice_id = data.get('invoice_number') or datetime.now().strftime('%d%m%Y%H%M%S')

#         return template.render({
#             'company_details': st.session_state.company_details,
#             'invoice_id': invoice_id,
#             'date': data.get('date', datetime.now().strftime('%d/%m/%Y')),
#             'customer_name': data.get('customer_name', '-'),
#             'address': data.get('address', '-'),
#             'mobile': data.get('mobile', '-'),
#             'gst_number': data.get('gst_number', '-'),
#             'items': processed_items,
#             'subtotal': f"{subtotal:.2f}",
#             'total_gst': f"{total_gst:.2f}",
#             'grand_total': f"{grand_total:.2f}",
#             'gst_rate': f"{gst_rate}%"
#         })
#     except Exception as e:
#         st.error(f"Error generating invoice HTML: {str(e)}")
#         return "<p>Error generating invoice</p>"

# # Main Function with Multi-Step Flow
# def main():
#     st.set_page_config(layout="wide")
    
#     if 'page' not in st.session_state:
#         st.session_state.page = 'company_details'

#     if st.session_state.page == 'company_details':
#         st.title("🏢 Company Details")

#         with st.form("company_form"):
#             name = st.text_input("Company Name *", value="", placeholder="e.g., XYZ Pvt Ltd")
#             logo = st.text_input("Company Logo URL *", value="", placeholder="URL of logo image")
#             email = st.text_input("Email *", value="", placeholder="e.g., contact@xyz.com")
#             phone = st.text_input("Phone Number *", value="", placeholder="e.g., +91 9876543210")
#             address = st.text_area("Address (Optional)", placeholder="Company address...")

#             gst_options = ["5%", "12%", "18%", "28%", "Other"]
#             gst_choice = st.selectbox("GST Rate", gst_options)
#             gst_manual = st.text_input("Custom GST Rate (only if 'Other')", placeholder="e.g., 15")

#             submitted = st.form_submit_button("Next ➡")

#             if submitted:
#                 if not all([name, logo, email, phone]):
#                     st.warning("Please fill all required fields.")
#                 else:
#                     final_gst = gst_manual if gst_choice == "Other" and gst_manual else gst_choice.replace("%", "")
#                     st.session_state.company_details = {
#                         "name": name,
#                         "logo": logo,
#                         "email": email,
#                         "phone": phone,
#                         "address": address,
#                         "gst_rate": final_gst or "18"
#                     }
#                     st.session_state.gst_rate = final_gst or 18
#                     st.session_state.page = 'invoice_prompt'
#                     st.rerun()

#     elif st.session_state.page == 'invoice_prompt':
#         st.title("🧾 Customer Invoice Prompt")

#         if st.button("⬅ Back"):
#             st.session_state.page = 'company_details'
#             st.rerun()

#         # Invoice number logic
#         st.subheader("Invoice Number (Optional)")
#         invoice_options = ["", "INV1001", "INV1002", "INV1003"]
#         selected_invoice = st.selectbox("Select Invoice Number", invoice_options, index=0)
#         manual_invoice = st.text_input("Or enter manually")

#         if selected_invoice:
#             invoice_number_final = selected_invoice
#         elif manual_invoice:
#             invoice_number_final = manual_invoice
#         else:
#             invoice_number_final = datetime.now().strftime('%d%m%Y%H%M%S')

#         text_input = st.text_area("Paste raw invoice/customer text here:", height=120)

#         if st.button("Generate Invoice"):
#             if text_input:
#                 with st.spinner("Extracting and generating invoice..."):
#                     invoice_data = extract_invoice_details(text_input, st.session_state.gst_rate)
#                     if invoice_data:
#                         invoice_data['invoice_number'] = invoice_number_final
#                         st.session_state.invoice_data = invoice_data
#                         st.session_state.invoice_html = generate_invoice_html(invoice_data)
#                         st.session_state.page = 'invoice_result'
#                         st.rerun()
#             else:
#                 st.warning("Please enter some invoice details.")

#     elif st.session_state.page == 'invoice_result':
#         st.title("✅ Generated Invoice")
        
#         if st.button("🔁 Regenerate Invoice"):
#             st.session_state.invoice_html = generate_invoice_html(st.session_state.invoice_data)

#         if st.button("⬅ Back to Edit Prompt"):
#             st.session_state.page = 'invoice_prompt'
#             st.rerun()

#         st.components.v1.html(st.session_state.invoice_html, height=900)

# if __name__ == "__main__":
#     main()
# import streamlit as st
# import google.generativeai as genai
# from datetime import datetime
# import json
# import os
# import random
# from dotenv import load_dotenv
# from jinja2 import Template
# import re

# # Load environment variables
# load_dotenv()

# # Configure Gemini API
# API_KEY = os.getenv("GOOGLE_API_KEY")
# if not API_KEY:
#     st.error("API key not found. Please check your .env file.")
#     st.stop()

# genai.configure(api_key=API_KEY)

# try:
#     model = genai.GenerativeModel('gemini-1.5-flash')
# except Exception as e:
#     st.error(f"Failed to load AI model: {str(e)}")
#     st.stop()

# # Step 1: Extract invoice details using Gemini
# def extract_invoice_details(text, gst_rate):
#     prompt = f"""
#     Extract invoice details from the following text. Return a JSON object with these fields:
#     - date: in DD/MM/YYYY format
#     - customer_name
#     - items: list of items with name and price
#     - mobile: phone number if present, else "-"
#     - address: if present, else "-"
#     - invoice_number: if present in text, else "-"
#     - gst_number: if present, else "-"
#     - gst_rate: {gst_rate} (apply this rate to all items)
#     Text: {text}
#     Format the response as a valid JSON object.
#     """
#     try:
#         response = model.generate_content(prompt)
#         json_str = response.text
#         json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         else:
#             raise ValueError("No valid JSON found in AI response.")
#     except Exception as e:
#         st.error(f"Error extracting invoice details: {str(e)}")
#         return None

# # Step 2: Generate invoice HTML
# def generate_invoice_html(data):
#     try:
#         with open('invoice_template.html', 'r') as file:
#             template = Template(file.read())
        
#         processed_items = []
#         subtotal = 0
#         total_gst = 0
#         gst_rate = float(str(data.get('gst_rate', '18')).replace('%', ''))

#         for idx, item in enumerate(data.get('items', [])):
#             price = st.number_input(f"Price for {item['name']}", min_value=0.0, value=float(item['price']), key=f'price_{idx}')
#             gst_amount = (price * gst_rate) / 100
#             total = price + gst_amount
#             processed_items.append({
#                 'name': item.get('name', '-'),
#                 'price': f"{price:.2f}",
#                 'gst_amount': f"{gst_amount:.2f}",
#                 'total': f"{total:.2f}"
#             })
#             subtotal += price
#             total_gst += gst_amount

#         # Determine invoice number
#         invoice_id = data.get('invoice_number')
#         if not invoice_id or invoice_id.strip() == "-":
#             lower = st.session_state.invoice_range.get('lower', 100)
#             upper = st.session_state.invoice_range.get('upper', 500)
#             if upper > lower:
#                 invoice_id = str(random.randint(lower, upper))
#             else:
#                 invoice_id = datetime.now().strftime('%d%m%Y%H%M%S')

#         grand_total = subtotal + total_gst

#         return template.render({
#             'company_details': st.session_state.company_details,
#             'invoice_id': invoice_id,
#             'date': data.get('date', datetime.now().strftime('%d/%m/%Y')),
#             'customer_name': data.get('customer_name', '-'),
#             'address': data.get('address', '-'),
#             'mobile': data.get('mobile', '-'),
#             'gst_number': data.get('gst_number', '-'),
#             'items': processed_items,
#             'subtotal': f"{subtotal:.2f}",
#             'total_gst': f"{total_gst:.2f}",
#             'grand_total': f"{grand_total:.2f}",
#             'gst_rate': f"{gst_rate}%"
#         })
#     except Exception as e:
#         st.error(f"Error generating invoice HTML: {str(e)}")
#         return "<p>Error generating invoice</p>"

# # Main Function with Multi-Step Flow
# def main():
#     st.set_page_config(layout="wide")
    
#     if 'page' not in st.session_state:
#         st.session_state.page = 'company_details'

#     if st.session_state.page == 'company_details':
#         st.title("🏢 Company Details")

#         with st.form("company_form"):
#             name = st.text_input("Company Name *", value="", placeholder="e.g., XYZ Pvt Ltd")
#             logo = st.text_input("Company Logo URL *", value="", placeholder="URL of logo image")
#             email = st.text_input("Email *", value="", placeholder="e.g., contact@xyz.com")
#             phone = st.text_input("Phone Number *", value="", placeholder="e.g., +91 9876543210")
#             address = st.text_area("Address (Optional)", placeholder="Company address...")

#             gst_options = ["5%", "12%", "18%", "28%", "Other"]
#             gst_choice = st.selectbox("GST Rate", gst_options)
#             gst_manual = st.text_input("Custom GST Rate (only if 'Other')", placeholder="e.g., 15")

#             invoice_lower = st.number_input("Invoice Number Lower Range", min_value=0, value=100)
#             invoice_upper = st.number_input("Invoice Number Upper Range", min_value=0, value=500)

#             if invoice_upper <= invoice_lower:
#                 st.warning("Upper range must be greater than lower range.")

#             submitted = st.form_submit_button("Next ➡")

#             if submitted:
#                 if not all([name, logo, email, phone]):
#                     st.warning("Please fill all required fields.")
#                 else:
#                     final_gst = gst_manual if gst_choice == "Other" and gst_manual else gst_choice.replace("%", "")
#                     st.session_state.company_details = {
#                         "name": name,
#                         "logo": logo,
#                         "email": email,
#                         "phone": phone,
#                         "address": address,
#                         "gst_rate": final_gst or "18"
#                     }
#                     st.session_state.gst_rate = final_gst or 18
#                     st.session_state.invoice_range = {
#                         "lower": invoice_lower,
#                         "upper": invoice_upper
#                     }
#                     st.session_state.page = 'invoice_prompt'
#                     st.rerun()

#     elif st.session_state.page == 'invoice_prompt':
#         st.title("🧾 Customer Invoice Prompt")

#         if st.button("⬅ Back"):
#             st.session_state.page = 'company_details'
#             st.rerun()

#         text_input = st.text_area("Paste raw invoice/customer text here:", height=120)

#         if st.button("Generate Invoice"):
#             if text_input:
#                 with st.spinner("Extracting and generating invoice..."):
#                     invoice_data = extract_invoice_details(text_input, st.session_state.gst_rate)
#                     if invoice_data:
#                         st.session_state.invoice_data = invoice_data
#                         st.session_state.invoice_html = generate_invoice_html(invoice_data)
#                         st.session_state.page = 'invoice_result'
#                         st.rerun()
#             else:
#                 st.warning("Please enter some invoice details.")

#     elif st.session_state.page == 'invoice_result':
#         st.title("✅ Generated Invoice")
        
      

#         if st.button("⬅ Back to Edit Prompt"):
#             st.session_state.page = 'invoice_prompt'
#             st.rerun()

#         st.components.v1.html(st.session_state.invoice_html, height=900)

# if __name__ == "__main__":
#     main()
# import streamlit as st
# import google.generativeai as genai
# from datetime import datetime
# import json
# import os
# import random
# from dotenv import load_dotenv
# from jinja2 import Template
# import re

# # Load environment variables
# load_dotenv()
# API_KEY = os.getenv("GOOGLE_API_KEY")
# if not API_KEY:
#     st.error("API key not found. Please check your .env file.")
#     st.stop()

# genai.configure(api_key=API_KEY)

# try:
#     model = genai.GenerativeModel('gemini-1.5-flash')
# except Exception as e:
#     st.error(f"Failed to load AI model: {str(e)}")
#     st.stop()

# # Extract invoice details using Gemini
# def extract_invoice_details(text, gst_rate):
#     prompt = f"""
#     Extract invoice details from the following text. Return a JSON object with:
#     - date: DD/MM/YYYY
#     - customer_name
#     - items: list of items with name and price
#     - mobile
#     - address
#     - invoice_number
#     - gst_number
#     - gst_rate: {gst_rate}
#     Text: {text}
#     Format as a valid JSON object.
#     """
#     try:
#         response = model.generate_content(prompt)
#         json_str = response.text
#         json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         else:
#             raise ValueError("No valid JSON found in AI response.")
#     except Exception as e:
#         st.error(f"Error extracting invoice details: {str(e)}")
#         return None

# # Generate invoice HTML
# def generate_invoice_html(data):
#     try:
#         with open('invoice_template.html', 'r') as file:
#             template = Template(file.read())

#         processed_items = []
#         subtotal, total_gst = 0, 0
#         gst_rate = float(str(data.get('gst_rate', '18')).replace('%', ''))

#         for idx, item in enumerate(data.get('items', [])):
#             price = st.number_input(f"Price for {item['name']}", min_value=0.0, value=float(item['price']), key=f'price_{idx}')
#             gst_amount = (price * gst_rate) / 100
#             total = price + gst_amount
#             processed_items.append({
#                 'name': item.get('name', '-'),
#                 'price': f"{price:.2f}",
#                 'gst_amount': f"{gst_amount:.2f}",
#                 'total': f"{total:.2f}"
#             })
#             subtotal += price
#             total_gst += gst_amount

#         invoice_id = data.get('invoice_number')
#         if not invoice_id or invoice_id.strip() == "-":
#             lower = st.session_state.invoice_range.get('lower', 100)
#             upper = st.session_state.invoice_range.get('upper', 500)
#             invoice_id = str(random.randint(lower, upper)) if upper > lower else datetime.now().strftime('%d%m%Y%H%M%S')

#         grand_total = subtotal + total_gst

#         return template.render({
#             'company_details': st.session_state.company_details,
#             'invoice_id': invoice_id,
#             'date': data.get('date', datetime.now().strftime('%d/%m/%Y')),
#             'customer_name': data.get('customer_name', '-'),
#             'address': data.get('address', '-'),
#             'mobile': data.get('mobile', '-'),
#             'gst_number': data.get('gst_number', '-'),
#             'items': processed_items,
#             'subtotal': f"{subtotal:.2f}",
#             'total_gst': f"{total_gst:.2f}",
#             'grand_total': f"{grand_total:.2f}",
#             'gst_rate': f"{gst_rate}%"
#         })
#     except Exception as e:
#         st.error(f"Error generating invoice HTML: {str(e)}")
#         return "<p>Error generating invoice</p>"

# # Navbar Component
# def navbar():
#     st.markdown("""
#         <style>
#             .navbar {
#                 background-color: #0e1117;
#                 padding: 1rem;
#                 color: white;
#                 font-size: 1.2rem;
#                 display: flex;
#                 justify-content: space-between;
#                 align-items: center;
#             }
#             .nav-links a {
#                 margin-left: 1.5rem;
#                 color: white;
#                 text-decoration: none;
#             }
#             .nav-links a:hover {
#                 text-decoration: underline;
#             }
#         </style>
#         <div class="navbar">
#             <div><b>📦 AI Invoice Generator</b></div>
    
#         </div>
#     """, unsafe_allow_html=True)

# # Footer Component
# def footer():
#     st.markdown("""
#         <style>
#             /* Footer Styling */
#             #footer {
#                 background-color: #0e1117;
#                 padding: 30px 0;
#                 color: white;
#                 font-family: 'Arial', sans-serif;
#                 position: relative;
#                 text-align: center;
#                 opacity: 0;
#                 animation: fadeIn 1s forwards;
#             }

#             /* Hover effects on links */
#             #footer a {
#                 color: #00B8A9;
#                 text-decoration: none;
#                 font-weight: bold;
#                 transition: all 0.3s ease;
#             }

#             #footer a:hover {
#                 color: #fff;
#                 text-decoration: underline;
#             }

#             /* Footer text styling */
#             #footer p {
#                 margin: 5px 0;
#                 font-size: 0.9rem;
#             }

#             /* Fade-in animation */
#             @keyframes fadeIn {
#                 from { opacity: 0; }
#                 to { opacity: 1; }
#             }
#         </style>

#         <div id="footer">
#             <p>Made with ❤️ by <b>Bhagya N. Patel</b> | 2025 ©</p>
#             <p>
#                 <a href="https://www.linkedin.com/in/bhagyapatel" target="_blank">LinkedIn</a> | 
#                 <a href="https://bhagyapatel-portfolio.vercel.app" target="_blank">PortFlolio</a>
#             </p>
#         </div>
#     """, unsafe_allow_html=True)


# # About the Product Section
# def about_section():
#     with st.expander("ℹ️ About this Product", expanded=False):
#         st.markdown("""
#         **AI Invoice Generator** is a powerful Streamlit app that:
#         - Uses **Google Gemini** to extract data from raw invoice text
#         - Automatically calculates GST and totals
#         - Generates a beautiful HTML invoice
#         - Allows for manual price correction
#         - Designed for freelancers, businesses, and automation

#         **Features:**
#         - 🧠 Gemini 1.5 Flash AI Integration
#         - 📄 PDF-ready Invoice Template
#         - 🔧 Custom GST rates and invoice numbers
#         - 💼 Company branding

#         **Security:**
#         - Your data is processed securely
#         - API keys are hidden using `.env`
#         """)

# # Main Function
# def main():
#     st.set_page_config(layout="wide", page_title="AI Invoice Generator")

#     navbar()
#     about_section()

#     if 'page' not in st.session_state:
#         st.session_state.page = 'company_details'

#     if st.session_state.page == 'company_details':
#         st.title("🏢 Company Details")

#         with st.form("company_form"):
#             name = st.text_input("Company Name *")
#             logo = st.text_input("Company Logo URL *")
#             email = st.text_input("Email *")
#             phone = st.text_input("Phone Number *")
#             address = st.text_area("Address (Optional)")

#             gst_options = ["5%", "12%", "18%", "28%", "Other"]
#             gst_choice = st.selectbox("GST Rate", gst_options)
#             gst_manual = st.text_input("Custom GST Rate (if Other)")

#             invoice_lower = st.number_input("Invoice Number Lower Range", min_value=0, value=100)
#             invoice_upper = st.number_input("Invoice Number Upper Range", min_value=0, value=500)

#             submitted = st.form_submit_button("Next ➡")

#             if submitted:
#                 if not all([name, logo, email, phone]):
#                     st.warning("Please fill all required fields.")
#                 else:
#                     final_gst = gst_manual if gst_choice == "Other" and gst_manual else gst_choice.replace("%", "")
#                     st.session_state.company_details = {
#                         "name": name,
#                         "logo": logo,
#                         "email": email,
#                         "phone": phone,
#                         "address": address,
#                         "gst_rate": final_gst or "18"
#                     }
#                     st.session_state.gst_rate = final_gst or 18
#                     st.session_state.invoice_range = {
#                         "lower": invoice_lower,
#                         "upper": invoice_upper
#                     }
#                     st.session_state.page = 'invoice_prompt'
#                     st.rerun()

#     elif st.session_state.page == 'invoice_prompt':
#         st.title("🧾 Customer Invoice Prompt")

#         if st.button("⬅ Back"):
#             st.session_state.page = 'company_details'
#             st.rerun()

#         text_input = st.text_area("Paste raw invoice/customer text here:", height=120)

#         if st.button("Generate Invoice"):
#             if text_input:
#                 with st.spinner("Extracting and generating invoice..."):
#                     invoice_data = extract_invoice_details(text_input, st.session_state.gst_rate)
#                     if invoice_data:
#                         st.session_state.invoice_data = invoice_data
#                         st.session_state.invoice_html = generate_invoice_html(invoice_data)
#                         st.session_state.page = 'invoice_result'
#                         st.rerun()
#             else:
#                 st.warning("Please enter some invoice details.")

#     elif st.session_state.page == 'invoice_result':
#         st.title("✅ Generated Invoice")

#         if st.button("⬅ Back to Edit Prompt"):
#             st.session_state.page = 'invoice_prompt'
#             st.rerun()

#         st.components.v1.html(st.session_state.invoice_html, height=900)

#     footer()

# if __name__ == "__main__":
#     main()
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
    <div style="text-align: center; margin-top: 40px;">
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
