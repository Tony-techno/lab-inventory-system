# app.py - BULLETPROOF Lab Inventory Management System
import streamlit as st
import qrcode
import io
import json
from datetime import datetime
import pandas as pd
import base64

# Initialize session state for inventory data
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'storages': {},  # No pre-defined storages - user will create them
        'categories': ['Chemical', 'Glassware', 'Instrument', 'Equipment', 'Consumable', 'Tool', 'Electronic', 'Safety'],
        'status_options': ['Free', 'Occupied', 'Ordered', 'Maintenance', 'Broken'],
        'storage_types': ['drawer', 'cupboard', 'almirah', 'shelf', 'cabinet', 'rack', 'fridge', 'freezer']
    }

# Initialize form states
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'current_form_id' not in st.session_state:
    st.session_state.current_form_id = None
if 'qr_cache' not in st.session_state:
    st.session_state.qr_cache = {}

def generate_qr_code_safe(url):
    """Generate QR code safely with caching"""
    try:
        # Check cache first
        if url in st.session_state.qr_cache:
            return st.session_state.qr_cache[url]
        
        # Generate new QR code
        qr = qrcode.QRCode(
            version=8,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)
        qr_bytes = buf.getvalue()
        
        # Cache the result
        st.session_state.qr_cache[url] = qr_bytes
        return qr_bytes
        
    except Exception as e:
        st.error(f"QR generation failed: {str(e)}")
        return None

def get_base64_encoded_image(qr_bytes):
    """Convert QR bytes to base64 for display"""
    try:
        if qr_bytes:
            return base64.b64encode(qr_bytes).decode()
        return None
    except:
        return None

def get_app_url():
    """Get the current app URL - CRITICAL: UPDATE THIS WITH YOUR ACTUAL URL"""
    # ⚠️ ⚠️ ⚠️ REPLACE THIS WITH YOUR ACTUAL STREAMLIT APP URL ⚠️ ⚠️ ⚠️
    return "https://lab-inventory-system-wgghkexsaoemscwwqxxfrj.streamlit.app/"

def reset_form_state():
    """Reset form submission state"""
    st.session_state.form_submitted = False
    st.session_state.current_form_id = None

def display_qr_code(qr_bytes, caption="QR Code", width=150):
    """Safely display QR code"""
    try:
        if qr_bytes:
            # Convert to base64 for reliable display
            img_str = get_base64_encoded_image(qr_bytes)
            if img_str:
                st.markdown(f'<img src="data:image/png;base64,{img_str}" width="{width}" alt="{caption}">', 
                           unsafe_allow_html=True)
                st.caption(caption)
                return True
        return False
    except Exception as e:
        st.error(f"QR display error: {str(e)}")
        return False

