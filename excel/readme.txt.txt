This folder contains an Excel file and instructions to help you retrieve existing KPIs from your PTV Flows instance and query the Historical Data Analysis (HDA) module.

## Files

- **`20250131 HDA Heatmap Example.xlsx`**: An Excel file that allows you to retrieve the existing KPIs of your PTV Flows instance via scripts and query the Historical Data Analysis (HDA) module for specific KPI detailed results, creating a heatmap for the specified date range.

## Prerequisites

- Microsoft Excel
- PTV Flows API Key

## Instructions:

- Insert your own API key and the KPI ID once you have downloaded the KPI definitions (name, KPI ID) by pressing the "Get All KPIs" button.
- Select a date range that is a maximum of 24 hours.
- Remember that the time is in UTC.
- by pressing the "Get HDA DETAILED data" button download the detailed data
- by pressing the "Create heatmap" button you create the heatmap in  the HEATMAP tab

## Notes

- Ensure that macros and external data connections are enabled in Excel to allow the scripts to run.
- The Excel file is designed to work with PTV Flows APIs, so an active internet connection is required.
- If you encounter any issues, please check your API key and KPI ID for accuracy.

## Additional Resources

- For more information on KPIs and how to obtain KPI IDs, refer to the PTV Flows documentation or the instructions in the `MICROSOFT BI FOR FLOWS` folder.
