import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database import initialize_database, add_expense, get_expenses, update_expense, delete_expense, delete_expenses, clear_expenses
from analytics import create_dataframe, total_expense, highest_spending_category, category_summary, monthly_summary

st.set_page_config(page_title="Smart Expense Tracker", page_icon="💸", layout="wide")

st.markdown("""
<style>
/* High-contrast, readable theme */
.stApp {background: linear-gradient(135deg,#f7f6ff 0%,#edf4ff 100%); color:#20243a;}
.main .block-container {max-width:1180px;padding-top:1.4rem;padding-bottom:2rem;}
html, body, [class*="st-"] {color:#20243a;}
p, label, .stMarkdown, .stText, [data-testid="stCaptionContainer"], [data-testid="stWidgetLabel"] {color:#20243a !important;}
h1,h2,h3,h4,h5,h6 {color:#211747 !important;}
[data-testid="stMetric"] {background:#ffffff;border:1px solid #c9c2f4;border-radius:16px;padding:15px;box-shadow:0 4px 16px #4c379115;}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {color:#45405f !important;opacity:1 !important;}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] div {color:#211747 !important;opacity:1 !important;}
[data-testid="stSidebar"] {background:#e6e0ff;}
[data-testid="stSidebar"] * {color:#262044 !important;}
.stButton>button,.stFormSubmitButton>button {border-radius:10px;font-weight:700;color:#ffffff !important;background:#b9382b;border:1px solid #a52d22;}
.stButton>button:hover,.stFormSubmitButton>button:hover {background:#92291f;color:#ffffff !important;}
.hero {padding:1.25rem 1.5rem;border-radius:22px;background:linear-gradient(120deg,#e0d7ff,#d9edff);border:1px solid #c6baf4;margin-bottom:1rem;}
.hero h1 {margin:0;color:#211747 !important;}
.hero p {margin:.4rem 0 0;color:#383151 !important;}
input, textarea, [data-baseweb="select"] > div {color:#20243a !important;}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea {color:#20243a !important;}
[data-testid="stAlert"] {color:#20243a !important;}
[data-testid="stDataFrame"] {border:1px solid #c9c2f4;border-radius:10px;}
div[data-testid="stVerticalBlock"] > div {animation:fadein .25s ease-out;}
@keyframes fadein {from{opacity:.85;transform:translateY(3px)}to{opacity:1;transform:translateY(0)}}
</style>
""", unsafe_allow_html=True)

initialize_database()

# Authentication: Google OIDC is enabled when [auth] is configured in Streamlit secrets.
# In local development without auth secrets, use an explicit local demo profile.
def has_auth_config():
    try:
        return bool(st.secrets.get("auth", {}).get("redirect_uri"))
    except Exception:
        return False

if has_auth_config():
    if not st.user.is_logged_in:
        st.markdown('<div class="hero"><h1>💸 Smart Expense Tracker</h1><p>Your personal spending, clearly organized.</p></div>', unsafe_allow_html=True)
        st.markdown("### Welcome! 👋")
        st.write("Sign in to keep your expense records private to your account.")
        if st.button("Continue with Google", type="primary", use_container_width=True):
            st.login("google")
        st.stop()
    user_id = str(st.user.get("email", "") or st.user.get("sub", ""))
    if not user_id:
        st.error("Could not identify your signed-in account. Please sign out and sign in again.")
        st.stop()
else:
    user_id = "local-user"

