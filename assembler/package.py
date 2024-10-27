from datetime import datetime
import json
import os
import time

from input.project_tree import ProjectTree
from selector.exclude import ExcludeFilter
from selector.include import IncludeFilter


class PackageExporter:
    def __init__(self, project_tree: ProjectTree):
        self.project_tree = project_tree

    def _get_file_content(self, file_path: str) -> str:
        """
        Reads the content of a file.
        :param file_path: Absolute path of the file
        :return: String content of the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Unable to read file {file_path}: {e}")
            return ""

    def export_to_json(self):
        """
        Exports all files in the ProjectTree to JSON format and saves them in data/<today's date>/<timestamp> folder.
        Includes both get_structure() and display_structure() output.
        """
        # Set up output directory and filename
        date_today = datetime.now().strftime("%Y%m%d")
        timestamp = time.strftime("combine_%H%M%S", time.localtime())
        output_dir = os.path.join("../data", date_today)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{timestamp}.json")

        # Get project structure
        structure = self.project_tree.get_structure()
        display_structure = self.project_tree.display_structure(structure)

        # Collect file paths and contents
        files_data = []
        self._collect_files_data(structure, files_data, self.project_tree.root_path)

        # Prepare JSON data with both structures and file data
        json_data = {
            "get_structure": structure,
            "display_structure": display_structure,
            "files": files_data
        }

        # Write to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        print(f"Files have been exported to: {output_file}")

    def _collect_files_data(self, structure, files_data, current_path):
        """
        Traverses the file structure and collects each file's path, name, and content.
        :param structure: Dictionary of file structure
        :param files_data: List of collected file data
        :param current_path: Current directory path
        """
        for name, path_or_substructure in structure.items():
            if isinstance(path_or_substructure, str):  # File with absolute path
                files_data.append({
                    "filename": name,
                    "path": path_or_substructure,
                    "content": self._get_file_content(path_or_substructure)
                })
            elif isinstance(path_or_substructure, dict):  # Directory structure
                self._collect_files_data(path_or_substructure, files_data, os.path.join(current_path, name))

    def print_combined_code(self):
        """
        Combines the content of all code files and prints the combined content.
        """
        # Collect file paths and contents again
        files_data = []
        self._collect_files_data(self.project_tree.get_structure(), files_data, self.project_tree.root_path)

        # Combine content of all files
        combined_content = "\n\n".join(file['content'] for file in files_data if file['content'])

        print("Combined Code Content:")
        print(combined_content)

# 使用示例
if __name__ == "__main__":
    # 定义过滤器
    include_filter = IncludeFilter(extensions=[''], folders=[''])
    exclude_filter = ExcludeFilter(extensions=['.pyc'], folders=['prompt'])

    # 初始化 ProjectTree 和 PackageExporter
    project_tree = ProjectTree(
        root_path="/Users/mailiya/documents/github/interviewai/interviewai/llm",
        display_mode="full",
        include_filter=include_filter,
        exclude_filter=exclude_filter
    )
    exporter = PackageExporter(project_tree)
    exporter.export_to_json()
    exporter.print_combined_code()
