"""
Data Cleaner Module
Handles data sanitization, currency parsing, and date normalization
"""

import pandas as pd
import numpy as np
import re
from typing import Union, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Data cleaning utilities for handling Indonesian currency formats,
    dates, and other common data quality issues
    """
    
    # Indonesian currency patterns
    CURRENCY_PATTERNS = [
        r'Rp\.?\s*',  # Rp, Rp., Rp followed by space
        r'IDR\.?\s*',  # IDR, IDR.
        r'[.,]00$',  # Trailing .00 or ,00
        r'\s+',  # Whitespace
    ]
    
    # Number word replacements
    NUMBER_WORDS = {
        'ribu': '000',
        'rb': '000',
        'k': '000',
        'juta': '000000',
        'jt': '000000',
        'million': '000000',
        'miliar': '000000000',
        'milyar': '000000000',
        'billion': '000000000',
    }
    
    @staticmethod
    def clean_currency(value: Union[str, int, float]) -> float:
        """
        Convert Indonesian currency format to clean float
        
        Handles formats like:
        - Rp 15.000,00
        - IDR 15000
        - 15k
        - 15 ribu
        - 15.000,-
        
        Args:
            value: Currency value in various formats
            
        Returns:
            Clean float value
        """
        if pd.isna(value):
            return 0.0
        
        # Already a number
        if isinstance(value, (int, float)):
            return float(value)
        
        # Convert to string and lowercase
        cleaned = str(value).lower().strip()
        
        # Remove currency symbols and prefixes
        for pattern in DataCleaner.CURRENCY_PATTERNS:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Handle number words (15k, 15ribu, etc)
        for word, replacement in DataCleaner.NUMBER_WORDS.items():
            if word in cleaned:
                # Extract the number before the word
                match = re.search(r'([\d,.]+)\s*' + word, cleaned)
                if match:
                    base_number = match.group(1)
                    # Clean the base number
                    base_number = base_number.replace('.', '').replace(',', '.')
                    try:
                        result = float(base_number) * (10 ** (len(replacement) / 3))
                        return result
                    except ValueError:
                        pass
        
        # Handle standard number format
        # Indonesian uses . for thousands and , for decimals
        # Remove thousand separators (.)
        cleaned = cleaned.replace('.', '')
        
        # Replace decimal comma with period
        cleaned = cleaned.replace(',', '.')
        
        # Remove any remaining non-numeric characters except period
        cleaned = re.sub(r'[^\d.]', '', cleaned)
        
        # Convert to float
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            logger.warning(f"Could not parse currency value: {value}")
            return 0.0
    
    @staticmethod
    def clean_date(value: Union[str, pd.Timestamp]) -> pd.Timestamp:
        """
        Parse and normalize date values
        
        Handles formats like:
        - 17-08-2024
        - 2024/08/17
        - 17 Agustus 2024
        - 17 Aug 24
        
        Args:
            value: Date value in various formats
            
        Returns:
            Normalized pandas Timestamp
        """
        if pd.isna(value):
            return pd.NaT
        
        if isinstance(value, pd.Timestamp):
            return value
        
        try:
            # Use pandas parser with dayfirst=True for Indonesian format
            return pd.to_datetime(value, dayfirst=True)
        except Exception as e:
            logger.warning(f"Could not parse date value: {value}")
            return pd.NaT
    
    @staticmethod
    def clean_numeric(value: Union[str, int, float]) -> float:
        """
        Convert string numbers to clean float
        
        Args:
            value: Numeric value in string or numeric format
            
        Returns:
            Clean float value
        """
        if pd.isna(value):
            return 0.0
        
        if isinstance(value, (int, float)):
            return float(value)
        
        # Remove whitespace and common separators
        cleaned = str(value).strip().replace(',', '').replace('.', '')
        
        try:
            return float(cleaned)
        except ValueError:
            logger.warning(f"Could not parse numeric value: {value}")
            return 0.0
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """
        Remove duplicate rows from dataframe
        
        Args:
            df: Input dataframe
            subset: Columns to consider for duplicates
            
        Returns:
            Dataframe with duplicates removed
        """
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep='first')
        removed_count = initial_count - len(df_clean)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate rows")
        
        return df_clean
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
        """
        Handle missing values in dataframe
        
        Args:
            df: Input dataframe
            strategy: How to handle missing values ('drop', 'fill_zero', 'fill_mean')
            
        Returns:
            Dataframe with missing values handled
        """
        if strategy == 'drop':
            df_clean = df.dropna()
        elif strategy == 'fill_zero':
            df_clean = df.fillna(0)
        elif strategy == 'fill_mean':
            df_clean = df.fillna(df.mean(numeric_only=True))
        else:
            df_clean = df.copy()
        
        logger.info(f"Applied missing value strategy: {strategy}")
        return df_clean
    
    @classmethod
    def clean_dataframe(cls, df: pd.DataFrame, column_types: dict) -> pd.DataFrame:
        """
        Apply appropriate cleaning to each column based on type
        
        Args:
            df: Input dataframe
            column_types: Dict mapping column names to types ('currency', 'date', 'numeric', 'text')
            
        Returns:
            Cleaned dataframe
        """
        df_clean = df.copy()
        
        for col, col_type in column_types.items():
            if col not in df_clean.columns:
                continue
            
            if col_type == 'currency':
                df_clean[col] = df_clean[col].apply(cls.clean_currency)
            elif col_type == 'date':
                df_clean[col] = df_clean[col].apply(cls.clean_date)
            elif col_type == 'numeric':
                df_clean[col] = df_clean[col].apply(cls.clean_numeric)
            # 'text' type requires no cleaning
        
        logger.info(f"Cleaned dataframe with {len(df_clean)} rows")
        return df_clean
    
    @staticmethod
    def standardize_product_names(df: pd.DataFrame, product_col: str) -> pd.DataFrame:
        """
        Standardize product names (trim, lowercase, remove extra spaces)
        
        Args:
            df: Input dataframe
            product_col: Name of product column
            
        Returns:
            Dataframe with standardized product names
        """
        if product_col not in df.columns:
            return df
        
        df_clean = df.copy()
        df_clean[product_col] = (
            df_clean[product_col]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r'\s+', ' ', regex=True)
        )
        
        logger.info(f"Standardized product names in column: {product_col}")
        return df_clean
    
    @staticmethod
    def validate_cleaned_data(df: pd.DataFrame) -> dict:
        """
        Validate cleaned data and return quality report
        
        Args:
            df: Cleaned dataframe
            
        Returns:
            Dictionary with validation results
        """
        report = {
            'total_rows': len(df),
            'null_count': df.isnull().sum().sum(),
            'duplicate_count': df.duplicated().sum(),
            'negative_values': {},
            'zero_values': {},
        }
        
        # Check for negative values in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            negative_count = (df[col] < 0).sum()
            zero_count = (df[col] == 0).sum()
            
            if negative_count > 0:
                report['negative_values'][col] = negative_count
            if zero_count > 0:
                report['zero_values'][col] = zero_count
        
        return report
