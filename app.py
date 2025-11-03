# app.py - Enhanced Lab Inventory Management System
import streamlit as st
import qrcode
import io
import json
from datetime import datetime
import pandas as pd

# Initialize session state for inventory data
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'storages': {
            'drawer_a1': {
                'name': 'Drawer A1 - Chemicals',
                'type': 'drawer',
                'location': 'Lab Room 101',
                'description': 'Chemical storage with safety lock',
                'items': [
                    {'id': 'chem_001', 'name': 'Sodium Chloride', 'quantity': '500g', 'category': 'Chemical', 'expiry': '2025-12-31', 'status': 'In Stock'},
                    {'id': 'chem_002', 'name': 'Distilled Water', 'quantity': '2L', 'category': 'Chemical', 'expiry': '2026-06-30', 'status': 'In Stock'}
                ],
                'last_updated': '2024-01-01'
            },
            'cupboard_b2': {
                'name': 'Cupboard B2 - Glassware',
                'type': 'cupboard', 
                'location': 'Lab Room 101',
                'description': 'Glassware and lab equipment',
                'items': [
                    {'id': 'glass_001', 'name': 'Beaker 250ml', 'quantity': '12 pieces', 'category': 'Glassware', 'expiry': '', 'status': 'In Stock'},
                    {'id': 'glass_002', 'name': 'Test Tubes', 'quantity': '50 pieces', 'category': 'Glassware', 'expiry': '', 'status': 'Low Stock'}
                ],
                'last_updated': '2024-01-01'
            },
            'almirah_c3': {
                'name': 'Almirah C3 - Instruments',
                'type': 'almirah',
                'location': 'Lab Room 102',
                'description': 'Precision instruments and devices', 
                'items': [
                    {'id': 'inst_001', 'name': 'Microscope', 'quantity': '2 units', 'category': 'Instrument', 'expiry': '', 'status': 'In Stock'},
                    {'id': 'inst_002', 'name': 'Centrifuge', 'quantity': '1 unit', 'category': 'Instrument', 'expiry': '', 'status': 'In Use'}
                ],
                'last_updated': '2024-01-01'
            }
        },
        'categories': ['Chemical', 'Glassware', 'Instrument', 'Equipment', 'Consumable', 'Tool'],
        'status_options': ['In Stock', 'Low Stock', 'Out of Stock', 'In Use', 'Maintenance']
    }

def generate_qr_code(url):
    """Generate QR code and return bytes"""
    try:
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
    except Exception as e:
        st.error(f"QR generation error: {e}")
        return None

def main_dashboard():
    """Central dashboard - shows all storages"""
    st.set_page_config(
        page_title="Lab Inventory System",
        page_icon="🔬",
        layout="wide"
    )
    
    st.title("🔬 Lab Inventory Management System")
    st.markdown("---")
    
    # CORRECTED: Use current app URL
    app_url = "https://lab-inventory-system-wgghkexsaoemscwwqxxfrj.streamlit.app/"
    
    # Header with quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    total_storages = len(st.session_state.inventory['storages'])
    total_items = sum(len(storage['items']) for storage in st.session_state.inventory['storages'].values())
    
    with col1:
        st.metric("🏠 Total Storages", total_storages)
    with col2:
        st.metric("📦 Total Items", total_items)
    with col3:
        low_stock_count = sum(1 for storage in st.session_state.inventory['storages'].values() 
                            for item in storage['items'] if item['status'] == 'Low Stock')
        st.metric("⚠️ Low Stock Items", low_stock_count)
    with col4:
        # Generate and display central QR code
        central_qr_data = generate_qr_code(app_url)
        if central_qr_data:
            st.image(central_qr_data, width=100)
            st.caption("Central QR")
    
    st.markdown("---")
    
    # Main content columns
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        st.subheader("📊 Storage Overview")
        
        # Display all storages in a nice grid
        for storage_id, storage in st.session_state.inventory['storages'].items():
            with st.container():
                col_a, col_b, col_c = st.columns([3, 1, 1])
                
                with col_a:
                    # Storage icon based on type
                    icon = "🗄️" if storage['type'] == 'almirah' else "📦" if storage['type'] == 'cupboard' else "🗃️"
                    st.write(f"### {icon} {storage['name']}")
                    st.write(f"**Location:** {storage['location']} | **Type:** {storage['type'].title()}")
                    st.write(f"**Items:** {len(storage['items'])} | **Last Updated:** {storage['last_updated']}")
                    if storage['description']:
                        st.write(f"*{storage['description']}*")
                
                with col_b:
                    # Storage QR code - FIXED: Now displaying the QR
                    storage_url = f"{app_url}?storage={storage_id}"
                    qr_data = generate_qr_code(storage_url)
                    if qr_data:
                        st.image(qr_data, width=120)
                        st.caption(f"QR for {storage['name']}")
                
                with col_c:
                    # Actions
                    if st.button(f"📋 View", key=f"view_{storage_id}"):
                        st.session_state.current_storage = storage_id
                        st.rerun()
                    
                    st.download_button(
                        f"📥 QR",
                        qr_data if qr_data else b"",
                        f"qr_{storage_id}.png",
                        "image/png",
                        key=f"dl_{storage_id}"
                    )
                
                st.markdown("---")
    
    with col_right:
        st.subheader("🎯 Quick Actions")
        
        # Central QR download
        if central_qr_data:
            st.download_button(
                "📥 Download Central QR",
                central_qr_data,
                "qr_central_dashboard.png",
                "image/png",
                key="download_central_main"
            )
        
        # Add new storage
        if st.button("➕ Add New Storage", use_container_width=True):
            st.session_state.show_add_storage = True
            st.rerun()
        
        # Export data
        if st.button("📤 Export Data", use_container_width=True):
            export_inventory_data()
        
        st.markdown("---")
        st.subheader("🔍 Search Items")
        search_term = st.text_input("Search across all storages")
        if search_term:
            search_results = search_items(search_term)
            if search_results:
                for result in search_results:
                    st.write(f"**{result['item']['name']}** in {result['storage_name']}")
            else:
                st.info("No items found")
        
        st.markdown("---")
        st.subheader("📈 Statistics")
        st.write(f"**Total Storages:** {total_storages}")
        st.write(f"**Total Items:** {total_items}")
        
        # Category distribution
        category_count = {}
        for storage in st.session_state.inventory['storages'].values():
            for item in storage['items']:
                category = item.get('category', 'Uncategorized')
                category_count[category] = category_count.get(category, 0) + 1
        
        if category_count:
            st.write("**Items by Category:**")
            for category, count in category_count.items():
                st.write(f"• {category}: {count}")

