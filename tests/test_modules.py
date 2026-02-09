"""
Unit Tests for JITU Modules
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.data_loader import DataLoader
from modules.cleaner import DataCleaner
from modules.analyzer import BusinessAnalyzer
from modules.narrator import InsightNarrator
from modules.validator import DataValidator


class TestDataCleaner:
    """Test cases for DataCleaner module"""
    
    def test_clean_currency_standard(self):
        """Test standard Indonesian currency format"""
        assert DataCleaner.clean_currency("Rp 15.000,00") == 15000.0
        assert DataCleaner.clean_currency("Rp 15.000") == 15000.0
        assert DataCleaner.clean_currency("IDR 15000") == 15000.0
    
    def test_clean_currency_shorthand(self):
        """Test shorthand currency formats"""
        assert DataCleaner.clean_currency("15k") == 15000.0
        assert DataCleaner.clean_currency("15ribu") == 15000.0
        assert DataCleaner.clean_currency("15rb") == 15000.0
        assert DataCleaner.clean_currency("1juta") == 1000000.0
    
    def test_clean_currency_numeric(self):
        """Test numeric input"""
        assert DataCleaner.clean_currency(15000) == 15000.0
        assert DataCleaner.clean_currency(15000.50) == 15000.50
    
    def test_clean_currency_edge_cases(self):
        """Test edge cases"""
        assert DataCleaner.clean_currency(None) == 0.0
        assert DataCleaner.clean_currency("") == 0.0
        assert DataCleaner.clean_currency("invalid") == 0.0
    
    def test_clean_date(self):
        """Test date parsing"""
        result = DataCleaner.clean_date("17-08-2024")
        assert isinstance(result, pd.Timestamp)
        assert result.year == 2024
        assert result.month == 8
        assert result.day == 17
    
    def test_clean_numeric(self):
        """Test numeric cleaning"""
        assert DataCleaner.clean_numeric("15000") == 15000.0
        assert DataCleaner.clean_numeric("15,000") == 15000.0
        assert DataCleaner.clean_numeric(15000) == 15000.0


class TestDataLoader:
    """Test cases for DataLoader module"""
    
    def test_detect_column_mapping(self):
        """Test column detection"""
        df = pd.DataFrame({
            'Tgl Transaksi': ['2024-01-01'],
            'Nama Produk': ['Kopi'],
            'Harga Jual': [10000],
            'Jumlah': [2]
        })
        
        mapping = DataLoader.detect_column_mapping(df)
        
        assert 'date' in mapping
        assert 'product' in mapping
        assert 'price' in mapping
        assert 'qty' in mapping
    
    def test_apply_column_mapping(self):
        """Test column renaming"""
        df = pd.DataFrame({
            'Tgl Transaksi': ['2024-01-01'],
            'Nama Produk': ['Kopi'],
            'Harga Jual': [10000]
        })
        
        mapping = {
            'date': 'Tgl Transaksi',
            'product': 'Nama Produk',
            'price': 'Harga Jual'
        }
        
        df_renamed = DataLoader.apply_column_mapping(df, mapping)
        
        assert 'date' in df_renamed.columns
        assert 'product' in df_renamed.columns
        assert 'price' in df_renamed.columns
    
    def test_validate_data(self):
        """Test data validation"""
        df = pd.DataFrame({
            'date': ['2024-01-01'],
            'product': ['Kopi'],
            'price': [10000]
        })
        
        is_valid, missing = DataLoader.validate_data(df, ['date', 'product', 'price'])
        assert is_valid == True
        assert len(missing) == 0
        
        is_valid, missing = DataLoader.validate_data(df, ['date', 'product', 'price', 'qty'])
        assert is_valid == False
        assert 'qty' in missing


class TestBusinessAnalyzer:
    """Test cases for BusinessAnalyzer module"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample transaction data"""
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        df = pd.DataFrame({
            'date': dates,
            'product': ['Kopi', 'Teh', 'Kopi', 'Teh', 'Kopi', 
                       'Roti', 'Kopi', 'Teh', 'Kopi', 'Roti'],
            'price': [10000, 5000, 10000, 5000, 10000, 
                     8000, 10000, 5000, 10000, 8000],
            'qty': [1, 1, 2, 1, 1, 1, 3, 1, 1, 2]
        })
        return df
    
    def test_get_total_revenue(self, sample_data):
        """Test revenue calculation"""
        total = BusinessAnalyzer.get_total_revenue(sample_data)
        assert total == 81000.0
    
    def test_get_total_transactions(self, sample_data):
        """Test transaction count"""
        count = BusinessAnalyzer.get_total_transactions(sample_data)
        assert count == 10
    
    def test_get_average_transaction_value(self, sample_data):
        """Test average transaction calculation"""
        avg = BusinessAnalyzer.get_average_transaction_value(sample_data)
        assert avg == 8100.0
    
    def test_get_best_selling_products(self, sample_data):
        """Test top products calculation"""
        top_products = BusinessAnalyzer.get_best_selling_products(sample_data, top_n=3)
        
        assert len(top_products) == 3
        assert top_products.iloc[0]['product'] == 'Kopi'
    
    def test_get_sales_trend(self, sample_data):
        """Test trend calculation"""
        trend = BusinessAnalyzer.get_sales_trend(sample_data)
        
        assert not trend.empty
        assert 'date' in trend.columns
        assert 'revenue' in trend.columns
    
    def test_get_pareto_analysis(self, sample_data):
        """Test Pareto analysis"""
        pareto_products, percentage = BusinessAnalyzer.get_pareto_analysis(sample_data)
        
        assert not pareto_products.empty
        assert 0 <= percentage <= 100


