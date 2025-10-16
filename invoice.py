import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import json

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Invoice Management System",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# CUSTOM CSS
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
.main-header {
    font-size: 3rem;
    font-weight: bold;
    color: #1f2937;
    margin-bottom: 0.5rem;
}
.status-paid {
    background: #10b981;
    color: white;
    padding: 0.4rem 1rem;
    border-radius: 4px;
}
.status-pending {
    background: #f59e0b;
    color: white;
    padding: 0.4rem 1rem;
    border-radius: 4px;
}
.status-overdue {
    background: #ef4444;
    color: white;
    padding: 0.4rem 1rem;
    border-radius: 4px;
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# DATABASE SETUP
# -----------------------------------------------------------------------------
def init_database():
    conn = sqlite3.connect("invoices.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE,
            client_name TEXT,
            client_email TEXT,
            client_address TEXT,
            issue_date TEXT,
            due_date TEXT,
            items TEXT,
            subtotal REAL,
            tax_rate REAL,
            tax_amount REAL,
            total REAL,
            status TEXT,
            notes TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    return conn


def generate_invoice_number():
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM invoices")
    count = cursor.fetchone()[0]
    return f"INV-{datetime.now().strftime('%Y%m')}-{str(count + 1).zfill(4)}"


def save_invoice(invoice_data):
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO invoices (
            invoice_number, client_name, client_email, client_address,
            issue_date, due_date, items, subtotal, tax_rate, tax_amount,
            total, status, notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            invoice_data["invoice_number"],
            invoice_data["client_name"],
            invoice_data["client_email"],
            invoice_data["client_address"],
            invoice_data["issue_date"],
            invoice_data["due_date"],
            json.dumps(invoice_data["items"]),
            invoice_data["subtotal"],
            invoice_data["tax_rate"],
            invoice_data["tax_amount"],
            invoice_data["total"],
            invoice_data["status"],
            invoice_data["notes"],
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ),
    )
    conn.commit()


def get_all_invoices():
    conn = st.session_state.db_conn
    df = pd.read_sql_query("SELECT * FROM invoices ORDER BY created_at DESC", conn)
    if not df.empty:
        df["items"] = df["items"].apply(json.loads)
    return df


def get_invoice_by_number(invoice_number):
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
    row = cursor.fetchone()
    if row:
        columns = [d[0] for d in cursor.description]
        inv = dict(zip(columns, row))
        inv["items"] = json.loads(inv["items"])
        return inv
    return None


def update_invoice(invoice_number, invoice_data):
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE invoices SET
            client_name=?, client_email=?, client_address=?,
            issue_date=?, due_date=?, items=?, subtotal=?, tax_rate=?,
            tax_amount=?, total=?, status=?, notes=?, updated_at=?
        WHERE invoice_number=?
    """,
        (
            invoice_data["client_name"],
            invoice_data["client_email"],
            invoice_data["client_address"],
            invoice_data["issue_date"],
            invoice_data["due_date"],
            json.dumps(invoice_data["items"]),
            invoice_data["subtotal"],
            invoice_data["tax_rate"],
            invoice_data["tax_amount"],
            invoice_data["total"],
            invoice_data["status"],
            invoice_data["notes"],
            datetime.now().isoformat(),
            invoice_number,
        ),
    )
    conn.commit()


def delete_invoice(invoice_number):
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE invoice_number=?", (invoice_number,))
    conn.commit()


def calculate_invoice_totals(items, tax_rate):
    subtotal = sum(i["quantity"] * i["rate"] for i in items)
    tax_amount = subtotal * (tax_rate / 100)
    return {
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total": subtotal + tax_amount,
    }


def generate_pdf_invoice(invoice):
    items_text = "\n".join(
        f"{i['description']:<40} {i['quantity']:>5} x ${i['rate']:>8.2f} = ${i['quantity'] * i['rate']:>10.2f}"
        for i in invoice["items"]
    )
    return f"""
INVOICE: {invoice["invoice_number"]}
Client: {invoice["client_name"]}
Total: ${invoice["total"]:,.2f}

Items:
{items_text}

Subtotal: ${invoice["subtotal"]:,.2f}
Tax: ${invoice["tax_amount"]:,.2f}
Total: ${invoice["total"]:,.2f}
"""


# -----------------------------------------------------------------------------
# SESSION INITIALIZATION
# -----------------------------------------------------------------------------
if "db_conn" not in st.session_state:
    st.session_state.db_conn = init_database()
if "editing_invoice" not in st.session_state:
    st.session_state.editing_invoice = None
if "invoice_items" not in st.session_state:
    st.session_state.invoice_items = [{"description": "", "quantity": 1, "rate": 0.0}]


# -----------------------------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------------------------
def main():
    st.markdown(
        '<div class="main-header">🧾 Invoice Management System</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**Create, manage, and track invoices easily**")
    st.markdown("---")

    page = st.sidebar.radio(
        "📋 Navigation",
        ["Dashboard", "Create Invoice", "View Invoices", "Analytics", "Settings"],
        key="nav",
    )

    # ✅ Fix: handle redirect flag
    if "next_page" in st.session_state:
        page = st.session_state.next_page
        del st.session_state.next_page

    df = get_all_invoices()

    if page == "Dashboard":
        show_dashboard(df)
    elif page == "Create Invoice":
        show_create_invoice()
    elif page == "View Invoices":
        show_view_invoices(df)
    elif page == "Analytics":
        show_analytics(df)
    elif page == "Settings":
        show_settings()

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#6b7280;'>"
        "<p><strong>Invoice Management System v1.0</strong></p>"
        "<p>Developed by Abdiwahid Hussein Ali | maqbuul@outlook.com</p></div>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# DASHBOARD
# -----------------------------------------------------------------------------
def show_dashboard(df):
    st.subheader("📊 Dashboard Overview")

    if df.empty:
        st.info("👋 Welcome! Create your first invoice to get started.")
        if st.button("➕ Create First Invoice", use_container_width=True):
            st.session_state.next_page = "Create Invoice"
            st.rerun()
        return

    total_revenue = df["total"].sum()
    paid = df[df["status"] == "paid"]["total"].sum()
    pending = df[df["status"] == "pending"]["total"].sum()
    overdue = df[df["status"] == "overdue"]["total"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"${total_revenue:,.2f}", f"{len(df)} invoices")
    c2.metric("Paid", f"${paid:,.2f}")
    c3.metric("Pending", f"${pending:,.2f}")
    c4.metric("Overdue", f"${overdue:,.2f}")

    st.markdown("---")
    st.subheader("📄 Recent Invoices")
    st.dataframe(
        df[["invoice_number", "client_name", "issue_date", "total", "status"]].head(5),
        use_container_width=True,
        hide_index=True,
    )


# -----------------------------------------------------------------------------
# CREATE / EDIT INVOICE
# -----------------------------------------------------------------------------
def show_create_invoice():
    editing = st.session_state.editing_invoice is not None
    invoice = (
        get_invoice_by_number(st.session_state.editing_invoice) if editing else None
    )

    st.subheader("✏️ Edit Invoice" if editing else "➕ Create New Invoice")

    with st.form("invoice_form"):
        c1, c2 = st.columns(2)
        with c1:
            client_name = st.text_input(
                "Client Name *", value=invoice["client_name"] if invoice else ""
            )
            client_email = st.text_input(
                "Client Email *", value=invoice["client_email"] if invoice else ""
            )
            client_address = st.text_area(
                "Client Address", value=invoice["client_address"] if invoice else ""
            )
        with c2:
            issue_date = st.date_input(
                "Issue Date *",
                value=datetime.fromisoformat(invoice["issue_date"])
                if invoice
                else datetime.now(),
            )
            due_date = st.date_input(
                "Due Date *",
                value=datetime.fromisoformat(invoice["due_date"])
                if invoice
                else datetime.now() + timedelta(days=30),
            )
            status = st.selectbox(
                "Status",
                ["pending", "paid", "overdue"],
                index=["pending", "paid", "overdue"].index(invoice["status"])
                if invoice
                else 0,
            )
            tax_rate = st.number_input(
                "Tax Rate (%)",
                0.0,
                100.0,
                value=float(invoice["tax_rate"]) if invoice else 10.0,
            )

        st.markdown("---")
        st.markdown("**📝 Invoice Items**")

        for idx, item in enumerate(st.session_state.invoice_items):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            item["description"] = c1.text_input(
                f"Description {idx + 1}", item["description"], key=f"desc_{idx}"
            )
            item["quantity"] = c2.number_input(
                "Qty", 1, value=int(item["quantity"]), key=f"qty_{idx}"
            )
            item["rate"] = c3.number_input(
                "Rate ($)", 0.0, value=float(item["rate"]), step=0.01, key=f"rate_{idx}"
            )
            c4.metric("Amount", f"${item['quantity'] * item['rate']:.2f}")

        c1, c2 = st.columns(2)
        if c1.form_submit_button("➕ Add Item"):
            st.session_state.invoice_items.append(
                {"description": "", "quantity": 1, "rate": 0.0}
            )
            st.rerun()
        if len(st.session_state.invoice_items) > 1 and c2.form_submit_button(
            "➖ Remove Last Item"
        ):
            st.session_state.invoice_items.pop()
            st.rerun()

        notes = st.text_area(
            "Notes (Optional)", value=invoice["notes"] if invoice else ""
        )
        totals = calculate_invoice_totals(st.session_state.invoice_items, tax_rate)

        c1, c2, c3 = st.columns([2, 1, 1])
        with c2:
            st.markdown("**Subtotal:**")
            st.markdown("**Tax:**")
            st.markdown("**Total:**")
        with c3:
            st.markdown(f"**${totals['subtotal']:.2f}**")
            st.markdown(f"**${totals['tax_amount']:.2f}**")
            st.markdown(f"**${totals['total']:.2f}**")

        if st.form_submit_button(
            "💾 Save Invoice" if editing else "✅ Create Invoice",
            use_container_width=True,
        ):
            if not client_name or not client_email:
                st.error("Please fill in required fields")
            else:
                inv_data = {
                    "invoice_number": invoice["invoice_number"]
                    if invoice
                    else generate_invoice_number(),
                    "client_name": client_name,
                    "client_email": client_email,
                    "client_address": client_address,
                    "issue_date": issue_date.isoformat(),
                    "due_date": due_date.isoformat(),
                    "items": st.session_state.invoice_items,
                    "subtotal": totals["subtotal"],
                    "tax_rate": tax_rate,
                    "tax_amount": totals["tax_amount"],
                    "total": totals["total"],
                    "status": status,
                    "notes": notes,
                }
                if editing:
                    update_invoice(invoice["invoice_number"], inv_data)
                    st.success(f"✅ Invoice {invoice['invoice_number']} updated!")
                else:
                    save_invoice(inv_data)
                    st.success(f"✅ Invoice {inv_data['invoice_number']} created!")
                st.session_state.invoice_items = [
                    {"description": "", "quantity": 1, "rate": 0.0}
                ]
                st.session_state.editing_invoice = None
                st.balloons()


# -----------------------------------------------------------------------------
# VIEW INVOICES
# -----------------------------------------------------------------------------
def show_view_invoices(df):
    st.subheader("📄 All Invoices")
    if df.empty:
        st.info("No invoices found.")
        return

    search = st.text_input("🔍 Search", placeholder="Invoice number or client name")
    status_filter = st.selectbox(
        "Filter by Status", ["All", "paid", "pending", "overdue"]
    )
    sort_by = st.selectbox(
        "Sort by", ["Date (Newest)", "Date (Oldest)", "Amount (High)", "Amount (Low)"]
    )

    fdf = df.copy()
    if search:
        fdf = fdf[
            fdf["invoice_number"].str.contains(search, case=False)
            | fdf["client_name"].str.contains(search, case=False)
        ]
    if status_filter != "All":
        fdf = fdf[fdf["status"] == status_filter]

    if sort_by == "Date (Newest)":
        fdf = fdf.sort_values("issue_date", ascending=False)
    elif sort_by == "Date (Oldest)":
        fdf = fdf.sort_values("issue_date")
    elif sort_by == "Amount (High)":
        fdf = fdf.sort_values("total", ascending=False)
    else:
        fdf = fdf.sort_values("total")

    for _, inv in fdf.iterrows():
        with st.expander(
            f"🧾 {inv['invoice_number']} - {inv['client_name']} (${inv['total']:,.2f})"
        ):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"**Client:** {inv['client_name']}")
            c1.write(f"**Email:** {inv['client_email']}")
            c1.write(f"**Issue Date:** {inv['issue_date']}")
            c1.write(f"**Due Date:** {inv['due_date']}")
            c2.write(f"**Subtotal:** ${inv['subtotal']:,.2f}")
            c2.write(f"**Tax:** ${inv['tax_amount']:,.2f}")
            c2.write(f"**Total:** ${inv['total']:,.2f}")
            c2.markdown(
                f"**Status:** <span class='status-{inv['status']}'>{inv['status'].upper()}</span>",
                unsafe_allow_html=True,
            )
            if c3.button("✏️ Edit", key=f"edit_{inv['invoice_number']}"):
                st.session_state.editing_invoice = inv["invoice_number"]
                st.session_state.next_page = "Create Invoice"
                st.rerun()
            if c3.button("🗑️ Delete", key=f"del_{inv['invoice_number']}"):
                delete_invoice(inv["invoice_number"])
                st.success("Invoice deleted!")
                st.rerun()


# -----------------------------------------------------------------------------
# ANALYTICS
# -----------------------------------------------------------------------------
def show_analytics(df):
    st.subheader("📈 Analytics & Insights")
    if df.empty:
        st.info("No invoices yet.")
        return
    df["month"] = pd.to_datetime(df["issue_date"]).dt.strftime("%Y-%m")
    monthly = df.groupby("month")["total"].sum().reset_index()
    st.plotly_chart(
        px.bar(monthly, x="month", y="total", title="Revenue by Month"),
        use_container_width=True,
    )
    st.plotly_chart(
        px.pie(df, names="status", title="Invoice Status Distribution"),
        use_container_width=True,
    )


# -----------------------------------------------------------------------------
# SETTINGS
# -----------------------------------------------------------------------------
def show_settings():
    st.subheader("⚙️ Settings")
    st.text_input("Company Name", value="Your Company Name")
    st.text_input("Company Email", value="billing@yourcompany.com")
    st.text_area("Address", value="123 Business Street\nCity, State, ZIP")
    st.number_input("Default Tax Rate (%)", 0.0, 100.0, value=10.0)
    if st.button("💾 Save Settings"):
        st.success("Settings saved!")


# -----------------------------------------------------------------------------
# RUN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
