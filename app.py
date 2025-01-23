
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import time

from data_validation import Validator
from data_analysis import Processor
from data_vizualisation import Visualizer  # Import the Visualizer class
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
                    ui.output_ui("country_select_ui"),
                    ui.input_file("valueset_input", "Upload valueset (default valueset already loaded)"),
                    ui.input_file("raw_input", "Upload raw data to be analysed"),
                    ui.input_action_button("generate_fake_data", "Click to generate Fake Data with the following parameters:"),
                    ui.output_ui('fas'),
                    ui.br(),
                    ui.br(),
                    ui.row(
                        ui.column(6, ui.input_select("patient_number", "Number of patients:", choices=[10**i for i in range(1, 11)], selected=10)),
                        ui.column(6, ui.input_select("time_intervals", "Number of time intervals:", choices=list(range(1, 11)), selected=1))
                    ),
                    ui.output_ui('filter_col_ui'),
                    ui.output_ui("filter_values_ui")
                ),
                ui.column(7,  # Right two-thirds of the page
                    ui.h2("Raw data"),
                    ui.output_table('rawdata_display'),
                    ui.h2("DATA WITH UTIL"),
                    ui.output_table("util_data_display"),
                    ui.h2(ui.output_text("filtered_data_heading")),
                    ui.output_table("filtered_data_display")
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
            #ui.output_text("hello_text"),
            ui.output_table("show_df1"),
            ui.output_plot("desc_plot"),
  # New table area for selected dataframe
        ),
        ui.nav_panel("Time-series analysis",
            ui.h2("Display table/plots of the change over time with n time intervals"),
            
            ui.output_ui("group_col_ui_page3"),
            
            #ui.input_text("new_time_group", "Add new time group column:", ""),
            #ui.input_action_button("add_time_group", "Add Time Group"),
            #ui.output_text("time_group_list"),
 
            #ui.output_ui("df_ui2"),
            #ui.output_plot("time_series_plot"),  # Existing plot area
            #ui.output_table("selected_ts_df")
        )
    )
)
# Define the server logic
default_valueset = pd.read_csv('valueset_data.csv')
default_country = "NewZealand"

