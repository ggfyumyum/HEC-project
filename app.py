import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from data_validation import Validator
from data_analysis import Processor
from data_vizualisation import Visualizer
from eq5d_profile import Eq5dvalue
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

    ui.output_text('testing'),

    ui.div(
        ui.output_table("dataframe_output"),
        style="overflow-x: auto; width: 100%;"
    ),
    ui.output_text("hello_text"),
    ui.output_plot('time_series_plot')
)

# Define the server logic
def server(input, output, session):
    raw_data = reactive.Value(None)
    validated_data = reactive.Value(None)
    value_set = reactive.Value(None)
    processed_data = reactive.Value(None)
    group_list = reactive.Value(None)
    extra_vars = reactive.Value({}) #store additional var here
    data_tables = reactive.Value({})
    validation_status = reactive.Value(False)

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

    @reactive.Effect
    @reactive.event(raw_data, input.group_col, input.multiple_groups)
    def validate_data():
        print('running validation')
        data = raw_data.get()
        group_c = input.group_col()
        
        multiple_groups = input.multiple_groups()

        if data is not None and group_c is not None:
            res = Validator(data,group_col=group_c)
            print(res.group_list,' the group list')
            print('the data',res.data)
            group_list.set(res.group_list)
            validated_data.set(res.data)
            validation_status.set(True)  # Set validation status to True
            print('validation has been set true')
        else:
            validation_status.set(False)


    @reactive.Effect
    def set_util():
        data = validated_data.get()
        values = value_set.get()
        country = input.country()

        if data is not None and values is not None and country:
            res = Eq5dvalue(data, values, country).calculate_util()
            processed_data.set(res)
        else:
            processed_data.set(pd.DataFrame({"Message": ["need to input data and VS first"]}))
        
    @output
    @render.text
    def testing():
        return input.country()
    
    
    @reactive.Effect
    @reactive.event(processed_data,validation_status)
    def process_data():
        print('trying2')
        if validation_status.get():  # Check if validation was successful
            country = 'NewZealand'
            group_c = 'TIME_INTERVAL'
            data = processed_data.get()
            values = value_set.get()
            groups = group_list.get()

            country = input.country()
            group_c = input.group_col()
            
            if data is not None and values is not None and country and group_c:
                print('trying, group list is',groups)
                processed = Processor(data, groups, group_col=group_c)
                data_tables.set({
                    't10_index': processed.top_frequency(),
                    'ts_delta_binary': processed.ts_binary(),
                    'paretian': processed.paretian(),
                    'data_LSS': processed.level_frequency_score(),
                    'avg_utility': processed.ts_utility(),
                    'avg_eqvas': processed.ts_eqvas(),
                })
                print("Data tables updated:", data_tables.get())  # Debugging statement
    

    @output
    @render.table
    def dataframe_output():
        dfs = data_tables.get()
        data = dfs.get('paretian', pd.DataFrame({"Message": ["need to input data and VS first"]}))
        if data is not None and not data.empty:
            return pd.DataFrame(data)
        return pd.DataFrame({"Message": ["need to input data and VS first"]})
    
        
    @output
    @render.text
    def hello_text():
        return "hello"
    
    @output
    @render.plot
    def time_series_plot():
        data = processed_data.get()
        if not data.empty:
            vis = Visualizer(data)
            fig = vis.time_series()
            return fig
        return plt.figure()
        
    
# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()