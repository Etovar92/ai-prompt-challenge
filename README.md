# 🤖 AI Prompt Challenge — Leaderboard Tracker

Pulls reaction counts from your Microsoft Teams challenge post and displays a ranked leaderboard in the terminal.

---

## 🔧 One-Time Setup

### 1. Register an Azure App (5 minutes)

1. Go to [portal.azure.com](https://portal.azure.com) → **Azure Active Directory** → **App registrations** → **New registration**
2. Name it `AI Prompt Challenge Leaderboard`, click **Register**
3. Copy the **Application (client) ID** and **Directory (tenant) ID**
4. Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions**
5. Add all three:
   - `ChannelMessage.Read.All`
   - `Team.ReadBasic.All`
   - `Channel.ReadBasic.All`
6. Click **Grant admin consent**
7. Under **Authentication**, enable **Allow public client flows** → Save

### 2. Configure your `.env`

```bash
cp .env.example .env
```

Fill in `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` from the portal.

### 3. Install dependencies

```bash
uv sync
```

---

## 🚀 Running the Leaderboard

```bash
make leaderboard
# or directly:
uv run leaderboard
```

**First run:** Opens a browser sign-in prompt (device code flow). Your token is cached in `.token_cache.json` for subsequent runs.

**Interactive flow:**
1. Pick your Team
2. Pick the Channel
3. Pick the challenge post (the message users replied to with their prompts)
4. The leaderboard displays instantly 🏆

**After first run**, copy the printed IDs into your `.env` to skip the menus:

```env
TEAMS_TEAM_ID=19:abc123...
TEAMS_CHANNEL_ID=19:xyz456...
CHALLENGE_MESSAGE_ID=1234567890
```

---

## 📊 How Scoring Works

| Metric | Points |
|---|---|
| Each emoji reaction on a submission | +1 |

Score = total emoji reactions on that reply. Run the script any time for a fresh snapshot.

---

## 🔒 Security Notes

- `.env` and `.token_cache.json` are in `.gitignore` — never commit them
- Uses **delegated permissions** (reads only what you can see as a logged-in user)
- No secrets stored — pure device code / OAuth2 flow
