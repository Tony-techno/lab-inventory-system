# app.py - Lab Inventory Management System
import streamlit as st
import qrcode
import io
import json
from datetime import datetime

# Initialize session state for inventory data
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'storages': {
            'drawer_a1': {
                'name': 'Drawer A1 - Chemicals',
                'type': 'drawer',
                'location': 'Lab Room 101',
                'items': [
                    {'id': 'chem_001', 'name': 'Sodium Chloride', 'quantity': '500g', 'expiry': '2025-12-31'},
                    {'id': 'chem_002', 'name': 'Distilled Water', 'quantity': '2L', 'expiry': '2026-06-30'}
                ],
                'last_updated': '2024-01-01'
            },
            'cupboard_b2': {
                'name': 'Cupboard B2 - Glassware',
                'type': 'cupboard', 
                'location': 'Lab Room 101',
                'items': [
                    {'id': 'glass_001', 'name': 'Beaker 250ml', 'quantity': '12 pieces', 'expiry': ''},
                    {'id': 'glass_002', 'name': 'Test Tubes', 'quantity': '50 pieces', 'expiry': ''}
                ],
                'last_updated': '2024-01-01'
            },
            'almirah_c3': {
                'name': 'Almirah C3 - Instruments',
                'type': 'almirah',
                'location': 'Lab Room 102', 
                'items': [
                    {'id': 'inst_001', 'name': 'Microscope', 'quantity': '2 units', 'expiry': ''},
                    {'id': 'inst_002', 'name': 'Centrifuge', 'quantity': '1 unit', 'expiry': ''}
                ],
                'last_updated': '2024-01-01'
            }
        }
    }

