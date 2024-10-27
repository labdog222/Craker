import os
import logging
from typing import Optional, Dict, List

logging.basicConfig(level=logging.INFO)

class IncludeFilter:
    def __init__(self, extensions: Optional[List[str]] = None, folders: Optional[List[str]] = None):
        """
        Initializes an inclusion filter with specified file extensions and folders.

        :param extensions: List of file extensions to include (e.g., ['.py']). None includes all file types.
        :param folders: List of folder names to include. None includes all folders.
        """
        # 过滤掉空字符串
        self.extensions = [ext for ext in extensions if ext] if extensions else None
        self.folders = [folder for folder in folders if folder] if folders else None


    def include(self, filename: str, filepath: str) -> bool:
        """
        Checks if a file should be included based on its extension and folder.

        :param filename: The name of the file
        :param filepath: The path of the file
        :return: True if the file should be included, False otherwise
        """
        # Check if the file extension matches
        if self.extensions and not any(filename.endswith(ext) for ext in self.extensions):
            return False
        # Check if the file is in the specified folders
        if self.folders and not any(folder in filepath for folder in self.folders):
            return False
        return True

