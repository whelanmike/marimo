import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    return alt, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Task Analysis: Tsk_1 vs Tsk_2
    Comparing task durations and identifying discrepancies.
    """)
    return


@app.cell(hide_code=True)
def _(pd):
    # Load Data
    tsk1_df = pd.read_csv("task_timelines.csv")
    tsk2_df = pd.read_csv("task_timelines_tsk2.csv")
    telemetry_df = pd.read_csv("machine_telemetry.csv")

    # Rename columns for merge
    tsk1_df = tsk1_df.rename(columns={"duration_sec": "duration_tsk1", "task_model": "model_tsk1", "start_event_timestamp": "start_tsk1"})
    tsk2_df = tsk2_df.rename(columns={"duration_sec": "duration_tsk2", "task_model": "model_tsk2", "start_event_timestamp": "start_tsk2", "end_event_timestamp": "end_tsk2"})

    # Merge on sequence
    # Assuming 'event_sequence' is the key
    merged_df = pd.merge(
        tsk1_df[["event_sequence", "machine_number", "task_status", "duration_tsk1", "start_tsk1", "end_event_timestamp"]],
        tsk2_df[["event_sequence", "duration_tsk2", "start_tsk2", "end_tsk2"]],
        on="event_sequence",
        how="inner"
    )

    # Calculate calc fields
    merged_df["duration_diff"] = merged_df["duration_tsk1"] - merged_df["duration_tsk2"]
    merged_df["diff_abs"] = merged_df["duration_diff"].abs()
    merged_df["start_date"] = pd.to_datetime(merged_df["start_tsk1"]).dt.date

    # Telemetry prep
    telemetry_df['event_timestamp'] = pd.to_datetime(telemetry_df['event_timestamp'])
    return merged_df, telemetry_df


@app.cell(hide_code=True)
def _(merged_df, mo):
    # Summary Metrics
    total_tasks = len(merged_df)
    discrepant_tasks = len(merged_df[merged_df["diff_abs"] > 0.001]) # Float tolerance

    mo.md(
        f"""
        ### High Level Summary
        - **Total Tasks Analyzed**: {total_tasks}
        - **Tasks with Duration Differences**: {discrepant_tasks}
        """
    )
    return


@app.cell
def _(merged_df, mo, pd):
    # Ensure start_date is datetime
    # Convert to pandas timestamp first to handle any mixed types, then extract date part for UI
    # We want consistent types. Let's start with timestamps in the DF for operations
    merged_df['start_date'] = pd.to_datetime(merged_df['start_date'])

    # For the UI slider, we explicitly need datetime.date objects to avoid "T00:00:00" parsing errors in some widgets
    min_ts = merged_df['start_date'].min()
    max_ts = merged_df['start_date'].max()

    # Handle implicit conversion safety
    if pd.isna(min_ts):
        # Fallback if empty
        min_date = pd.Timestamp.now().date()
        max_date = pd.Timestamp.now().date()
    else:
        min_date = min_ts.date()
        max_date = max_ts.date()

    statuses = sorted(merged_df['task_status'].unique().tolist())

    date_filter = mo.ui.date_range(
        start=min_date, 
        stop=max_date, 
        value=(min_date, max_date), 
        label="Date Range"
    )

    status_filter = mo.ui.multiselect(
        options=statuses, 
        value=statuses, 
        label="Task Status"
    )
    return date_filter, status_filter


@app.cell
def _(alt, date_filter, merged_df, mo, pd, status_filter):
    # Filter Data
    # Handle possible empty selection
    s_val = status_filter.value if status_filter.value else []
    d_val = date_filter.value

    filtered_df = merged_df[
        (merged_df['start_date'] >= pd.to_datetime(d_val[0])) &
        (merged_df['start_date'] <= pd.to_datetime(d_val[1])) &
        (merged_df['task_status'].isin(s_val))
    ]

    # Aggregate
    agg_df = filtered_df.groupby(["start_date", "task_status"]).agg(
        count=("event_sequence", "count"),
        total_duration_tsk1=("duration_tsk1", "sum"),
        total_duration_tsk2=("duration_tsk2", "sum"),
        mean_diff=("duration_diff", "mean"),
        sum_diff=("duration_diff", "sum")
    ).reset_index()

    # Stacked Bar Chart with Brush
    brush = alt.selection_interval(encodings=['x'])

    chart = alt.Chart(agg_df).mark_bar().encode(
        x='start_date:T',
        y=alt.Y('sum_diff:Q', title="Total Duration Difference (s)"),
        color='task_status:N',
        tooltip=['start_date', 'task_status', 'count', 'mean_diff', 'sum_diff']
    ).properties(
        title="Summary: Duration Difference by Date & Status"
    ).add_params(brush)

    chart_ui = mo.ui.altair_chart(chart)

    mo.vstack([
        mo.hstack([date_filter, status_filter]),
        chart_ui
    ])
    return agg_df, chart_ui


@app.cell(hide_code=True)
def _(agg_df, mo):
    mo.md("### Daily Aggregation Data")
    mo.ui.table(agg_df, selection=None)
    return


@app.cell(hide_code=True)
def _(merged_df, mo):
    max_diff = int(merged_df["diff_abs"].max()) + 1 if not merged_df.empty else 100
    min_diff_slider = mo.ui.slider(start=0, stop=max_diff, step=1, value=0, label="Min Duration Diff (s)")
    return (min_diff_slider,)


@app.cell(hide_code=True)
def _(chart_ui, merged_df, min_diff_slider, mo, pd):
    mo.md("### Discrepancy Analysis (Tsk_1 - Tsk_2)")

    # Filter for diffs
    diff_df = merged_df[merged_df["diff_abs"] >= min_diff_slider.value].sort_values("diff_abs", ascending=False)

    # Filter by Chart Selection (Brush)
    if not chart_ui.value.empty:
        # chart_ui.value contains the aggregated rows in the selection
        # Extract the date range from the selected aggregation
        selected_dates = pd.to_datetime(chart_ui.value['start_date'])
        if not selected_dates.empty:
            min_sel = selected_dates.min().date()
            max_sel = selected_dates.max().date()

            # Filter diff_df
            # ensure diff_df 'start_date' is comparable (it was created as date object in merge step)
            diff_df = diff_df[
                (diff_df['start_date'] >= min_sel) &
                (diff_df['start_date'] <= max_sel)
            ]

    # Selection Table
    table = mo.ui.table(
        diff_df, 
        selection='single',
        pagination=True,
        label="Tasks with Differences"
    )

    mo.vstack([min_diff_slider, table])
    return (table,)


@app.cell(hide_code=True)
def _(mo, table, telemetry_df):
    selected_row = table.value

    # Initialize defaults
    seq_id = None
    dur_1 = None
    dur_2 = None

    if hasattr(selected_row, 'empty') and selected_row.empty:
        content = mo.md("Select a row above to see telemetry details.")
    elif isinstance(selected_row, list) and not selected_row:
         content = mo.md("Select a row above to see telemetry details.")
    else:
        try:
            if isinstance(selected_row, list):
                # row is a dict
                row = selected_row[0]
                seq_id = row.get('event_sequence')
                dur_1 = row.get('duration_tsk1')
                dur_2 = row.get('duration_tsk2')
            else:
                # row is a DataFrame
                if len(selected_row) > 0:
                    row = selected_row.iloc[0]
                    seq_id = row['event_sequence']
                    dur_1 = row['duration_tsk1']
                    dur_2 = row['duration_tsk2']
        except (IndexError, KeyError, AttributeError):
            seq_id = None

        if seq_id:
            # Filter telemetry
            events = telemetry_df[telemetry_df['event_sequence'] == seq_id].sort_values('event_timestamp').copy()
            # Add durations
            # Calculate delta (safely handling None/NaN)
            try:
                events['duration_delta'] = dur_1 - dur_2
            except (TypeError, ValueError):
                events['duration_delta'] = None

            events['duration_tsk1'] = dur_1
            events['duration_tsk2'] = dur_2

            content = mo.vstack([
                mo.md(f"#### Telemetry for Sequence: {seq_id}"),
                mo.ui.table(events, selection=None, pagination=False)
            ])
        else:
            content = mo.md("Select a row above.")

    content
    return


if __name__ == "__main__":
    app.run()
