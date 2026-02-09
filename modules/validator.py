"""
Validator Module
Performs data quality checks and validation
"""

import pandas as pd
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates data quality and completeness
    """
    
    # Minimum data requirements
    MIN_ROWS = 5
    MIN_DATE_RANGE_DAYS = 1
    
    @staticmethod
    def validate_file_format(filename: str) -> Tuple[bool, str]:
        """
        Check if file format is supported
        
        Args:
            filename: Name of uploaded file
            
        Returns:
            Tuple of (is_valid, message)
        """
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        
        file_ext = None
        for ext in allowed_extensions:
            if filename.lower().endswith(ext):
                file_ext = ext
                break
        
        if file_ext:
            return True, f"File format {file_ext} is supported"
        else:
            return False, f"File format not supported. Please upload {', '.join(allowed_extensions)}"
    
    @staticmethod
    def validate_minimum_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Check if dataframe meets minimum requirements
        
        Args:
            df: Input dataframe
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check minimum rows
        if len(df) < DataValidator.MIN_ROWS:
            issues.append(
                f"Data terlalu sedikit. Minimal {DataValidator.MIN_ROWS} baris transaksi diperlukan, "
                f"Anda memiliki {len(df)} baris."
            )
        
        # Check if completely empty
        if df.empty:
            issues.append("File tidak berisi data apapun.")
        
        # Check if all columns are empty
        if not df.empty and df.isnull().all().all():
            issues.append("Semua kolom kosong. Pastikan file berisi data yang valid.")
        
        is_valid = len(issues) == 0
        
        if not is_valid:
            logger.warning(f"Validation failed: {'; '.join(issues)}")
        
        return is_valid, issues
    
    @staticmethod
    def validate_required_columns(
        df: pd.DataFrame, 
        required_columns: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Check if all required columns are present
        
        Args:
            df: Input dataframe
            required_columns: List of required column names
            
        Returns:
            Tuple of (is_valid, list of missing columns)
        """
        missing_columns = [col for col in required_columns if col not in df.columns]
        is_valid = len(missing_columns) == 0
        
        if not is_valid:
            logger.warning(f"Missing required columns: {missing_columns}")
        
        return is_valid, missing_columns
    
    @staticmethod
    def validate_date_range(df: pd.DataFrame, date_col: str) -> Tuple[bool, str]:
        """
        Validate date column has reasonable range
        
        Args:
            df: Input dataframe
            date_col: Name of date column
            
        Returns:
            Tuple of (is_valid, message)
        """
        if date_col not in df.columns:
            return False, f"Kolom tanggal '{date_col}' tidak ditemukan."
        
        # Check for null dates
        null_count = df[date_col].isnull().sum()
        if null_count > 0:
            return False, f"Ada {null_count} baris dengan tanggal kosong."
        
        # Check date range
        try:
            date_range = (df[date_col].max() - df[date_col].min()).days
            
            if date_range < 0:
                return False, "Rentang tanggal tidak valid (ada tanggal masa depan)."
            
            if date_range < DataValidator.MIN_DATE_RANGE_DAYS:
                return False, f"Rentang tanggal terlalu pendek ({date_range} hari). Minimal {DataValidator.MIN_DATE_RANGE_DAYS} hari."
            
            return True, f"Rentang tanggal valid: {date_range} hari"
            
        except Exception as e:
            return False, f"Error validating dates: {str(e)}"
    
    @staticmethod
    def validate_numeric_columns(
        df: pd.DataFrame, 
        numeric_columns: List[str]
    ) -> Tuple[bool, Dict[str, str]]:
        """
        Validate that numeric columns contain valid numbers
        
        Args:
            df: Input dataframe
            numeric_columns: List of columns that should be numeric
            
        Returns:
            Tuple of (is_valid, dict of column issues)
        """
        issues = {}
        
        for col in numeric_columns:
            if col not in df.columns:
                issues[col] = "Kolom tidak ditemukan"
                continue
            
            # Check for negative values
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                issues[col] = f"Ada {negative_count} nilai negatif"
            
            # Check for zero or null values
            zero_or_null = ((df[col] == 0) | df[col].isnull()).sum()
            if zero_or_null == len(df):
                issues[col] = "Semua nilai adalah 0 atau kosong"
        
        is_valid = len(issues) == 0
        
        if not is_valid:
            logger.warning(f"Numeric validation issues: {issues}")
        
        return is_valid, issues
    
    @staticmethod
    def validate_product_names(df: pd.DataFrame, product_col: str) -> Tuple[bool, str]:
        """
        Validate product names are not empty
        
        Args:
            df: Input dataframe
            product_col: Name of product column
            
        Returns:
            Tuple of (is_valid, message)
        """
        if product_col not in df.columns:
            return False, f"Kolom produk '{product_col}' tidak ditemukan."
        
        # Check for empty or null product names
        empty_count = (
            df[product_col].isnull() | 
            (df[product_col].astype(str).str.strip() == '')
        ).sum()
        
        if empty_count > 0:
            return False, f"Ada {empty_count} baris dengan nama produk kosong."
        
        return True, "Nama produk valid"
    
    @staticmethod
    def get_data_quality_score(df: pd.DataFrame) -> Dict[str, any]:
        """
        Calculate overall data quality score
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary with quality metrics
        """
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        duplicate_rows = df.duplicated().sum()
        
        completeness = ((total_cells - null_cells) / total_cells * 100) if total_cells > 0 else 0
        uniqueness = ((len(df) - duplicate_rows) / len(df) * 100) if len(df) > 0 else 0
        
        # Overall quality score (weighted average)
        quality_score = (completeness * 0.6 + uniqueness * 0.4)
        
        return {
            'quality_score': quality_score,
            'completeness': completeness,
            'uniqueness': uniqueness,
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'null_cells': int(null_cells),
            'duplicate_rows': int(duplicate_rows),
            'quality_level': DataValidator._get_quality_level(quality_score)
        }
    
    @staticmethod
    def _get_quality_level(score: float) -> str:
        """
        Get quality level label based on score
        
        Args:
            score: Quality score (0-100)
            
        Returns:
            Quality level string
        """
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 60:
            return 'Fair'
        else:
            return 'Poor'
    
    @staticmethod
    def validate_all(
        df: pd.DataFrame,
        required_columns: List[str] = None,
        numeric_columns: List[str] = None,
        date_col: str = None,
        product_col: str = None
    ) -> Dict[str, any]:
        """
        Run all validations and return comprehensive report
        
        Args:
            df: Input dataframe
            required_columns: List of required columns
            numeric_columns: List of numeric columns to validate
            date_col: Name of date column
            product_col: Name of product column
            
        Returns:
            Dictionary with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'quality_score': None
        }
        
        # Minimum data validation
        min_valid, min_issues = DataValidator.validate_minimum_data(df)
        if not min_valid:
            results['is_valid'] = False
            results['errors'].extend(min_issues)
        
        # Required columns validation
        if required_columns:
            req_valid, missing_cols = DataValidator.validate_required_columns(df, required_columns)
            if not req_valid:
                results['is_valid'] = False
                results['errors'].append(f"Kolom wajib tidak ditemukan: {', '.join(missing_cols)}")
        
        # Numeric columns validation
        if numeric_columns:
            num_valid, num_issues = DataValidator.validate_numeric_columns(df, numeric_columns)
            if not num_valid:
                for col, issue in num_issues.items():
                    results['warnings'].append(f"{col}: {issue}")
        
        # Date validation
        if date_col:
            date_valid, date_msg = DataValidator.validate_date_range(df, date_col)
            if not date_valid:
                results['warnings'].append(date_msg)
        
        # Product validation
        if product_col:
            prod_valid, prod_msg = DataValidator.validate_product_names(df, product_col)
            if not prod_valid:
                results['warnings'].append(prod_msg)
        
        # Quality score
        results['quality_score'] = DataValidator.get_data_quality_score(df)
        
        logger.info(f"Validation complete. Valid: {results['is_valid']}, Quality: {results['quality_score']['quality_level']}")
        
        return results
