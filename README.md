# 💸 Smart Expense Tracker

A polished personal expense manager built with Python, Streamlit, Pandas, Matplotlib, and SQLite/PostgreSQL.

## Features

- Dashboard with total spending, number of records, and highest-spending category
- Compact category and monthly trend charts
- Add, view, search, edit, and delete expenses
- Select multiple expenses for deletion
- Confirmed **Clear all my expenses** action
- Input validation and duplicate-submit protection
- Google sign-in support through Streamlit's native OIDC authentication
- Per-account filtering when Google sign-in is configured
- SQLite for local development and PostgreSQL for deployment
- Responsive layout, animated page entrance, and friendly visual styling

## Project structure

```text
Smart_Expense_Tracker/
├── app.py
├── database.py
├── analytics.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/                 # Local database is generated here; do not commit it
```

## Run locally (demo mode)

1. Install Python 3.11 or later.
2. Open this folder in VS Code.
3. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

4. Install packages:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

6. Open the local URL shown in the terminal (usually `http://localhost:8501`).

Without authentication secrets, the app runs in **local demo mode** and uses the local SQLite database.

## Public deployment: required setup

For a public multi-user deployment, configure **both Google OIDC and a persistent PostgreSQL database**. Do not rely on a local SQLite file for deployed user data.

### 1. Create a PostgreSQL database

Create a project in Supabase or another PostgreSQL provider and copy its connection string. Keep it private. The app creates its `expenses` table automatically on startup.

### 2. Configure Google sign-in

Create an OAuth 2.0 Web application in Google Cloud Console. Add the deployed app's callback URL to **Authorized redirect URIs**:

`https://YOUR-APP-NAME.streamlit.app/oauth2callback`

For local testing, also add:

`http://localhost:8501/oauth2callback`

Create `.streamlit/secrets.toml` locally (do not commit it) with the following structure, replacing every placeholder:

```toml
DATABASE_URL = "YOUR_PRIVATE_POSTGRESQL_CONNECTION_STRING"

[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "REPLACE_WITH_A_LONG_RANDOM_SECRET"
client_id = "YOUR_GOOGLE_OAUTH_CLIENT_ID"
client_secret = "YOUR_GOOGLE_OAUTH_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

For deployment, add the same keys in Streamlit Community Cloud's **App settings → Secrets**, but change `redirect_uri` to your deployed callback URL. Keep the OAuth client secret and database URL private. Never put secrets in `app.py`, GitHub, screenshots, or a public README.

### 3. Publish on GitHub and deploy

1. Create a GitHub repository and upload the project files (not `.venv`, `data/expenses.db`, or `.streamlit/secrets.toml`).
2. Open Streamlit Community Cloud and deploy the repository, selecting `app.py` as the entry point.
3. Add the secrets above in the app's settings.
4. Confirm the deployed callback URI exactly matches the URI configured in Google Cloud.
5. Test using two different Google accounts: each account should see only its own records.

Streamlit Community Cloud provides an app URL ending in `streamlit.app`. A custom domain is a separate optional setup.

## Data safety notes

- Local demo mode uses one local profile. It is intended for development, not shared use.
- When authentication is configured, database queries are scoped to the signed-in account ID/email.
- For deployed use, configure PostgreSQL so data persists and multiple accounts can safely use the app.
- Clear/delete actions permanently remove records and require confirmation.
- `.streamlit/secrets.toml`, `.env`, `.venv/`, and `data/expenses.db` must remain out of Git.

## Troubleshooting

- If PowerShell says `streamlit` is not recognized, run `\.venv\Scripts\python.exe -m streamlit run app.py` from the project folder.
- If Google sign-in does not appear, verify that `[auth]` secrets are configured and that the redirect URI matches exactly.
- If PostgreSQL is configured, ensure the provider allows connections from the deployment environment and that the connection string is correct.

## Author

**Bhuvaneshwari Balla**  
B.Tech – Computer Science and Engineering

## License

Educational and portfolio project.
