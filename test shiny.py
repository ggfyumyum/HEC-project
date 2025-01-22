from shiny import App, ui, render, reactive

# Define the UI
app_ui = ui.page_fluid(
    ui.h2("Checkbox Group Example"),
    ui.input_checkbox_group("checkbox_group", "Select options:", choices=["Option 1", "Option 2", "Option 3"]),
    ui.input_action_button("clear_button", "Clear Selection"),
    ui.output_text("selected_values")
)

# Define the server logic
def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.clear_button)
    def clear_selection():
        print("Clear button pressed")
        ui.update_checkbox_group("checkbox_group", selected=[])
        print("Checkbox group cleared")

    @output
    @render.text
    @reactive.event(input.checkbox_group)
    def selected_values():
        selected = input.checkbox_group()
        print("Current selected values:", selected)
        return f"Selected values: {selected}"

# Create the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()