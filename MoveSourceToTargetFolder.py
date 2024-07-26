import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil

# Function to save paths to a file
def save_paths(source_path, target_path):
    with open('paths.txt', 'w') as file:
        file.write(f'{source_path}\n{target_path}')

# Function to load paths from the file
def load_paths():
    if os.path.exists('paths.txt'):
        with open('paths.txt', 'r') as file:
            paths = file.read().splitlines()
            if len(paths) == 2:
                return paths[0], paths[1]
    return '', ''  # Return empty strings if the file doesn't exist or doesn't contain two lines

def choose_folder(var, label):
    folder_path = filedialog.askdirectory()
    if folder_path:
        print(f"Folder selected: {folder_path}")  # Print test
        var.set(folder_path)
        label.config(text=folder_path)  # Update the label to show the selected path
        if source_var.get() and target_var.get():
            begin_button.config(state=tk.NORMAL)
            save_paths(source_var.get(), target_var.get())  # Save the paths when both are selected


def get_all_folders(path):
    """
    Recursively list all subfolders in a given directory path, excluding folders that start with "-".
    
    Args:
    path (str): The directory path to list subfolders from.

    Returns:
    list: A list of paths to all subfolders within the given directory, excluding those starting with "-".
    """
    folders = []
    for root, dirs, _ in os.walk(path):
        for dir in dirs:
            if not dir.startswith("-"):  # Skip folders starting with "-"
                folder_path = os.path.join(root, dir)
                folders.append(folder_path)
                print(f"Found folder: {folder_path}")  # Print test

    return folders


def extract_product_id(folder_name):
    """
    Extract the product ID (first characters before the first space) from a folder name.
    
    Args:
    folder_name (str): The name of the folder.

    Returns:
    str: The extracted product ID.
    """
    # from the target, id should be caracters before the -, if no - then is not a product, so ignore
    return folder_name.split()[0].upper()

# At the beginning of the process_folders function, initialize a list to store non-empty directories
non_empty_directories = []

def process_folders():
    """
    Process the folders based on the product IDs.
    Moves contents from the source folder to the matching target folder,
    tries to delete the source folder, and keeps track of non-empty source folders.
    """
    source_folders = get_all_folders(source_var.get())
    target_folders = get_all_folders(target_var.get())

    source_ids = {extract_product_id(os.path.basename(folder)): folder for folder in source_folders}
    target_ids = {extract_product_id(os.path.basename(folder)): folder for folder in target_folders}

    for id, source_folder in source_ids.items():
        if id in target_ids:
            target_folder = target_ids[id]
            print(f"Moving contents from {source_folder} to {target_folder}")  # Print test
            for item in os.listdir(source_folder):
                src_item_path = os.path.join(source_folder, item)
                dst_item_path = os.path.join(target_folder, item)
                if not os.path.exists(dst_item_path):
                    shutil.move(src_item_path, target_folder)
                else:
                    print(f"Skipping {src_item_path}: destination exists.")

            # Try to delete the source folder, catch the exception if it is not empty
            try:
                os.rmdir(source_folder)
            except OSError as e:
                print(f"Could not delete {source_folder}: {e}")
                non_empty_directories.append(source_folder)

    # After processing all folders, check if there are any non-empty directories
    if non_empty_directories:
        message = "Processed folders successfully, but could not delete the following non-empty directories:\n" + '\n'.join(non_empty_directories)
        messagebox.showinfo("Operation Completed with Exceptions", message)
    else:
        messagebox.showinfo("Operation Completed", "Folders processed successfully.")


# Initialize the main window
root = tk.Tk()
root.title("Folder Processor")

# Load the saved paths
source_path, target_path = load_paths()

# Tkinter variables to store the paths of source and target folders
source_var = tk.StringVar(value=source_path)
target_var = tk.StringVar(value=target_path)

# Labels to display the selected paths
source_path_label = tk.Label(root, text=source_path)
target_path_label = tk.Label(root, text=target_path)

# Button to choose the source folder
choose_source_button = tk.Button(root, text="Choose source folders", command=lambda: choose_folder(source_var, source_path_label))
choose_source_button.pack(side=tk.TOP, padx=10, pady=10)
source_path_label.pack(side=tk.TOP, padx=10, pady=10)

# Button to choose the target folder
choose_target_button = tk.Button(root, text="Choose target folders", command=lambda: choose_folder(target_var, target_path_label))
choose_target_button.pack(side=tk.TOP, padx=10, pady=10)
target_path_label.pack(side=tk.TOP, padx=10, pady=10)

# Button to begin the folder processing, initially disabled if paths are not set
begin_button_state = tk.NORMAL if source_path and target_path else tk.DISABLED
begin_button = tk.Button(root, text="Begin", state=begin_button_state, command=process_folders)
begin_button.pack(pady=10)

root.mainloop()