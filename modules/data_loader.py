"""
Data Loader Module
Handles file upload, reading, and intelligent column mapping
"""

import pandas as pd
import io
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """
    Smart data loader that automatically detects and maps columns
    from user-uploaded files to standardized internal schema
    """
    
    # Column mapping dictionary - maps common variations to standard names
    COLUMN_MAPPINGS = {
        'date': [
            'tgl', 'tanggal', 'date', 'waktu', 'time', 'datetime',
            'tgl_transaksi', 'tanggal_transaksi', 'transaction_date',
            'tgl_jual', 'tgl_beli', 'created_at', 'order_date'
        ],
        'product': [
            'nama', 'produk', 'item', 'menu', 'barang', 'product',
            'nama_produk', 'nama_barang', 'product_name', 'item_name',
            'sku', 'deskripsi', 'description'
        ],
        'price': [
            'harga', 'price', 'total', 'bayar', 'nilai', 'rp', 'amount',
            'hrg_jual', 'harga_jual', 'selling_price', 'sale_price',
            'nominal', 'jumlah_bayar', 'total_harga', 'subtotal'
        ],
        'qty': [
            'jumlah', 'qty', 'quantity', 'pcs', 'unit', 'banyak',
            'jml', 'kuantitas', 'volume', 'pieces'
        ],
        'category': [
            'kategori', 'category', 'jenis', 'type', 'group',
            'klasifikasi', 'golongan'
        ],
        'customer': [
            'pelanggan', 'customer', 'pembeli', 'buyer', 'nama_pelanggan',
            'customer_name', 'client'
        ]
    }
    
    @staticmethod
    def read_file(file_obj, file_extension: str) -> pd.DataFrame:
        """
        Read uploaded file and convert to DataFrame
        
        Args:
            file_obj: File object from Streamlit uploader
            file_extension: File extension (.csv, .xlsx, etc)
            
        Returns:
            pd.DataFrame: Raw dataframe from file
        """
        try:
            if file_extension == '.csv':
                # Try different encodings
                try:
                    df = pd.read_csv(file_obj, encoding='utf-8')
                except UnicodeDecodeError:
                    file_obj.seek(0)
                    df = pd.read_csv(file_obj, encoding='latin-1')
                    
            elif file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(file_obj, engine='openpyxl')
                
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            logger.info(f"Successfully loaded file with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            raise
    
    @staticmethod
    def detect_column_mapping(df: pd.DataFrame) -> Dict[str, str]:
        """
        Automatically detect which columns map to standard schema
        
        Args:
            df: Input dataframe with original column names
            
        Returns:
            Dict mapping standard names to actual column names
        """
        mapping = {}
        df_columns_lower = [col.lower().strip() for col in df.columns]
        
        for standard_name, variations in DataLoader.COLUMN_MAPPINGS.items():
            for col_idx, col_lower in enumerate(df_columns_lower):
                # Check if any variation matches
                for variation in variations:
                    if variation in col_lower or col_lower in variation:
                        actual_column = df.columns[col_idx]
                        mapping[standard_name] = actual_column
                        break
                if standard_name in mapping:
                    break
        
        logger.info(f"Detected column mapping: {mapping}")
        return mapping
    
    @staticmethod
    def apply_column_mapping(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Rename columns based on detected mapping
        
        Args:
            df: Original dataframe
            mapping: Dictionary of standard_name -> actual_column
            
        Returns:
            DataFrame with renamed columns
        """
        # Create reverse mapping for renaming
        rename_dict = {actual_col: standard_name 
                      for standard_name, actual_col in mapping.items()}
        
        df_renamed = df.rename(columns=rename_dict)
        
        logger.info(f"Applied column mapping. New columns: {list(df_renamed.columns)}")
        return df_renamed
    
    @staticmethod
    def validate_data(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that dataframe has required columns
        
        Args:
            df: Dataframe to validate
            required_columns: List of required column names
            
        Returns:
            Tuple of (is_valid, missing_columns)
        """
        missing = [col for col in required_columns if col not in df.columns]
        is_valid = len(missing) == 0
        
        if not is_valid:
            logger.warning(f"Missing required columns: {missing}")
        
        return is_valid, missing
    
    @staticmethod
    def get_data_summary(df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics about the dataset
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary with summary information
        """
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'column_names': list(df.columns),
            'date_range': None,  # Will be populated after cleaning
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
            'null_counts': df.isnull().sum().to_dict()
        }
    
    @classmethod
    def load_and_map(cls, file_obj, file_extension: str) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        Convenience method to load file and auto-detect mapping
        
        Args:
            file_obj: File object from uploader
            file_extension: File extension
            
        Returns:
            Tuple of (raw_dataframe, detected_mapping)
        """
        df = cls.read_file(file_obj, file_extension)
        mapping = cls.detect_column_mapping(df)
        
        return df, mapping
