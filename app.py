"""
🗺️ Sales Leads Map — Bareilly, Uttar Pradesh
Interactive map dashboard for institutional sales teams.
Reads company data from Excel, geocodes addresses, and plots on an interactive map.
"""

import json
import os
import time
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

# ─── Configuration ───────────────────────────────────────────────────────────
BAREILLY_CENTER = (28.3670, 79.4304)
DEFAULT_ZOOM = 13
GEOCODE_CACHE_FILE = "geocode_cache.json"
REQUIRED_COLUMNS = ["Company", "Address", "Contact_Person", "Designation", "Phone", "Email"]

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Leads Map — Bareilly",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Header area */
    .main-header {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0 0 0.3rem 0;
    }
    .main-header p {
        color: rgba(255, 255, 255, 0.65);
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
    }

    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 1.3rem 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
    .stat-number {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .stat-label {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.5);
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-top: 0.3rem;
    }

    /* Company list in sidebar */
    .company-item {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    .company-item:hover {
        background: rgba(102, 126, 234, 0.08);
        border-color: rgba(102, 126, 234, 0.25);
    }
    .company-name {
        font-weight: 600;
        font-size: 0.9rem;
        color: #e0e0e0;
        margin: 0;
    }
    .company-contact {
        font-size: 0.78rem;
        color: rgba(255, 255, 255, 0.45);
        margin: 0.15rem 0 0 0;
    }

    /* Status badges */
    .badge-success {
        display: inline-block;
        background: rgba(46, 213, 115, 0.15);
        color: #2ed573;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-warning {
        display: inline-block;
        background: rgba(255, 165, 2, 0.15);
        color: #ffa502;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-error {
        display: inline-block;
        background: rgba(255, 71, 87, 0.15);
        color: #ff4757;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e0e0;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 0.5rem;
    }

    /* Table */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


# ─── Geocoding Cache ─────────────────────────────────────────────────────────
def load_geocode_cache() -> dict:
    """Load cached geocode results from disk."""
    if os.path.exists(GEOCODE_CACHE_FILE):
        try:
            with open(GEOCODE_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_geocode_cache(cache: dict):
    """Persist geocode cache to disk."""
    with open(GEOCODE_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


# ─── Geocoding Agent ─────────────────────────────────────────────────────────
def geocode_address(address: str, cache: dict) -> tuple[float | None, float | None]:
    """
    Geocode an address within Bareilly using Nominatim.
    Uses a multi-strategy approach for best results:
      1. Try full address + "Bareilly, Uttar Pradesh, India"
      2. Try simplified address + "Bareilly"
      3. Fallback to just "Bareilly, Uttar Pradesh" (city center)
    """
    cache_key = address.strip().lower()
    if cache_key in cache:
        return cache[cache_key]["lat"], cache[cache_key]["lon"]

    geolocator = Nominatim(user_agent="bareilly_sales_map_v1", timeout=10)

    # Strategy 1: Full address with Bareilly context
    queries = [
        f"{address}, Bareilly, Uttar Pradesh, India",
        f"{address}, Bareilly, India",
        f"{address}, Bareilly",
    ]

    for query in queries:
        try:
            location = geolocator.geocode(query, exactly_one=True)
            if location:
                lat, lon = location.latitude, location.longitude
                # Verify it's roughly within Bareilly bounds (generous range)
                if 28.2 <= lat <= 28.6 and 79.2 <= lon <= 79.6:
                    cache[cache_key] = {"lat": lat, "lon": lon, "query": query}
                    save_geocode_cache(cache)
                    return lat, lon
            time.sleep(1.1)  # Respect Nominatim rate limit
        except (GeocoderTimedOut, GeocoderUnavailable):
            time.sleep(2)
            continue

    # Fallback: Bareilly city center with small random offset to avoid overlap
    import random

    lat = BAREILLY_CENTER[0] + random.uniform(-0.008, 0.008)
    lon = BAREILLY_CENTER[1] + random.uniform(-0.008, 0.008)
    cache[cache_key] = {"lat": lat, "lon": lon, "query": "fallback_city_center"}
    save_geocode_cache(cache)
    return lat, lon


def geocode_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Geocode all rows in the dataframe that lack coordinates."""
    cache = load_geocode_cache()
    has_coords = "Latitude" in df.columns and "Longitude" in df.columns

    if not has_coords:
        df["Latitude"] = None
        df["Longitude"] = None

    progress = st.progress(0, text="🌐 Geocoding addresses...")
    total = len(df)
    geocoded_count = 0
    failed_count = 0

    for idx, row in df.iterrows():
        # Skip if already has valid coordinates
        if has_coords and pd.notna(row.get("Latitude")) and pd.notna(row.get("Longitude")):
            progress.progress((idx + 1) / total, text=f"⏭️ Skipping {row['Company']} (has coordinates)")
            continue

        address = str(row.get("Address", ""))
        if not address or address.lower() == "nan":
            failed_count += 1
            continue

        progress.progress(
            (idx + 1) / total,
            text=f"🔍 Geocoding: {row['Company']} — {address[:40]}...",
        )

        lat, lon = geocode_address(address, cache)
        if lat and lon:
            df.at[idx, "Latitude"] = lat
            df.at[idx, "Longitude"] = lon
            geocoded_count += 1
        else:
            failed_count += 1

    progress.empty()
    return df, geocoded_count, failed_count


# ─── Map Builder ──────────────────────────────────────────────────────────────
def build_popup_html(row: pd.Series) -> str:
    """Build a styled HTML popup for a map marker."""
    company = row.get("Company", "N/A")
    contact = row.get("Contact_Person", "N/A")
    designation = row.get("Designation", "N/A")
    phone = row.get("Phone", "N/A")
    email = row.get("Email", "N/A")
    address = row.get("Address", "N/A")

    return f"""
    <div style="
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        min-width: 280px;
        max-width: 320px;
        padding: 0;
        margin: 0;
    ">
        <div style="
            background: linear-gradient(135deg, #302b63, #24243e);
            padding: 14px 16px;
            border-radius: 10px 10px 0 0;
        ">
            <h3 style="
                margin: 0;
                color: #fff;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: -0.3px;
            ">🏢 {company}</h3>
        </div>
        <div style="
            padding: 14px 16px;
            background: #fafbfc;
            border-radius: 0 0 10px 10px;
            border: 1px solid #e8ecf0;
            border-top: none;
        ">
            <table style="width:100%; border-collapse:collapse; font-size:13px; color:#333;">
                <tr>
                    <td style="padding:5px 8px 5px 0; color:#888; white-space:nowrap; vertical-align:top;">👤</td>
                    <td style="padding:5px 0; font-weight:600;">{contact}</td>
                </tr>
                <tr>
                    <td style="padding:5px 8px 5px 0; color:#888; vertical-align:top;">💼</td>
                    <td style="padding:5px 0; color:#555;">{designation}</td>
                </tr>
                <tr>
                    <td style="padding:5px 8px 5px 0; color:#888; vertical-align:top;">📞</td>
                    <td style="padding:5px 0;">
                        <a href="tel:{phone}" style="color:#302b63; text-decoration:none; font-weight:500;">{phone}</a>
                    </td>
                </tr>
                <tr>
                    <td style="padding:5px 8px 5px 0; color:#888; vertical-align:top;">✉️</td>
                    <td style="padding:5px 0;">
                        <a href="mailto:{email}" style="color:#302b63; text-decoration:none; font-weight:500;">{email}</a>
                    </td>
                </tr>
                <tr>
                    <td style="padding:5px 8px 5px 0; color:#888; vertical-align:top;">📍</td>
                    <td style="padding:5px 0; color:#555; line-height:1.4;">{address}</td>
                </tr>
            </table>
        </div>
    </div>
    """


MARKER_COLORS = [
    "#667eea", "#764ba2", "#f093fb", "#4facfe",
    "#43e97b", "#fa709a", "#fee140", "#30cfd0",
    "#a18cd1", "#fbc2eb", "#ff9a9e", "#fad0c4",
]


def create_map(df: pd.DataFrame, use_clustering: bool = True) -> folium.Map:
    """Create a Folium map with company markers."""
    # Calculate center from data if available, else use Bareilly
    valid = df.dropna(subset=["Latitude", "Longitude"])
    if len(valid) > 0:
        center_lat = valid["Latitude"].mean()
        center_lon = valid["Longitude"].mean()
    else:
        center_lat, center_lon = BAREILLY_CENTER

    # Base map with dark tile style
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=DEFAULT_ZOOM,
        tiles="CartoDB Positron",
        control_scale=True,
    )

    # Add alternate tile layers
    folium.TileLayer("CartoDB dark_matter", name="Dark Mode").add_to(m)
    folium.TileLayer("OpenStreetMap", name="Street Map").add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)

    # Marker cluster or individual markers
    if use_clustering and len(valid) > 5:
        marker_group = MarkerCluster(name="Companies").add_to(m)
    else:
        marker_group = m

    for i, (_, row) in enumerate(valid.iterrows()):
        lat = row["Latitude"]
        lon = row["Longitude"]
        company = row.get("Company", "Unknown")
        color = MARKER_COLORS[i % len(MARKER_COLORS)]

        popup_html = build_popup_html(row)

        # Custom icon with colored marker
        icon = folium.DivIcon(
            html=f"""
            <div style="
                background: {color};
                width: 32px;
                height: 32px;
                border-radius: 50% 50% 50% 4px;
                transform: rotate(-45deg);
                border: 3px solid white;
                box-shadow: 0 3px 12px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            ">
                <span style="
                    transform: rotate(45deg);
                    color: white;
                    font-size: 14px;
                    font-weight: 800;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.3);
                ">{company[0]}</span>
            </div>
            """,
            icon_size=(32, 32),
            icon_anchor=(16, 32),
        )

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=340),
            tooltip=folium.Tooltip(
                f"<b style='font-size:13px;'>{company}</b>",
                sticky=True,
            ),
            icon=icon,
        ).add_to(marker_group)

    # Add Bareilly city boundary circle (approx)
    folium.Circle(
        location=BAREILLY_CENTER,
        radius=8000,
        color="#667eea",
        weight=1.5,
        fill=True,
        fill_color="#667eea",
        fill_opacity=0.03,
        tooltip="Bareilly City Area",
    ).add_to(m)

    return m


# ─── Data Loading ─────────────────────────────────────────────────────────────
def load_data(source) -> pd.DataFrame | None:
    """Load data from uploaded file or file path."""
    try:
        if isinstance(source, str):
            # File path
            if source.endswith(".xlsx"):
                df = pd.read_excel(source, engine="openpyxl")
            elif source.endswith(".xls"):
                df = pd.read_excel(source, engine="xlrd")
            elif source.endswith(".csv"):
                df = pd.read_csv(source)
            else:
                st.error("Unsupported file format. Use .xlsx, .xls, or .csv")
                return None
        else:
            # Uploaded file object
            name = source.name
            if name.endswith(".xlsx"):
                df = pd.read_excel(source, engine="openpyxl")
            elif name.endswith(".xls"):
                df = pd.read_excel(source, engine="xlrd")
            elif name.endswith(".csv"):
                df = pd.read_csv(source)
            else:
                st.error("Unsupported file format. Use .xlsx, .xls, or .csv")
                return None

        # Validate columns
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            st.error(
                f"Missing required columns: **{', '.join(missing)}**\n\n"
                f"Expected columns: {', '.join(REQUIRED_COLUMNS)}"
            )
            return None

        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    # ── Header ──
    st.markdown(
        """
        <div class="main-header">
            <h1>🗺️ Sales Leads Map — Bareilly</h1>
            <p>Interactive map dashboard for your institutional sales team. 
            Upload your Excel sheet to visualize all company leads on the map.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("## 📁 Data Source")

        source_mode = st.radio(
            "Choose input method",
            ["📤 Upload Excel File", "📂 Link File Path"],
            label_visibility="collapsed",
        )

        df = None

        if source_mode == "📤 Upload Excel File":
            uploaded = st.file_uploader(
                "Drop your Excel or CSV file here",
                type=["xlsx", "xls", "csv"],
                help="Required columns: Company, Address, Contact_Person, Designation, Phone, Email",
            )
            if uploaded:
                df = load_data(uploaded)

        else:
            file_path = st.text_input(
                "Enter file path",
                placeholder=r"C:\Users\...\companies.xlsx",
                help="Absolute path to your Excel/CSV file",
            )
            if file_path and os.path.exists(file_path):
                df = load_data(file_path)
            elif file_path:
                st.warning("File not found. Check the path.")

        # ── Auto-detect sample file ──
        if df is None:
            sample_files = [f for f in os.listdir(".") if f.endswith((".xlsx", ".csv")) and "sample" in f.lower()]
            if sample_files:
                st.markdown("---")
                st.markdown("### 🧪 Sample Data Found")
                if st.button(f"Load `{sample_files[0]}`", use_container_width=True):
                    df = load_data(sample_files[0])
                    if df is not None:
                        st.session_state["loaded_df"] = df

        # Use session state to persist
        if df is not None:
            st.session_state["loaded_df"] = df
        elif "loaded_df" in st.session_state:
            df = st.session_state["loaded_df"]

        # ── Settings ──
        st.markdown("---")
        st.markdown("## ⚙️ Map Settings")
        use_clustering = st.toggle("Cluster nearby markers", value=True)
        show_table = st.toggle("Show data table", value=False)
        auto_refresh = st.toggle("Auto-refresh (file path mode)", value=False)

        if auto_refresh and source_mode == "📂 Link File Path" and file_path:
            st.info("Map will refresh every 30 seconds")

        # ── Company list ──
        if df is not None:
            st.markdown("---")
            st.markdown(f"## 📋 Companies ({len(df)})")
            search = st.text_input("🔍 Search", placeholder="Filter companies...")

            display_df = df
            if search:
                mask = df.apply(lambda row: search.lower() in str(row).lower(), axis=1)
                display_df = df[mask]

            for _, row in display_df.iterrows():
                geocoded = pd.notna(row.get("Latitude")) and pd.notna(row.get("Longitude"))
                badge = '<span class="badge-success">📍 mapped</span>' if geocoded else '<span class="badge-warning">⏳ pending</span>'
                st.markdown(
                    f"""
                    <div class="company-item">
                        <p class="company-name">{row['Company']} {badge}</p>
                        <p class="company-contact">{row.get('Contact_Person', '')} · {row.get('Designation', '')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ── Main Content ──
    if df is None:
        # Empty state
        st.markdown("---")
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            st.markdown(
                """
                <div style="text-align:center; padding: 3rem 1rem;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
                    <h2 style="color: #667eea; margin-bottom: 0.5rem;">Upload Your Sales Data</h2>
                    <p style="color: #888; font-size: 1rem; max-width: 500px; margin: 0 auto;">
                        Upload an Excel file with your company leads using the sidebar. 
                        The map will populate automatically with geocoded markers.
                    </p>
                    <div style="
                        background: rgba(102, 126, 234, 0.08);
                        border: 1px solid rgba(102, 126, 234, 0.2);
                        border-radius: 12px;
                        padding: 1.2rem;
                        margin-top: 1.5rem;
                        text-align: left;
                        font-size: 0.88rem;
                        color: #aaa;
                    ">
                        <strong style="color: #667eea;">Required columns:</strong><br/>
                        Company · Address · Contact_Person · Designation · Phone · Email
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Show empty map centered on Bareilly
        st.markdown("### 📍 Bareilly, Uttar Pradesh")
        empty_map = folium.Map(location=BAREILLY_CENTER, zoom_start=12, tiles="CartoDB Positron")
        folium.Circle(
            location=BAREILLY_CENTER, radius=8000,
            color="#667eea", weight=1.5, fill=True, fill_color="#667eea", fill_opacity=0.04,
            tooltip="Bareilly City",
        ).add_to(empty_map)
        st_folium(empty_map, width=None, height=500, use_container_width=True)
        return

    # ── Geocode ──
    needs_geocoding = "Latitude" not in df.columns or df["Latitude"].isna().any()
    if needs_geocoding:
        with st.status("🌐 Geocoding addresses...", expanded=True) as status:
            df, geocoded_count, failed_count = geocode_dataframe(df)
            st.session_state["loaded_df"] = df
            status.update(
                label=f"✅ Geocoded {geocoded_count} addresses ({failed_count} used fallback)",
                state="complete",
            )

    # ── Stats Row ──
    valid_coords = df.dropna(subset=["Latitude", "Longitude"])
    total = len(df)
    mapped = len(valid_coords)
    unique_designations = df["Designation"].nunique() if "Designation" in df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="stat-card"><p class="stat-number">{total}</p><p class="stat-label">Total Leads</p></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="stat-card"><p class="stat-number">{mapped}</p><p class="stat-label">Mapped</p></div>',
            unsafe_allow_html=True,
        )
    with c3:
        pct = int((mapped / total) * 100) if total else 0
        st.markdown(
            f'<div class="stat-card"><p class="stat-number">{pct}%</p><p class="stat-label">Coverage</p></div>',
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f'<div class="stat-card"><p class="stat-number">{unique_designations}</p><p class="stat-label">Roles</p></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # ── Map ──
    m = create_map(df, use_clustering=use_clustering)
    map_data = st_folium(m, width=None, height=580, use_container_width=True)

    # ── Data Table ──
    if show_table:
        st.markdown("### 📊 Company Data")
        display_cols = [c for c in REQUIRED_COLUMNS + ["Latitude", "Longitude"] if c in df.columns]
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Company": st.column_config.TextColumn("🏢 Company", width="medium"),
                "Contact_Person": st.column_config.TextColumn("👤 Contact"),
                "Phone": st.column_config.TextColumn("📞 Phone"),
                "Email": st.column_config.TextColumn("✉️ Email"),
                "Latitude": st.column_config.NumberColumn("Lat", format="%.4f"),
                "Longitude": st.column_config.NumberColumn("Lon", format="%.4f"),
            },
        )

    # ── Auto-refresh for file path mode ──
    if auto_refresh and source_mode == "📂 Link File Path":
        time.sleep(30)
        st.rerun()


if __name__ == "__main__":
    main()
