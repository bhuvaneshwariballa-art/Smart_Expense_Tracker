import pandas as pd


# Convert database records into a Pandas DataFrame
def create_dataframe(expenses):
    columns = [
        "id",
        "amount",
        "category",
        "description",
        "expense_date"
    ]

    df = pd.DataFrame(expenses, columns=columns)

    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"])
        df["expense_date"] = pd.to_datetime(df["expense_date"])

    return df


# Calculate total expenses
def total_expense(df):
    if df.empty:
        return 0

    return df["amount"].sum()


# Calculate category-wise expenses
def category_summary(df):
    if df.empty:
        return pd.Series(dtype="float64")

    return (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )


# Calculate monthly expenses
def monthly_summary(df):
    if df.empty:
        return pd.DataFrame(
            columns=["month", "amount"]
        )

    data = df.copy()

    data["month"] = (
        data["expense_date"]
        .dt.to_period("M")
        .astype(str)
    )

    return (
        data.groupby("month")["amount"]
        .sum()
        .reset_index()
    )


# Find the highest spending category
def highest_spending_category(df):
    if df.empty:
        return None, 0

    category_data = (
        df.groupby("category")["amount"]
        .sum()
    )

    category = category_data.idxmax()
    amount = category_data.max()

    return category, amount