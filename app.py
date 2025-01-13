import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import jinja2

from data_validation import Validator
from data_analysis import Processor
from data_vizualisation import Visualizer
from eq5d_profile import Eq5dvalue
from eq5d_decrement_processing import Decrement_processing
from shiny import reactive
from shiny import App, ui, render

'''
value_set = pd.read_csv('valueset_data.csv')
raw_data = pd.read_csv('fake_data.csv')

multiple_groups = True
group_col = 'TIME_INTERVAL'
country = 'NewZealand'

validated = Validator(raw_data,multiple_groups,group_col)
group_list = validated.group_list
data = Eq5dvalue(validated.data, value_set,country).calculate_util()
siloed_data = Processor(data,group_list,group_col).siloed_data

t10_index = Processor(data,group_list,group_col).top_frequency()
ts_delta_binary = Processor(data,group_list,group_col).ts_binary()
paretian = Processor(data,group_list,group_col).paretian()
data_LSS = Processor(data,group_list,group_col).level_frequency_score()
avg_utility = Processor(data,group_list,group_col).ts_utility()
avg_eqvas = Processor(data,group_list,group_col).ts_eqvas()
hdsc = Processor(data,group_list,group_col).health_state_density_curve()

    valueset = input.valueset_input()
    group_col = input.group_col()
    country = input.country()

'''

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
    ui.output_table("vs_output")
    
    
    
)
# Define the server logic
def server(input, output, session):
    raw_data = reactive.Value(None)
    valueset = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.raw_input)
    def _():
        file_info = input.raw_input()
        if file_info:
            if file_info:
                if isinstance(file_info, list):
                    file_info = file_info[0]
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
            if file_info:
                if isinstance(file_info, list):
                    file_info = file_info[0]
            file_path = file_info['datapath']
            if file_path.endswith('.csv'):
                valueset.set(pd.read_csv(file_path))
            elif file_path.endswith('.xlsx'):
                valueset.set(pd.read_excel(file_path))

    @output
    @render.plot
    def line_plot():
        name = input.multiple_groups()
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1], label='Line')
        ax.set_title(name)
        ax.legend()
        return fig
    
    @output
    @render.table
    def new_table():
        data = raw_data.get()
        if data is not None:
            processed_data = Processor(data).simple_desc()
            return processed_data
        return pd.DataFrame()
    
    @output
    @render.text
    def hello_text():
        return input.valueset_input()
    
    @reactive.Calc
    def process_data():
        raw_data2 = raw_data.get()
        country = input.country()
        multiple_groups = input.multiple_groups()
        return raw_data2
    
    @output
    @render.table
    def dataframe_output():
        return process_data()
    
    @output
    @render.table
    def vs_output():
        v = valueset.get()
        return v

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()