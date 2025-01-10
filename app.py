import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from data_validation import Validator
from data_analysis import Processor
from data_vizualisation import visualizer
from eq5d_profile import eq5dvalue
from eq5d_decrement_processing import decrement_processing

from shiny import reactive
from shiny.express import input, ui, render

ui.input_slider("val", "Slider label", min=0, max=100, value=50)

ui.input_text("text", label="Enter some text")

data = ui.input_file(
    'datafile',
    'Upload xl file',
    multiple=False,
    accept=['.csv'],
    button_label='Browse...',
    placeholder='No file selected',
    capture=None,
)
data

@render.text
def slider_val():
    return f"Slider valsss: {input.val()}"

#rsconnect add --account ggfyumyum --name ggfyumyum --token 7786280A193F55618C6EE283771D22A9 --secret uapcUJM9pCePsljUVYZX1zgTaSZKX7koVsSxSSpm
print('just testing!')
