# JITU - Jaringan Informasi Transaksi UMKM

**Data to Duit** - Transform your raw transaction data into actionable business insights.

## Overview

JITU is a smart analytics application designed specifically for Indonesian SMEs (UMKM) to understand their business performance through data. Upload your transaction records and get instant insights about sales trends, top products, and actionable recommendations.

## Features

- **Smart Column Detection**: Automatically identifies columns in your data files
- **Indonesian Currency Support**: Handles various Rupiah formats (Rp 15.000, 15k, 15ribu, etc.)
- **Flexible Date Parsing**: Supports multiple Indonesian date formats
- **Business Metrics**:
  - Total revenue and transaction count
  - Average transaction value
  - Top selling products by quantity and revenue
  - Sales trends over time
  - Pareto analysis (80/20 rule)
  - Day-of-week patterns
  - Slow-moving product detection
- **Actionable Insights**: Converts metrics into plain Indonesian language recommendations
- **Data Validation**: Ensures your data quality before analysis

## Quick Start

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd jitu_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser to `http://localhost:8501`

### Using Sample Data

Try the application with sample data:
```bash
streamlit run app.py
```
Then upload `data_samples/warung_kopi.csv`

## Data Format Requirements

### Required Columns

Your data file must contain:
- **Date**: Transaction date (any format)
- **Product**: Product/item name
- **Price**: Transaction value/price

### Optional Columns

- **Quantity**: Number of items sold
- **Category**: Product category
- **Customer**: Customer name

### Supported File Formats

- CSV (.csv)
- Excel (.xlsx, .xls)

### Example Data Format

```csv
tgl_transaksi,nama_produk,hrg_jual,jumlah
2024-01-15,Kopi Hitam,Rp 8.000,3
2024-01-15,Kopi Susu,Rp 12.000,5
2024-01-16,Kopi Hitam,Rp 8.000,4
```

## Project Structure

```
jitu_app/
├── .streamlit/
│   └── config.toml              # UI theme configuration
├── assets/
│   └── logo_jitu.png            # Application logo
├── data_samples/
│   └── warung_kopi.csv          # Sample transaction data
├── modules/
│   ├── __init__.py              # Package initialization
│   ├── data_loader.py           # File reading and column detection
│   ├── cleaner.py               # Data cleaning and normalization
│   ├── analyzer.py              # Business metrics calculation
│   ├── narrator.py              # Insight generation
│   └── validator.py             # Data quality validation
├── tests/
│   └── test_modules.py          # Unit tests
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Module Documentation

### data_loader.py

Handles file upload and intelligent column mapping.

**Key Functions:**
- `read_file()`: Reads CSV/Excel files
- `detect_column_mapping()`: Auto-detects standard column names
- `apply_column_mapping()`: Renames columns to standard schema

### cleaner.py

Cleans and normalizes data.

**Key Functions:**
- `clean_currency()`: Converts Indonesian currency to float
- `clean_date()`: Parses various date formats
- `clean_dataframe()`: Applies cleaning to entire dataframe

**Supported Currency Formats:**
- Rp 15.000,00
- IDR 15000
- 15k / 15rb / 15ribu
- 15.000,-

### analyzer.py

Calculates business metrics.

**Key Functions:**
- `get_total_revenue()`: Calculate total sales
- `get_best_selling_products()`: Find top products
- `get_sales_trend()`: Analyze trends over time
- `get_pareto_analysis()`: Apply 80/20 rule
- `get_day_of_week_analysis()`: Find best/worst days
- `get_slow_moving_products()`: Identify stagnant inventory

### narrator.py

Converts metrics into human-readable insights.

**Key Functions:**
- `narrate_trend()`: Explain sales trend direction
- `narrate_top_product()`: Describe best sellers
- `narrate_pareto()`: Explain product concentration
- `generate_recommendations()`: Create action items

### validator.py

Ensures data quality.

**Key Functions:**
- `validate_file_format()`: Check file type
- `validate_minimum_data()`: Ensure sufficient data
- `validate_required_columns()`: Check for mandatory columns
- `get_data_quality_score()`: Calculate quality metrics

## Configuration

### Theme Customization

Edit `.streamlit/config.toml` to change colors:

```toml
[theme]
primaryColor = "#FF6B35"        # Orange (JITU brand color)
backgroundColor = "#FFFFFF"      # White background
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

### Deploy to Other Platforms

The app can be deployed to:
- Heroku
- AWS
- Google Cloud
- Azure

Ensure Python 3.11+ is available on the platform.

## Testing

Run unit tests:
```bash
python -m pytest tests/
```

## Troubleshooting

### File Upload Issues

**Problem**: "File format not supported"
**Solution**: Ensure file is .csv, .xlsx, or .xls

**Problem**: "Data terlalu sedikit"
**Solution**: Upload at least 5 transaction records

### Data Parsing Issues

**Problem**: Currency not parsed correctly
**Solution**: Ensure format is Rp X.XXX or similar Indonesian format

**Problem**: Dates not recognized
**Solution**: Use DD-MM-YYYY or similar format

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Contact: support@jitu.app

## Roadmap

### Version 1.1 (Planned)
- Export reports to PDF
- More advanced forecasting
- Multi-location support
- Inventory management integration

### Version 1.2 (Planned)
- Mobile app (iOS/Android)
- WhatsApp integration for reports
- Comparison with industry benchmarks

## Credits

Developed by JITU Development Team

**Technologies Used:**
- Streamlit (UI Framework)
- Pandas (Data Processing)
- Python 3.11+ (Core Language)

---

**JITU** - Turning Your Data Into Profit
