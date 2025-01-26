
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time

from data_validation import Validator
from data_analysis import Processor
from data_vizualisation import Visualizer
from eq5d_profile import Eq5dvalue
from data_generator import Generator
from shiny import reactive
from shiny import App, ui, render

# Define the UI
app_ui = ui.page_fluid(
    ui.navset_tab(
        ui.nav_panel("Raw Data Input",
            ui.row(
                ui.column(4,  # Left third of the page
                    ui.h2("Shiny app for EQ-5D data analysis"),
                    ui.br(),
                    ui.output_ui("country_select_ui"),
                    ui.input_file("valueset_input", "Upload valueset (default valueset already loaded)"),
                    ui.input_file("raw_input", "Upload raw data to be analysed"),
                    ui.input_action_button("generate_fake_data", "Click to generate Fake Data with the following parameters:"),
                    ui.br(),
                    ui.br(),
                    ui.row(
                        ui.column(6, ui.input_select("patient_number", "Number of patients:", choices=[10**i for i in range(1, 5)], selected=10)),
                        ui.column(6, ui.input_select("time_intervals", "Number of time intervals:", choices=list(range(1, 11)), selected=1))
                    ),
                    ui.output_ui('filter_col_ui'),
                    ui.output_ui("filter_values_ui")
                ),
                ui.column(7,  # Right two-thirds of the page
                    ui.h2("Raw data"),
                    ui.output_table('rawdata_display'),
                    ui.br(),
                    ui.h2("Data with utility scores"),
                    ui.output_table("util_data_display"),
                    ui.br(),
                    ui.h2(ui.output_text("filtered_data_heading")),
                    ui.output_table("filtered_data_display"),
                )
            )
        ),
        ui.nav_panel("Data analysis",
            ui.h2("Display tables and plots of data from one or more groups"),
            ui.h2("Select whole analysis to display"),
            ui.output_ui("group_col_ui"),
            ui.output_ui("df_ui"),
            ui.output_ui("group_options_ui"),
            ui.output_text("print_grouplist"),
            ui.input_checkbox("reverse_grouplist_checkbox", "Reverse Group List", value=False),
            ui.output_table("show_df1"),
            ui.output_plot("desc_plot"),

        ),
        ui.nav_panel("Time-series analysis",
            ui.h2("Display table/plots of the change over time with n time intervals"),
            ui.br(),
            ui.br(),
            ui.output_text("time_group_list"),
            ui.output_ui("group_col_ui_page3"),

            ui.input_text("new_time_group", "Add new time group column:", ""),
            ui.input_action_button("add_time_group", "Add Time Group"),
            
            ui.output_text('time_intervals_text'),
            ui.output_ui("df_ui2"),
            ui.output_table("selected_ts_df"),
            ui.output_plot("time_series_plot"), 
        ),
        ui.nav_panel('Ideal Data format',
            ui.h2('Displays data from the last time data gen was run'),
            ui.output_table('fake_data_display')
        ),
        ui.nav_panel('info-',
            ui.h2(' features ')
        )
    ),
    ui.div(
        ui.input_dark_mode(),
        style="position: fixed; top: 10px; right: 10px; background-color: white; padding: 2px 5px; font-size: 12px; z-index: 1000;"
    ),
    ui.div(
        ui.output_text("display_info"),
        style="position: fixed; top: 50px; right: 10px; background-color: white; padding: 10px; border: 1px solid black; z-index: 1000;"
    )
)
# default values
default_valueset = pd.read_csv('valueset_data.csv')
default_country = "NewZealand"
time_groups = ['TIME_INTERVAL','TIMESTAMP','TIME']


