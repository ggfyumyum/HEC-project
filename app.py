
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
        ui.nav_panel("Raw Data Input",
            ui.h2("Simple Shiny App"),
            ui.input_text("country", "Enter country:", ""),
            ui.input_file("raw_input", "Upload raw data to be analysed"),
            ui.input_file("valueset_input", "Upload valueset"),
            ui.h2("Raw data"),
            ui.output_table('rawdata_display'),
            ui.h2("Processed data"),
            ui.output_table("validated_data_display"),
        ),

        
        ui.nav_panel("Data analysis",
            ui.h2("Display tables and plots of data from one or more groups"),
            ui.h2("Select whole analysis to display)"),

            
            ui.output_ui("group_col_ui"),

            ui.output_ui("df_ui"),
            ui.output_text('print_grouplist'),
            ui.output_ui("group_options_ui"),
            ui.output_table("show_df1"),
            ui.output_plot("desc_plot")
            
        ),
        ui.nav_panel("Time-series analysis",
                     
            ui.h2("Display table/plots of the change over time with n time intervals"),
            ui.output_ui("group_col_ui_page3"),
            ui.output_text("time_intervals_text"),
            ui.output_ui("df_ui2"),
            ui.output_table("selected_ts_df"),
            ui.output_plot('time_series_plot')

        ),
    )
)
# Define the server logic
def server(input, output, session):

    value_set = reactive.Value(pd.read_csv('valueset_data.csv'))

    raw_data = reactive.Value(None)
    validated_data = reactive.Value(None)  # Reactive value to store validated data
    data_with_util = reactive.Value(None)

    grouped_dfs = reactive.Value([])
    data_tables = reactive.Value({})  # Reactive value to store data tables
    group_data_tables = reactive.Value({})
    time_series_tables = reactive.value({})

    groups = reactive.Value(['NO_GROUP_CHOSEN'])

    util_added = reactive.Value(False)
    validation_status = reactive.Value(False)  # Reactive value to track validation status
    ready_to_validate = reactive.Value(False)

    column_choices = reactive.Value(['None'])
    df_output_choices = reactive.Value(['No Dataframes Created'])
    ts_output_choices = reactive.Value(['No Time series Created'])

    
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
        print('running groupcol extraction')
        data = raw_data.get()
        if data is not None:
            columns = data.columns.tolist()
            column_choices.set(['None'] + columns)
            ready_to_validate.set(True)
            print('ready to validate, column choices are',column_choices.get())

    @reactive.Effect
    @reactive.event(raw_data,ready_to_validate)
    def validate_data():
        if ready_to_validate.get():
            print('Running validation')
            data = raw_data.get()
            if data is not None:
                res = Validator(data)
                validated_data.set(res.data)
                validation_status.set(True)  # Set validation status to True
                print('Validation has been set true')
            else:
                validation_status.set(False)

    @reactive.Effect
    @reactive.event(validation_status)
    def set_util():
        if validation_status.get():
            print('setting util')
            data = validated_data.get()

            values = value_set.get()
            country = input.country() or default_country
            if data is not None and values is not None and country:
                res = Eq5dvalue(data, values, country).calculate_util()
                data_with_util.set(res)
                util_added.set(True)

    
    @output
    @render.table
    @reactive.event(raw_data)
    def rawdata_display():
        df = raw_data.get()
        if df is not None:
            old_index = df.index.name if df.index.name else 'index'
            fixed_index = df.reset_index()
            fixed_index.rename(columns={'index': old_index}, inplace=True)
            return pd.DataFrame(fixed_index).head(2)
        else:
            return pd.DataFrame({"No data uploaded": ["Dataframe will display here when raw data is uploaded"]})
    

    @output
    @render.table
    @reactive.event(data_with_util)
    def validated_data_display():
        df = data_with_util.get()
        if df is not None:
            old_index = df.index.name if df.index.name else 'index'
            fixed_index = df.reset_index()
            fixed_index.rename(columns={'index': old_index}, inplace=True)
            return pd.DataFrame(fixed_index).head(100)
        else:
            return pd.DataFrame({"No validated data": ["Validated dataframe will display here when data is validated"]})

    @output
    @render.ui
    def group_col_ui():
        return ui.input_select("group_col", "Group data By:", choices=column_choices.get())
    
    @reactive.Effect
    @reactive.event(input.group_col)
    def print_group_col():
        group_c = input.group_col()
        print(f"The group_col has been set to: {group_c}")
        
    
    @reactive.Effect
    @reactive.event(input.group_col)
    def process_data():
        print('Trying to process data')
        if util_added.get():  # Check if validation was successful
            data = data_with_util.get()
            values = value_set.get()

            print(f"Before accessing group_col: {input.group_col()}")
            group_c = input.group_col()
            print(f"After accessing group_col: {group_c}")

            country = input.country() or default_country

            groups.set(Processor(data,group_c).group_list)

            groups_list = groups.get()
            print('groups is ',groups_list)

            if data is not None and values is not None and country and groups_list==['NO_GROUP_CHOSEN']:
                print("generating whole analysis")
                processed = Processor(data,group_col='None')
                groups.set(processed.group_list)
                data_tables.set({
                    'simple_desc':processed.simple_desc(),
                    'binary_desc':processed.binary_desc(),
                    't10_index': processed.top_frequency(),
                    'data_LFS': processed.level_frequency_score(),
                    'health_state_density_curve':processed.health_state_density_curve(),
                })
                print("ive updated data_tables",data_tables.get().keys())

            if data is not None and group_c!='None' and input.dataframe_select()!='None' and len(groups_list)>1:
                res = {}
                grouped_dfs.set(['simple_desc','binary_desc','top_frequency'])
                groups_wanted = grouped_dfs.get()
                all_dfs = Processor(data,group_c).siloed_data

                res = {
                    group_name: {
                        groups_wanted[n]: df
                for n, df in enumerate([Processor(group_data).simple_desc(), Processor(group_data).binary_desc(), Processor(group_data).top_frequency()])
            }
            for group_name, group_data in all_dfs.items()
        }           
                
                hsdc_df = Processor(data,group_c).health_state_density_curve()
                for group_name, group_data in res.items():
                    res[group_name]['health_state_density_curve'] = hsdc_df
                
                grouped_dfs.set(['simple_desc','binary_desc','top_frequency','health_state_density_curve'])
                group_data_tables.set(res)
            
            if data is not None and group_c!='None' and input.dataframe_select()!='None' and len(groups_list)==2:
                final = group_data_tables.get()
                this_data = data_with_util.get().reset_index()
                px_df = Processor(this_data, group_c).paretian()

                for group_name, group_data in all_dfs.items():
                    final[group_name]['paretian'] = px_df

                group_data_tables.set(final)
                grouped_dfs.set(['simple_desc','binary_desc','top_frequency','health_state_density_curve','paretian'])
                
    

    @output
    @render.ui
    def df_ui():
        return ui.input_select("dataframe_select", "Select df type:", choices=df_output_choices.get())
    
    @reactive.Effect
    @reactive.event(input.group_col)
    def update_dataframe_select():
        print('updating df select based on gorup col')
        print('data tables is', data_tables.get(), 'grouped dfs is',grouped_dfs.get())

        if input.group_col()=='None':
            print('set it to the whole list options')
            k = data_tables.get()
            print(k,'jqwehjqe')
            df_output_choices.set(list(k))
            print("Dataqweqeqes updated:", df_output_choices.get())
        else:
            df_output_choices.set(grouped_dfs.get())

        print("Dataframe options updated:", df_output_choices.get())

    @output
    @render.text
    def print_grouplist():
        out = groups.get()
        return f"Group list for selected group: {out}"
    
    @output
    @render.ui
    def group_options_ui():
        return ui.input_radio_buttons("group_options", "Select Group to display:", groups.get())
    
    
    @output
    @render.table
    def show_df1():
        if input.group_col()=='None' or groups.get()=='NO_GROUP_CHOSEN':
            tables = data_tables.get()
        
        else:
            table_list = group_data_tables.get()
  
            tables = table_list[input.group_options()]


        df = tables[input.dataframe_select()]

        if df is not None:
            old_index = df.index.name if df.index.name else 'index'
            fixed_index = df.reset_index()
            fixed_index.rename(columns={'index': old_index}, inplace=True)
            return pd.DataFrame(fixed_index).head(10)
        else:
            return pd.DataFrame({"No data uploaded": ["Dataframe will display here when raw data is uploaded"]})
        

    @output
    @render.plot
    def desc_plot():

        selected_df = input.dataframe_select()
        data = data_with_util.get()
        grouplist = groups.get()
        group_c = input.group_col()
        
        if grouplist == ['NO_GROUP_CHOSEN']:

            dfs = data_tables.get()
            data = dfs[selected_df]
            vis = Visualizer(data)
            print('created vis',vis)

            if selected_df == 'simple_desc':
                data = Processor(validated_data.get())
                vis = Visualizer(data.get_percent())
                fig = vis.histogram()

            elif selected_df == 'binary_desc':
                problems_df = data[['% problems']].copy()
                problems_df['%no problems'] = 100 - problems_df['% problems']
                vis = Visualizer(problems_df)
                fig = vis.histogram()

            elif selected_df == 'health_state_density_curve':
                data = data_tables.get()['health_state_density_curve']
                vis = Visualizer(data)
                fig = vis.health_state_density_curve()

            elif selected_df == 't10_index' or selected_df == 'data_LFS':
                # Placeholder for t10_index plot
                pass

        else:
            
            if selected_df=='simple_desc':
                grouped_pct = {}
                siloed = Processor(validated_data.get(),group_c).siloed_data

                for key, item in siloed.items():
                    grouped_pct[key] = Processor(item).get_percent()

                vis = Visualizer(grouped_pct)
                fig = vis.histogram_by_group()

            elif selected_df=='binary_desc':
                dfs = group_data_tables.get()
                new_dict = {group_name: group_data[selected_df] for group_name, group_data in dfs.items()}

                for key, item in new_dict.items():
                    as_pct = new_dict[key][['% problems']].copy()
                    as_pct['%no problems'] = 100 - as_pct['% problems']
                    new_dict[key] = as_pct

                vis = Visualizer(new_dict)
                fig = vis.histogram_by_group()

            elif selected_df == 'health_state_density_curve':
                vis = Visualizer(group_data_tables.get()[grouplist[0]]['health_state_density_curve'])
                fig = vis.health_state_density_curve()


        return fig
    
    @output
    @render.ui
    def group_col_ui_page3():
        return ui.input_select("group_col_page3", "Select Column containing time intervals:", choices=column_choices.get())
    
    @output
    @render.ui
    def df_ui2():
        return ui.input_select("ts_select", "Select df type:", choices=ts_output_choices.get())
    
              
    
    @reactive.Effect
    @reactive.event(time_series_tables,input.group_col_page3)
    def update_ts_select():
        if input.group_col_page3=='None':
            ts_output_choices.set(['No Choice available'])


    @reactive.Effect
    @reactive.event(util_added,input.group_col_page3)
    def process_ts_data():
        print('generating timeseries data')
        if util_added.get():  # Check if validation was successful
            data = data_with_util.get()
            groupcol = input.group_col_page3()

            if data is not None and groupcol!='None':

                processor = Processor(data,groupcol)
                wanted_ts = ['ts_delta_binary','avg_utility','avg_eqvas']
                res = {}
                for n, df in enumerate ( [processor.ts_binary(), processor.ts_utility(), processor.ts_eqvas()]):
                    res[wanted_ts[n]] = df

                time_series_tables.set(res)
                ts_output_choices.set(wanted_ts)
    
    @output
    @render.text
    @reactive.event(input.group_col_page3)
    def time_intervals_text():
        group_col = input.group_col_page3()
        if group_col!='TIME_INTERVAL':
            return "Invalid time grouping selection"
        
        if group_col:
            data = data_with_util.get()
            if data is not None:
                time_groups = Processor(data, group_col).group_list
                return f"Time intervals found in selected column: {time_groups}"
        return "Invalid time grouping selection"


    @output
    @render.ui
    def df_ui2():
        return ui.input_select("ts_select", "Select df type:", choices=ts_output_choices.get())
    
    @output
    @render.plot
    def time_series_plot():
        selected_ts = input.ts_select()
        
        if selected_ts == 'No Time series Created':
            return plt.figure()  # Display nothing (empty plot)
        
        ts_data = time_series_tables.get().get(selected_ts)
        if ts_data is not None:
            vis = Visualizer(ts_data)
            fig = vis.time_series()  # Assuming Visualizer has a method time_series()
            return fig
        
        return plt.figure()  # Default empty plot if no data or no matching selection
    
    @output
    @render.table
    def selected_ts_df():
        selected_ts = input.ts_select()
        
        if selected_ts == 'No Time series Created':
            return pd.DataFrame({"Message": ["No time series selected"]})
        
        ts_data = time_series_tables.get().get(selected_ts)

        print('ts_data',ts_data)

        if ts_data is not None:

            ts_copy = ts_data.copy()

            old_index = ts_copy.index.name if ts_copy.index.name else 'index'
            fixed_index = ts_copy.reset_index()
            fixed_index.rename(columns={'index': old_index}, inplace=True)

            return pd.DataFrame(fixed_index).head(10)
        
        return pd.DataFrame({"Message": ["No data available"]})
    
    
# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()


'''
    @output
    @render.table
    def dataframe_output():
        selected_df = input.dataframe_select()
        dfs = data_tables.get()
        data = dfs.get(selected_df, pd.DataFrame({"Message": ["Need to input data and VS first"]}))
        if data is not None and not data.empty:
            old_index = data.index.name if data.index.name else 'index'
            fixed_index = data.reset_index()
            fixed_index.rename(columns={'index': old_index}, inplace=True)
            return pd.DataFrame(fixed_index)

            if len(groups) == 2:
                current_data_tables = data_tables.get()
                current_data_tables.update({
                    'paretian': grouped_df.paretian(),
                })
                data_tables.set(current_data_tables)
if len(groups)>1:
                grouped_df = Processor(data, groups, group_col=group_c)
                current_data_tables = data_tables.get()
                current_data_tables.update({
                    'ts_delta_binary': grouped_df.ts_binary(),
                    'avg_utility': grouped_df.ts_utility(),
                    'avg_eqvas': grouped_df.ts_eqvas(),
                })
                data_tables.set(current_data_tables)
'''