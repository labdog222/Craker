import json
import os
import datetime

class FileProcessor:
    def __init__(self, file_structure, files):
        """
        Initialize the file processing class
        :param file_structure: JSON representation of the file directory structure
        :param files: List of files, including file name, path, and content
        """
        self.file_structure = file_structure
        self.files = {file['path']: file for file in files}
        self.processed_files = set()  # Track processed file paths

    def process_single_file(self):
        """Single file processing mode: returns each file with filename, path, and content."""
        result = []

        for file_path, file_data in self.files.items():
            if file_path not in self.processed_files:
                self.processed_files.add(file_path)
                result.append({
                    "filename": file_data.get('filename'),
                    "path": file_path,
                    "content": file_data.get('content')
                })

        return result

    def save_result(self, data):
        """Save the merged result as a JSON file with a filename containing the current date and time."""
        # Get the current date and time
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")  # Format: 20241027
        time_str = now.strftime("%H%M%S")  # Format: 153045 for time

        # Construct save path: data/<date>
        save_dir = os.path.join("../data", date_str)
        os.makedirs(save_dir, exist_ok=True)  # Create directory if it doesn't exist

        # Filename and complete path
        filename = f"split_{time_str}.json"
        file_path = os.path.join(save_dir, filename)

        # Save data to JSON file
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Result saved to {file_path}")

    def execute(self, mode="single", count=1, search_mode="bfs"):
        """
        Execute file processing.
        :param mode: Processing mode, options are single, multiple, random
        :param count: File count, used for multiple and random modes
        :param search_mode: Search mode, options are bfs, dfs
        """
        if mode == "single":
            result = self.process_single_file()
        else:
            raise ValueError("Invalid processing mode")

        # Save the single file processing result
        self.save_result(result)


if __name__ == "__main__":
    # JSON file path
    file_path = "/Users/mailiya/Documents/GitHub/Craker/data/20241027/combine_142752.json"

    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    # Read JSON data
    with open(file_path, "r") as f:
        data = json.load(f)

    # Extract file structure and file list
    file_structure = data.get("get_structure", {})
    files = data.get("files", [])

    # Initialize the file processor
    processor = FileProcessor(file_structure, files)

    # Execute single-file processing
    processor.execute(mode="single")
