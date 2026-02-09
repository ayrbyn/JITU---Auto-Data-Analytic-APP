"""
Analyzer Module
Calculates business metrics and performs data analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessAnalyzer:
    """
    Analyzes transaction data and calculates key business metrics
    """
    
    @staticmethod
    def get_total_revenue(df: pd.DataFrame, price_col: str = 'price') -> float:
        """
        Calculate total revenue
        
        Args:
            df: Transaction dataframe
            price_col: Name of price column
            
        Returns:
            Total revenue
        """
        if price_col not in df.columns:
            logger.warning(f"Price column '{price_col}' not found")
            return 0.0
        
        total = df[price_col].sum()
        logger.info(f"Total revenue calculated: {total:,.2f}")
        return float(total)
    
    @staticmethod
    def get_total_transactions(df: pd.DataFrame) -> int:
        """
        Get total number of transactions
        
        Args:
            df: Transaction dataframe
            
        Returns:
            Number of transactions
        """
        return len(df)
    
    @staticmethod
    def get_average_transaction_value(df: pd.DataFrame, price_col: str = 'price') -> float:
        """
        Calculate average transaction value
        
        Args:
            df: Transaction dataframe
            price_col: Name of price column
            
        Returns:
            Average transaction value
        """
        if price_col not in df.columns or len(df) == 0:
            return 0.0
        
        return float(df[price_col].mean())
    
    @staticmethod
    def get_best_selling_products(
        df: pd.DataFrame, 
        product_col: str = 'product',
        qty_col: str = 'qty',
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Get top selling products by quantity
        
        Args:
            df: Transaction dataframe
            product_col: Name of product column
            qty_col: Name of quantity column
            top_n: Number of top products to return
            
        Returns:
            DataFrame with top products and their quantities
        """
        if product_col not in df.columns:
            logger.warning(f"Product column '{product_col}' not found")
            return pd.DataFrame()
        
        # If qty column doesn't exist, count transactions
        if qty_col not in df.columns:
            product_sales = df.groupby(product_col).size().reset_index(name='total_qty')
        else:
            product_sales = (
                df.groupby(product_col)[qty_col]
                .sum()
                .reset_index(name='total_qty')
            )
        
        # Sort and get top N
        top_products = (
            product_sales
            .sort_values('total_qty', ascending=False)
            .head(top_n)
        )
        
        logger.info(f"Calculated top {len(top_products)} selling products")
        return top_products
    
    @staticmethod
    def get_revenue_by_product(
        df: pd.DataFrame,
        product_col: str = 'product',
        price_col: str = 'price',
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Get top products by revenue
        
        Args:
            df: Transaction dataframe
            product_col: Name of product column
            price_col: Name of price column
            top_n: Number of top products to return
            
        Returns:
            DataFrame with products and their revenue
        """
        if product_col not in df.columns or price_col not in df.columns:
            return pd.DataFrame()
        
        product_revenue = (
            df.groupby(product_col)[price_col]
            .sum()
            .reset_index(name='total_revenue')
            .sort_values('total_revenue', ascending=False)
            .head(top_n)
        )
        
        return product_revenue
    
    @staticmethod
    def get_sales_trend(
        df: pd.DataFrame,
        date_col: str = 'date',
        price_col: str = 'price',
        freq: str = 'D'
    ) -> pd.DataFrame:
        """
        Calculate sales trend over time
        
        Args:
            df: Transaction dataframe
            date_col: Name of date column
            price_col: Name of price column
            freq: Frequency for grouping ('D' for daily, 'W' for weekly, 'M' for monthly)
            
        Returns:
            DataFrame with date and revenue
        """
        if date_col not in df.columns or price_col not in df.columns:
            return pd.DataFrame()
        
        # Ensure date column is datetime
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        
        # Group by date and sum revenue
        trend = (
            df_copy.groupby(pd.Grouper(key=date_col, freq=freq))[price_col]
            .sum()
            .reset_index()
        )
        
        trend.columns = ['date', 'revenue']
        
        logger.info(f"Calculated sales trend with {len(trend)} periods")
        return trend
    
    @staticmethod
    def get_pareto_analysis(
        df: pd.DataFrame,
        product_col: str = 'product',
        price_col: str = 'price',
        threshold: float = 0.8
    ) -> Tuple[pd.DataFrame, float]:
        """
        Perform Pareto analysis (80/20 rule)
        Find products that contribute to X% of revenue
        
        Args:
            df: Transaction dataframe
            product_col: Name of product column
            price_col: Name of price column
            threshold: Revenue percentage threshold (default 0.8 for 80%)
            
        Returns:
            Tuple of (DataFrame with products, percentage of products)
        """
        if product_col not in df.columns or price_col not in df.columns:
            return pd.DataFrame(), 0.0
        
        # Calculate revenue by product
        product_revenue = (
            df.groupby(product_col)[price_col]
            .sum()
            .reset_index(name='revenue')
            .sort_values('revenue', ascending=False)
        )
        
        # Calculate cumulative percentage
        total_revenue = product_revenue['revenue'].sum()
        product_revenue['cumulative_revenue'] = product_revenue['revenue'].cumsum()
        product_revenue['cumulative_percentage'] = (
            product_revenue['cumulative_revenue'] / total_revenue
        )
        
        # Find products contributing to threshold percentage
        pareto_products = product_revenue[
            product_revenue['cumulative_percentage'] <= threshold
        ]
        
        percentage_of_products = len(pareto_products) / len(product_revenue) * 100
        
        logger.info(
            f"Pareto analysis: {len(pareto_products)} products "
            f"({percentage_of_products:.1f}%) contribute to "
            f"{threshold*100}% of revenue"
        )
        
        return pareto_products, percentage_of_products
    
    @staticmethod
    def get_trend_direction(
        df: pd.DataFrame,
        date_col: str = 'date',
        price_col: str = 'price',
        window: int = 3
    ) -> Dict[str, any]:
        """
        Analyze if sales trend is going up or down
        
        Args:
            df: Transaction dataframe
            date_col: Name of date column
            price_col: Name of price column
            window: Number of recent days to compare
            
        Returns:
            Dictionary with trend analysis
        """
        trend_data = BusinessAnalyzer.get_sales_trend(df, date_col, price_col, freq='D')
        
        if len(trend_data) < window * 2:
            return {
                'direction': 'insufficient_data',
                'change_percentage': 0.0,
                'recent_avg': 0.0,
                'previous_avg': 0.0
            }
        
        # Compare last N days with previous N days
        recent_data = trend_data.tail(window)
        previous_data = trend_data.tail(window * 2).head(window)
        
        recent_avg = recent_data['revenue'].mean()
        previous_avg = previous_data['revenue'].mean()
        
        if previous_avg == 0:
            change_percentage = 0.0
        else:
            change_percentage = ((recent_avg - previous_avg) / previous_avg) * 100
        
        if change_percentage > 5:
            direction = 'up'
        elif change_percentage < -5:
            direction = 'down'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'change_percentage': change_percentage,
            'recent_avg': recent_avg,
            'previous_avg': previous_avg
        }
    
    @staticmethod
    def get_day_of_week_analysis(
        df: pd.DataFrame,
        date_col: str = 'date',
        price_col: str = 'price'
    ) -> pd.DataFrame:
        """
        Analyze sales by day of week
        
        Args:
            df: Transaction dataframe
            date_col: Name of date column
            price_col: Name of price column
            
        Returns:
            DataFrame with day of week and average revenue
        """
        if date_col not in df.columns or price_col not in df.columns:
            return pd.DataFrame()
        
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        df_copy['day_of_week'] = df_copy[date_col].dt.day_name()
        
        day_analysis = (
            df_copy.groupby('day_of_week')[price_col]
            .agg(['mean', 'sum', 'count'])
            .reset_index()
        )
        
        # Order by day of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_analysis['day_of_week'] = pd.Categorical(
            day_analysis['day_of_week'], 
            categories=day_order, 
            ordered=True
        )
        day_analysis = day_analysis.sort_values('day_of_week')
        
        return day_analysis
    
    @staticmethod
    def get_slow_moving_products(
        df: pd.DataFrame,
        product_col: str = 'product',
        date_col: str = 'date',
        days_threshold: int = 14
    ) -> pd.DataFrame:
        """
        Identify products that haven't sold recently
        
        Args:
            df: Transaction dataframe
            product_col: Name of product column
            date_col: Name of date column
            days_threshold: Number of days without sales to be considered slow
            
        Returns:
            DataFrame with slow moving products
        """
        if product_col not in df.columns or date_col not in df.columns:
            return pd.DataFrame()
        
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        
        # Get last sale date for each product
        last_sale = (
            df_copy.groupby(product_col)[date_col]
            .max()
            .reset_index()
        )
        last_sale.columns = [product_col, 'last_sale_date']
        
        # Calculate days since last sale
        latest_date = df_copy[date_col].max()
        last_sale['days_since_last_sale'] = (
            latest_date - last_sale['last_sale_date']
        ).dt.days
        
        # Filter slow moving products
        slow_products = last_sale[
            last_sale['days_since_last_sale'] >= days_threshold
        ].sort_values('days_since_last_sale', ascending=False)
        
        return slow_products
    
    @staticmethod
    def get_summary_metrics(df: pd.DataFrame) -> Dict[str, any]:
        """
        Calculate all key metrics in one call
        
        Args:
            df: Transaction dataframe
            
        Returns:
            Dictionary with all metrics
        """
        metrics = {
            'total_revenue': BusinessAnalyzer.get_total_revenue(df),
            'total_transactions': BusinessAnalyzer.get_total_transactions(df),
            'average_transaction': BusinessAnalyzer.get_average_transaction_value(df),
            'unique_products': df['product'].nunique() if 'product' in df.columns else 0,
            'date_range': {
                'start': df['date'].min() if 'date' in df.columns else None,
                'end': df['date'].max() if 'date' in df.columns else None,
            }
        }
        
        return metrics
