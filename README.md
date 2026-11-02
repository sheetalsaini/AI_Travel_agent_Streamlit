# AI Travel Agent

Streamlit assistant for travel research, weather, itineraries, cost breakdowns,
currency calculations and YouTube searches using LangChain and LangGraph.

## Local setup

Use Python 3.11 or later:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run streamlit_app.py
```

Windows activation: `.venv\Scripts\activate`.
Fill in `.env` locally before requesting a plan:

| Credential | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | Required for the `gpt-4o` model, with API billing/access. |
| `SERPER_API_KEY` | Optional Google Serper search. DuckDuckGo is used without it. |
| `OPENWEATHERMAP_API_KEY` | Required for current weather; missing weather is reported without it. |

DuckDuckGo and YouTube require internet access and may have provider limits.
Currency rates come from search, not a dedicated currency API. Verify rate
freshness, prices and availability before booking. Current weather is not a
forecast for future travel dates.

Environment variables or `.streamlit/secrets.toml` can also supply these names.
Streamlit secrets take precedence. Never commit real credentials or include them
in chat or screenshots. `.env.example` contains blank placeholders only.
For Streamlit Cloud, select `streamlit_app.py` as the entry point and add keys in
the deployment's Secrets settings. Do not disable CORS or XSRF protections.

## Security scope

The active app no longer exposes a Python shell to the model. Four allowlisted
arithmetic tools use validated numeric schemas. They accept decimals and reject
code strings, booleans, nonfinite values, extra fields and operands outside
+/- 1 trillion. Zero division and nonfinite results fail explicitly.
Python floating point is used for travel estimates, not accounting-grade math.
The existing `substraction` tool name is preserved for compatibility.

The experimental LangChain dependency is removed. Search, weather, video and
itinerary tools remain. Raw provider exceptions are no longer displayed in the
UI, and missing Streamlit secrets files allow environment-variable fallback.
Historical notebooks are not the hardened entry point.

This change does not certify all dependencies, prompt injection defenses or a
live deployment. If a key was previously published, revoke/rotate it with the
provider. Ignore rules do not remove secrets from Git history.

## Tests and release verification

Credential-free tests:

```bash
python -m unittest discover -s tests -v
python -m py_compile streamlit_app.py calculations.py
```

Tests cover decimal costs, currency multiplication, invalid/code operands,
extra fields, zero division, overflow and the app's tool allowlist.
They do not call external services.

Before release, install dependencies in a clean environment and test the UI
with valid credentials. Check weather, Google search, DuckDuckGo without Serper,
YouTube links, decimal budgets, currency conversion, missing keys and provider
failures. Model tool selection, live responses and deployment behavior require
separate verification.
