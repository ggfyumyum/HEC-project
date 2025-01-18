
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from data_validation import Validator
from data_analysis import Processor
from data_vizualisation import Visualizer  # Import the Visualizer class
from eq5d_profile import Eq5dvalue
from shiny import reactive
from shiny import App, ui, render

# Define the UI
app_ui = ui.page_fluid(
    ui.navset_tab(
        ui.nav_panel("Home",
            ui.h2("Simple Shiny App"),
            ui.input_text("country", "Enter country:", ""),
            ui.input_file("raw_input", "Upload raw data to be analysed"),
            ui.input_file("valueset_input", "Upload valueset"),
            ui.output_ui("group_col_ui"),
            ui.output_ui("df_ui"),
            ui.output_text("hello_text"),
            ui.output_plot("time_series_plot")
        ),
        ui.nav_panel("Page 2",
            ui.h2("Page 2"),
            ui.output_table("dataframe_output"),
            ui.p("This is the second page.")
        )
    )
)
# Define the server logic
def server(input, output, session):
    raw_data = reactive.Value(None)
    value_set = reactive.Value(None)
    validated_data = reactive.Value(None)  # Reactive value to store validated data
    processed_data = reactive.Value(None)  # Reactive value to store processed data
    data_tables = reactive.Value({})  # Reactive value to store data tables
    group_list = reactive.Value(None)

    validation_status = reactive.Value(False)  # Reactive value to track validation status
    ready_to_validate = reactive.Value(False)
    column_choices = reactive.Value(['None'])
    df_output_choices = reactive.Value(['No Dataframes Created'])

    # Set default values
    default_country = "NewZealand"

    @reactive.Effect
    @reactive.event(input.raw_input)
    def load_raw_data():
        file_info = input.raw_input()
        if file_info:
            if isinstance(file_info, list):
                file_info = file_info[0]  # Take the first file if multiple files are allowed
            file_path = file_info['datapath']
            if file_path.endswith('.csv'):
                raw_data.set(pd.read_csv(file_path))
            elif file_path.endswith('.xlsx'):
                raw_data.set(pd.read_excel(file_path))
        print("Raw data loaded:", raw_data.get())  # Debugging statement

    @reactive.Effect
    @reactive.event(input.valueset_input)
    def load_value_set():
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
    @reactive.event(raw_data)
    def extract_group_col():
        print("Updating group column options") 
        data = raw_data.get()
        if data is not None:
            columns = data.columns.tolist()
            print('The column list:', columns)  # Debugging statement
            column_choices.set(['None'] + columns)
            ready_to_validate.set(True)

    @output
    @render.ui
    def group_col_ui():
        return ui.input_select("group_col", "Select Group Column:", choices=column_choices.get())


    @reactive.Effect
    @reactive.event(raw_data, input.group_col)
    def validate_data():
        if ready_to_validate.get():
            print('Running validation')
            data = raw_data.get()
            group_c = input.group_col()

            if data is not None:
                res = Validator(data, group_col=group_c)
                print(res.group_list, 'The group list')
                group_list.set(res.group_list)
                validated_data.set(res.data)
                validation_status.set(True)  # Set validation status to True
                print('Validation has been set true')
            else:
                validation_status.set(False)

    @reactive.Effect
    def set_util():
        data = validated_data.get()
        values = value_set.get()
        country = input.country() or default_country
        if data is not None and values is not None and country:
            res = Eq5dvalue(data, values, country).calculate_util()
            processed_data.set(res)
        else:
            processed_data.set(pd.DataFrame({"Message": ["Need to input data and VS first"]}))


    @reactive.Effect
    @reactive.event(processed_data, validation_status,input.group_col)
    def process_data():
        print('Trying to process data')
        if validation_status.get():  # Check if validation was successful
            data = processed_data.get()
            values = value_set.get()
            groups = group_list.get()

            country = input.country() or default_country
            group_c = input.group_col()

            if data is not None and values is not None and country and group_c=='None':
    
                print('Trying, group list is', groups, 'group col is',group_c)
                processed = Processor(data,group_list=['FULL_DATASET'])
                print(processed.sum_df,'examp')
                data_tables.set({
                    'simple_desc':processed.simple_desc(),
                    'binary_desc':processed.binary_desc(),
                    't10_index': processed.top_frequency(),
                    'data_LFS': processed.level_frequency_score(),
                    'HSDC':processed.health_state_density_curve(),
                })

            if len(groups)>1:
                grouped_df = Processor(data, groups, group_col=group_c)
                current_data_tables = data_tables.get()
                current_data_tables.update({
                    'ts_delta_binary': grouped_df.ts_binary(),
                    'avg_utility': grouped_df.ts_utility(),
                    'avg_eqvas': grouped_df.ts_eqvas(),
                })
                data_tables.set(current_data_tables)

            if len(groups) == 2:
                current_data_tables = data_tables.get()
                current_data_tables.update({
                    'paretian': grouped_df.paretian(),
                })
                data_tables.set(current_data_tables)

            print("Data tables updated:", data_tables.get())  # Debugging statement


    @output
    @render.ui
    def df_ui():
        return ui.input_select("dataframe_select", "Select df:", choices=df_output_choices.get())
    

    @reactive.Effect
    @reactive.event(data_tables,input.group_col)
    def update_dataframe_select():
        current_data_tables = data_tables.get()
        df_output_choices.set(list(current_data_tables.keys()))

    @output
    @render.table
    def dataframe_output():
        selected_df = input.dataframe_select()
        dfs = data_tables.get()
        data = dfs.get(selected_df, pd.DataFrame({"Message": ["Need to input data and VS first"]}))
        if data is not None and not data.empty:
            fixed_index = data.reset_index()
            old_index = data.index.name if data.index.name else 'index'
            fixed_index.rename(columns={'index': old_index}, inplace=True)
            return pd.DataFrame(fixed_index)

    @output
    @render.text
    def hello_text():
        return input.country() or default_country
    
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


