from typing import Callable

from dependency import toolIntegration
from tempConstant import BYTE


class DataOperation:
    """
    此类用于执行基本的文件操作，如读取、写入、追加等。
    """
    __slots__ = ["operate_log_do", "operate_log_path_do", "operate_dir_do", "deleted_file_do"]

    def __init__(self):
        self.operate_log_do: str = "__null__"  # 当前操作目录日志存根名
        self.operate_log_path_do: str = "__null__"  # 当前操作目录的路径
        self.operate_dir_do: dict = {}  # 当前操作目录解析数据
        self.deleted_file_do: list = []  # 被删除文件路径列表
        ...

    @staticmethod
    def writeOperateLog(func) -> Callable:
        def wrapper(self, *arg, **kwarg) -> None: ...

    @staticmethod
    def furtherAnalysisJSON(func) -> Callable:
        def writeInner(self, root_dir: dict) -> None: ...

        def analysisInner(self, root_dir, a_path: list) -> None: ...

        def wrapper(self, *arg, **kwarg) -> None: ...

    def openJson(self) -> dict: ...

    def cleanDirectory(self, *, mode: int = None, sub_mode=1) -> None: ...

    def __cleanEmptyFolders(self, dir_map: dict) -> None: ...

    def __cleanTargetNameFiles(self, dir_map: dict, target_name: str, switch: int = 1) -> None:...

    def __cleanTargetFileExtensionsFiles(self, dir_map: dict, file_extensions: str, switch: int = 1) -> None:...


    def __cleanTargetSizeAreaFiles(self, dir_map: dict, file_size: int, switch: int = 1,
                                   diffusion_boundary: int = BYTE["kb"]) -> None: ...

    def __cleanFilesFolders(self, dir_map_value: dict | str, switch: bool, func: Callable) -> None: ...


class FileProcessingRoot:
    def __dict__(self) -> list: ...

    @staticmethod
    def resetSettings() -> None: ...

    @staticmethod
    def resetProtectedFiles() -> None: ...

    @staticmethod
    def resetJsonLog() -> None: ...

    def initialization(self) -> None: ...


class AnalyticalPaper(FileProcessingRoot, DataOperation):
    __slots__ = ["input_path", "file_layers", "cut_floor", "files_number", "folders_number",
                 "protected_files_number"]

    def __init__(self):
        super().__init__()
        self.input_path: str = "__path__"  # 输入路径
        self.save_path: str = "__savePath__"  # 保存路径
        self.file_layers: int = 0  # 文件层级
        self.cut_floor: int = 0  # 记录输入初始路径所停靠的文件(夹)的层数
        self.json_dict: dict = {}  # 字典存储器 后续打印文件夹结构的json文件
        self.dir_path_list_tp: list[any] = []  # 临时存放文件夹路径
        self.json_dir_path_name_tp: dict = {}  # 临时存放文件夹名
        self.json_path_name_tp: dict = {}  # 临时存放文件名
        self.protected_files_json: dict = {}  # 受保护文件字典
        self.files_number: int = 0  # 文件数量
        self.folders_number: int = 0  # 文件夹数量
        self.protected_files_number: int = 0  # 受保护文件数量
        ...

    def __str__(self): ...

    @toolIntegration.catchError
    @toolIntegration.timer
    def analysis(self) -> None: ...

    def inputPath(self) -> str | tuple[str]: ...

    def __getAllFiles(self, path_: str = None, switch: bool = False) -> None: ...

    def __readPath(self, path_any: str) -> None: ...

    def __refreshCacheJSON(self, path_: str) -> None: ...

    def __searchDict(self, dictInside: dict, cut_path_list: list) -> None | dict: ...

    def __writeJSON(self) -> None: ...

    def __del__(self): ...


class FilesCompress:
    def __init__(self, _path=None):
        self.input_path: str = _path  # 输入路径 [ 默认为当前数据操作路径 ]
