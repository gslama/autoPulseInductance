import os
import win32com.client as win32


def btnPrintChart(base_path, bar_num, part_num):
    try:
        # Define file paths
        template_file = os.path.join(base_path, "Test Data", "Auto Output Chart.xls")
        data_dir = os.path.join(base_path, "Test Data", "Output_Test", bar_num, "*.csv")
        data_path = os.path.join(base_path, "Test Data", "Output_Test", bar_num)
        chart_file = os.path.join(base_path, "95_series", part_num, "Test Data", f"{bar_num} Output Chart.xls")

        # Get the list of CSV files
        data_files = []
        for file in os.listdir(data_path):
            if file.endswith(".csv"):
                data_files.append(os.path.join(data_path, file))

        # Ensure we have data files to process
        if not data_files:
            print("No data files found.")
            return

        # Start Excel
        xlapp = win32.Dispatch("Excel.Application")
        xlapp.Visible = True  # Make Excel visible for debugging

        # Open the template file
        xlbook = xlapp.Workbooks.Open(template_file)

        # Call the macro to load data
        xlapp.Run("LoadFiles", data_files, part_num)

        # Call the macro to save the chart file
        xlapp.Run("SaveChartFile", chart_file)

        # Call the macro to print charts
        xlapp.Run("PrintCharts")

        # Close Excel
        xlapp.Quit()
        print("Process completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
base_path = "C:\\Path\\To\\Base\\Directory\\"
bar_num = "SomeBarText"  # Replace with actual text from your UI
part_num = "Part1234"  # Replace with actual part number from your UI

btnPrintChart(base_path, bar_num, part_num)
