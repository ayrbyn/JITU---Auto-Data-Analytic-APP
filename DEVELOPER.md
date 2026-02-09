# Developer Guide

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- Code editor (VS Code recommended)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/jitu-app.git
cd jitu-app

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8
```

### Running Development Server

```bash
# Method 1: Using run script
./run.sh

# Method 2: Direct streamlit command
streamlit run app.py

# Method 3: With specific port
streamlit run app.py --server.port 8502
```

## Project Architecture

### Data Flow

```
User Upload
    |
    v
DataLoader (read file, detect columns)
    |
    v
DataValidator (validate quality)
    |
    v
DataCleaner (clean currency, dates)
    |
    v
BusinessAnalyzer (calculate metrics)
    |
    v
InsightNarrator (generate insights)
    |
    v
Streamlit UI (display to user)
```

### Module Responsibilities

#### data_loader.py
- **Purpose**: File I/O and column mapping
- **Key Classes**: `DataLoader`
- **Dependencies**: pandas, logging
- **Output**: Raw DataFrame + column mapping

#### cleaner.py
- **Purpose**: Data sanitization
- **Key Classes**: `DataCleaner`
- **Key Methods**:
  - `clean_currency()`: Handle Rupiah formats
  - `clean_date()`: Parse date formats
  - `clean_dataframe()`: Batch cleaning

#### analyzer.py
- **Purpose**: Business metric calculation
- **Key Classes**: `BusinessAnalyzer`
- **Key Methods**:
  - `get_total_revenue()`: Sum revenue
  - `get_best_selling_products()`: Top products
  - `get_sales_trend()`: Time series analysis
  - `get_pareto_analysis()`: 80/20 rule
  - `get_trend_direction()`: Trend detection

#### narrator.py
- **Purpose**: Convert metrics to insights
- **Key Classes**: `InsightNarrator`
- **Output**: Structured insight dictionaries

#### validator.py
- **Purpose**: Data quality assurance
- **Key Classes**: `DataValidator`
- **Output**: Validation reports

## Adding New Features

### Example: Adding Customer Segmentation

#### 1. Create Analyzer Function

Add to `modules/analyzer.py`:

```python
@staticmethod
def get_customer_segments(
    df: pd.DataFrame,
    customer_col: str = 'customer',
    price_col: str = 'price'
) -> pd.DataFrame:
    """
    Segment customers by purchase behavior
    
    Args:
        df: Transaction dataframe
        customer_col: Customer column name
        price_col: Price column name
    
    Returns:
        DataFrame with customer segments
    """
    customer_stats = (
        df.groupby(customer_col)[price_col]
        .agg(['sum', 'count', 'mean'])
        .reset_index()
    )
    
    customer_stats.columns = ['customer', 'total_spent', 'frequency', 'avg_order']
    
    # Define segments
    high_value = customer_stats['total_spent'].quantile(0.75)
    
    def categorize(row):
        if row['total_spent'] >= high_value:
            return 'VIP'
        elif row['frequency'] >= 10:
            return 'Loyal'
        else:
            return 'Regular'
    
    customer_stats['segment'] = customer_stats.apply(categorize, axis=1)
    
    return customer_stats
```

#### 2. Add Narrator Function

Add to `modules/narrator.py`:

```python
@staticmethod
def narrate_customer_segments(segments: pd.DataFrame) -> Dict[str, str]:
    """
    Generate insight about customer segments
    
    Args:
        segments: DataFrame from get_customer_segments()
    
    Returns:
        Dictionary with insight
    """
    vip_count = len(segments[segments['segment'] == 'VIP'])
    total_customers = len(segments)
    vip_percentage = (vip_count / total_customers * 100) if total_customers > 0 else 0
    
    return {
        'type': 'info',
        'title': 'Segmentasi Pelanggan',
        'message': f'Anda memiliki {vip_count} pelanggan VIP ({vip_percentage:.1f}%) '
                   f'yang berkontribusi signifikan terhadap pendapatan.'
    }
```

#### 3. Add to UI

Update `app.py`:

```python
# In display_dashboard() function

st.markdown("---")
st.markdown("### Segmentasi Pelanggan")

if 'customer' in df_clean.columns:
    segments = BusinessAnalyzer.get_customer_segments(df_clean)
    
    # Display segments chart
    segment_counts = segments['segment'].value_counts()
    st.bar_chart(segment_counts)
    
    # Display insight
    segment_insight = InsightNarrator.narrate_customer_segments(segments)
    st.markdown(
        f'<div class="insight-{segment_insight["type"]}">'
        f'<strong>{segment_insight["title"]}</strong><br>'
        f'{segment_insight["message"]}'
        f'</div>',
        unsafe_allow_html=True
    )
else:
    st.info("Tambahkan kolom 'Customer' di data Anda untuk melihat segmentasi.")
```

#### 4. Add Tests

Add to `tests/test_modules.py`:

```python
def test_get_customer_segments(self):
    """Test customer segmentation"""
    df = pd.DataFrame({
        'customer': ['A', 'A', 'B', 'B', 'B', 'C'],
        'price': [100000, 150000, 50000, 60000, 70000, 30000]
    })
    
    segments = BusinessAnalyzer.get_customer_segments(df)
    
    assert not segments.empty
    assert 'segment' in segments.columns
    assert set(segments['segment'].unique()).issubset({'VIP', 'Loyal', 'Regular'})
