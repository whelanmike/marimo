import marimo

__generated_with = "0.16.3"
app = marimo.App(width="full", app_title="Car Sales Ireland 2025")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Car Sales 2025
    ## SIMI Data: National Vehicle Statistics
    https://www.simi.ie/en/motorstats/national-vehicle-statistics
    """
    )
    return


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import polars as pl
    import duckdb as db
    import plotly.express as px
    # import os
    return mo, pl, px


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Read data from Excel file using SQL and create a dataframe called `sales_ytd`""")
    return


@app.cell
def _(mo):
    sales_ytd = mo.sql(
        f"""
        ;
        with c_passenger_cars as 
            (
            select 
                   marque				as make
                  ,"01/09 - 30/09"      as mth_sep 
                  ,"01/01 - 30/09"		as ytd
            	  ,dense_rank() over(order by ytd desc)   as ranking_ytd
            from  read_xlsx('./data/September_StatsPressRel2025.xlsx', range = 'A4:C48')
        	)
            select 
            	   make 
            	  ,mth_sep
            	  ,ytd
            	  ,round(100.0 * ytd / sum(ytd) over (), 2) as pct_ytd 
            	  ,ranking_ytd
            from  c_passenger_cars
            order by make 
        ;
        """
    )
    return (sales_ytd,)


@app.cell
def _(mo, sales_ytd):
    range_slider = mo.ui.range_slider.from_series(sales_ytd["ytd"], label='Number of Sales', full_width=True)
    return (range_slider,)


@app.cell
def _(mo, range_slider):
    mo.hstack([range_slider, mo.md(f"Has value: {range_slider.value}")])
    return


@app.cell
def _(pl, range_slider, sales_ytd):
    # 2. Filtering Logic
    df_slider = sales_ytd.filter((pl.col('ytd') >= range_slider.value[0]) & (pl.col('ytd') <= range_slider.value[1]))
    return (df_slider,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Percentage of overall sales for selected vehicles""")
    return


@app.cell
def _(df_slider):
    df_slider['pct_ytd'].sum()
    return


@app.cell(hide_code=True)
def _(df_slider, px):
    fig = px.bar(df_slider
                 ,y='make'
                 ,x='pct_ytd'
                 ,orientation='h'
                 ,color='make'
                 # ,text='pct_ytd'
                 ,text_auto=True
                 ,title='2025 Car Sales Ireland (Sep. Data)'
                 ,hover_data=["ytd", "mth_sep", "ranking_ytd"]
                 ,height=800
                 ,
                )
    fig.update_layout(barmode='stack', yaxis={'categoryorder':'total ascending'})
    fig.show()
    return


if __name__ == "__main__":
    app.run()
