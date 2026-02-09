"""
Narrator Module
Converts raw metrics into human-readable insights and recommendations
"""

from typing import Dict, List, Tuple
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightNarrator:
    """
    Translates analytical results into business insights and actionable recommendations
    """
    
@staticmethod
def narrate_trend(trend_analysis: Dict[str, any]) -> Dict[str, str]:
    """
    Generate insight from trend analysis
    
    Args:
        trend_analysis: Dictionary from BusinessAnalyzer.get_trend_direction()
        
    Returns:
        Dictionary with insight type and message
    """
    direction = trend_analysis['direction']
    change = trend_analysis['change_percentage']
    volatility = trend_analysis.get('volatility', 'unknown')
    cv = trend_analysis.get('coefficient_of_variation', 0)
    
    if direction == 'insufficient_data':
        return {
            'type': 'warning',
            'title': 'Data Terbatas',
            'message': 'Belum cukup data untuk menganalisis tren. Upload lebih banyak transaksi untuk mendapat insight yang lebih baik.'
        }
    
    # Handle volatile patterns
    if direction == 'volatile':
        return {
            'type': 'warning',
            'title': 'Penjualan Tidak Stabil',
            'message': f'Penjualan Anda sangat fluktuatif (volatilitas {cv:.1f}%). Grafik naik-turun drastis menandakan bisnis tidak predictable. Identifikasi penyebabnya: apakah stok tidak konsisten, harga berubah-ubah, atau faktor eksternal seperti hari libur? Stabilkan operasional untuk pertumbuhan yang lebih sehat.'
        }
    
    if direction == 'up':
        if volatility == 'high':
            return {
                'type': 'info',
                'title': 'Tren Naik Tapi Tidak Stabil',
                'message': f'Penjualan naik {abs(change):.1f}% tapi sangat fluktuatif (volatilitas {cv:.1f}%). Meskipun tren positif, penjualan naik-turun drastis. Cari cara untuk stabilkan operasional agar pertumbuhan lebih konsisten.'
            }
        else:
            return {
                'type': 'success',
                'title': 'Tren Positif',
                'message': f'Penjualan naik {abs(change):.1f}% dalam periode ini. Pertahankan strategi yang sedang berjalan dan pastikan stok selalu tersedia.'
            }
    
    elif direction == 'down':
        if volatility == 'high':
            return {
                'type': 'danger',
                'title': 'Penjualan Turun dan Tidak Stabil',
                'message': f'PERHATIAN: Penjualan turun {abs(change):.1f}% DAN sangat fluktuatif (volatilitas {cv:.1f}%). Ini kombinasi berbahaya. Segera evaluasi: kualitas produk, harga, kompetitor, dan konsistensi stok. Bisnis dalam kondisi kritis.'
            }
        else:
            return {
                'type': 'danger',
                'title': 'Peringatan Dini',
                'message': f'Penjualan turun {abs(change):.1f}% dalam periode ini. Pertimbangkan untuk membuat promo atau evaluasi harga dan kualitas produk.'
            }
    
    else:  # stable
        if volatility == 'high':
            return {
                'type': 'warning',
                'title': 'Stabil Tapi Fluktuatif',
                'message': f'Rata-rata penjualan stabil (perubahan {abs(change):.1f}%), TAPI grafik naik-turun drastis (volatilitas {cv:.1f}%). Ini bukan kondisi sehat. Cari penyebab fluktuasi: hari libur, stok tidak teratur, atau faktor lain. Stabilkan operasional Anda.'
            }
        else:
            return {
                'type': 'info',
                'title': 'Tren Stabil',
                'message': f'Penjualan relatif stabil (perubahan {abs(change):.1f}%). Ini waktu yang baik untuk mencoba strategi baru tanpa risiko besar.'
            }
    
    @staticmethod
    def narrate_top_product(top_products: pd.DataFrame, metric: str = 'quantity') -> Dict[str, str]:
        """
        Generate insight about top performing products
        
        Args:
            top_products: DataFrame with top products
            metric: What metric to focus on ('quantity' or 'revenue')
            
        Returns:
            Dictionary with insight
        """
        if len(top_products) == 0:
            return {
                'type': 'warning',
                'title': 'Tidak Ada Data Produk',
                'message': 'Tidak ditemukan data produk untuk dianalisis.'
            }
        
        top_product_name = top_products.iloc[0, 0]
        
        if metric == 'quantity':
            col_name = 'total_qty' if 'total_qty' in top_products.columns else top_products.columns[1]
            top_value = top_products.iloc[0][col_name]
            
            return {
                'type': 'success',
                'title': 'Produk Terlaris',
                'message': f'"{top_product_name}" adalah produk paling laku dengan {int(top_value)} unit terjual. Pastikan stok produk ini selalu tersedia dan pertimbangkan untuk meningkatkan margin atau membuat varian baru.'
            }
        else:
            col_name = 'total_revenue' if 'total_revenue' in top_products.columns else top_products.columns[1]
            top_value = top_products.iloc[0][col_name]
            
            return {
                'type': 'success',
                'title': 'Penyumbang Omzet Terbesar',
                'message': f'"{top_product_name}" menghasilkan pendapatan Rp {top_value:,.0f}. Produk ini adalah tulang punggung bisnis Anda. Jaga kualitas dan ketersediaan stoknya.'
            }
    
    @staticmethod
    def narrate_pareto(pareto_products: pd.DataFrame, percentage: float) -> Dict[str, str]:
        """
        Generate insight from Pareto analysis
        
        Args:
            pareto_products: DataFrame from pareto analysis
            percentage: Percentage of products contributing to 80% revenue
            
        Returns:
            Dictionary with insight
        """
        if len(pareto_products) == 0:
            return {
                'type': 'info',
                'title': 'Analisis Pareto',
                'message': 'Tidak cukup data untuk analisis Pareto.'
            }
        
        num_products = len(pareto_products)
        
        if percentage <= 20:
            return {
                'type': 'success',
                'title': 'Fokus Produk Sangat Baik',
                'message': f'Hanya {num_products} produk ({percentage:.1f}%) yang menghasilkan 80% pendapatan Anda. Ini efisiensi yang baik. Fokuskan perhatian pada produk-produk ini untuk maksimalkan profit.'
            }
        elif percentage <= 40:
            return {
                'type': 'info',
                'title': 'Fokus Produk Normal',
                'message': f'{num_products} produk ({percentage:.1f}%) menghasilkan 80% pendapatan. Ini cukup normal. Pertimbangkan untuk mengurangi produk yang kurang laku agar operasional lebih efisien.'
            }
        else:
            return {
                'type': 'warning',
                'title': 'Terlalu Banyak Produk',
                'message': f'{num_products} produk ({percentage:.1f}%) diperlukan untuk mencapai 80% pendapatan. Ini menandakan portfolio produk terlalu luas. Pertimbangkan untuk fokus pada produk terlaris dan kurangi produk yang tidak menguntungkan.'
            }
    
    @staticmethod
    def narrate_day_pattern(day_analysis: pd.DataFrame) -> Dict[str, str]:
        """
        Generate insight from day of week analysis
        
        Args:
            day_analysis: DataFrame from day of week analysis
            
        Returns:
            Dictionary with insight
        """
        if len(day_analysis) == 0:
            return {
                'type': 'info',
                'title': 'Pola Harian',
                'message': 'Tidak cukup data untuk menganalisis pola harian.'
            }
        
        # Find best and worst days
        best_day = day_analysis.loc[day_analysis['mean'].idxmax(), 'day_of_week']
        worst_day = day_analysis.loc[day_analysis['mean'].idxmin(), 'day_of_week']
        
        best_revenue = day_analysis['mean'].max()
        worst_revenue = day_analysis['mean'].min()
        
        # Translate day names to Indonesian
        day_translation = {
            'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
            'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
        }
        
        best_day_id = day_translation.get(best_day, best_day)
        worst_day_id = day_translation.get(worst_day, worst_day)
        
        return {
            'type': 'info',
            'title': 'Pola Hari Terbaik',
            'message': f'Hari {best_day_id} adalah hari paling ramai (rata-rata Rp {best_revenue:,.0f}), sedangkan {worst_day_id} paling sepi (Rp {worst_revenue:,.0f}). Manfaatkan hari ramai untuk upselling, dan buat promo khusus di hari sepi.'
        }
    
    @staticmethod
    def narrate_slow_products(slow_products: pd.DataFrame) -> Dict[str, str]:
        """
        Generate insight about slow moving products
        
        Args:
            slow_products: DataFrame with slow moving products
            
        Returns:
            Dictionary with insight
        """
        if len(slow_products) == 0:
            return {
                'type': 'success',
                'title': 'Tidak Ada Produk Mati',
                'message': 'Semua produk Anda aktif terjual. Pertahankan rotasi stok yang baik ini.'
            }
        
        num_slow = len(slow_products)
        slowest_product = slow_products.iloc[0]
        product_name = slowest_product.iloc[0]
        days_idle = int(slowest_product['days_since_last_sale'])
        
        return {
            'type': 'warning',
            'title': 'Produk Tidak Laku',
            'message': f'Ada {num_slow} produk yang tidak terjual lebih dari 2 minggu. "{product_name}" sudah {days_idle} hari tidak laku. Pertimbangkan untuk membuat diskon besar-besaran atau stop order produk ini.'
        }
    
    @staticmethod
    def narrate_summary(metrics: Dict[str, any]) -> List[str]:
        """
        Generate executive summary from metrics
        
        Args:
            metrics: Dictionary from BusinessAnalyzer.get_summary_metrics()
            
        Returns:
            List of summary sentences
        """
        summary = []
        
        # Revenue summary
        total_revenue = metrics.get('total_revenue', 0)
        total_transactions = metrics.get('total_transactions', 0)
        avg_transaction = metrics.get('average_transaction', 0)
        
        summary.append(
            f"Total pendapatan Anda adalah Rp {total_revenue:,.0f} "
            f"dari {total_transactions} transaksi."
        )
        
        summary.append(
            f"Rata-rata nilai per transaksi adalah Rp {avg_transaction:,.0f}."
        )
        
        # Product diversity
        unique_products = metrics.get('unique_products', 0)
        if unique_products > 0:
            summary.append(
                f"Anda memiliki {unique_products} produk berbeda yang terjual."
            )
        
        # Date range
        date_range = metrics.get('date_range', {})
        if date_range.get('start') and date_range.get('end'):
            summary.append(
                f"Data transaksi mencakup periode {date_range['start'].strftime('%d %B %Y')} "
                f"hingga {date_range['end'].strftime('%d %B %Y')}."
            )
        
        return summary
    
    @staticmethod
    def generate_recommendations(all_insights: Dict[str, Dict]) -> List[str]:
        """
        Generate actionable recommendations based on all insights
        
        Args:
            all_insights: Dictionary of all insights from various analyses
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        # Check trend
        if 'trend' in all_insights:
            trend = all_insights['trend']
            if trend['type'] == 'danger':
                recommendations.append(
                    "PRIORITAS TINGGI: Segera evaluasi strategi penjualan karena tren menurun."
                )
        
        # Check slow products
        if 'slow_products' in all_insights:
            slow = all_insights['slow_products']
            if slow['type'] == 'warning':
                recommendations.append(
                    "Buat program clearance sale untuk produk yang tidak laku."
                )
        
        # Check pareto
        if 'pareto' in all_insights:
            pareto = all_insights['pareto']
            if pareto['type'] == 'warning':
                recommendations.append(
                    "Kurangi variasi produk dan fokus pada produk yang benar-benar menguntungkan."
                )
        
        # General recommendations
        recommendations.extend([
            "Pantau data penjualan secara rutin minimal seminggu sekali.",
            "Pastikan produk terlaris selalu tersedia stoknya.",
            "Gunakan data ini untuk negosiasi dengan supplier."
        ])
        
        return recommendations[:5]  # Return top 5 recommendations
