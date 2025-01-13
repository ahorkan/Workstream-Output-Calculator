import pandas as pd
import numpy as np
import panel as pn
import os
import sys

pn.extension()

# Determine if the script is running in a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # If running in a bundle, use the PyInstaller temp directory
    script_dir = sys._MEIPASS
else:
    # If running normally, use the script directory
    script_dir = os.path.dirname(__file__)

# Construct the full path to the data directory
data_dir = os.path.join(script_dir, 'data')

scope = ['NBFF Storefronts','ROSE Reviews','US Admin','Hitched/CA Lites Storefronts','Hitched/CA Lites Admin','Missing Attributes (US)','Ad Units (Creation)','360 Virtual Tours']

# Use the full path to read the CSV files
nbff_storefronts_hours = pd.read_csv(os.path.join(data_dir, 'nbff_storefronts_hours.csv'))
nbff_storefronts_output = pd.read_csv(os.path.join(data_dir, 'nbff_storefronts_output.csv'))
rose_reviews_hours = pd.read_csv(os.path.join(data_dir, 'rose_reviews_hours.csv'))
rose_reviews_output = pd.read_csv(os.path.join(data_dir, 'rose_reviews_output.csv'))
us_admin_hours = pd.read_csv(os.path.join(data_dir, 'us_admin_hours.csv'))
us_admin_output = pd.read_csv(os.path.join(data_dir, 'us_admin_output.csv'))
hitched_ca_lites_storefronts_hours = pd.read_csv(os.path.join(data_dir, 'hitched_ca_lites_storefronts_hours.csv'))
hitched_ca_lites_storefronts_output = pd.read_csv(os.path.join(data_dir, 'hitched_ca_lites_storefronts_output.csv'))
hitched_ca_lites_admin_hours = pd.read_csv(os.path.join(data_dir, 'hitched_ca_lites_admin_hours.csv'))
hitched_ca_lites_admin_output = pd.read_csv(os.path.join(data_dir, 'hitched_ca_lites_admin_output.csv'))
missing_attributes_us_hours = pd.read_csv(os.path.join(data_dir, 'missing_attributes_us_hours.csv'))
missing_attributes_us_output = pd.read_csv(os.path.join(data_dir, 'missing_attributes_us_output.csv'))
ad_units_creation_hours = pd.read_csv(os.path.join(data_dir, 'ad_units_creation_hours.csv'))
ad_units_creation_output = pd.read_csv(os.path.join(data_dir, 'ad_units_creation_output.csv'))
virtual_tours_hours = pd.read_csv(os.path.join(data_dir, 'virtual_tours_hours.csv'))
virtual_tours_output = pd.read_csv(os.path.join(data_dir, 'virtual_tours_output.csv'))

workstream_data = {
    'NBFF Storefronts': (nbff_storefronts_hours, nbff_storefronts_output),
    'ROSE Reviews': (rose_reviews_hours, rose_reviews_output),
    'US Admin': (us_admin_hours, us_admin_output),
    'Hitched/CA Lites Storefronts': (hitched_ca_lites_storefronts_hours, hitched_ca_lites_storefronts_output),
    'Hitched/CA Lites Admin': (hitched_ca_lites_admin_hours, hitched_ca_lites_admin_output),
    'Missing Attributes (US)': (missing_attributes_us_hours, missing_attributes_us_output),
    'Ad Units (Creation)': (ad_units_creation_hours, ad_units_creation_output),
    '360 Virtual Tours': (virtual_tours_hours, virtual_tours_output)
}

