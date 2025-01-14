import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from data_validation import Validator
from data_analysis import Processor
from shiny import reactive
from shiny import App, ui, render

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("Simple Shiny App"),
    ui.input_checkbox("multiple_groups", "Enable Multiple Groups", False),
    ui.input_checkbox("funny_groups", "Enable Funny Groups", False),
    ui.input_text("group_col", "Enter Group Column:", ""),
    ui.input_text("country", "Enter country:", ""),
    ui.input_file("raw_input", "Upload Excel or CSV File"),
    ui.input_file("valueset_input", "Upload Excel or CSV File"),
    ui.output_plot("line_plot"),
    ui.output_table("new_table"),
    ui.output_text("hello_text"),
    ui.output_table("dataframe_output"),
    ui.output_table("vs_output"),
    ui.output_plot("time_series_plot")
)

# Define the server logic
def server(input, output, session):
    raw_data = reactive.Value(None)
    value_set = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.raw_input)
    def _():
        file_info = input.raw_input()
        if file_info:
            if isinstance(file_info, list):
                file_info = file_info[0]  # Take the first file if multiple files are allowed
            file_path = file_info['datapath']
            if file_path.endswith('.csv'):
                raw_data.set(pd.read_csv(file_path))
            elif file_path.endswith('.xlsx'):
                raw_data.set(pd.read_excel(file_path))

    @reactive.Effect
    @reactive.event(input.valueset_input)
    def _():
        file_info = input.valueset_input()
        if file_info:
            if isinstance(file_info, list):
                file_info = file_info[0]  # Take the first file if multiple files are allowed
            file_path = file_info['datapath']
            if file_path.endswith('.csv'):
                value_set.set(pd.read_csv(file_path))
            elif file_path.endswith('.xlsx'):
                value_set.set(pd.read_excel(file_path))

    @reactive.Calc
    def new_table():
        data = raw_data.get()
        if data is not None:
            processed_data = Processor(data).get_percent()
            return processed_data
        return pd.DataFrame()

    @output
    @render.table
    def dataframe_output():
        return process_data()

    @output
    @render.table
    def vs_output():
        v = value_set.get()
        return v

    @output
    @render.plot
    def time_series_plot():
        data = new_table()
        if data is not None and not data.empty:
            data.set_index(data.columns[0], inplace=True)
            fig, ax = plt.subplots()
            for column in data.columns:
                ax.plot(data.index, data[column], label=column)
            ax.set_xlabel(data.index.name)
            ax.set_ylabel("Values")
            ax.set_title(f"Time Series of {', '.join(map(str, data.columns))}")
            ax.legend()
            return fig

    @output
    @render.text
    def hello_text():
        return "hello"

    @reactive.Calc
    def process_data():
        raw_data_df = raw_data.get()
        country = input.country()
        multiple_groups = input.multiple_groups()
        return raw_data_df

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()