class TestInsightNarrator:
    """Test cases for InsightNarrator module"""
    
    def test_narrate_trend_up(self):
        """Test upward trend narration"""
        trend_analysis = {
            'direction': 'up',
            'change_percentage': 15.5,
            'recent_avg': 100000,
            'previous_avg': 85000
        }
        
        insight = InsightNarrator.narrate_trend(trend_analysis)
        
        assert insight['type'] == 'success'
        assert 'naik' in insight['message'].lower()
    
    def test_narrate_trend_down(self):
        """Test downward trend narration"""
        trend_analysis = {
            'direction': 'down',
            'change_percentage': -10.0,
            'recent_avg': 80000,
            'previous_avg': 100000
        }
        
        insight = InsightNarrator.narrate_trend(trend_analysis)
        
        assert insight['type'] == 'danger'
        assert 'turun' in insight['message'].lower()
    
    def test_narrate_top_product(self):
        """Test top product narration"""
        top_products = pd.DataFrame({
            'product': ['Kopi Hitam', 'Teh Manis'],
            'total_qty': [100, 50]
        })
        
        insight = InsightNarrator.narrate_top_product(top_products, 'quantity')
        
        assert insight['type'] == 'success'
        assert 'Kopi Hitam' in insight['message']
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        insights = {
            'trend': {'type': 'danger'},
            'slow_products': {'type': 'warning'}
        }
        
        recommendations = InsightNarrator.generate_recommendations(insights)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0


class TestDataValidator:
    """Test cases for DataValidator module"""
    
    def test_validate_file_format(self):
        """Test file format validation"""
        is_valid, msg = DataValidator.validate_file_format("data.csv")
        assert is_valid == True
        
        is_valid, msg = DataValidator.validate_file_format("data.xlsx")
        assert is_valid == True
        
        is_valid, msg = DataValidator.validate_file_format("data.txt")
        assert is_valid == False
    
    def test_validate_minimum_data(self):
        """Test minimum data requirements"""
        # Valid data
        df_valid = pd.DataFrame({
            'col1': range(10),
            'col2': range(10)
        })
        is_valid, issues = DataValidator.validate_minimum_data(df_valid)
        assert is_valid == True
        
        # Insufficient data
        df_small = pd.DataFrame({
            'col1': [1, 2],
            'col2': [1, 2]
        })
        is_valid, issues = DataValidator.validate_minimum_data(df_small)
        assert is_valid == False
    
    def test_get_data_quality_score(self):
        """Test data quality scoring"""
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': [1, 2, np.nan, 4, 5],
            'col3': [1, 2, 3, 4, 5]
        })
        
        quality = DataValidator.get_data_quality_score(df)
        
        assert 'quality_score' in quality
        assert 0 <= quality['quality_score'] <= 100
        assert quality['null_cells'] == 1


class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_full_workflow(self):
        """Test complete data processing workflow"""
        # Create sample data
        df_raw = pd.DataFrame({
            'Tanggal': ['2024-01-01', '2024-01-02', '2024-01-03', 
                       '2024-01-04', '2024-01-05', '2024-01-06'],
            'Produk': ['Kopi', 'Teh', 'Kopi', 'Teh', 'Kopi', 'Roti'],
            'Harga': ['Rp 10.000', 'Rp 5.000', 'Rp 10.000', 
                     'Rp 5.000', 'Rp 10.000', 'Rp 8.000'],
            'Jumlah': [1, 2, 1, 1, 2, 1]
        })
        
        # Step 1: Detect mapping
        mapping = DataLoader.detect_column_mapping(df_raw)
        assert 'date' in mapping
        assert 'product' in mapping
        assert 'price' in mapping
        
        # Step 2: Apply mapping
        df_mapped = DataLoader.apply_column_mapping(df_raw, mapping)
        
        # Step 3: Clean data
        column_types = {
            'date': 'date',
            'price': 'currency',
            'qty': 'numeric',
            'product': 'text'
        }
        df_clean = DataCleaner.clean_dataframe(df_mapped, column_types)
        
        # Step 4: Analyze
        total_revenue = BusinessAnalyzer.get_total_revenue(df_clean)
        assert total_revenue > 0
        
        top_products = BusinessAnalyzer.get_best_selling_products(df_clean)
        assert not top_products.empty
        
        # Step 5: Generate insights
        trend_analysis = BusinessAnalyzer.get_trend_direction(df_clean)
        insight = InsightNarrator.narrate_trend(trend_analysis)
        assert 'message' in insight


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