```

## Code Style Guidelines

### Python Style

Follow PEP 8 with these specifics:

```python
# Good: Descriptive variable names
total_revenue = df['price'].sum()

# Bad: Cryptic names
tr = df['p'].sum()

# Good: Type hints
def calculate_total(df: pd.DataFrame, col: str) -> float:
    return df[col].sum()

# Good: Docstrings
def process_data(df):
    """
    Process transaction data
    
    Args:
        df: Input dataframe with transactions
    
    Returns:
        Processed dataframe
    """
    pass
```

### Import Order

```python
# 1. Standard library
import sys
from pathlib import Path
from typing import Dict, List

# 2. Third-party
import pandas as pd
import numpy as np
import streamlit as st

# 3. Local
from modules.data_loader import DataLoader
from modules.cleaner import DataCleaner
```

### Function Design

```python
# Good: Single responsibility
def clean_currency(value: str) -> float:
    """Clean single currency value"""
    pass

def clean_date(value: str) -> pd.Timestamp:
    """Clean single date value"""
    pass

# Bad: Multiple responsibilities
def clean_everything(value):
    """Clean currency, date, and product"""
    pass
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=modules tests/

# Run specific test file
pytest tests/test_modules.py

# Run specific test
pytest tests/test_modules.py::TestDataCleaner::test_clean_currency
```

### Writing Tests

```python
import pytest
from modules.cleaner import DataCleaner

class TestNewFeature:
    """Test suite for new feature"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for tests"""
        return pd.DataFrame({'col': [1, 2, 3]})
    
    def test_basic_case(self, sample_data):
        """Test basic functionality"""
        result = some_function(sample_data)
        assert result == expected_value
    
    def test_edge_case(self):
        """Test edge case"""
        result = some_function(None)
        assert result == default_value
    
    def test_error_handling(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            some_function(invalid_input)
```

## Debugging

### Streamlit Debugging

```python
# Use st.write() for quick debugging
st.write("Debug:", variable_name)

# Use st.json() for complex objects
st.json(data_dict)

# Use Python debugger
import pdb; pdb.set_trace()

# Use logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Variable value: {variable}")
```

### Common Issues

**Module import errors:**
```python
# Add to top of app.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
```

**Session state issues:**
```python
# Initialize in main()
if 'key' not in st.session_state:
    st.session_state.key = default_value
```

## Performance Optimization

### Data Processing

```python
# Use vectorized operations
# Good:
df['new_col'] = df['old_col'].apply(clean_currency)

# Better (if possible):
df['new_col'] = pd.to_numeric(df['old_col'].str.replace(',', ''))

# Cache expensive operations
@st.cache_data
def load_large_dataset():
    return pd.read_csv('large_file.csv')
```

### Streamlit Caching

```python
# Cache data processing
@st.cache_data
def process_data(df):
    # Expensive operations
    return processed_df

# Cache resource loading
@st.cache_resource
def load_model():
    # Load ML model
    return model
```

## Version Control

### Commit Messages

```bash
# Format: <type>: <description>

# Types:
# feat: New feature
# fix: Bug fix
# docs: Documentation
# style: Code style
# refactor: Code refactoring
# test: Tests
# chore: Maintenance

# Examples:
git commit -m "feat: add customer segmentation"
git commit -m "fix: currency parsing for edge cases"
git commit -m "docs: update API documentation"
```

### Branching Strategy

```bash
# Main branch: production-ready code
main

# Development branch
dev

# Feature branches
feature/customer-segmentation
feature/export-pdf

# Bug fix branches
fix/currency-parsing
fix/date-validation

# Workflow
git checkout -b feature/new-feature
# Make changes
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
# Create pull request to dev
```

## Documentation

### Code Documentation

```python
def complex_function(param1: str, param2: int) -> Dict:
    """
    Brief description of function
    
    Longer description explaining what the function does,
    why it exists, and any important considerations.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
    
    Returns:
        Dictionary containing:
        - key1: Description
        - key2: Description
    
    Raises:
        ValueError: When param2 is negative
    
    Example:
        >>> result = complex_function("test", 5)
        >>> print(result['key1'])
        'value'
    """
    pass
```

### README Updates

When adding features, update:
- Feature list
- Usage examples
- API documentation
- Troubleshooting section

## Release Process

### Version Numbering

Follow Semantic Versioning (semver):
- MAJOR.MINOR.PATCH
- Example: 1.2.3

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version number bumped
- [ ] Git tag created
- [ ] Deployed to staging
- [ ] User testing completed
- [ ] Deployed to production

## Contributing

### Pull Request Process

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Update documentation
6. Submit pull request
7. Address review comments

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Resources

### Documentation
- [Streamlit Docs](https://docs.streamlit.io)
- [Pandas Docs](https://pandas.pydata.org/docs)
- [Python Style Guide](https://pep8.org)

### Tools
- [Black](https://github.com/psf/black) - Code formatter
- [Flake8](https://flake8.pycqa.org) - Linter
- [Pytest](https://pytest.org) - Testing framework

### Community
- GitHub Issues
- Stack Overflow
- Python Discord