def generate_qr_code(url):
    """Generate QR code and return bytes"""
    qr = qrcode.QRCode(
        version=8,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    return buf.getvalue()

def main_dashboard():
    """Central dashboard - shows all storages"""
    st.set_page_config(
        page_title="Lab Inventory System",
        page_icon="🔬",
        layout="wide"
    )
    
    st.title("🔬 Lab Inventory Management System")
    st.markdown("---")
    
    # App URL
    app_url = "https://dynamic-qr-system-akma5nenm2jg5fj3tyhfu9.streamlit.app/"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏠 Central Dashboard")
        st.info("Overview of all storage units in the lab")
        
        # Display all storages
        for storage_id, storage in st.session_state.inventory['storages'].items():
            with st.expander(f"📦 {storage['name']} ({storage['type'].title()})", expanded=True):
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.write(f"**Location:** {storage['location']}")
                    st.write(f"**Items:** {len(storage['items'])}")
                    st.write(f"**Last Updated:** {storage['last_updated']}")
                    
                    # Show items preview
                    if storage['items']:
                        st.write("**Items:**")
                        for item in storage['items'][:3]:  # Show first 3 items
                            st.write(f"• {item['name']} ({item['quantity']})")
                        if len(storage['items']) > 3:
                            st.write(f"*... and {len(storage['items']) - 3} more*")
                
                with col_b:
                    storage_url = f"{app_url}?storage={storage_id}"
                    qr_data = generate_qr_code(storage_url)
                    
                    st.download_button(
                        f"📥 {storage['name']} QR",
                        qr_data,
                        f"qr_{storage_id}.png",
                        "image/png",
                        key=f"download_{storage_id}"
                    )
    
    with col2:
        st.subheader("🎯 Central QR Code")
        
        # Generate central QR code
        central_url = app_url
        central_qr = generate_qr_code(central_url)
        
        st.image(central_qr, width=200)
        st.caption("Scan this for central dashboard")
        
        st.download_button(
            "📥 Download Central QR",
            central_qr,
            "qr_central_dashboard.png",
            "image/png",
            key="download_central"
        )
        
        st.subheader("📊 Quick Stats")
        total_storages = len(st.session_state.inventory['storages'])
        total_items = sum(len(storage['items']) for storage in st.session_state.inventory['storages'].values())
        
        st.metric("Total Storages", total_storages)
        st.metric("Total Items", total_items)
        
        st.markdown("---")
        st.subheader("🔧 Management")
        if st.button("➕ Add New Storage"):
            st.session_state.show_add_storage = True
            st.rerun()

def storage_view(storage_id):
    """View for individual storage"""
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.set_page_config(
        page_title=f"{storage['name']}",
        page_icon="📦",
        layout="wide"
    )
    
    # Hide sidebar for clean view
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            .main > div {padding: 2rem 1rem;}
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title(f"📦 {storage['name']}")
        st.write(f"**Type:** {storage['type'].title()} | **Location:** {storage['location']}")
        st.write(f"**Last Updated:** {storage['last_updated']}")
        
        st.markdown("---")
        st.subheader("📋 Items List")
        
        if storage['items']:
            for i, item in enumerate(storage['items']):
                with st.expander(f"🔹 {item['name']} - {item['quantity']}", expanded=True):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(f"**ID:** {item['id']}")
                        if item['expiry']:
                            st.write(f"**Expiry:** {item['expiry']}")
                    with col_b:
                        if st.button(f"✏️ Edit", key=f"edit_{i}"):
                            st.session_state.editing_item = (storage_id, i)
                            st.rerun()
                        if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                            del st.session_state.inventory['storages'][storage_id]['items'][i]
                            st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                            st.rerun()
        else:
            st.info("No items in this storage yet.")
        
        # Add new item
        st.markdown("---")
        st.subheader("➕ Add New Item")
        with st.form(f"add_item_{storage_id}"):
            new_name = st.text_input("Item Name")
            new_quantity = st.text_input("Quantity")
            new_expiry = st.text_input("Expiry Date (optional)")
            
            if st.form_submit_button("Add Item"):
                if new_name and new_quantity:
                    new_id = f"item_{len(storage['items']) + 1:03d}"
                    st.session_state.inventory['storages'][storage_id]['items'].append({
                        'id': new_id,
                        'name': new_name,
                        'quantity': new_quantity,
                        'expiry': new_expiry
                    })
                    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                    st.rerun()
    
    with col2:
        st.subheader("🔗 Navigation")
        app_url = "https://dynamic-qr-system-akma5nenm2jg5fj3tyhfu9.streamlit.app/"
        
        # Current storage QR
        current_url = f"{app_url}?storage={storage_id}"
        current_qr = generate_qr_code(current_url)
        
        st.image(current_qr, width=150)
        st.caption(f"QR for {storage['name']}")
        
        st.download_button(
            "📥 Download This QR",
            current_qr,
            f"qr_{storage_id}.png",
            "image/png"
        )
        
        # Central dashboard link
        central_url = app_url
        st.markdown("---")
        st.subheader("🏠 Go to Central")
        central_qr = generate_qr_code(central_url)
        st.image(central_qr, width=150)
        st.caption("QR for Central Dashboard")
        
        st.download_button(
            "📥 Central QR",
            central_qr,
            "qr_central.png",
            "image/png",
            key="central_from_storage"
        )

def add_storage_view():
    """View for adding new storage"""
    st.set_page_config(page_title="Add Storage", page_icon="➕")
    
    st.title("➕ Add New Storage")
    
    with st.form("add_storage_form"):
        name = st.text_input("Storage Name (e.g., 'Drawer A1 - Chemicals')")
        storage_type = st.selectbox("Storage Type", ["drawer", "cupboard", "almirah", "shelf", "cabinet"])
        location = st.text_input("Location (e.g., 'Lab Room 101')")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("➕ Add Storage", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            st.session_state.show_add_storage = False
            st.rerun()
            
        if submit and name and location:
            # Generate storage ID
            storage_id = f"{storage_type}_{name.lower().replace(' ', '_')}"
            
            # Add to inventory
            st.session_state.inventory['storages'][storage_id] = {
                'name': name,
                'type': storage_type,
                'location': location,
                'items': [],
                'last_updated': datetime.now().strftime("%Y-%m-%d")
            }
            
            st.session_state.show_add_storage = False
            st.success(f"✅ Storage '{name}' added successfully!")
            st.rerun()

def edit_item_view(storage_id, item_index):
    """View for editing an item"""
    st.set_page_config(page_title="Edit Item", page_icon="✏️")
    
    item = st.session_state.inventory['storages'][storage_id]['items'][item_index]
    storage_name = st.session_state.inventory['storages'][storage_id]['name']
    
    st.title(f"✏️ Edit Item - {storage_name}")
    
    with st.form("edit_item_form"):
        name = st.text_input("Item Name", value=item['name'])
        quantity = st.text_input("Quantity", value=item['quantity'])
        expiry = st.text_input("Expiry Date", value=item['expiry'])
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            st.session_state.editing_item = None
            st.rerun()
            
        if submit and name and quantity:
            st.session_state.inventory['storages'][storage_id]['items'][item_index] = {
                'id': item['id'],
                'name': name,
                'quantity': quantity,
                'expiry': expiry
            }
            st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            st.session_state.editing_item = None
            st.success("✅ Item updated successfully!")
            st.rerun()

# Main routing logic
def main():
    try:
        # Check query parameters for routing
        query_params = st.experimental_get_query_params()
        
        # Route to appropriate view
        if 'storage' in query_params:
            storage_id = query_params['storage'][0]
            if storage_id in st.session_state.inventory['storages']:
                storage_view(storage_id)
                return
        
        if hasattr(st.session_state, 'show_add_storage') and st.session_state.show_add_storage:
            add_storage_view()
            return
            
        if hasattr(st.session_state, 'editing_item') and st.session_state.editing_item:
            storage_id, item_index = st.session_state.editing_item
            edit_item_view(storage_id, item_index)
            return
        
        # Default to main dashboard
        main_dashboard()
        
    except Exception as e:
        # Fallback to main dashboard
        main_dashboard()

if __name__ == "__main__":
    main()