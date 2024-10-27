import os
import json
import threading
from datetime import datetime
import re
import time
from assembler.package import PackageExporter
from process.file_processor import FileProcessor
from input.project_tree import ProjectTree
from selector.exclude import ExcludeFilter
from selector.include import IncludeFilter


class FlowManager:
    write_lock = threading.Lock()  # 初始化为 threading.Lock 实例

    def __init__(self, root_path: str, include_extensions=None, include_folders=None,
                 exclude_extensions=None, exclude_folders=None):
        """
        :param root_path: The root path of the project tree.
        :param include_extensions: List of extensions to include.
        :param include_folders: List of folders to include.
        :param exclude_extensions: List of extensions to exclude.
        :param exclude_folders: List of folders to exclude.
        """
        # Set default values if none provided
        include_extensions = include_extensions if include_extensions is not None else ['']
        include_folders = include_folders if include_folders is not None else ['']
        exclude_extensions = exclude_extensions if exclude_extensions is not None else ['.pyc']
        exclude_folders = exclude_folders if exclude_folders is not None else ['prompt']

        # Initialize filters
        include_filter = IncludeFilter(extensions=include_extensions, folders=include_folders)
        exclude_filter = ExcludeFilter(extensions=exclude_extensions, folders=exclude_folders)

        # Initialize ProjectTree and PackageExporter
        self.project_tree = ProjectTree(root_path=root_path, display_mode="full",
                                        include_filter=include_filter, exclude_filter=exclude_filter)
        self.exporter = PackageExporter(self.project_tree)
        self.processor = None  # To be initialized after export

    def export_project(self):
        """
        Exports project structure and file contents to JSON format.
        Initializes the FileProcessor with the exported data.
        """
        # 使用锁来确保写入操作是原子的
        with FlowManager.write_lock:
            self.exporter.export_to_json()

        # 获取当天日期以创建相应的目录路径
        date_today = datetime.now().strftime("%Y%m%d")
        output_dir = os.path.join("../data", date_today)

        # 正则表达式匹配文件名中的时间戳
        def extract_timestamp(file_name):
            match = re.search(r'combine_(\d{6})\.json', file_name)
            return match.group(1) if match else None

        # 查找符合条件的文件并按时间戳倒序排序
        json_files = [f for f in os.listdir(output_dir) if f.startswith("combine_") and f.endswith(".json")]
        json_files.sort(key=lambda x: extract_timestamp(x), reverse=True)

        # 检查是否找到符合条件的文件
        if not json_files:
            raise FileNotFoundError("No JSON files found in the output directory.")

        # 选择最新的文件
        latest_export = json_files[0]
        file_path = os.path.join(output_dir, latest_export)

        # 尝试读取文件
        with open(file_path, "r") as f:
            data = json.load(f)

        # 检查数据是否为字典格式
        if not isinstance(data, dict):
            raise ValueError("Loaded JSON data is not a dictionary.")

        # 初始化 FileProcessor
        file_structure = data.get("get_structure", {})
        files = data.get("files", [])
        self.processor = FileProcessor(file_structure, files)
        print("Project exported and FileProcessor initialized.")

    def process_files(self, mode="batch", count=3):
        """
        Processes files using FileProcessor based on the specified mode.
        :param mode: "batch" for batch processing, "single" for single file processing.
        :param count: Number of files per batch (only applicable for batch mode).
        """
        if not self.processor:
            raise ValueError("FileProcessor not initialized. Run export_project() first.")

        # Process files and save results
        self.processor.execute(mode=mode, count=count)
        print(f"Files processed in {mode} mode with count={count}.")


# Usage example
if __name__ == "__main__":
    root_path = "/Users/mailiya/documents/github/interviewai/interviewai/llm"
    include_extensions = ['.py']  # Only include Python files
    include_folders = ['src', 'tests']  # Only include 'src' and 'tests' folders
    exclude_extensions = ['.pyc']  # Exclude compiled Python files
    exclude_folders = ['build', 'dist']  # Exclude build and distribution folders

    manager = FlowManager(
        root_path=root_path,
        include_extensions=include_extensions,
        include_folders=include_folders,
        exclude_extensions=exclude_extensions,
        exclude_folders=exclude_folders
    )
    manager.export_project()
    manager.process_files(mode="multiple", count=3)  # Or mode="batch"
