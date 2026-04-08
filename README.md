# Sales Leads Map — Bareilly
### Interactive map dashboard for institutional sales teams

---

## Quick Start (2 steps)

### Step 1: First-time setup (only once)
1. Double-click **`SETUP.bat`**
2. Wait for it to finish (2-3 minutes)
3. If it asks for admin permission, click **Yes**

### Step 2: Run the app (every time)
1. Double-click **`START.bat`**
2. The map opens in your browser at http://localhost:8501
3. Upload your Excel file using the sidebar
4. **Keep the black window open** while using the app

---

## Your Excel File Format

Your Excel must have these columns (exact spelling):

| Column | What to fill |
|--------|-------------|
| Company | Company name |
| Address | Address in Bareilly (e.g. "Civil Lines, Bareilly") |
| Contact_Person | Contact person's name |
| Designation | Their job title |
| Phone | Phone number |
| Email | Email address |

> **Tip:** Save your file as `.xlsx` (not `.xls`) for best results.

---

## Map Features
- **Hover** on a marker → see company name
- **Click** a marker → see full contact details
- Use the **layer icon** (top-right) to switch map styles
- Toggle **Cluster mode** in sidebar to group nearby markers

---

## Updating Data
When you update your Excel:
- **Upload mode**: just re-upload the new file
- **File path mode**: enable "Auto-refresh" in sidebar — map updates every 30 seconds

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | Run `SETUP.bat` again, or install Python from python.org (check "Add to PATH") |
| App won't start | Make sure no other app is using port 8501 |
| Map shows no markers | Check your Excel column names match exactly |
| Slow first load | Geocoding takes ~1 sec per company. Subsequent loads use cache. |
