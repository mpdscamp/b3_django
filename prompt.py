import os

def write_folder_structure(directory, output_file):
    """
    Write the folder structure to the output file.
    """
    for root, dirs, files in os.walk(directory):
        if any(ignored in root for ignored in ["env", "migrations", "__pycache__", ".bak", ".dat", ".dir", "db.sqlite3", ".txt", "prompt.py", ".git", ".pyc"]):
            continue

        # Write the relative path
        relative_path = os.path.relpath(root, directory)
        if relative_path == ".":
            relative_path = directory
        output_file.write(f"{relative_path}/\n")

        # Indent files for better structure visibility
        for file in files:
            if not any(file.endswith(ext) for ext in [".bak", ".dat", ".dir", "db.sqlite3", ".txt", "prompt.py", ".git", ".pyc"]):
                output_file.write(f"  {file}\n")


def write_files_content(directory, output_file):
    """
    Write the content of files to the output file.
    """
    for root, dirs, files in os.walk(directory):
        if any(ignored in root for ignored in ["env", ".bak", ".dat", ".dir", "db.sqlite3", ".txt", "prompt.py", ".git", ".pyc"]):
            continue

        for file in files:
            if not any(file.endswith(ext) for ext in [".bak", ".dat", ".dir", "db.sqlite3", ".txt", "prompt.py", ".git", ".pyc"]):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    output_file.write(f"\n{'-' * 80}\n")
                    output_file.write(f"File: {file_path}\n")
                    output_file.write(f"{'-' * 80}\n")
                    output_file.write(content)
                    output_file.write("\n")
                except Exception as e:
                    output_file.write(f"\n{'-' * 80}\n")
                    output_file.write(f"File: {file_path}\n")
                    output_file.write(f"{'-' * 80}\n")
                    output_file.write(f"Error reading file: {e}\n")


def main(directory, output_filename):
    """
    Main function to write folder structure and file contents to a .txt file.
    """
    with open(output_filename, "w", encoding="utf-8") as output_file:
        # Write folder structure
        output_file.write("Folder Structure:\n")
        output_file.write("=" * 80 + "\n")
        write_folder_structure(directory, output_file)

        # Write file contents
        output_file.write("\n\nFile Contents:\n")
        output_file.write("=" * 80 + "\n")
        write_files_content(directory, output_file)


if __name__ == "__main__":
    # Specify the directory to scan and the output file
    target_directory = input("Enter the target directory: ").strip()
    output_file_name = "codebase_structure_and_contents.txt"

    main(target_directory, output_file_name)
    print(f"Folder structure and file contents written to {output_file_name}")
