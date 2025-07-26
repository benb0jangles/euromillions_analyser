# EuroMillions Lottery Analyser

A comprehensive tkinter-based desktop application for analysing EuroMillions lottery data with advanced statistical tools and pattern recognition capabilities.

![app_img1](https://github.com/benb0jangles/euromillions_analyser/blob/main/img/Screenshot%202025-07-26%20at%2021.48.40.png)


![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Features

### 📊 **Statistical Analysis**
- **Frequency Analysis**: Most and least drawn numbers and lucky stars
- **Overdue Numbers**: Track numbers that haven't appeared recently
- **Pattern Recognition**: Identify hot/cold streaks and number combinations
- **Advanced Analytics**: Chi-square tests, coefficient of variation, autocorrelation analysis

### 🎯 **Smart Number Generation**
- **Multiple Strategies**: Balanced, hot numbers, overdue numbers, pattern-based
- **Hybrid Tickets**: Combination of different generation methods
- **Historical Performance**: See how generated numbers would have performed

### 💾 **Personal Number Management**
- **Save Number Sets**: Store your favorite combinations with custom names
- **Historical Analysis**: Check how your numbers performed in past draws
- **Bulk Analysis**: Analyse all saved number sets simultaneously

### 🔍 **Advanced Features**
- **Bias Detection**: Statistical analysis for lottery equipment anomalies
- **Winner Analysis**: Comprehensive analysis of historical winning combinations
- **Seasonal Effects**: Time-based pattern detection
- **Physical Equipment Analysis**: Ball wear and machine bias detection

### 🌐 **Data Management**
- **Live Data**: Downloads latest results from official EuroMillions API
- **Offline Mode**: Cached data for analysis without internet connection
- **CSV Export**: Save historical data in spreadsheet format
- **Data Validation**: Comprehensive error handling and data integrity checks

## Installation

### Prerequisites
- Python 3.6 or higher
- tkinter (usually included with Python)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/benb0jangles/euromillions_analyser.git
cd euromillions_analyser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python3 euromillions_analyser.py
```

## Usage

### Getting Started
1. **Download Data**: Click "Download Latest Data" to fetch the most recent EuroMillions results
2. **Explore Analysis**: Navigate through the different tabs to view various statistical analyses
3. **Generate Numbers**: Use the generator tab to create number combinations based on different strategies
4. **Save Your Numbers**: Store your favorite combinations and track their historical performance

### Main Tabs Overview

#### 📈 Most/Least Drawn
View frequency statistics for all numbers and lucky stars, including:
- Most frequently drawn numbers
- Least frequently drawn numbers
- Hot and cold streak analysis

#### ⏰ Overdue Numbers
Track numbers that haven't appeared recently:
- Days since last appearance
- Overdue analysis for main numbers and lucky stars
- Historical average return periods

#### 🔮 Number Generator
Generate smart number combinations using various strategies:
- **Balanced**: Even distribution across number ranges
- **Hot Numbers**: Focus on frequently drawn numbers
- **Overdue**: Target numbers that haven't appeared recently
- **Pattern-based**: Use historical patterns
- **Hybrid**: Combination of multiple strategies

#### 📚 Saved Numbers
Manage your personal number combinations:
- Save sets with custom names
- Analyse historical performance
- Load and modify existing sets

#### 🎲 Your Numbers
Input and analyse your own number combinations:
- Frequency analysis of your chosen numbers
- Historical match tracking
- Win probability calculations

#### 🏆 Historical Winners
Comprehensive analysis of past winning combinations:
- All historical winners
- Jackpot winners analysis
- Prize distribution statistics

#### 🔬 Bias Analysis
Advanced statistical analysis including:
- Chi-square tests for randomness
- Equipment bias detection
- Seasonal pattern analysis
- Anomaly detection

## Data Source

The application uses the official EuroMillions API:
- **Source**: `https://euromillions.api.pedromealha.dev/v1/draws`
- **Coverage**: Complete historical data from 2004 to present (1800+ draws)
- **Update Frequency**: Latest draws available shortly after official announcement

## Technical Details

### Architecture
- **Single-class GUI**: Clean, maintainable tkinter application
- **Threaded Operations**: Non-blocking data downloads and processing
- **Data Caching**: Local storage for offline analysis
- **Modular Design**: Separate tabs for different analysis types

### File Structure
```
euromillions_analyser.py      # Main application
requirements.txt              # Python dependencies
saved_numbers.json           # Stored user number combinations (created on first save)
euromillions_data_cache.json # Cached lottery data (created on first download)
```

### Dependencies
- `requests>=2.25.0` - For API data fetching
- `tkinter` - GUI framework (included with Python)
- Standard library modules: `json`, `csv`, `threading`, `datetime`, `collections`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This application is for educational and entertainment purposes only. Playing the lottery involves risk, and this tool does not guarantee winning numbers or outcomes. Please gamble responsibly.

## Screenshots

![app_img2](https://github.com/benb0jangles/euromillions_analyser/blob/main/img/Screenshot%202025-07-26%20at%2021.51.37.png)

![app_img3](https://github.com/benb0jangles/euromillions_analyser/blob/main/img/Screenshot%202025-07-26%20at%2021.52.39.png)

## Support

If you encounter any issues or have questions:
1. Check the existing [Issues](https://github.com/yourusername/euromillions_analyser/issues)
2. Create a new issue with detailed information about the problem
3. Include your Python version and operating system

---

**Happy analysing! 🍀**
