import logging
import os
from typing import Optional, Dict

from selector.exclude import ExcludeFilter
from selector.include import IncludeFilter


class ProjectTree:
    def __init__(self, root_path: str, display_mode: str = 'full',
                 include_filter: Optional[IncludeFilter] = None,
                 exclude_filter: Optional[ExcludeFilter] = None):
        """
        Initializes the ProjectTree class with specified display mode and file filters.

        :param root_path: Absolute path to the root directory of the project
        :param display_mode: Display mode, can be 'full' or 'folders_only'
        :param include_filter: IncludeFilter instance to specify file types to include
        :param exclude_filter: ExcludeFilter instance to specify file types to exclude
        """
        if not os.path.isabs(root_path):
            raise ValueError("Please provide an absolute path for root_path.")
        if not os.path.isdir(root_path):
            raise NotADirectoryError(f"The path {root_path} is not a valid directory.")
        if display_mode not in ['full', 'folders_only']:
            raise ValueError("display_mode must be either 'full' or 'folders_only'")

        self.root_path = root_path
        self.display_mode = display_mode
        self.include_filter = include_filter if include_filter else IncludeFilter()
        self.exclude_filter = exclude_filter if exclude_filter else ExcludeFilter()

    def _should_include_file(self, filename: str, filepath: str) -> bool:
        """
        根据 include 和 exclude 过滤器确定是否包含文件。

        :param filename: 文件名
        :param filepath: 文件路径
        :return: 如果文件应被包含则返回 True，否则返回 False
        """
        # 情况 1：如果 include 设置了文件夹参数，忽略 exclude 的文件夹参数
        if self.include_filter and self.include_filter.folders:
            if any(folder in filepath for folder in self.include_filter.folders):
                # 已满足 include 的文件夹条件，忽略 exclude 文件夹过滤规则
                return True

        # 情况 2：如果 include 设置了文件名参数，忽略 exclude 的文件名参数
        if self.include_filter and self.include_filter.extensions:
            if any(filename.endswith(ext) for ext in self.include_filter.extensions):
                # 已满足 include 的文件名条件，忽略 exclude 文件名过滤规则
                return True

        # 情况 3：常规处理，应用 include 和 exclude 过滤器
        # 首先检查 include 规则
        if self.include_filter and not self.include_filter.include(filename, filepath):
            return False

        # 然后检查 exclude 规则
        if self.exclude_filter and self.exclude_filter.exclude(filename, filepath):
            return False

        return True  # 符合所有条件，包含文件


    def get_structure(self, current_path: Optional[str] = None) -> Dict[str, Optional[Dict]]:
        """
        根据过滤器递归获取文件和文件夹结构，并将文件存储为路径。

        :param current_path: 当前递归的路径
        :return: 表示文件结构的字典，其中文件为路径
        """
        if current_path is None:
            current_path = self.root_path

        structure = {}
        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    # 文件夹检查
                    if entry.is_dir():
                        # 检查是否满足 include 文件夹过滤条件
                        if self.include_filter and self.include_filter.folders:
                            if any(folder in entry.path for folder in self.include_filter.folders):
                                structure[entry.name] = self.get_structure(entry.path)
                                continue  # 忽略 exclude 文件夹规则
                        # 检查是否满足 exclude 文件夹条件
                        elif self.exclude_filter and any(folder in entry.path for folder in self.exclude_filter.folders):
                            continue  # 跳过该文件夹
                        else:
                            structure[entry.name] = self.get_structure(entry.path)  # 常规文件夹处理
                    elif entry.is_file() and self.display_mode == 'full':
                        # 检查是否应包含文件
                        if self._should_include_file(entry.name, current_path):
                            # 将文件的路径保存而不是 None
                            structure[entry.name] = os.path.join(current_path, entry.name)
        except PermissionError as e:
            logging.warning(f"权限被拒绝：{current_path} - {e}")

        return structure


    def display_structure(self, structure: Optional[Dict[str, Optional[Dict]]] = None, indent: int = 0) -> str:
            """
            Recursively formats and returns the project structure as a single string.

            :param structure: File structure dictionary
            :param indent: Indentation level for nested folders
            :return: String representation of the project structure
            """
            if structure is None:
                structure = self.get_structure()

            result = ""
            for name, substructure in structure.items():
                # Add the current item with indentation
                result += "    " * indent + f"- {name}\n"
                # Recursively add subdirectories
                if isinstance(substructure, dict):
                    result += self.display_structure(substructure, indent + 1)

            return result


    def find_path(self, file_name: str, current_path: Optional[str] = None) -> Optional[str]:
        """
        Recursively searches for a specified file path.

        :param file_name: Name of the file to search for
        :param current_path: Path for the current recursion
        :return: Absolute path of the file if found, or None if not found
        """
        if current_path is None:
            current_path = self.root_path

        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name == file_name:
                        # Apply filters to ensure file matches inclusion/exclusion criteria
                        if self._should_include_file(entry.name, current_path):
                            return os.path.join(current_path, file_name)
                    elif entry.is_dir():
                        found_path = self.find_path(file_name, entry.path)
                        if found_path:
                            return found_path  # Early exit to avoid redundant recursion
        except PermissionError as e:
            logging.warning(f"Permission denied: {current_path} - {e}")

        return None

# Example usage
if __name__ == "__main__":
    # Define filters to include only .py files in the 'src' folder and exclude .css files in the 'static' folder
    include_filter = IncludeFilter(extensions=[''], folders=['prompt'])
    exclude_filter = ExcludeFilter(extensions=['.pyc'], folders=['prompt'])

    # Initialize ProjectTree with filters
    project_tree = ProjectTree(
        "/Users/mailiya/documents/github/interviewai/interviewai",
        display_mode="full",
        include_filter=include_filter,
        exclude_filter=exclude_filter
    )

    # Display the project structure
    print("Project Structure:")
    print(project_tree.display_structure())
    print(project_tree.get_structure())

