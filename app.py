"""
JITU - Jaringan Informasi Transaksi UMKM
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add modules to path
sys.path.append(str(Path(__file__).parent))

from modules.data_loader import DataLoader
from modules.cleaner import DataCleaner
from modules.analyzer import BusinessAnalyzer
from modules.narrator import InsightNarrator
from modules.validator import DataValidator


# Page configuration
st.set_page_config(
    page_title="JITU - Data to Duit",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6B35;
    }
    .insight-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .insight-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .insight-danger {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .insight-info {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'df_raw' not in st.session_state:
        st.session_state.df_raw = None
    if 'df_clean' not in st.session_state:
        st.session_state.df_clean = None
    if 'column_mapping' not in st.session_state:
        st.session_state.column_mapping = {}
    if 'mapping_confirmed' not in st.session_state:
        st.session_state.mapping_confirmed = False


def display_welcome_screen():
    """Display welcome screen with upload option"""
    st.markdown('<div class="main-header">JITU</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload Data, Temukan Cuan</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        ### Cara Menggunakan JITU:
        
        1. Upload file transaksi Anda (CSV atau Excel)
        2. Konfirmasi mapping kolom
        3. Dapatkan insight dan rekomendasi bisnis
        
        **Format data yang didukung:**
        - File CSV (.csv)
        - File Excel (.xlsx, .xls)
        
        **Kolom yang diperlukan:**
        - Tanggal transaksi
        - Nama produk
        - Harga/Total
        - Jumlah (opsional)
        """)
        
        uploaded_file = st.file_uploader(
            "Pilih file transaksi Anda",
            type=['csv', 'xlsx', 'xls'],
            help="Upload file CSV atau Excel yang berisi data transaksi"
        )
        
        if uploaded_file is not None:
            process_uploaded_file(uploaded_file)


def process_uploaded_file(uploaded_file):
    """Process uploaded file and store in session state"""
    try:
        # Validate file format
        file_extension = Path(uploaded_file.name).suffix
        is_valid, message = DataValidator.validate_file_format(uploaded_file.name)
        
        if not is_valid:
            st.error(message)
            return
        
        # Read file
        with st.spinner("Membaca file..."):
            df_raw, mapping = DataLoader.load_and_map(uploaded_file, file_extension)
        
        # Validate minimum data requirements
        min_valid, min_issues = DataValidator.validate_minimum_data(df_raw)
        if not min_valid:
            st.error("Data tidak valid:")
            for issue in min_issues:
                st.error(f"- {issue}")
            return
        
        # Store in session state
        st.session_state.df_raw = df_raw
        st.session_state.column_mapping = mapping
        st.session_state.mapping_confirmed = False
        
        st.success(f"File berhasil dimuat! Total {len(df_raw)} baris data.")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error membaca file: {str(e)}")
        st.info("Pastikan file Anda dalam format yang benar dan tidak corrupt.")


