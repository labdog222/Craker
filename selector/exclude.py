from typing import Optional, List


class ExcludeFilter:
    def __init__(self, extensions: Optional[List[str]] = None, folders: Optional[List[str]] = None):
        """
        Initializes an exclusion filter with specified file extensions and folders.

        :param extensions: List of file extensions to exclude (e.g., ['.css']). None excludes no file types.
        :param folders: List of folder names to exclude. None excludes no folders.
        """
        # 过滤掉空字符串
        self.extensions = [ext for ext in extensions if ext] if extensions else None
        self.folders = [folder for folder in folders if folder] if folders else None


    def exclude(self, filename: str, filepath: str) -> bool:
        """
        Checks if a file should be excluded based on its extension and folder.

        :param filename: The name of the file
        :param filepath: The path of the file
        :return: True if the file should be excluded, False otherwise
        """
        # Check if the file extension matches
        if self.extensions and any(filename.endswith(ext) for ext in self.extensions):
            return True
        # Check if the file is in the specified folders
        if self.folders and any(folder in filepath for folder in self.folders):
            return True
        return False