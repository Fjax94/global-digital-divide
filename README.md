# 🌍 Global Digital Divide Dashboard

### Interactive Data Analysis & Visualization of Global Internet Access

**Python | Streamlit | Pandas | Plotly | Data Analytics | Data Visualization**

[![GitHub Actions](https://github.com/Fjax94/global-digital-divide/actions/workflows/dashboard-checks.yml/badge.svg)](https://github.com/Fjax94/global-digital-divide/actions/workflows/dashboard-checks.yml)

## 📌 Project Overview

The **Global Digital Divide Dashboard** is an interactive data analytics application designed to explore and visualize internet adoption across countries and over time.

Built with Python and Streamlit, this project transforms real-world internet usage statistics into interactive visualizations, allowing users to investigate differences in digital connectivity, compare countries, and identify historical trends.

The dashboard analyzes internet adoption data covering **212 countries and territories from 1990 to 2025**, using a locally stored dataset published by Our World in Data.

The project demonstrates practical skills in data processing, exploratory data analysis, interactive visualization, and dashboard development.

---

## ✨ Key Features

### 🌐 Interactive World Map

- Visualizes internet adoption percentages geographically.
- Uses a color-coded choropleth map.
- Highlights selected countries with distinctive borders.
- Displays country-specific statistics and reporting years.
- Supports historical exploration through the year selector.

### 📈 Historical Trend Analysis

- Interactive time-series visualizations of internet adoption.
- Comparison of up to 10 countries.
- Chronological exploration from older to newer years.
- Consistent country colors across charts.
- Interactive tooltips for exploring observations.

### 📊 Country Comparison

- Side-by-side comparison of selected countries.
- Ranking by internet adoption percentage.
- Comparison of historical percentage-point changes.
- Sorting by reporting year or country name.
- Detailed statistical tables.

### 📉 Growth & Statistical Insights

The dashboard calculates key analytical indicators, including:

- Highest recorded internet adoption among selected countries.
- Largest observed percentage-point increase.
- Average recorded increase across selected countries.
- Number of observations and countries included in the analysis.
- Average internet adoption among the selected countries.

### 🎨 Modern Dark Interface

- Modern dark-themed dashboard.
- Interactive country selection.
- Custom chronological year slider.
- Responsive layout.
- Intuitive data exploration experience.

### 📥 Data Export

Users can download selected country observations as CSV files for further analysis.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Streamlit | Interactive dashboard framework |
| Pandas | Data cleaning, processing, and analysis |
| Plotly Express | Interactive line and bar charts |
| Plotly Graph Objects | Geographic data visualization |
| HTML & CSS | Custom interface styling |
| JavaScript | Custom interactive year slider |
| Git & GitHub | Version control and project management |
| GitHub Actions | Automated testing |

---

## 📂 Project Structure

```text
global-digital-divide/
│
├── app.py
├── internet_usage.csv
├── requirements.txt
├── README.md
│
├── year_slider/
│   └── index.html
│
└── tests/
    └── test_dashboard.py
```

---

## 🚀 Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/Fjax94/global-digital-divide.git
cd global-digital-divide
```

### 2. Install dependencies

Python 3.10 or newer is recommended.

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

Streamlit will launch the dashboard in your browser.

### 4. Explore the data

1. Select one or more countries from the sidebar.
2. Adjust the year slider to explore historical data.
3. Examine statistical indicators and country comparisons.
4. Explore the interactive world map.
5. Download selected observations when needed.

---

## 📊 Dataset & Methodology

**Data source:** Our World in Data

**Indicator:** Share of the population using the Internet (%)

**Underlying statistical sources:** International Telecommunication Union (ITU) and World Bank.

**Dataset period:** 1990–2025

**Geographic coverage:** 212 countries and territories represented in the local dataset.

The application uses a locally stored CSV snapshot rather than live API requests.

### Data Processing

The analysis workflow includes:

- Loading and validating CSV records.
- Converting numeric fields into appropriate data types.
- Removing invalid or missing observations.
- Filtering geographic records using three-letter country codes.
- Removing duplicate country-year observations.
- Identifying the latest available observation for each country.
- Calculating percentage-point changes between available observations.

### Analytical Considerations

- Missing annual observations are not interpolated or artificially generated.
- Countries may have different reporting years.
- The selected year acts as a historical cutoff.
- Percentage-point changes are not equivalent to annual growth rates.
- Selected-country averages are unweighted and should not be interpreted as global population-weighted averages.
- The dashboard provides descriptive analysis rather than causal explanations.

---

## 🧪 Testing & Quality Assurance

The repository includes automated tests using Python and GitHub Actions.

Tests cover:

- Python syntax validation.
- Dataset structure and integrity.
- Reproducibility of selected statistical calculations.
- Dashboard initialization.
- Country selection behavior.
- Custom year-slider integration.

To run the tests locally:

```bash
pip install pytest
python -m pytest -q tests/test_dashboard.py
```

---

## 🎯 Project Objectives

This project was developed to:

1. Investigate differences in internet connectivity across countries.
2. Explore long-term global internet adoption trends.
3. Practice real-world data cleaning and exploratory data analysis.
4. Develop interactive geographic and statistical visualizations.
5. Demonstrate end-to-end Python dashboard development.
6. Communicate data insights through a user-friendly analytical interface.

---

## 🔮 Potential Future Improvements

- Integration with additional digital development indicators.
- Broadband and mobile connectivity analysis.
- Regional comparisons and classifications.
- Automated dataset refreshes.
- Additional statistical insights and trend analysis.
- Enhanced geographic filtering.

---

## 👨‍💻 Author

**Fahad Abbas Shihab**

Computer Science Graduate | Python & Data Analytics

GitHub: [@Fjax94](https://github.com/Fjax94)

---

## 📜 License

This project is distributed under the terms specified in the repository's [LICENSE](LICENSE) file.

Dataset rights and attribution remain subject to the original data providers' terms.

---

*Built to explore global digital connectivity through interactive data analysis and visualization.*