def display_mapping_confirmation():
    """Display column mapping confirmation screen"""
    st.markdown('<div class="main-header">Konfirmasi Kolom Data</div>', unsafe_allow_html=True)
    
    st.info("JITU telah mendeteksi kolom-kolom berikut. Silakan periksa dan konfirmasi.")
    
    # Show sample data
    st.subheader("Preview Data (5 Baris Pertama)")
    st.dataframe(st.session_state.df_raw.head(), use_container_width=True)
    
    st.markdown("---")
    
    # Show detected mapping
    st.subheader("Kolom yang Terdeteksi")
    
    mapping = st.session_state.column_mapping
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Kolom Standar → Kolom Anda**")
        
        if 'date' in mapping:
            st.success(f"Tanggal: {mapping['date']}")
        else:
            st.error("Tanggal: Tidak terdeteksi")
        
        if 'product' in mapping:
            st.success(f"Produk: {mapping['product']}")
        else:
            st.error("Produk: Tidak terdeteksi")
        
        if 'price' in mapping:
            st.success(f"Harga: {mapping['price']}")
        else:
            st.error("Harga: Tidak terdeteksi")
        
        if 'qty' in mapping:
            st.info(f"Jumlah: {mapping['qty']}")
        else:
            st.warning("Jumlah: Tidak terdeteksi (opsional)")
    
    with col2:
        st.markdown("**Kolom Tambahan**")
        
        if 'category' in mapping:
            st.info(f"Kategori: {mapping['category']}")
        
        if 'customer' in mapping:
            st.info(f"Pelanggan: {mapping['customer']}")
    
    # Manual mapping adjustment
    st.markdown("---")
    st.subheader("Sesuaikan Mapping (Jika Perlu)")
    
    with st.form("mapping_form"):
        all_columns = list(st.session_state.df_raw.columns)
        
        date_col = st.selectbox(
            "Kolom Tanggal",
            options=[''] + all_columns,
            index=all_columns.index(mapping['date']) + 1 if 'date' in mapping else 0
        )
        
        product_col = st.selectbox(
            "Kolom Produk",
            options=[''] + all_columns,
            index=all_columns.index(mapping['product']) + 1 if 'product' in mapping else 0
        )
        
        price_col = st.selectbox(
            "Kolom Harga",
            options=[''] + all_columns,
            index=all_columns.index(mapping['price']) + 1 if 'price' in mapping else 0
        )
        
        qty_col = st.selectbox(
            "Kolom Jumlah (Opsional)",
            options=[''] + all_columns,
            index=all_columns.index(mapping['qty']) + 1 if 'qty' in mapping else 0
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            if st.form_submit_button("Konfirmasi", use_container_width=True):
                # Update mapping
                new_mapping = {}
                if date_col:
                    new_mapping['date'] = date_col
                if product_col:
                    new_mapping['product'] = product_col
                if price_col:
                    new_mapping['price'] = price_col
                if qty_col:
                    new_mapping['qty'] = qty_col
                
                # Validate required columns
                if not all(k in new_mapping for k in ['date', 'product', 'price']):
                    st.error("Kolom Tanggal, Produk, dan Harga wajib dipilih!")
                else:
                    st.session_state.column_mapping = new_mapping
                    st.session_state.mapping_confirmed = True
                    st.rerun()
        
        with col3:
            if st.form_submit_button("Mulai Ulang", use_container_width=True):
                st.session_state.df_raw = None
                st.session_state.column_mapping = {}
                st.session_state.mapping_confirmed = False
                st.rerun()


def clean_and_analyze_data():
    """Clean data and perform analysis"""
    df_raw = st.session_state.df_raw
    mapping = st.session_state.column_mapping
    
    # Apply column mapping
    df_mapped = DataLoader.apply_column_mapping(df_raw, mapping)
    
    # Define column types for cleaning
    column_types = {
        'date': 'date',
        'price': 'currency',
        'product': 'text'
    }
    
    if 'qty' in df_mapped.columns:
        column_types['qty'] = 'numeric'
    
    # Clean data
    df_clean = DataCleaner.clean_dataframe(df_mapped, column_types)
    
    # Remove duplicates
    df_clean = DataCleaner.remove_duplicates(df_clean)
    
    # Handle missing values
    df_clean = df_clean.dropna(subset=['date', 'product', 'price'])
    
    # If no qty column, create one with value 1
    if 'qty' not in df_clean.columns:
        df_clean['qty'] = 1
    
    # Store cleaned data
    st.session_state.df_clean = df_clean
    
    return df_clean


def display_dashboard():
    """Display main analytics dashboard"""
    st.markdown('<div class="main-header">Dashboard JITU</div>', unsafe_allow_html=True)
    
    # Clean and analyze if not done yet
    if st.session_state.df_clean is None:
        with st.spinner("Membersihkan dan menganalisis data..."):
            df_clean = clean_and_analyze_data()
    else:
        df_clean = st.session_state.df_clean
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### Pengaturan")
        
        if st.button("Upload File Baru"):
            st.session_state.df_raw = None
            st.session_state.df_clean = None
            st.session_state.column_mapping = {}
            st.session_state.mapping_confirmed = False
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### Info Data")
        st.metric("Total Transaksi", len(df_clean))
        st.metric("Produk Unik", df_clean['product'].nunique())
        
        if 'date' in df_clean.columns:
            date_range = (df_clean['date'].max() - df_clean['date'].min()).days
            st.metric("Rentang Hari", f"{date_range} hari")
    
    # Main metrics
    metrics = BusinessAnalyzer.get_summary_metrics(df_clean)
    
    st.markdown("### Ringkasan Bisnis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Total Pendapatan",
            f"Rp {metrics['total_revenue']:,.0f}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Total Transaksi",
            f"{metrics['total_transactions']:,}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Rata-rata per Transaksi",
            f"Rp {metrics['average_transaction']:,.0f}"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Trends and insights
    st.markdown("### Tren Penjualan")
    
    # Sales trend chart
    trend_data = BusinessAnalyzer.get_sales_trend(df_clean)
    
    if not trend_data.empty:
        st.line_chart(
            trend_data.set_index('date')['revenue'],
            use_container_width=True
        )
        
        # Trend analysis
        trend_analysis = BusinessAnalyzer.get_trend_direction(df_clean)
        trend_insight = InsightNarrator.narrate_trend(trend_analysis)
        
        insight_class = f"insight-{trend_insight['type']}"
        st.markdown(
            f'<div class="{insight_class}">'
            f'<strong>{trend_insight["title"]}</strong><br>'
            f'{trend_insight["message"]}'
            f'</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Top products
    st.markdown("### Produk Terlaris")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Berdasarkan Jumlah Terjual")
        top_qty = BusinessAnalyzer.get_best_selling_products(df_clean, top_n=5)
        
        if not top_qty.empty:
            st.dataframe(
                top_qty.rename(columns={'product': 'Produk', 'total_qty': 'Jumlah'}),
                use_container_width=True,
                hide_index=True
            )
            
            qty_insight = InsightNarrator.narrate_top_product(top_qty, 'quantity')
            st.markdown(
                f'<div class="insight-{qty_insight["type"]}">'
                f'<strong>{qty_insight["title"]}</strong><br>'
                f'{qty_insight["message"]}'
                f'</div>',
                unsafe_allow_html=True
            )
    
    with col2:
        st.markdown("#### Berdasarkan Pendapatan")
        top_revenue = BusinessAnalyzer.get_revenue_by_product(df_clean, top_n=5)
        
        if not top_revenue.empty:
            st.dataframe(
                top_revenue.rename(columns={'product': 'Produk', 'total_revenue': 'Pendapatan'}).assign(
                    Pendapatan=lambda x: x['Pendapatan'].apply(lambda v: f"Rp {v:,.0f}")
                ),
                use_container_width=True,
                hide_index=True
            )
            
            rev_insight = InsightNarrator.narrate_top_product(top_revenue, 'revenue')
            st.markdown(
                f'<div class="insight-{rev_insight["type"]}">'
                f'<strong>{rev_insight["title"]}</strong><br>'
                f'{rev_insight["message"]}'
                f'</div>',
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    
    # Pareto Analysis
    st.markdown("### Analisis Pareto (Prinsip 80/20)")
    
    pareto_products, pareto_percentage = BusinessAnalyzer.get_pareto_analysis(df_clean)
    
    if not pareto_products.empty:
        st.info(
            f"{len(pareto_products)} produk ({pareto_percentage:.1f}% dari total produk) "
            f"menghasilkan 80% dari total pendapatan"
        )
        
        pareto_insight = InsightNarrator.narrate_pareto(pareto_products, pareto_percentage)
        st.markdown(
            f'<div class="insight-{pareto_insight["type"]}">'
            f'<strong>{pareto_insight["title"]}</strong><br>'
            f'{pareto_insight["message"]}'
            f'</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Day of week analysis
    st.markdown("### Pola Penjualan Berdasarkan Hari")
    
    day_analysis = BusinessAnalyzer.get_day_of_week_analysis(df_clean)
    
    if not day_analysis.empty:
        st.bar_chart(
            day_analysis.set_index('day_of_week')['mean'],
            use_container_width=True
        )
        
        day_insight = InsightNarrator.narrate_day_pattern(day_analysis)
        st.markdown(
            f'<div class="insight-{day_insight["type"]}">'
            f'<strong>{day_insight["title"]}</strong><br>'
            f'{day_insight["message"]}'
            f'</div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Slow moving products
    st.markdown("### Produk Lambat Bergerak")
    
    slow_products = BusinessAnalyzer.get_slow_moving_products(df_clean, days_threshold=14)
    
    slow_insight = InsightNarrator.narrate_slow_products(slow_products)
    st.markdown(
        f'<div class="insight-{slow_insight["type"]}">'
        f'<strong>{slow_insight["title"]}</strong><br>'
        f'{slow_insight["message"]}'
        f'</div>',
        unsafe_allow_html=True
    )
    
    if not slow_products.empty:
        st.dataframe(
            slow_products.head(10).rename(columns={
                'product': 'Produk',
                'last_sale_date': 'Terakhir Terjual',
                'days_since_last_sale': 'Hari Tidak Terjual'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # Recommendations
    st.markdown("### Rekomendasi Aksi")
    
    all_insights = {
        'trend': trend_insight if 'trend_insight' in locals() else {},
        'slow_products': slow_insight,
        'pareto': pareto_insight if 'pareto_insight' in locals() else {}
    }
    
    recommendations = InsightNarrator.generate_recommendations(all_insights)
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")


def main():
    """Main application entry point"""
    initialize_session_state()
    
    # Navigation logic
    if st.session_state.df_raw is None:
        display_welcome_screen()
    elif not st.session_state.mapping_confirmed:
        display_mapping_confirmation()
    else:
        display_dashboard()


if __name__ == "__main__":
    main()