def storage_view(storage_id):
    """View for individual storage"""
    if storage_id not in st.session_state.inventory['storages']:
        st.error("Storage not found!")
        st.session_state.current_storage = None
        st.rerun()
        return
    
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
            .main > div {padding: 1rem;}
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Storage icon based on type
        icon = "🗄️" if storage['type'] == 'almirah' else "📦" if storage['type'] == 'cupboard' else "🗃️"
        st.title(f"{icon} {storage['name']}")
        st.write(f"**Type:** {storage['type'].title()} | **Location:** {storage['location']}")
        if storage['description']:
            st.write(f"**Description:** {storage['description']}")
        st.write(f"**Last Updated:** {storage['last_updated']}")
    
    with col2:
        # CORRECTED: Current app URL
        app_url = "https://lab-inventory-system-wgghkexsaoemscwwqxxfrj.streamlit.app/"
        
        # Current storage QR - FIXED: Now displaying
        current_url = f"{app_url}?storage={storage_id}"
        current_qr = generate_qr_code(current_url)
        
        if current_qr:
            st.image(current_qr, width=150)
            st.caption(f"QR for this storage")
            
            st.download_button(
                "📥 Download This QR",
                current_qr,
                f"qr_{storage_id}.png",
                "image/png",
                key="download_current"
            )
        
        # Navigation
        st.markdown("---")
        if st.button("🏠 Back to Central", use_container_width=True):
            st.session_state.current_storage = None
            st.rerun()
    
    st.markdown("---")
    
    # Items Management Section - FIXED: Now properly showing add item form
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📋 Items in this Storage")
        
        if storage['items']:
            # Display items in a table format
            items_data = []
            for i, item in enumerate(storage['items']):
                items_data.append({
                    'Name': item['name'],
                    'Quantity': item['quantity'],
                    'Category': item.get('category', ''),
                    'Status': item['status'],
                    'Expiry': item.get('expiry', ''),
                    'Actions': i
                })
            
            # Display as dataframe for better visualization
            df = pd.DataFrame(items_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Detailed view with actions
            st.subheader("🛠️ Item Management")
            for i, item in enumerate(storage['items']):
                with st.expander(f"🔹 {item['name']} - {item['quantity']} ({item['status']})", expanded=False):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(f"**ID:** {item['id']}")
                        st.write(f"**Category:** {item.get('category', 'Not specified')}")
                        if item.get('expiry'):
                            st.write(f"**Expiry:** {item['expiry']}")
                    
                    with col_b:
                        if st.button(f"✏️ Edit", key=f"edit_{i}"):
                            st.session_state.editing_item = (storage_id, i)
                            st.rerun()
                        if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                            del st.session_state.inventory['storages'][storage_id]['items'][i]
                            st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                            st.success("Item deleted successfully!")
                            st.rerun()
        else:
            st.info("📭 No items in this storage yet. Add some items using the form on the right.")
    
    with col_right:
        st.subheader("➕ Add New Item")
        
        # FIXED: Proper add item form
        with st.form(f"add_item_{storage_id}", clear_on_submit=True):
            new_name = st.text_input("Item Name*", placeholder="Enter item name")
            new_quantity = st.text_input("Quantity*", placeholder="e.g., 500g, 10 pieces")
            new_category = st.selectbox("Category", st.session_state.inventory['categories'])
            new_status = st.selectbox("Status", st.session_state.inventory['status_options'])
            new_expiry = st.text_input("Expiry Date (optional)", placeholder="YYYY-MM-DD")
            
            submitted = st.form_submit_button("➕ Add Item to Storage", type="primary")
            
            if submitted:
                if new_name and new_quantity:
                    # Generate unique ID
                    new_id = f"{storage_id}_{len(storage['items']) + 1:03d}"
                    
                    # Add item
                    st.session_state.inventory['storages'][storage_id]['items'].append({
                        'id': new_id,
                        'name': new_name,
                        'quantity': new_quantity,
                        'category': new_category,
                        'status': new_status,
                        'expiry': new_expiry
                    })
                    
                    # Update timestamp
                    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d")
                    
                    st.success(f"✅ Item '{new_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in at least Name and Quantity fields")
        
        st.markdown("---")
        st.subheader("📊 Storage Stats")
        st.write(f"**Total Items:** {len(storage['items']}")
        
        # Status distribution
        status_count = {}
        for item in storage['items']:
            status = item['status']
            status_count[status] = status_count.get(status, 0) + 1
        
        if status_count:
            st.write("**Items by Status:**")
            for status, count in status_count.items():
                st.write(f"• {status}: {count}")

def add_storage_view():
    """View for adding new storage"""
    st.set_page_config(page_title="Add Storage", page_icon="➕")
    
    st.title("➕ Add New Storage")
    
    with st.form("add_storage_form"):
        name = st.text_input("Storage Name*", placeholder="e.g., Drawer A1 - Chemicals")
        storage_type = st.selectbox("Storage Type*", ["drawer", "cupboard", "almirah", "shelf", "cabinet", "rack"])
        location = st.text_input("Location*", placeholder="e.g., Lab Room 101")
        description = st.text_area("Description (optional)", placeholder="Additional details about this storage")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("➕ Add Storage", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            st.session_state.show_add_storage = False
            st.rerun()
            
        if submit and name and location and storage_type:
            # Generate storage ID
            storage_id = f"{storage_type}_{name.lower().replace(' ', '_').replace('-', '_')}"
            
            # Add to inventory
            st.session_state.inventory['storages'][storage_id] = {
                'name': name,
                'type': storage_type,
                'location': location,
                'description': description,
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
        name = st.text_input("Item Name*", value=item['name'])
        quantity = st.text_input("Quantity*", value=item['quantity'])
        category = st.selectbox("Category", st.session_state.inventory['categories'], 
                               index=st.session_state.inventory['categories'].index(item['category']) 
                               if item['category'] in st.session_state.inventory['categories'] else 0)
        status = st.selectbox("Status", st.session_state.inventory['status_options'],
                             index=st.session_state.inventory['status_options'].index(item['status']))
        expiry = st.text_input("Expiry Date", value=item.get('expiry', ''))
        
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
                'category': category,
                'status': status,
                'expiry': expiry
            }
            st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            st.session_state.editing_item = None
            st.success("✅ Item updated successfully!")
            st.rerun()

# Enhanced functionalities
def search_items(search_term):
    """Search items across all storages"""
    results = []
    search_term = search_term.lower()
    
    for storage_id, storage in st.session_state.inventory['storages'].items():
        for item in storage['items']:
            if (search_term in item['name'].lower() or 
                search_term in item.get('category', '').lower() or
                search_term in item.get('id', '').lower()):
                results.append({
                    'storage_id': storage_id,
                    'storage_name': storage['name'],
                    'item': item
                })
    
    return results

def export_inventory_data():
    """Export inventory data as JSON"""
    inventory_json = json.dumps(st.session_state.inventory, indent=2)
    
    st.download_button(
        "📥 Download Inventory Data",
        inventory_json,
        "lab_inventory_export.json",
        "application/json",
        key="export_json"
    )

# Main routing logic
def main():
    try:
        # Check for various view states
        if hasattr(st.session_state, 'show_add_storage') and st.session_state.show_add_storage:
            add_storage_view()
            return
            
        if hasattr(st.session_state, 'editing_item') and st.session_state.editing_item:
            storage_id, item_index = st.session_state.editing_item
            edit_item_view(storage_id, item_index)
            return
        
        # Check query parameters for storage view
        query_params = st.experimental_get_query_params()
        if 'storage' in query_params:
            storage_id = query_params['storage'][0]
            if storage_id in st.session_state.inventory['storages']:
                storage_view(storage_id)
                return
        
        # Check session state for storage view
        if hasattr(st.session_state, 'current_storage') and st.session_state.current_storage:
            storage_view(st.session_state.current_storage)
            return
        
        # Default to main dashboard
        main_dashboard()
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        # Fallback to main dashboard
        main_dashboard()

if __name__ == "__main__":
    main()