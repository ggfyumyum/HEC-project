import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from data_validation import Validator
from data_analysis import Processor
from data_vizualisation import Visualizer
from shiny import reactive
from shiny import App, ui, render

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("Simple Shiny App"),
    ui.input_checkbox("multiple_groups", "Enable Multiple Groups", False),
    ui.input_text("group_col", "Enter Group Column:", ""),
    ui.input_text("country", "Enter country:", ""),

    ui.input_file("raw_input", "Upload raw data"),
    ui.input_file("valueset_input", "Upload valueset"),

    ui.output_table("dataframe_output"),
    ui.output_text("hello_text"),
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
    def show_percent():
        data = raw_data.get()
        if data is not None:
            processed_data = Processor(data).simple_desc()
            return processed_data
        return pd.DataFrame()

    @output
    @render.table
    def dataframe_output():
        return show_percent()
        
    @output
    @render.text
    def hello_text():
        return "hello"
    
    @output
    @render.plot
    def time_series_plot():
        data = show_percent()
        if not data.empty:
            vis = Visualizer(data)
            fig = vis.time_series()
            return fig
        return plt.figure()
    
    


# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()