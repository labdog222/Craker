import json
import os
import random
import datetime
from collections import deque

class FileProcessor:
    def __init__(self, file_structure, files):
        """
        初始化文件处理类
        :param file_structure: 文件目录结构的JSON表示
        :param files: 文件列表，包含文件名、路径和内容
        """
        self.file_structure = file_structure
        self.files = {file['path']: file for file in files}
        self.processed_files = set()  # 记录已处理的文件路径

    def process_single_file(self):
        """单文件处理模式"""
        for file_path, file_data in self.files.items():
            if file_path not in self.processed_files:
                self.processed_files.add(file_path)
                return {file_path: file_data}

    def save_result(self, data):
        """将合并结果保存为 JSON 文件，文件名包含当前日期时间，路径位于 data/当前日期"""
        # 获取当前日期和时间
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")  # 日期形式：20241027
        time_str = now.strftime("%H%M%S")  # 日期+时间形式：20241027153045

        # 构建保存路径：data/日期
        save_dir = os.path.join("../data", date_str)
        os.makedirs(save_dir, exist_ok=True)  # 创建日期目录（若不存在）

        # 文件名和完整路径
        filename = f"split_{time_str}.json"
        file_path = os.path.join(save_dir, filename)

        # 保存数据为 JSON 文件
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"结果已保存到 {file_path}")

    def execute(self, mode="single", count=1, search_mode="bfs"):
        """
        执行文件处理
        :param mode: 处理模式，可选 single, multiple, random
        :param count: 文件数量，适用于 multiple 和 random 模式
        :param search_mode: 搜索模式，可选 bfs, dfs
        """
        if mode == "single":
            result = self.process_single_file()
        else:
            raise ValueError("无效的处理模式")

        # 根据搜索模式合并文件内容
        if search_mode == "bfs":
            merged_result = self.bfs_merge()
        elif search_mode == "dfs":
            merged_result = self.dfs_merge()
        else:
            raise ValueError("无效的搜索模式")

        # 保存最终结果
        self.save_result(merged_result)


if __name__ == "__main__":
    # JSON 文件路径
    file_path = "/Users/mailiya/Documents/GitHub/Craker/data/20241027/combine_133501.json"

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 {file_path} 不存在。")

    # 读取 JSON 数据
    with open(file_path, "r") as f:
        data = json.load(f)

    # 提取文件结构和文件列表
    file_structure = data.get("get_structure", {})
    files = data.get("files", [])

    # 初始化文件处理类
    processor = FileProcessor(file_structure, files)

    # 示例：执行单文件处理模式
    processor.execute(mode="single")

    # 示例：多文件处理（一次处理 3 个文件）
    processor.execute(mode="multiple", count=3)


