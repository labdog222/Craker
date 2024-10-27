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

    def process_batch_files(self, count):
        """Processes a batch of files up to the specified count."""
        batch = []

        files_processed = 0
        for file_path, file_data in self.files.items():
            if file_path not in self.processed_files and files_processed < count:
                self.processed_files.add(file_path)
                batch.append({
                    "filename": file_data.get('filename'),
                    "path": file_path,
                    "content": file_data.get('content')
                })
                files_processed += 1

        return batch if batch else None  # Return None if no files left to process

    def save_result(self, data, batch_index):
        """Save each batch result as a JSON file with a filename containing the current date, time, and batch index."""
        # Get the current date and time
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")  # Format: 20241027
        time_str = now.strftime("%H%M%S")  # Format: 153045 for time

        # Construct save path: data/<date>
        save_dir = os.path.join("../data", date_str)
        os.makedirs(save_dir, exist_ok=True)  # Create directory if it doesn't exist

        # Filename and complete path
        filename = f"batch_{batch_index}_{time_str}.json"
        file_path = os.path.join(save_dir, filename)

        # Save data to JSON file
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Batch {batch_index} saved to {file_path}")

    def execute(self, mode="batch", count=3):
        """
        Execute file processing in batch mode.
        :param mode: Processing mode, currently only supports batch mode
        :param count: File count per batch
        """
        if mode != "batch":
            raise ValueError("Invalid processing mode, only 'batch' mode is supported for this method")

        batch_index = 1
        while True:
            # Process a batch of files
            result = self.process_batch_files(count)
            if not result:
                break  # Exit loop if no more files to process

            # Save each batch result
            self.save_result(result, batch_index)
            batch_index += 1


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

    # Execute batch processing with a count of 3 files per batch
    processor.execute(mode="batch", count=3)
