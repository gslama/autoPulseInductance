import tkinter as tk
from tkinter import messagebox
import win32com.client as win32


def run_excel_macro():
    try:
        # Path to your Excel file
        excel_file = r"C:\Users\gslam\Dropbox\SlamaTech\Consulting\AUTO Programs\AutoOutput\Excel Template\Auto Output Chart r3.xlsm"

        # Macro name (include the module name if needed, e.g., 'Module1.MyMacro')
        macro_name = "CommandButton1_Click1"

        # Open Excel
        excel = win32.Dispatch("Excel.Application")
        excel.Visible = True  # Set to True to see Excel open

        # Open the workbook
        workbook = excel.Workbooks.Open(excel_file)

        # Run the macro
        excel.Application.Run(macro_name)

        # Save and close the workbook
        workbook.Save()
        workbook.Close()

        # Quit Excel
        excel.Quit()

        messagebox.showinfo("Success", "Macro ran successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to run macro: {e}")


# Create the tkinter window
root = tk.Tk()
root.title("Run Excel Macro")

# Add a button to run the macro
run_button = tk.Button(root, text="Run Excel Macro", command=run_excel_macro)
run_button.pack(pady=20)

root.mainloop()
