import json
import os
import datetime
class FileProcessor:
    def __init__(self, file_structure, files):
        self.file_structure = file_structure
        self.files = {file['path']: file for file in files}
        self.processed_files = set()  # Track processed file paths

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

    def execute(self, mode="batch", count=3):
        all_files_data = []  # List to hold each file's data as a dictionary with array values

        if mode == "single":
            while True:
                result = self.process_single_file()
                if not result:
                    break
                all_files_data.append(result)

        elif mode == "multiple":
            while True:
                result = self.process_batch_files(count)
                if not result:
                    break
                all_files_data.extend(result)  # Append batch results

        if all_files_data:
            self.save_result(all_files_data, mode)

    def process_batch_files(self, count):
        """Multi-file processing mode: processes a batch of files up to the specified count."""
        batch_data = []
        files_processed = 0

        for file_path, file_data in self.files.items():
            if file_path not in self.processed_files and files_processed < count:
                self.processed_files.add(file_path)
                batch_data.append({
                    "filename": [file_data.get('filename')],
                    "path": [file_path],
                    "content": [file_data.get('content')]
                })
                files_processed += 1

        return batch_data if files_processed > 0 else None

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
    processor.execute(mode="single")

    # Execute multiple-file processing with a count of 3 files per batch
    # processor.execute(mode="multiple", count=3)