def server(input, output, session):
    # load default values

    value_set = reactive.Value(default_valueset)
    country_choice = reactive.Value(default_valueset.columns.tolist()[1:])
    fake_data = pd.read_csv('fake_data.csv')
    patient_number = reactive.Value(int(10))
    time_intervals = reactive.Value(int(1))
    valid_time_groups = reactive.Value(time_groups) 

    # track the program status

    program_status = reactive.Value(None)
    app_initialized = reactive.Value(True)

    # track the data status

    raw_data = reactive.Value(pd.DataFrame())
    validated_data = reactive.Value(None) 
    util_added = reactive.Value(False)
    data_with_util = reactive.Value(None)
    filter_options = reactive.value([])
    filtered_data = reactive.Value(None)
    
    # store the processed data

    grouped_dfs = reactive.Value([])
    data_tables = reactive.Value({})  
    group_data_tables = reactive.Value({})
    time_series_tables = reactive.value({})

    # trigger other processes

    show_util = reactive.Value(0)
    run_filter = reactive.Value(0)
    show_filter = reactive.Value(0)
    trigger_process = reactive.Value(0)
    trigger_df1 = reactive.Value(0)
    activate_plot1 = reactive.Value(0)
    trigger_ts_process = reactive.Value(0)

    #set the selection menus

    groups = reactive.Value(['NO_GROUP_CHOSEN'])
    preserve_selection = reactive.Value(False)
    reverse_grouplist = reactive.Value(False)

    column_choices = reactive.Value(['None'])
    df_output_choices = reactive.Value(['No Dataframes Created'])
    ts_output_choices = reactive.Value(['No Time series Created'])
    
    new_text = reactive.Value("Filtered data - choose filter for data")

    @reactive.Effect
    @reactive.event(app_initialized)
    def start_program():
        program_status.set('INITIALIZED')
        print('App initialized')

        # INITIALIZED -> DATA_LOADED -> VALIDATED -> UTIL_ADDED -> CHECK_FILTER -> 
        # FILTER_APPLIED or NOFILTER_APPLIED -> READY_TO_PROCESS -> READY_TO_DISPLAY -> plots/data displayed
    
    @output
    @render.text
    @reactive.event(program_status)
    def program_status_debug():
        print('Current program status:',program_status.get())
        return

    @reactive.Effect
    @reactive.event(raw_data)
    def watch_raw_data():
        if not raw_data.get().empty:
            print('Raw data has been loaded')
            program_status.set('DATA_LOADED')

    @reactive.Effect
    @reactive.event(value_set)
    def watch_valueset():
        if not value_set.get().equals(default_valueset):
            if not raw_data.get().empty:
                print('New valueset has been loaded')
                program_status.set('VALIDATED')
            else:
                print('New valueset has been loaded, waiting for data')
        else:
            print('Default vaueset loaded')

    @output
    @render.ui
    def country_select_ui():
        return ui.input_select("country", "Select country:", choices=country_choice.get(),selected=default_country)
    
    @reactive.Effect
    @reactive.event(input.country)
    def watch_country():
        print('Country changed to:',input.country())
        if not raw_data.get().empty:
            program_status.set('VALIDATED') 
            #Dont need to re-validate the data when country is changed, but have to re-add utility
        return

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
            print(value_set.get().columns.tolist(),'the countrylist')
            country_choice.set(value_set.get().columns.tolist()[1:])
        print("Value set loaded:", value_set.get())  # Debugging statement
                
    @reactive.Effect
    @reactive.event(program_status)
    def extract_group_col():
        if program_status.get()=='VALIDATED':
            data = raw_data.get()
            if data is not None:
                columns = data.columns.tolist()
                column_choices.set(['None'] + columns)
                program_status.set('EXTRACTED')
                print('Group column extracted, column choices are',column_choices.get())

    @reactive.Effect
    @reactive.event(program_status)
    def validate_data():
        if program_status.get()=='DATA_LOADED':
            data = raw_data.get()
            if data is not None:
                res = Validator(data)
                validated_data.set(res.data)
                program_status.set('VALIDATED')
                print('Data validated')

    @reactive.Effect
    @reactive.event(input.patient_number)
    def update_patient_number():
        patient_number.set(input.patient_number())
        print(f"Patient number updated to: {patient_number.get()}")

    @reactive.Effect
    @reactive.event(input.time_intervals)
    def update_time_intervals():
        time_intervals.set(input.time_intervals())
        print(f"Time intervals updated to: {time_intervals.get()}")
    
    @reactive.Effect
    @reactive.event(input.generate_fake_data)
    def generate_data():
        num = int(input.patient_number())
        time_intervals = int(input.time_intervals())
        fake_data = Generator.generate_data(num, time_intervals)
        print(f'Fake data generated with {num} people, {time_intervals}, time intervals')
        raw_data.set(fake_data)
    
    @output
    @render.table
    @reactive.event(program_status)
    def rawdata_display():
        if program_status.get() !='INITIALIZED':
            df = raw_data.get()
            if df is not None:
                old_index = df.index.name if df.index.name else 'index'
                fixed_index = df.reset_index()
                fixed_index.rename(columns={'index': old_index}, inplace=True)
                return pd.DataFrame(fixed_index).head(10)
        return pd.DataFrame({"No data uploaded": ["Dataframe will display here when raw data is uploaded"]})

    @reactive.Effect
    @reactive.event(program_status)
    def set_util():
        if program_status.get()=='EXTRACTED':
            print('Adding utility to validated data')
            data = validated_data.get()
            values = value_set.get()
            country = input.country() or default_country
            if data is not None and values is not None and country:
                res = Eq5dvalue(data, values, country).calculate_util()
                data_with_util.set(res)
                print('Utility added')
                program_status.set('UTIL_ADDED')
            else:
                print('Error trying to set utility')
                util_added.set(False)
   
    @reactive.Effect
    @reactive.event(program_status)
    def trigger_util_display():
        dont_show_util = ['INITIALIZED','DATA_LOADED','EXTRACTED','VALIDATED']
        if program_status.get() in dont_show_util:
            show_util.set(0)
        elif program_status.get()=='UTIL_ADDED':
            show_util.set(show_util.get()+1)

    @output
    @render.table
    @reactive.event(show_util)
    def util_data_display():
        if show_util.get()>0:
            df = data_with_util.get()
            if df is not None:
                if 'UID' in df.columns:
                    df = df.sort_values(by='UID')
                print('Utility set and displaying successfully, checking filter')
                program_status.set('CHECK_FILTER')
                return pd.DataFrame(df).head(10)
        else:
            print('Not ready to display utility')
        return pd.DataFrame({"No validated data": ["Validated dataframe will display here when data is validated"]})
    
    @output
    @render.ui
    def filter_col_ui():
        return ui.input_select("filter_column", "Select column to filter by:", choices=column_choices.get(),selected='None')
    
    @reactive.Effect
    @reactive.event(program_status)
    def update_filter_col():
        if program_status.get()=='EXTRACTED':
            ui.update_select("filter_column", selected='None')
    
    @output
    @render.ui
    @reactive.event(filter_options)
    def filter_values_ui():
        column = input.filter_column()
        unique_values = filter_options.get()
        return ui.div(
        ui.div(
            ui.input_checkbox_group("filter_values", f"Filter by {column}:", choices=unique_values),
            style="display: inline-block; vertical-align: top;"
        ),
        ui.div(
            ui.input_action_button("select_all", "Select All/Deselect All"),
            style="display: inline-block; margin-left: 10px; vertical-align: top;"
        )
    )

    @reactive.Effect
    @reactive.event(input.filter_column)
    def update_filter_options():
        column = input.filter_column()
        if column and column != 'None':
            unique_values = data_with_util.get()[column].unique().tolist()
            filter_options.set(unique_values)
        
        elif column=='None':
            filter_options.set([])
            if program_status.get()=='READY_TO_PROCESS' or program_status.get()=='READY_TO_DISPLAY':
                program_status.set('NOFILTER_APPLIED')
        print('filter options have been updated to', filter_options.get())
    
    @reactive.Effect
    @reactive.event(input.select_all)
    def select_all_filter_values():
        #If not all selected, select all. Otherwise, select none.
        print('Select all button has been activated')
        column = input.filter_column()
        if column and column != 'None':
            unique_values = filter_options.get()
            current_selection = input.filter_values()

            if isinstance(unique_values[0], (int, float)):
                    unique_values = [str(v) for v in unique_values]
            if set(current_selection) == set(unique_values):
                ui.update_select("filter_values", selected='None')
            else:
                ui.update_select("filter_values", selected=unique_values)
        else:
            return
    
    @output
    @render.text
    @reactive.event(new_text)
    def filtered_data_heading():
        return new_text.get()
  
    @reactive.effect
    @reactive.event(input.filter_values,input.filter_column)
    def update_filter_heading():
        column = input.filter_column.get()
        value = input.filter_values.get()
        if column!='None' and value!='None':
            new_text.set(f"Filtered data - selection includes {value} members of {column} group ")
        else:
            new_text.set("Optional - select filter to display filtered data")

    @reactive.Effect
    @reactive.event(input.filter_values)
    def debug_filter_values():
        print('input.filter_values has been updated:', input.filter_values())
        if input.filter_values()!=():
            run_filter.set(run_filter.get()+1)
        elif input.filter_values()==():
            if program_status.get()=='FILTER_APPLIED' or program_status.get()=='READY_TO_PROCESS' or program_status.get()=='READY_TO_DISPLAY':
                if not raw_data.get().empty:
                    run_filter.set(run_filter.get()+1)

    @reactive.Effect
    @reactive.event(program_status)
    def activate_filter_check():
        if program_status.get()=='CHECK_FILTER':
            if not raw_data.get().empty:
                run_filter.set(run_filter.get()+1)
    
    @reactive.Effect
    @reactive.event(run_filter)
    def apply_filter():
        print('Applying filter')
        column = input.filter_column()
        value = input.filter_values()

        if column == 'None' or value == ():
            print('The column is None or the filter values are empty, not applying filter')
            filtered_data.set(data_with_util.get())
            program_status.set('NOFILTER_APPLIED')
            return

        if column!='None' and value:
            old_data = data_with_util.get()

            if old_data[column].dtype == 'float64' or old_data[column].dtype == 'int64':
                value = (float(v) for v in value)

            new_data = old_data[old_data[column].isin(value)]
            filtered_data.set(new_data)
            print('Filtered data has been created')
            program_status.set('FILTER_APPLIED')

    @reactive.Effect
    @reactive.event(program_status)
    def trigger_filter_display():
        dont_show_filter = ['DATA_LOADED','EXTRACTED','VALIDATED','UTIL_ADDED','NOFILTER_APPLIED']

        if program_status.get()=='FILTER_APPLIED':
            show_filter.set(show_filter.get()+1)

        elif program_status.get() in dont_show_filter:
            show_filter.set(0)
            return

    @output
    @render.table
    @reactive.event(show_filter)
    def filtered_data_display():
        if show_filter.get()>0:
            df = filtered_data.get()

            if df is None:
                program_status.set('NOFILTER_APPLIED')
                return pd.DataFrame({"No data available": ["Filtered dataframe will display here when data is filtered"]})
            
            if df is not None:
                if 'UID' in df.columns:
                    df = df.sort_values(by='UID')
                program_status.set('READY_TO_PROCESS')
                return pd.DataFrame(df).head(10)
        
        if not raw_data.get().empty and show_util.get()>0:
            program_status.set('READY_TO_PROCESS')
        return pd.DataFrame({"No data available": ["Filtered dataframe will display here when data is filtered"]})
    
    
    @reactive.Effect
    @reactive.event(program_status)
    def advance_prog():
        if program_status.get()=='NOFILTER_APPLIED':
            time.sleep(0.1)
            program_status.set('READY_TO_PROCESS')

    @reactive.Effect
    @reactive.event(program_status)
    def checkpoint():
        if program_status.get()=='READY_TO_PROCESS':
            print('***************** data loaded and filter applied successfully, ready for processing*************************')
        
    @output
    @render.ui
    @reactive.event(column_choices)
    def group_col_ui():
        return ui.input_select("group_column", "Group data By:", choices=column_choices.get())


    @reactive.Effect
    @reactive.event(input.group_column,program_status)
    def start_process():
        group_column = input.group_column()
        print(f"The grouping column has been set to: {group_column}")
        if program_status.get()=='READY_TO_PROCESS' or program_status.get()=='READY_TO_DISPLAY':
            trigger_process.set(trigger_process.get()+1)

    @reactive.Effect
    @reactive.event(reverse_grouplist)
    def watch_reverse_group():
        print('Reverse group toggled')
        if program_status.get()=='READY_TO_PROCESS' or program_status.get()=='READY_TO_DISPLAY':
            preserve_selection.set(True)
            trigger_process.set(trigger_process.get()+1)
        
    @reactive.Effect
    @reactive.event(trigger_process)
    def process_data():
        if program_status.get()=='READY_TO_PROCESS' or program_status.get()=='READY_TO_DISPLAY':
            print('Processing data')

            data = filtered_data.get()
            group_column = input.group_column()
            process = Processor(data,group_column)
            if reverse_grouplist.get():
                process = Processor(data,group_column,reverse_grouplist=True)
            else:
                process = Processor(data,group_column,reverse_grouplist=False)
            groups.set(process.group_list)
            groups_list = groups.get()

            if data is not None and (groups_list==['NO_GROUP_CHOSEN'] or len(groups_list)==1):

                processed = Processor(data,group_column='None')
                groups.set(processed.group_list)
                data_tables.set({
                    'simple_desc':processed.simple_desc(),
                    'binary_desc':processed.binary_desc(),
                    't10_index': processed.top_frequency(),
                    'data_LFS': processed.level_frequency_score(),
                    'health_state_density_curve':processed.health_state_density_curve(),
                })
                print("Data_tables updated",data_tables.get().keys())
            
            if data is not None and group_column!='None' and input.dataframe_select()!='None' and len(groups_list)>1:
                #grouping chosen for data analysis
                res = {}
                grouped_dfs.set(['simple_desc','binary_desc','top_frequency'])
                groups_wanted = grouped_dfs.get()
                all_dfs = Processor(data,group_column,reverse_grouplist=reverse_grouplist.get()).siloed_data

                res = {group_name: {groups_wanted[n]: df for n, df in enumerate([Processor(group_data).simple_desc(), Processor(group_data).binary_desc(), Processor(group_data).top_frequency()])} for group_name, group_data in all_dfs.items()}           
                hsdc_df = Processor(data,group_column).health_state_density_curve()
                #hscdf is a unique case since it is the same regardless of which group is selected, as the lines are layered on the same plot
                for group_name, group_data in res.items():
                    res[group_name]['health_state_density_curve'] = hsdc_df
                
                grouped_dfs.set(['simple_desc','binary_desc','top_frequency','health_state_density_curve'])
                group_data_tables.set(res)
            
            if data is not None and group_column in valid_time_groups.get() and input.dataframe_select()!='None' and len(groups_list)==2:
                #special case if the number of groups in column is exactly 2, can create the paretian dataframe
                group_tables = group_data_tables.get()
                try:
                    px_df = Processor(data, group_column,reverse_grouplist=reverse_grouplist.get()).paretian()
                    group_1 = groups_list[0]
                    group_2 = groups_list[1]
                    hpg = Processor(data,group_column,reverse_grouplist=reverse_grouplist.get()).hpg(px_df,group_1,group_2)

                except Exception as e:
                    print(f"Error trying to create paretian dataframe: {e}")
                else:
                    for group_name, group_data in all_dfs.items():
                        group_tables[group_name]['paretian/health_profile_grid'] = hpg
                    group_data_tables.set(group_tables)
                    grouped_dfs.set(['simple_desc','binary_desc','top_frequency','health_state_density_curve','paretian/health_profile_grid'])
            print('Processing successful, dataframes are created and ready to display')
        else:
            print('Group column was changed but not ready to process yet')
            return
        
    @output
    @render.ui
    @reactive.event(df_output_choices)
    def df_ui():
        return ui.input_select("dataframe_select", "Select df type:", choices=df_output_choices.get())
    
    @reactive.Effect
    @reactive.event(trigger_process)
    def update_dataframe_select():
        if preserve_selection.get():
            preserve_selection.set(False)
            return
        if input.group_column()=='None' or len(groups.get())==1:
            available_dfs = data_tables.get()
            df_output_choices.set(list(available_dfs))
        else:
            df_output_choices.set(grouped_dfs.get())
        print("Dataframe options updated:", df_output_choices.get())
        program_status.set('READY_TO_DISPLAY')


    @output
    @render.text
    @reactive.event(groups)
    def print_grouplist():
        out = groups.get()
        return f"Group list for selected group: {out}"
    
    @reactive.Effect
    @reactive.event(input.reverse_grouplist_checkbox)
    def update_reverse_grouplist():
        reverse_grouplist.set(input.reverse_grouplist_checkbox())
        print(f"Reverse Group List set to: {reverse_grouplist.get()}")


    @output
    @render.ui
    def group_options_ui():
        return ui.input_radio_buttons("group_options", "Select group to include in dataframe:", groups.get())
    
    @reactive.Effect
    @reactive.event(input.dataframe_select,program_status,input.group_options)
    def trigger_df():
        print(f"The df select has been set to: {input.dataframe_select.get()}")
        if program_status.get()=='READY_TO_DISPLAY':
            trigger_df1.set(trigger_df1.get()+1)
            
    @reactive.Effect
    @reactive.event(program_status,input.group_column,input.dataframe_select,groups)
    def trigger_plot():
        print(f"The plot has been set to: {input.dataframe_select.get()}")
        if program_status.get()=='READY_TO_DISPLAY':
            activate_plot1.set(activate_plot1.get()+1)

    @output
    @render.table
    @reactive.event(trigger_df1)
    def show_df1():
        if input.dataframe_select()=='No Dataframes Created':
            return

        if input.group_column()=='None' or len(groups.get())==1 or input.group_options.get()=='NO_GROUP_CHOSEN':
            tables = data_tables.get()
        else:
            table_list = group_data_tables.get()
            tables = table_list[input.group_options()]

        df = tables[input.dataframe_select()]

        if df is not None:
            old_index = df.index.name if df.index.name else 'index'
            fixed_index = df.reset_index()
            fixed_index.rename(columns={'index': old_index}, inplace=True)
            if 'UID' in fixed_index.columns:
                fixed_index = fixed_index.sort_values('UID')
            return pd.DataFrame(fixed_index).head(10)
        else:
            return pd.DataFrame({"No data uploaded": ["Dataframe will display here when raw data is uploaded"]})
        
        
    @output
    @render.plot
    @reactive.event(activate_plot1)
    def desc_plot():

        if input.dataframe_select()=='No Dataframes Created':
            return
        
        data = filtered_data.get()
        grouplist = groups.get()
        group_column = input.group_column()
        selected_df = input.dataframe_select()
        
        if grouplist == ['NO_GROUP_CHOSEN']:
            dfs = data_tables.get()
            print('selectd df is ',selected_df)
            if selected_df == 'simple_desc':
                processed = Processor(data)
                vis = Visualizer(processed.get_percent())
                fig = vis.histogram()

            elif selected_df == 'binary_desc':
                data = dfs['binary_desc']
                problems_df = data[['% problems']].copy()
                problems_df['%no problems'] = 100 - problems_df['% problems']
                vis = Visualizer(problems_df)
                fig = vis.histogram()

            elif selected_df == 'health_state_density_curve':
                data = dfs['health_state_density_curve']
                vis = Visualizer(data)
                fig = vis.health_state_density_curve()

            elif selected_df == 't10_index' or selected_df == 'data_LFS':
                print(' No plot available for t10 index or LFS')
                pass

        else:
            #the grouped plots
            if selected_df=='simple_desc':
                grouped_pct = {}
                siloed = Processor(data,group_column).siloed_data

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

            elif selected_df=='paretian/health_profile_grid':

                hpg = group_data_tables.get()[grouplist[0]]['paretian/health_profile_grid']
                vis = Visualizer(hpg)
                fig = vis.hpg()
        return fig
    
    @output
    @render.ui
    def group_col_ui_page3():
        return ui.input_select("ts_group_column", "Select Column containing time intervals:", choices=column_choices.get())
    
    @output
    @render.ui
    @reactive.event(ts_output_choices)
    def df_ui2():
        return ui.input_select("ts_select", "Select df type:", choices=ts_output_choices.get())
    
    @reactive.Effect
    @reactive.event(program_status,input.ts_group_column)
    def trigger_plot():
        print(f"The time column: {input.ts_group_column.get()}")
        if program_status.get()=='READY_TO_PROCESS' or program_status.get()=='READY_TO_DISPLAY':
            trigger_ts_process.set(trigger_ts_process.get()+1)


    @reactive.Effect
    @reactive.event(trigger_ts_process,valid_time_groups)
    def process_ts_data():
        print('actiating ts processor')
        if program_status.get()=='INITIALIZED':
            return

        groupcol = input.ts_group_column()
        valid_ts_columns = valid_time_groups.get()
        if groupcol not in valid_ts_columns:
            print('Invalid time column selected')
            ts_output_choices.set(['No Choice available'])
            return

        data = filtered_data.get()

        #I should probably raise value error here, but technically you can legally graph average scores between 2 groups without UID
        #However this uses the assumption that the groups contain the same patients, which is why it is probably good to assert a UID column
        if not 'UID' in data.columns:
            print('*** WARNING, creating timeseries with no UID')

        print('Generating timeseries data')

        if data is not None:
            processor = Processor(data,groupcol)
            wanted_ts = ['ts_delta_binary','avg_utility','avg_eqvas']
            res = {}
            for n, df in enumerate ( [processor.ts_binary(), processor.ts_utility(), processor.ts_eqvas()]):
                res[wanted_ts[n]] = df

            time_series_tables.set(res)
            ts_output_choices.set(wanted_ts)
            
    @output
    @render.table
    @reactive.event(input.ts_select)
    def selected_ts_df():
        selected_ts = input.ts_select()
        
        if selected_ts == 'No Time series Created':
            return pd.DataFrame({"Message": ["No time series selected"]})
        
        ts_data = time_series_tables.get().get(selected_ts)

        if ts_data is not None:

            ts_copy = ts_data.copy()

            old_index = ts_copy.index.name if ts_copy.index.name else 'index'
            fixed_index = ts_copy.reset_index()
            fixed_index.rename(columns={'index': old_index}, inplace=True)
            return pd.DataFrame(fixed_index).head(5)
        
        return pd.DataFrame({"Message": ["No data available"]})
    
    
    @output
    @render.plot
    @reactive.event(input.ts_select, time_series_tables)
    def time_series_plot():
        selected_ts = input.ts_select()
        
        if selected_ts == 'No Time series Created':
            return plt.figure()
        
        ts_data = time_series_tables.get().get(selected_ts)
        if ts_data is not None:
            vis = Visualizer(ts_data)
            fig = vis.time_series() 
            return fig
        
        return plt.figure()
    
    
    @reactive.Effect
    @reactive.event(input.add_time_group)
    def add_time_group():
        new_group = input.new_time_group()
        if new_group and new_group not in valid_time_groups.get():
            valid_time_groups.set(valid_time_groups.get() + [new_group])
            print(f"Added new time group: {new_group}")
            print(f"Updated valid time groups: {valid_time_groups.get()}")

    @output
    @render.text
    @reactive.event(input.ts_group_column,valid_time_groups)
    def time_intervals_text():

        group_col = input.ts_group_column()
        if group_col not in valid_time_groups.get():
            return "Invalid time grouping selection"
        
        if group_col:
            data = filtered_data.get()
            if data is not None:
                time_groups = Processor(data, group_col).group_list
                return f"Time intervals found in selected column: {time_groups}"
    
    @output
    @render.text
    def time_group_list():
        return f"Valid time groups: {', '.join(valid_time_groups.get())}"
    
    @output
    @render.table
    def fake_data_display():
        return fake_data
    
    @output
    @render.text
    def display_info():
        return f"Selected Country: {input.country()}, Program status: {program_status.get()}"
    
# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