def main_dashboard():
    """Central dashboard - shows all storages"""
    st.set_page_config(
        page_title="Lab Inventory System",
        page_icon="🔬",
        layout="wide"
    )
    
    # Reset form state when coming to main dashboard
    reset_form_state()
    
    st.title("🔬 Lab Inventory Management System")
    st.markdown("---")
    
    app_url = get_app_url()
    
    # Header with quick stats
    total_storages = len(st.session_state.inventory['storages'])
    total_items = sum(len(storage['items']) for storage in st.session_state.inventory['storages'].values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Total Storages", total_storages)
    with col2:
        st.metric("📦 Total Items", total_items)
    with col3:
        occupied_count = sum(1 for storage in st.session_state.inventory['storages'].values() 
                           for item in storage['items'] if item['status'] == 'Occupied')
        st.metric("🔴 Occupied Items", occupied_count)
    with col4:
        # Generate and display central QR code
        central_qr_data = generate_qr_code_safe(app_url)
        display_qr_code(central_qr_data, "Central QR", 100)
    
    st.markdown("---")
    
    # Main content
    if not st.session_state.inventory['storages']:
        st.info("🏗️ No storages created yet. Start by adding your first storage!")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("➕ Create Your First Storage", use_container_width=True, type="primary"):
                st.session_state.show_add_storage = True
                st.rerun()
    else:
        col_left, col_right = st.columns([3, 1])
        
        with col_left:
            st.subheader("📊 All Storage Units")
            
            # Display all storages
            for storage_id, storage in st.session_state.inventory['storages'].items():
                with st.container():
                    # Storage header
                    col_a, col_b, col_c = st.columns([3, 1, 1])
                    
                    with col_a:
                        # Storage icon based on type
                        icon = get_storage_icon(storage['type'])
                        st.write(f"### {icon} {storage['name']}")
                        st.write(f"**Location:** {storage['location']} | **Type:** {storage['type'].title()}")
                        st.write(f"**Items:** {len(storage['items'])} | **Last Updated:** {storage['last_updated']}")
                        if storage.get('description'):
                            st.write(f"*{storage['description']}*")
                    
                    with col_b:
                        # Storage QR code
                        storage_url = f"{app_url}?storage={storage_id}"
                        qr_data = generate_qr_code_safe(storage_url)
                        if display_qr_code(qr_data, f"QR for {storage['name']}", 120):
                            # Download button
                            if qr_data:
                                st.download_button(
                                    f"📥 Download QR",
                                    qr_data,
                                    f"qr_{storage_id}.png",
                                    "image/png",
                                    key=f"dl_{storage_id}",
                                    use_container_width=True
                                )
                    
                    with col_c:
                        # Actions
                        if st.button(f"📋 View", key=f"view_{storage_id}", use_container_width=True):
                            st.session_state.current_storage = storage_id
                            reset_form_state()
                            st.rerun()
                        
                        if st.button(f"🗑️ Delete", key=f"delete_storage_{storage_id}", use_container_width=True):
                            st.session_state.storage_to_delete = storage_id
                            reset_form_state()
                            st.rerun()
                    
                    # Quick items preview
                    if storage['items']:
                        with st.expander(f"📦 Items Preview ({len(storage['items'])} items)"):
                            for item in storage['items'][:5]:  # Show first 5 items
                                status_color = "🟢" if item['status'] == 'Free' else "🔴" if item['status'] == 'Occupied' else "🟡"
                                st.write(f"{status_color} {item['name']} - {item['quantity']} ({item['status']})")
                            if len(storage['items']) > 5:
                                st.write(f"... and {len(storage['items']) - 5} more items")
                    
                    st.markdown("---")
        
        with col_right:
            st.subheader("🎯 Quick Actions")
            
            # Central QR download
            central_qr_data = generate_qr_code_safe(app_url)
            if central_qr_data:
                st.download_button(
                    "📥 Download Central QR",
                    central_qr_data,
                    "qr_central_dashboard.png",
                    "image/png",
                    use_container_width=True
                )
            
            # Add new storage
            if st.button("➕ Add New Storage", use_container_width=True, type="primary"):
                st.session_state.show_add_storage = True
                reset_form_state()
                st.rerun()
            
            # Export data
            if st.button("📤 Export Data", use_container_width=True):
                export_inventory_data()
            
            st.markdown("---")
            st.subheader("🔍 Search Items")
            search_term = st.text_input("Search across all storages", key="main_search")
            if search_term:
                search_results = search_items(search_term)
                if search_results:
                    st.write("**Search Results:**")
                    for result in search_results[:3]:  # Show first 3 results
                        status_icon = "🟢" if result['item']['status'] == 'Free' else "🔴" if result['item']['status'] == 'Occupied' else "🟡"
                        st.write(f"{status_icon} **{result['item']['name']}** in {result['storage_name']}")
                    if len(search_results) > 3:
                        st.write(f"... and {len(search_results) - 3} more results")
                else:
                    st.info("No items found")
            
            st.markdown("---")
            st.subheader("📈 Quick Stats")
            st.write(f"**Total Storages:** {total_storages}")
            st.write(f"**Total Items:** {total_items}")
            
            # Status distribution
            status_count = {'Free': 0, 'Occupied': 0, 'Ordered': 0, 'Maintenance': 0, 'Broken': 0}
            for storage in st.session_state.inventory['storages'].values():
                for item in storage['items']:
                    status_count[item['status']] = status_count.get(item['status'], 0) + 1
            
            st.write("**Items by Status:**")
            for status, count in status_count.items():
                if count > 0:
                    icon = "🟢" if status == 'Free' else "🔴" if status == 'Occupied' else "🟡"
                    st.write(f"{icon} {status}: {count}")

def storage_view(storage_id):
    """View for individual storage"""
    if storage_id not in st.session_state.inventory['storages']:
        st.error("Storage not found!")
        st.session_state.current_storage = None
        reset_form_state()
        st.rerun()
        return
    
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.set_page_config(
        page_title=f"{storage['name']}",
        page_icon="📦",
        layout="wide"
    )
    
    # Custom CSS for better mobile view
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            .main > div {padding: 1rem;}
            .stButton button {width: 100%;}
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        icon = get_storage_icon(storage['type'])
        st.title(f"{icon} {storage['name']}")
        st.write(f"**Type:** {storage['type'].title()} | **Location:** {storage['location']}")
        if storage.get('description'):
            st.write(f"**Description:** {storage['description']}")
        st.write(f"**Last Updated:** {storage['last_updated']}")
        st.write(f"**Total Items:** {len(storage['items'])}")
    
    with col2:
        app_url = get_app_url()
        
        # Current storage QR
        current_url = f"{app_url}?storage={storage_id}"
        current_qr = generate_qr_code_safe(current_url)
        
        if display_qr_code(current_qr, f"QR for {storage['name']}", 150):
            if current_qr:
                st.download_button(
                    "📥 Download This QR",
                    current_qr,
                    f"qr_{storage_id}.png",
                    "image/png",
                    use_container_width=True
                )
        
        # Navigation and actions
        st.markdown("---")
        if st.button("🏠 Back to Central", use_container_width=True):
            st.session_state.current_storage = None
            reset_form_state()
            st.rerun()
        
        if st.button("✏️ Edit Storage", use_container_width=True):
            st.session_state.editing_storage = storage_id
            reset_form_state()
            st.rerun()
        
        if st.button("🗑️ Delete Storage", use_container_width=True):
            st.session_state.storage_to_delete = storage_id
            reset_form_state()
            st.rerun()
    
    st.markdown("---")
    
    # Items Management Section
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📋 Items Management")
        
        if storage['items']:
            # Display items with status
            for i, item in enumerate(storage['items']):
                with st.expander(f"{get_status_icon(item['status'])} {item['name']} - {item['quantity']}", expanded=False):
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    
                    with col_a:
                        st.write(f"**ID:** {item['id']}")
                        st.write(f"**Category:** {item.get('category', 'Not specified')}")
                        if item.get('expiry'):
                            st.write(f"**Expiry:** {item['expiry']}")
                        st.write(f"**Status:** {item['status']}")
                        if item.get('notes'):
                            st.write(f"**Notes:** {item['notes']}")
                    
                    with col_b:
                        if st.button(f"✏️ Edit", key=f"edit_{storage_id}_{i}", use_container_width=True):
                            st.session_state.editing_item = (storage_id, i)
                            reset_form_state()
                            st.rerun()
                    
                    with col_c:
                        if st.button(f"🗑️ Delete", key=f"delete_{storage_id}_{i}", use_container_width=True):
                            delete_item(storage_id, i)
                            reset_form_state()
                            st.rerun()
        else:
            st.info("📭 No items in this storage yet. Add some items using the form on the right.")
    
    with col_right:
        st.subheader("➕ Add New Item")
        
        # Use a unique form key to prevent continuous adding
        form_key = f"add_item_{storage_id}"
        
        # Check if this form was just submitted
        form_just_submitted = (st.session_state.form_submitted and 
                             st.session_state.current_form_id == form_key)
        
        with st.form(form_key, clear_on_submit=True):
            new_name = st.text_input("Item Name*", placeholder="Enter item name", 
                                   value="" if not form_just_submitted else "")
            new_quantity = st.text_input("Quantity*", placeholder="e.g., 500g, 10 pieces", 
                                       value="" if not form_just_submitted else "")
            new_category = st.selectbox("Category", st.session_state.inventory['categories'])
            new_status = st.selectbox("Status*", st.session_state.inventory['status_options'])
            new_expiry = st.text_input("Expiry Date (optional)", placeholder="YYYY-MM-DD",
                                     value="" if not form_just_submitted else "")
            new_notes = st.text_area("Notes (optional)", placeholder="Additional notes",
                                   value="" if not form_just_submitted else "")
            
            submitted = st.form_submit_button("➕ Add Item to Storage", type="primary", use_container_width=True)
            
            if submitted:
                if new_name and new_quantity and new_status:
                    # Set form state to prevent continuous adding
                    st.session_state.form_submitted = True
                    st.session_state.current_form_id = form_key
                    
                    add_item_to_storage(storage_id, new_name, new_quantity, new_category, new_status, new_expiry, new_notes)
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (Name, Quantity, Status)")
        
        st.markdown("---")
        st.subheader("📊 Storage Stats")
        
        # Status distribution for this storage
        status_count = {'Free': 0, 'Occupied': 0, 'Ordered': 0, 'Maintenance': 0, 'Broken': 0}
        for item in storage['items']:
            status_count[item['status']] += 1
        
        st.write("**Items by Status:**")
        for status, count in status_count.items():
            if count > 0:
                st.write(f"{get_status_icon(status)} {status}: {count}")

def add_storage_view():
    """View for adding new storage"""
    st.set_page_config(page_title="Add Storage", page_icon="➕")
    
    st.title("➕ Add New Storage")
    
    form_key = "add_storage_form"
    form_just_submitted = (st.session_state.form_submitted and 
                         st.session_state.current_form_id == form_key)
    
    with st.form(form_key, clear_on_submit=True):
        name = st.text_input("Storage Name*", placeholder="e.g., Drawer A1 - Chemicals",
                           value="" if not form_just_submitted else "")
        storage_type = st.selectbox("Storage Type*", st.session_state.inventory['storage_types'])
        location = st.text_input("Location*", placeholder="e.g., Lab Room 101",
                               value="" if not form_just_submitted else "")
        description = st.text_area("Description (optional)", placeholder="Additional details about this storage",
                                 value="" if not form_just_submitted else "")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("➕ Add Storage", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.show_add_storage = False
            reset_form_state()
            st.rerun()
            
        if submit:
            if name and location and storage_type:
                # Set form state
                st.session_state.form_submitted = True
                st.session_state.current_form_id = form_key
                
                add_new_storage(name, storage_type, location, description)
                st.session_state.show_add_storage = False
                reset_form_state()
                st.rerun()
            else:
                st.error("Please fill in all required fields (Name, Type, Location)")

def edit_storage_view(storage_id):
    """View for editing a storage"""
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.set_page_config(page_title="Edit Storage", page_icon="✏️")
    st.title(f"✏️ Edit Storage: {storage['name']}")
    
    with st.form("edit_storage_form"):
        name = st.text_input("Storage Name*", value=storage['name'])
        storage_type = st.selectbox("Storage Type*", st.session_state.inventory['storage_types'], 
                                   index=st.session_state.inventory['storage_types'].index(storage['type']))
        location = st.text_input("Location*", value=storage['location'])
        description = st.text_area("Description", value=storage.get('description', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.editing_storage = None
            reset_form_state()
            st.rerun()
            
        if submit:
            if name and location and storage_type:
                update_storage(storage_id, name, storage_type, location, description)
                st.session_state.editing_storage = None
                reset_form_state()
                st.rerun()
            else:
                st.error("Please fill in all required fields")

def edit_item_view(storage_id, item_index):
    """View for editing an item"""
    item = st.session_state.inventory['storages'][storage_id]['items'][item_index]
    storage_name = st.session_state.inventory['storages'][storage_id]['name']
    
    st.set_page_config(page_title="Edit Item", page_icon="✏️")
    st.title(f"✏️ Edit Item - {storage_name}")
    
    with st.form("edit_item_form"):
        name = st.text_input("Item Name*", value=item['name'])
        quantity = st.text_input("Quantity*", value=item['quantity'])
        category = st.selectbox("Category", st.session_state.inventory['categories'], 
                               index=st.session_state.inventory['categories'].index(item['category']) 
                               if item['category'] in st.session_state.inventory['categories'] else 0)
        status = st.selectbox("Status*", st.session_state.inventory['status_options'],
                             index=st.session_state.inventory['status_options'].index(item['status']))
        expiry = st.text_input("Expiry Date", value=item.get('expiry', ''))
        notes = st.text_area("Notes", value=item.get('notes', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.editing_item = None
            reset_form_state()
            st.rerun()
            
        if submit:
            if name and quantity and status:
                update_item(storage_id, item_index, name, quantity, category, status, expiry, notes)
                st.session_state.editing_item = None
                reset_form_state()
                st.rerun()
            else:
                st.error("Please fill in all required fields")

def delete_confirmation_view():
    """View for confirming storage deletion"""
    storage_id = st.session_state.storage_to_delete
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.set_page_config(page_title="Confirm Delete", page_icon="🗑️")
    st.title("🗑️ Confirm Storage Deletion")
    
    st.warning(f"⚠️ You are about to delete the storage: **{storage['name']}**")
    st.error(f"❌ This will permanently delete {len(storage['items'])} items and cannot be undone!")
    
    col1, col2, col3 = st.columns([1,1,1])
    
    with col2:
        if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
            delete_storage(storage_id)
            st.session_state.storage_to_delete = None
            reset_form_state()
            st.success("Storage deleted successfully!")
            st.rerun()
    
    with col3:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.storage_to_delete = None
            reset_form_state()
            st.rerun()

# Core CRUD Operations
def add_new_storage(name, storage_type, location, description=""):
    """Add a new storage to inventory"""
    storage_id = f"{storage_type}_{name.lower().replace(' ', '_').replace('-', '_')}_{datetime.now().strftime('%H%M%S')}"
    
    st.session_state.inventory['storages'][storage_id] = {
        'name': name,
        'type': storage_type,
        'location': location,
        'description': description,
        'items': [],
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.success(f"✅ Storage '{name}' added successfully!")

def update_storage(storage_id, name, storage_type, location, description=""):
    """Update storage details"""
    st.session_state.inventory['storages'][storage_id].update({
        'name': name,
        'type': storage_type,
        'location': location,
        'description': description,
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.success(f"✅ Storage '{name}' updated successfully!")

def delete_storage(storage_id):
    """Delete a storage and all its items"""
    storage_name = st.session_state.inventory['storages'][storage_id]['name']
    del st.session_state.inventory['storages'][storage_id]
    st.session_state.current_storage = None
    st.success(f"✅ Storage '{storage_name}' deleted successfully!")

def add_item_to_storage(storage_id, name, quantity, category, status, expiry="", notes=""):
    """Add an item to a storage"""
    item_id = f"item_{len(st.session_state.inventory['storages'][storage_id]['items']) + 1:03d}"
    
    st.session_state.inventory['storages'][storage_id]['items'].append({
        'id': item_id,
        'name': name,
        'quantity': quantity,
        'category': category,
        'status': status,
        'expiry': expiry,
        'notes': notes
    })
    
    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"✅ Item '{name}' added successfully!")

def update_item(storage_id, item_index, name, quantity, category, status, expiry="", notes=""):
    """Update an item"""
    st.session_state.inventory['storages'][storage_id]['items'][item_index].update({
        'name': name,
        'quantity': quantity,
        'category': category,
        'status': status,
        'expiry': expiry,
        'notes': notes
    })
    
    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"✅ Item '{name}' updated successfully!")

def delete_item(storage_id, item_index):
    """Delete an item from storage"""
    item_name = st.session_state.inventory['storages'][storage_id]['items'][item_index]['name']
    del st.session_state.inventory['storages'][storage_id]['items'][item_index]
    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"✅ Item '{item_name}' deleted successfully!")

# Utility Functions
def get_storage_icon(storage_type):
    """Get icon for storage type"""
    icons = {
        'drawer': '🗃️', 'cupboard': '📦', 'almirah': '🗄️', 
        'shelf': '📚', 'cabinet': '🚪', 'rack': '🛒',
        'fridge': '🧊', 'freezer': '❄️'
    }
    return icons.get(storage_type, '📦')

def get_status_icon(status):
    """Get icon for item status"""
    icons = {
        'Free': '🟢',
        'Occupied': '🔴', 
        'Ordered': '🟡',
        'Maintenance': '🔧',
        'Broken': '❌'
    }
    return icons.get(status, '⚪')

def search_items(search_term):
    """Search items across all storages"""
    results = []
    search_term = search_term.lower()
    
    for storage_id, storage in st.session_state.inventory['storages'].items():
        for item in storage['items']:
            if (search_term in item['name'].lower() or 
                search_term in item.get('category', '').lower() or
                search_term in str(item.get('id', '')).lower()):
                results.append({
                    'storage_id': storage_id,
                    'storage_name': storage['name'],
                    'item': item
                })
    
    return results

def export_inventory_data():
    """Export inventory data as JSON"""
    inventory_json = json.dumps(st.session_state.inventory, indent=2, ensure_ascii=False)
    
    st.download_button(
        "📥 Download Inventory Data (JSON)",
        inventory_json,
        f"lab_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "application/json",
        use_container_width=True
    )

# Main routing logic
def main():
    try:
        # Handle delete confirmation
        if hasattr(st.session_state, 'storage_to_delete') and st.session_state.storage_to_delete:
            delete_confirmation_view()
            return
            
        # Handle various view states
        if hasattr(st.session_state, 'show_add_storage') and st.session_state.show_add_storage:
            add_storage_view()
            return
            
        if hasattr(st.session_state, 'editing_storage') and st.session_state.editing_storage:
            edit_storage_view(st.session_state.editing_storage)
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
        st.error(f"An error occurred: {str(e)}")
        # Fallback to main dashboard
        reset_form_state()
        main_dashboard()

if __name__ == "__main__":
    main()