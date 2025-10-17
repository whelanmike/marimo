# Car Sales Ireland 2025

This project analyzes car sales data in Ireland for the year 2025, based on data from the Society of the Irish Motor Industry (SIMI). The analysis is presented in an interactive Marimo notebook.

## Data Source

The data used in this analysis is from the SIMI's National Vehicle Statistics, specifically the September 2025 press release.

- [SIMI Motorstats](https://www.simi.ie/en/motorstats/national-vehicle-statistics)

## Features

- **Interactive Filtering:** Filter car sales data by the number of sales (Year-to-Date).
- **Data Visualization:** View the percentage of overall sales for selected vehicles in a bar chart.
- **Detailed Information:** Hover over the chart to see more details, including month-over-month sales and year-to-date rankings.

## Setup

1.  **Clone the repository:**
    ```bash
    # Make sure to replace <repository-url> with the actual URL of your repository
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**

    This project requires the following Python packages: `marimo`, `polars`, `duckdb`, `plotly`, and `openpyxl`. You can install them using pip:
    ```bash
    pip install marimo polars duckdb plotly openpyxl
    ```

## Running the Notebook

To run the interactive notebook, use the following command:

```bash
marimo run car_stats.py
```

This will start the Marimo server and open the notebook in your web browser.