st.markdown('<div class="hero"><h1>💸 Smart Expense Tracker</h1><p>Spend mindfully. Track effortlessly. ✨</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🌷 Your money space")
    if has_auth_config():
        st.caption(f"Signed in: {user_id}")
        if st.button("Log out", use_container_width=True):
            st.logout()
    else:
        st.info("Local demo mode")
        st.caption("Google sign-in becomes active after auth secrets are configured.")
        if st.session_state.pop("jump_add",False):
           st.session_state["nav_selection"] = "Add Expense"
    menu = st.radio("Navigate", ["Dashboard", "Add Expense", "View Expenses", "Edit Expense", "Delete Expenses", "Settings"], key="nav_selection")
    st.markdown("---")
    st.caption("Small steps today, better money habits tomorrow 🌱")

expenses = get_expenses(user_id)
df = create_dataframe(expenses)

if menu == "Dashboard":
    st.subheader("📊 Your spending at a glance")
    total = total_expense(df)
    highest_category, highest_amount = highest_spending_category(df) if not df.empty else ("N/A", 0)
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total spending", f"₹{total:,.2f}")
    c2.metric("🧾 Expenses recorded", len(df))
    c3.metric("🏆 Top category", highest_category)
    st.divider()
    if df.empty:
        st.info("Your dashboard is ready! Add your first expense to see your insights. 🌼")
        if st.button("➕ Add my first expense", type="primary"):
            st.session_state["jump_add"] = True
            st.rerun()
    else:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("#### 📊 Category breakdown")
            cat = category_summary(df)
            fig, ax = plt.subplots(figsize=(5.2, 2.8))
            cat.plot(kind="bar", ax=ax, color="#8B7BE8", width=.62, legend=False)
            ax.set_xlabel(""); ax.set_ylabel("Amount (₹)", fontsize=8)
            ax.tick_params(axis="x", labelrotation=25, labelsize=8); ax.tick_params(axis="y", labelsize=8)
            ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            ax.grid(axis="y", linestyle="--", alpha=.2); fig.tight_layout()
            st.pyplot(fig, width="content"); plt.close(fig)
        with right:
            st.markdown("#### 📈 Monthly trend")
            monthly = monthly_summary(df)
            fig2, ax2 = plt.subplots(figsize=(5.2, 2.8))
            ax2.plot(range(len(monthly)), monthly["amount"], marker="o", markersize=4, linewidth=2, color="#7561D8")
            ax2.fill_between(range(len(monthly)), monthly["amount"], alpha=.1, color="#8B7BE8")
            ax2.set_xticks(range(len(monthly))); ax2.set_xticklabels(monthly["month"], rotation=25, ha="right", fontsize=8)
            ax2.set_ylabel("Amount (₹)", fontsize=8); ax2.set_xlabel("")
            ax2.tick_params(axis="y", labelsize=8); ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
            ax2.grid(axis="y", linestyle="--", alpha=.2); fig2.tight_layout()
            st.pyplot(fig2, width="content"); plt.close(fig2)
        st.markdown("#### 💡 Spending insight")
        st.success(f"Your highest spending category is **{highest_category}** (₹{highest_amount:,.2f}).")
        recent = df.head(5).copy()
        recent["expense_date"] = recent["expense_date"].astype(str).str[:10]
        st.markdown("#### 🕒 Recent expenses")
        st.dataframe(recent, width="stretch", hide_index=True)

elif menu == "Add Expense":
    st.subheader("➕ Add a new expense")
    if st.session_state.get("expense_added", False):
        st.success("Expense added successfully! 🎉")
        if st.button("Add another expense"):
            st.session_state.expense_added = False; st.rerun()
    else:
        with st.form("expense_form", clear_on_submit=True):
            amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, value=None, placeholder="Enter amount")
            category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Education", "Entertainment", "Health", "Bills", "Other"], index=None, placeholder="Choose a category")
            description = st.text_input("Description", placeholder="e.g., lunch with friends")
            expense_date = st.date_input("Expense date", value=None, format="YYYY-MM-DD")
            submitted = st.form_submit_button("Save expense 💜", type="primary", use_container_width=True)
        if submitted:
            if amount is None or amount <= 0: st.error("Enter an amount greater than zero.")
            elif category is None: st.error("Please choose a category.")
            elif expense_date is None: st.error("Please select the expense date.")
            else:
                add_expense(user_id, float(amount), category, description.strip(), expense_date.isoformat())
                st.session_state.expense_added = True; st.rerun()