def calculate_output(workstream, hours=None, output=None):
    hours_data, output_data = workstream_data[workstream]
    
    # Convert columns to numeric, coercing errors to NaN
    hours_data = hours_data.apply(pd.to_numeric, errors='coerce')
    output_data = output_data.apply(pd.to_numeric, errors='coerce')

    # Drop columns that couldn't be converted to numeric
    hours_data = hours_data.dropna(axis=1, how='all')
    output_data = output_data.dropna(axis=1, how='all')

    # Align the indices of both Series
    hours_mean = hours_data.mean()
    output_mean = output_data.mean()
    common_index = hours_mean.index.intersection(output_mean.index)

    # Define x and y for the plot
    x = hours_mean[common_index]
    y = output_mean[common_index]

    # Fit a linear model
    coefficients = np.polyfit(x, y, 1)
    poly = np.poly1d(coefficients)

    if hours is not None:
        # Calculate the predicted output
        predicted_output = poly(hours)

        # Calculate the IQR of the output
        q1 = y.quantile(0.25)
        q3 = y.quantile(0.75)
        iqr = q3 - q1

        # Calculate the output range
        output_upper = predicted_output + iqr
        output_lower = max(predicted_output - iqr, 0)

        return {
            'Predicted Output': predicted_output,
            'Output Upper': output_upper,
            'Output Lower': output_lower
        }
    elif output is not None:
        # Calculate the required hours
        required_hours = np.ceil((output - coefficients[1]) / coefficients[0])

        # Calculate the IQR of the hours
        q1 = x.quantile(0.25)
        q3 = x.quantile(0.75)
        iqr = q3 - q1

        # Calculate the hours range
        hours_upper = required_hours + iqr
        hours_lower = max(required_hours - iqr, 0)

        return {
            'Required Hours': required_hours,
            'Hours Upper': hours_upper,
            'Hours Lower': hours_lower
        }

# Create dropdown menu for workstream selection
workstream_dropdown = pn.widgets.Select(name='Workstream', options=scope)

# Create dropdown menu for input type selection
input_type_dropdown = pn.widgets.Select(name='Input Type', options=['Select Input Type', 'Hours', 'Output'])

# Create input box for hours
hours_input = pn.widgets.FloatInput(name='Hours', value=1.0, visible=False, step=1)

# Create input box for output
output_input = pn.widgets.FloatInput(name='Output', value=1.0, visible=False, step=1)

# Create output area
output_area = pn.pane.HTML()

def update_output(event=None):
    workstream = workstream_dropdown.value
    input_type = input_type_dropdown.value

    if input_type == 'Output':
        output = output_input.value
        result = calculate_output(workstream, output=output)
        # Round down the required hours and convert to integers
        result['Required Hours'] = np.ceil(result['Required Hours']).astype(int)
        result['Hours Upper'] = np.ceil(result['Hours Upper']).astype(int)
        result['Hours Lower'] = np.ceil(result['Hours Lower']).astype(int)

        output_text = f"""
                        <h3>Required Hours for {output} output in {workstream}</h3>
                            <table>
                                <tr>
                                    <th>Required Hours</th>
                                    <td>{result['Required Hours']}</td>
                                </tr>
                                <tr>
                                    <th>Hours Range</th>
                                    <td>{result['Hours Lower']} - {result['Hours Upper']}</td>
                                </tr>
                            </table>
                        """
    else:
        hours = hours_input.value
        result = calculate_output(workstream, hours=hours)
        # Round down the predicted outputs and convert to integers
        result['Predicted Output'] = np.floor(result['Predicted Output']).astype(int)
        result['Output Upper'] = np.floor(result['Output Upper']).astype(int)
        result['Output Lower'] = np.floor(result['Output Lower']).astype(int)

        # Display the hours as int if it is an integer, otherwise as float
        if isinstance(hours, float) and hours.is_integer():
            hours = int(hours)

        output_text = f"""
                        <h3>Predicted Output for {hours} hours in {workstream}</h3>
                            <table>
                                <tr>
                                    <th>Predicted Output</th>
                                    <td>{result['Predicted Output']}</td>
                                </tr>
                                <tr>
                                    <th>Output Range</th>
                                    <td>{result['Output Lower']} - {result['Output Upper']}</td>
                                </tr>
                            </table>
                        """
    output_area.object = output_text

def toggle_input_fields(event):
    input_type = input_type_dropdown.value
    if input_type == 'Hours':
        hours_input.visible = True
        output_input.visible = False
    else:
        hours_input.visible = False
        output_input.visible = True

# Create button to calculate output
calculate_button = pn.widgets.Button(name='Calculate', button_type='primary')
calculate_button.on_click(lambda event: update_output())

# Update output on input type, hours, or output input change
input_type_dropdown.param.watch(toggle_input_fields, 'value')
hours_input.param.watch(update_output, 'value')
output_input.param.watch(update_output, 'value')

# Display widgets
layout = pn.Column(workstream_dropdown, input_type_dropdown, hours_input, output_input, calculate_button, output_area)

# Create a template and add the layout to the main area
template = pn.template.MaterialTemplate(title="Workstream Output Calculator")
template.main.append(layout)

# Serve the application
pn.serve(template)