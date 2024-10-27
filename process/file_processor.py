import json
import os
import datetime
class FileProcessor:
    def __init__(self, file_structure, files):
        self.file_structure = file_structure
        self.files = {file['path']: file for file in files}
        self.processed_files = set()  # Track processed file paths

    def process_batch_files(self, count):
        """Process files in batches up to the specified count."""
        batch_data = {"filename": [], "path": [], "content": []}
        files_processed = 0

        for file_path, file_data in self.files.items():
            if file_path not in self.processed_files:
                # Add file data to the current batch
                self.processed_files.add(file_path)
                batch_data["filename"].append(file_data.get('filename'))
                batch_data["path"].append(file_path)
                batch_data["content"].append(file_data.get('content'))
                files_processed += 1

                # If batch is full, yield it and reset for the next batch
                if files_processed == count:
                    yield batch_data
                    batch_data = {"filename": [], "path": [], "content": []}
                    files_processed = 0

        # Yield any remaining files if they don't form a full batch
        if batch_data["filename"]:
            yield batch_data

    def execute(self, mode="batch", count=3):
        all_files_data = []  # List to hold each batch as a dictionary

        if mode == "multiple":
            # Process files in batches
            for batch in self.process_batch_files(count):
                all_files_data.append(batch)

        elif mode == "single":
            # Process files one by one
            while True:
                result = self.process_single_file()
                if not result:
                    break
                all_files_data.append(result)

        if all_files_data:
            self.save_result(all_files_data, mode)

    def process_single_file(self):
        """Process each unprocessed file one by one continuously."""
        for file_path, file_data in self.files.items():
            if file_path not in self.processed_files:
                self.processed_files.add(file_path)
                return {
                    "filename": [file_data.get('filename')],
                    "path": [file_path],
                    "content": [file_data.get('content')]
                }
        return None  # No unprocessed files remain

    def save_result(self, data, mode):
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")
        save_dir = os.path.join("../data", date_str)
        os.makedirs(save_dir, exist_ok=True)

        filename = f"{mode}_all_{now.strftime('%H%M%S')}.json"
        file_path = os.path.join(save_dir, filename)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"All results saved to {file_path}")

if __name__ == "__main__":
    # JSON file path
    file_path = "/Users/mailiya/Documents/GitHub/Craker/data/20241027/combine_145942.json"

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

    # Execute single-file processing (processing one file at a time)
    processor.execute(mode="multiple")

    # Execute multiple-file processing with a count of 3 files per batch
    # processor.execute(mode="multiple", count=3)