def server(input, output, session):

    value_set = reactive.Value(default_valueset)
    country_choice = reactive.Value(default_valueset.columns.tolist()[1:])
    country_chosen = reactive.Value(False)

    raw_data = reactive.Value(pd.DataFrame())
    validated_data = reactive.Value(None)  # Reactive value to store validated data
    data_with_util = reactive.Value(None)
    filtered_data = reactive.Value(None)

    filter_applied = reactive.Value(False)
   

    grouped_dfs = reactive.Value([])
    data_tables = reactive.Value({})  # Reactive value to store data tables
    group_data_tables = reactive.Value({})
    time_series_tables = reactive.value({})

    groups = reactive.Value(['NO_GROUP_CHOSEN'])

    #if user tries to group by something that is not in this list, or create timeseries from a different column, it will not work
    valid_time_groups = reactive.Value(['TIME_INTERVAL','TIMESTAMP','TIME']) 
    


    column_choices = reactive.Value(['None'])
    df_output_choices = reactive.Value(['No Dataframes Created'])
    ts_output_choices = reactive.Value(['No Time series Created'])

    filter_options = reactive.value([])
    filter_values = reactive.Value([])

    patient_number = reactive.Value(int(10))
    time_intervals = reactive.Value(int(1))

    app_initialized = reactive.Value(True)
    display_ftext = reactive.Value(False)
    new_text = reactive.Value("Filtered data - choose filter for data")

    ready_to_display_df1=reactive.Value(False)
    ready_to_apply_filter = reactive.Value(False)

    program_status = reactive.Value(None)

    util_added = reactive.Value(False)
    ready_to_validate = reactive.Value(False)
    validation_status = reactive.Value(False)  # Reactive value to track validation status
    ready_to_process = reactive.Value(False)

    show_util = reactive.Value(0)
    run_filter = reactive.Value(0)
    show_filter = reactive.Value(0)
    trigger_process = reactive.Value(0)
    trigger_df1 = reactive.Value(0)
    activate_plot1 = reactive.Value(0)

    

    
    @output
    @render.text
    @reactive.event(program_status)
    def fas():
        print('program status updated',program_status.get())
        return 'rogram status updated',program_status.get()

    
    @reactive.Effect
    @reactive.event(app_initialized)
    def set_program_status():
        program_status.set('INITIAL')
        print('app has been initialized')

        # DATA_LOADED -> validated -> util added -> filterered/not -> ready to process
        #each of the later functions first checks ready to process, does absolutely nothing if not
        #whenever a change happens before ready to process, we need to change status back

    @reactive.Effect
    @reactive.event(raw_data)
    def watch_raw_data():

        if not raw_data.get().empty:
            print('a change in raw data')
            program_status.set('DATA_LOADED')

    @reactive.Effect
    @reactive.event(input.country)
    def watch_country():
        print('country has been changed to',input.country())
        if not raw_data.get().empty:
            program_status.set('VALIDATED')
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
            print("new raw data loaded")
            print('running groupcol extraction')
            data = raw_data.get()
            if data is not None:
                columns = data.columns.tolist()
                column_choices.set(['None'] + columns)
                program_status.set('EXTRACTED')
                print('ready to validate, column choices are',column_choices.get())

    @reactive.Effect
    @reactive.event(program_status)
    def validate_data():
        if program_status.get()=='DATA_LOADED':
            print('Running validation')
            data = raw_data.get()
            if data is not None:
                res = Validator(data)
                validated_data.set(res.data)
                program_status.set('VALIDATED')# Set validation status to True
                print('Validation has been set true')

    
    @reactive.Effect
    @reactive.event(input.generate_fake_data)
    def generate_data():
        num = int(input.patient_number())
        time_intervals = int(input.time_intervals())
        print(num,time_intervals,'params')
        fake_data = Generator.generate_data(num, time_intervals)
        print('generated data and sent to raw data')
        raw_data.set(fake_data)

    # Set default values
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

    @output
    @render.ui
    def country_select_ui():
        return ui.input_select("country", "Select country:", choices=country_choice.get(),selected=default_country)
    
    
    @output
    @render.table
    @reactive.event(program_status)
    def rawdata_display():
        if program_status.get() !='INITIAL':
            df = raw_data.get()
            if df is not None:
                old_index = df.index.name if df.index.name else 'index'
                fixed_index = df.reset_index()
                fixed_index.rename(columns={'index': old_index}, inplace=True)
                return pd.DataFrame(fixed_index).head(3)
        return pd.DataFrame({"No data uploaded": ["Dataframe will display here when raw data is uploaded"]})

    
    @reactive.Effect
    @reactive.event(program_status)
    def set_util():
        if program_status.get()=='EXTRACTED':
            print('validation status is validated, now setting util')
            data = validated_data.get()
            values = value_set.get()
            country = input.country() or default_country
            if data is not None and values is not None and country:
                res = Eq5dvalue(data, values, country).calculate_util()
                data_with_util.set(res)
                print('ive just set the data with util')
                program_status.set('UTIL_ADDED')
            else:
                print('there was an error, I have not set the util')
                util_added.set(False)
    
   
    @reactive.Effect
    @reactive.event(program_status)
    def trigger_util_display():

        dont_show_util = ['INITIAL','DATA_LOADED','EXTRACTED','VALIDATED']
        if program_status.get() in dont_show_util:
            show_util.set(0)
        elif program_status.get()=='UTIL_ADDED':
        #if program_status.get()=='UTIL_ADDED':
            show_util.set(show_util.get()+1)
            print('util display triggered')

    @output
    @render.table
    @reactive.event(show_util)
    def util_data_display():
        print('received trigger to show util')
        if show_util.get()>0:
            df = data_with_util.get()
            if df is not None:
                df = df.sort_values(by='UID')
                print('util should be displaying, setting program to CHECK_FILTER')
                program_status.set('CHECK_FILTER')
                return pd.DataFrame(df).head(5)
        else:
            print('not ready to show util yet..')
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
        print('filter column has changed, im now resetting the filter values')
        column = input.filter_column()

        if column and column != 'None':
            unique_values = data_with_util.get()[column].unique().tolist()
            filter_options.set(unique_values)
        
        elif column=='None':
            filter_options.set([])

            print('column is none!, do nothing')
            print('the current program status',program_status.get())
            if program_status.get()=='RTP' or program_status.get()=='READY_TO_DF1':
                program_status.set('NOFILTER_APPLIED')
            #new_text.set("Filtered data - choose filter for data")

        print('fi;ter options have been updated to', filter_options.get())

    
    
    @reactive.Effect
    @reactive.event(input.select_all)
    def select_all_filter_values():
        print('select all button has been activated')
        column = input.filter_column()
        if column and column != 'None':
            unique_values = filter_options.get()
            print('choices', unique_values)
            current_selection = input.filter_values()
            print('the current selctoin is',current_selection)
        
            if isinstance(unique_values[0], (int, float)):
                    unique_values = [str(v) for v in unique_values]

            if set(current_selection) == set(unique_values):
                print('all seelcted, so deselcting all')
                #ui.update_checkbox_group("filter_values", selected=[])
                ui.update_select("filter_values", selected='None')
            else:
                print('not all selected, so filling all values')
                #ui.update_checkbox_group("filter_values", selected=unique_values)
                ui.update_select("filter_values", selected=unique_values)
        else:
            print('column is none!')
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
            new_text.set("Filtered data - choose filter for data")

    @reactive.Effect
    @reactive.event(input.filter_values)
    def debug_filter_values():
        print('input.filter_values has been updated:', input.filter_values())
        if input.filter_values()!=():
            print('found something')
            run_filter.set(run_filter.get()+1)
        elif input.filter_values()==():
            if program_status.get()=='FILTER_APPLIED' or program_status.get()=='RTP' or program_status.get()=='READY_TO_DF1':
                print('found nothing')
                if not raw_data.get().empty:
                    run_filter.set(run_filter.get()+1)

    @reactive.Effect
    @reactive.event(program_status)
    def activate_filter_check():
        if program_status.get()=='CHECK_FILTER':
            print('sending pulse to check the filter')
            if not raw_data.get().empty:
                run_filter.set(run_filter.get()+1)
    
    @reactive.Effect
    @reactive.event(run_filter)
    def apply_filter():
        print('applying filter')
        column = input.filter_column()
        value = input.filter_values()

        print('ive found what the coluimn and value are', column, value)

        if column == 'None':
            print('detected that the columns is none')
            filtered_data.set(data_with_util.get())
            program_status.set('NOFILTER_APPLIED')
            return

        if value == ():
            print('no values selected, so not applying a filter!')
            filtered_data.set(data_with_util.get())
            program_status.set('NOFILTER_APPLIED')
            return

        print('values',value,'column is',column)

        if column!='None' and value:
            old_data = data_with_util.get()
            print('the column is',column,'the data im allowing',value)
            #print('Data types of the columns:', old_data.dtypes)
            print('Unique values in the column:', old_data[column].unique())

            if old_data[column].dtype == 'float64' or old_data[column].dtype == 'int64':
                value = (float(v) for v in value)

            new_data = old_data[old_data[column].isin(value)]
            filtered_data.set(new_data)
            print('filtered data has been created')
            program_status.set('FILTER_APPLIED')


    @reactive.Effect
    @reactive.event(program_status)
    def trigger_filter_display():
        dont_show_filter = ['DATA_LOADED','EXTRACTED','VALIDATED','UTIL_ADDED','NOFILTER_APPLIED']

        if program_status.get()=='FILTER_APPLIED':
            print('im sending show filter trigger')
            show_filter.set(show_filter.get()+1)

        elif program_status.get() in dont_show_filter:
            show_filter.set(0)
            return


    @output
    @render.table
    @reactive.event(show_filter)
    def filtered_data_display():
        print('i been triggered, show filter is',show_filter.get())
        if show_filter.get()>0:
            print('Running filtered_data_display')
            df = filtered_data.get()

            if df is None:
                program_status.set('NOFILTER_APPLIED')
                return pd.DataFrame({"No data available": ["Filtered dataframe will display here when data is filtered"]})
            
            if df is not None:
                print('THELAST****************************************************************')
                df = df.sort_values(by='UID')
                print('a filtered table has been found successfully, now setting program to the next step')
                program_status.set('RTP')
                return pd.DataFrame(df).head(5)
        
        if not raw_data.get().empty and show_util.get()>0:
            print(' i am now ready to process')
            program_status.set('RTP')
        return pd.DataFrame({"No data available": ["Filtered dataframe will display here when data is filtered"]})
    
    
    @reactive.Effect
    @reactive.event(program_status)
    def advance_prog():
        if program_status.get()=='NOFILTER_APPLIED':
            time.sleep(0.2)
            program_status.set('RTP')

    @reactive.Effect
    @reactive.event(program_status)
    def checkpoint_1():
        if program_status.get()=='RTP':
            print('ready to advance to next stage')
        

    @output
    @render.ui
    @reactive.event(column_choices)
    def group_col_ui():
        return ui.input_select("group_col", "Group data By:", choices=column_choices.get())
    
    
    @reactive.Effect
    @reactive.event(input.group_col,program_status)
    def start_process():
        group_c = input.group_col()
        print(f"The group_col has been set to: {group_c}")
        if program_status.get()=='RTP' or program_status.get()=='READY_TO_DF1':
            trigger_process.set(trigger_process.get()+1)
        

    
    @reactive.Effect
    @reactive.event(trigger_process)
    def process_data():
        if program_status.get()=='RTP' or program_status.get()=='READY_TO_DF1':
            print('Trying to process data')
            data = filtered_data.get()
            # Check if validation was successful
            print('got the data')
            group_c = input.group_col()
            #country = input.country() or default_country
            #values = value_set.get()
            print('got group c')
            groups.set(Processor(data,group_c).group_list)

            groups_list = groups.get()
            print('groups is ',groups_list)

            if data is not None and groups_list==['NO_GROUP_CHOSEN'] or len(groups_list)==1:
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

                res = {group_name: {groups_wanted[n]: df for n, df in enumerate([Processor(group_data).simple_desc(), Processor(group_data).binary_desc(), Processor(group_data).top_frequency()])} for group_name, group_data in all_dfs.items()}           
                hsdc_df = Processor(data,group_c).health_state_density_curve()
                for group_name, group_data in res.items():
                    res[group_name]['health_state_density_curve'] = hsdc_df
                
                grouped_dfs.set(['simple_desc','binary_desc','top_frequency','health_state_density_curve'])
                group_data_tables.set(res)
            
            if data is not None and group_c in valid_time_groups.get() and input.dataframe_select()!='None' and len(groups_list)==2:
                
                final = group_data_tables.get()

                try:
                    px_df = Processor(data, group_c).paretian()
                    group1 = groups_list[0]
                    group2 = groups_list[1]

                    hpg = Processor(data,group_c).hpg(px_df,group1,group2)

                except Exception as e:
                    print(f"Error creating paretian dataframe: {e}")
                else:
                    print('trying to make  hpg ')

                    for group_name, group_data in all_dfs.items():
                        final[group_name]['paretian/health_profile_grid'] = hpg

                    group_data_tables.set(final)
                    grouped_dfs.set(['simple_desc','binary_desc','top_frequency','health_state_density_curve','paretian/health_profile_grid'])

            print('looks like processing was sucessful, now setting readyt o display')
            
        else:
            print('i aint processing, wrong status')
            return
        

    
    @output
    @render.ui
    @reactive.event(df_output_choices)
    def df_ui():
        print('df_ui is updated')
        return ui.input_select("dataframe_select", "Select df type:", choices=df_output_choices.get())
    
    
    @reactive.Effect
    @reactive.event(trigger_process)
    def update_dataframe_select():
        print('updating df select based on gorup col')
        #print('data tables is', data_tables.get(), 'grouped dfs is',grouped_dfs.get())
        if input.group_col()=='None' or len(groups.get())==1:
            print('set it to the whole list options')
            k = data_tables.get()
            #print(k,'jqwehjqe')
            df_output_choices.set(list(k))
            print("Df_output_choices has been updated to:", df_output_choices.get())
        else:
            df_output_choices.set(grouped_dfs.get())

        print("Dataframe options updated:", df_output_choices.get())
        program_status.set('READY_TO_DF1')

    @output
    @render.text
    def print_grouplist():
        out = groups.get()
        return f"Group list for selected group: {out}"
    
    
    @output
    @render.ui
    def group_options_ui():
        return ui.input_radio_buttons("group_options", "Select Group to display:", groups.get())
    

    @reactive.Effect
    @reactive.event(input.dataframe_select,program_status)
    def trigger_df():
        print(f"The df select has been set to: {input.dataframe_select.get()}")
        if program_status.get()=='READY_TO_DF1':
            trigger_df1.set(trigger_df1.get()+1)
            activate_plot1.set(activate_plot1.get()+1)
    
    @reactive.Effect
    @reactive.event(program_status,input.group_col)
    def trigger_plot():
        print(f"The plot has been set to: {input.dataframe_select.get()}")
        if program_status.get()=='READY_TO_DF1':
            activate_plot1.set(activate_plot1.get()+1)

    @output
    @render.table
    @reactive.event(trigger_df1)
    def show_df1():
        print('seems ready to display now')
        
        if input.dataframe_select()=='No Dataframes Created':
            print('nothing is created, not ready yet')
            return

        if input.group_col()=='None' or len(groups.get())==1 or input.group_options.get()=='NO_GROUP_CHOSEN':
            print('fetching tables from big list',data_tables.get())
            tables = data_tables.get()
        else:
            table_list = group_data_tables.get()
  
            tables = table_list[input.group_options()]

        df = tables[input.dataframe_select()]

        if df is not None:
            old_index = df.index.name if df.index.name else 'index'
            fixed_index = df.reset_index()
            fixed_index.rename(columns={'index': old_index}, inplace=True)
            return pd.DataFrame(fixed_index).head(3)
        else:
            return pd.DataFrame({"No data uploaded": ["Dataframe will display here when raw data is uploaded"]})
        
        
        
    
    @output
    @render.plot
    @reactive.event(activate_plot1)
    
    def desc_plot():
        print('RUNNING PLOTTING FUNCTION*********************')
        '''
            #if something
            #print('not ready to display yet!')
        
        '''

        if input.dataframe_select()=='No Dataframes Created':
            print('nothing is created, not ready to plotyet')
            return
        
        data = filtered_data.get()
        grouplist = groups.get()
        group_c = input.group_col()
        selected_df = input.dataframe_select()
        
        if grouplist == ['NO_GROUP_CHOSEN']:
            dfs = data_tables.get()
            #print('NO GROUP CHOSEN YET, data tables is ',dfs)
            print('selectd df is ',selected_df)
            if selected_df == 'simple_desc':
                print('creating simpledesc')
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
                # Placeholder for t10_index plot
                pass

        else:
            if selected_df=='simple_desc':
                grouped_pct = {}
                siloed = Processor(data,group_c).siloed_data

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
        return ui.input_select("group_col_page3", "Select Column containing time intervals:", choices=column_choices.get())
    
    
    '''
    @output
    @render.ui
    @reactive.event(ts_output_choices)
    def df_ui2():
        print('change in ts output choices detected, new ts out put choiuces are ',ts_output_choices.get())
        return ui.input_select("ts_select", "Select df type:", choices=ts_output_choices.get())
    
    @reactive.Effect
    @reactive.event(ready_to_process,input.group_col_page3)
    def process_ts_data():
        print('actiating ts processor')
        if not ready_to_process.get():
            print('not ready to process TS data yet')

        groupcol = input.group_col_page3()
        valid_ts_columns = valid_time_groups.get()
        if groupcol not in valid_ts_columns:
            print('invalid time column selected')
            print('changing it to zero')
            ts_output_choices.set(['No Choice available'])
            return

        print('generating timeseries data')

        if filter_applied.get():
            data = filtered_data.get()
        else: 
            data = data_with_util.get()

        if data is not None:
            processor = Processor(data,groupcol)
            wanted_ts = ['ts_delta_binary','avg_utility','avg_eqvas']
            res = {}
            for n, df in enumerate ( [processor.ts_binary(), processor.ts_utility(), processor.ts_eqvas()]):
                res[wanted_ts[n]] = df

            time_series_tables.set(res)
            print('im boutt achange it')
            ts_output_choices.set(wanted_ts)

            
        print('within process ts data, ts output choiuces has been modified to',ts_output_choices.get())

    
    @output
    @render.text
    @reactive.event(input.group_col_page3,input.country,input.add_time_group)
    def time_intervals_text():
        group_col = input.group_col_page3()
        if group_col!='TIME_INTERVAL':
            return "Invalid time grouping selection"
        
        if group_col:
            data = data_with_util.get()
            if data is not None:
                time_groups = Processor(data, group_col).group_list
                return f"Time intervals found in selected column: {time_groups}"
    
    @output
    @render.plot
    @reactive.event(input.ts_select, time_series_tables)
    def time_series_plot():
        print('running timeseries plot')
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
    @reactive.event(input.ts_select)
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

            return pd.DataFrame(fixed_index).head(3)
        
        return pd.DataFrame({"Message": ["No data available"]})
    
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
    def time_group_list():
        return f"Valid time groups: {', '.join(valid_time_groups.get())}"

'''


# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