elif menu == "View Expenses":
    st.subheader("📋 Your expense history")
    if df.empty: st.info("No expenses yet. Add an expense to get started.")
    else:
        search = st.text_input("🔎 Search description or category", placeholder="Type to filter")
        view = df.copy()
        if search.strip():
            mask = view["category"].astype(str).str.contains(search, case=False, na=False) | view["description"].astype(str).str.contains(search, case=False, na=False)
            view = view[mask]
        view["expense_date"] = view["expense_date"].astype(str).str[:10]
        st.dataframe(view, width="stretch", hide_index=True)
        st.caption(f"Showing {len(view)} of {len(df)} expenses")

elif menu == "Edit Expense":
    st.subheader("✏️ Edit an expense")
    if df.empty: st.info("No expenses available to edit.")
    else:
        labels = {int(r.id): f"#{int(r.id)} · ₹{float(r.amount):,.2f} · {r.category} · {str(r.expense_date)[:10]}" for r in df.itertuples()}
        expense_id = st.selectbox("Choose expense", list(labels), format_func=lambda x: labels[x])
        expense = df[df["id"] == expense_id].iloc[0]
        categories = ["Food", "Travel", "Shopping", "Education", "Entertainment", "Health", "Bills", "Other"]
        with st.form("edit_form"):
            amount = st.number_input("Amount (₹)", min_value=.01, value=float(expense["amount"]), step=10.0)
            category = st.selectbox("Category", categories, index=categories.index(expense["category"]) if expense["category"] in categories else 0)
            description = st.text_input("Description", value="" if pd.isna(expense["description"]) else str(expense["description"]))
            date_value = pd.to_datetime(expense["expense_date"]).date()
            expense_date = st.date_input("Expense date", value=date_value)
            save = st.form_submit_button("Save changes", type="primary")
        if save:
            update_expense(user_id, int(expense_id), float(amount), category, description.strip(), expense_date.isoformat())
            st.success("Expense updated."); st.rerun()

elif menu == "Delete Expenses":
    st.subheader("🗑️ Manage and delete expenses")
    if df.empty: st.info("No expenses available to delete.")
    else:
        st.warning("Deletion is permanent. Double-check the selected records before confirming.")
        labels = {int(r.id): f"#{int(r.id)} · ₹{float(r.amount):,.2f} · {r.category} · {str(r.expense_date)[:10]} · {str(r.description or '')}" for r in df.itertuples()}
        selected = st.multiselect("Select one or more expenses", list(labels), format_func=lambda x: labels[x])
        confirm = st.checkbox("I understand that the selected expenses will be permanently deleted.", key="confirm_multi_delete")
        if st.button("Delete selected expenses", type="primary", disabled=not selected):
            if confirm:
                delete_expenses(user_id, selected)
                st.session_state.confirm_multi_delete = False
                st.success(f"Deleted {len(selected)} expense(s).")
                st.rerun()
            else: st.error("Please confirm the deletion first.")
        st.divider()
        st.markdown("#### ⚠️ Clear all my expenses")
        clear_confirm = st.checkbox("I want to permanently clear every expense in my account.", key="confirm_clear_all")
        if st.button("Clear all my data", disabled=not clear_confirm):
            clear_expenses(user_id)
            st.session_state.confirm_clear_all = False
            st.success("All your expenses have been cleared."); st.rerun()

elif menu == "Settings":
    st.subheader("⚙️ Settings & data safety")
    st.write("Your records are filtered by the signed-in account when Google authentication is configured.")
    st.write("Local development stores data in `data/expenses.db`. For a public multi-user deployment, configure PostgreSQL using `DATABASE_URL` so records persist reliably.")
    st.info("Never commit passwords, OAuth client secrets, or database connection strings to GitHub.")

st.markdown("---")
st.caption("Made with Python and Streamlit · Manage your money with confidence 💜")
