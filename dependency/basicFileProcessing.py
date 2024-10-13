"""
{
基础文件处理: {
    基础组件 id: 1
}
}
"""
import shutil
import json
import os
import re
from typing import final, Callable

from dependency.toolIntegration import (
    catchError,
    timer
)

from tempConstant import (
    DEFAULT_JSON_STORAGE_PATH,  # 默认存根数据存储路径
    SHORT_INFORMATION,  # 短提示信息
    DIALOGUE_TUPLE,  # 对话框信息元组
    PATH_JSONLOG,  # 默认存根日志路径
    PATH_OUTPUTS,  # 输出目录路径
    CONFIG_FILE,  # 总配置文件信息
    PATH_INNER,  # 内部设置存放目录路径
    BYTE_SIZE,  # 转化输入文件大小边界获取文件字节大小
    OP_ISDIR,  # 判断路径是否指向文件夹
    W_PATH,  # 规范输入路径信息
    ERROR,  # 错误提示信息
    NAME,  # 获得路径所指向文件名
    BYTE,  # 获得标准字节大小
    OP,  # os模块路径相关引入
)

__all__ = ["AnalyticalPaper"]


class DataOperation:
    """
    数据操作类

    主要负责 [
        数据更新后产生新数据存根，
        更新当前操作存根日志，
        数据的 增 删 改 查，
        数据的二次解析
    ]
    """
    __slots__ = ["operate_log_do", "operate_log_path_do", "operate_dir_do", "deleted_file_do"]

    def __init__(self):
        self.operate_log_do: str = "__null__"  # 当前操作目录日志存根名
        self.operate_log_path_do: str = "__null__"  # 当前操作目录的路径
        self.operate_dir_do: dict = {}  # 当前操作目录解析数据
        self.deleted_file_do: list = []  # 被删除文件路径列表

    @staticmethod
    def writeOperateLog(func) -> Callable:
        """
        装饰器：获得当前操作存根的路径信息
              采用DOM解析方案解析并将目前操作目录存根日志载入栈内
        :param func: 待回调函数
        :return: 无返回值
        """

        def wrapper(self, *arg, **kwarg) -> None:
            """
            闭包函数
            :param self: 实例内部可调用方法
            :param arg: 可接收若干个变量数据
            :param kwarg: 可接收若干个变量 构成键值对
            :return:
            """
            with open(PATH_INNER + "\\.internalData.json", "r", encoding="utf-8") as f:
                internal_data = json.load(f)
                # [当前操作目录日志存根名, 当前操作目录的路径]
                self.operate_log_do = internal_data["currentDirectory"]
                self.operate_log_path_do = internal_data["fileStub"][internal_data["currentDirectory"]]
                self.operate_dir_do = self.openJson()  # 获取当前操作目录的数据
            func(self, *arg, **kwarg)
            return

        return wrapper

    @staticmethod
    def furtherAnalysisJSON(func) -> Callable:
        """
        装饰器：数据操作后二次分析当前操作目录数据并更新存根日志并写入新存根
        :param func: 待回调函数
        :return: 无返回值
        """

        def writeInner(self, root_dir: dict) -> None:
            """
            闭包内部函数 用于向存根写入新数据
            :param self: 实例内部可调用方法
            :param root_dir: 解析后的新待写入字典存根数据
            :return: 无返回值
            """
            with open(DEFAULT_JSON_STORAGE_PATH(), "w", encoding="utf-8") as f:
                json.dump({next(iter(self.operate_dir_do)): root_dir}, f, ensure_ascii=False)

        def analysisInner(self, root_dir, a_path: list) -> None:
            """
            分析路径指向信息是否存在 更新栈内当前操作目录映射字典数据
            :param self: 实例内部可调用方法
            :param root_dir: 当前操作目录待更新字典数据
            :param a_path: 更新过数据的对应路径列表
            :return: 无返回值
            """
            try:
                dir_or_str = root_dir[a_path[0]]
                if isinstance(dir_or_str, dict):
                    if OP.exists(dir_or_str["path"]):
                        analysisInner(self, root_dir[a_path[0]], a_path[1:])
                    else:
                        del root_dir[a_path[0]]
                else:
                    if not OP.exists(dir_or_str):
                        del root_dir[a_path[0]]
            except Exception as e:
                if e == KeyError:  # 找不到目标键 说明已经被删除
                    print(ERROR[3])
                elif e == IndexError:  # 找不到根路径说明根目录被删除
                    del root_dir

        def wrapper(self, *arg, **kwarg) -> None:
            """
            闭包函数
            :param self: 实例内部可调用方法
            :param arg: 可接收若干个变量数据
            :param kwarg: 可接收若干个变量 构成键值对
            :return:
            """
            func(self, *arg, **kwarg)
            root_dir: dict = self.operate_dir_do[next(iter(self.operate_dir_do))]
            #  root_dir 为当前操作json的根对象数据
            root_path: str = root_dir["path"]
            # root_path 为当前操作json的根对象目录 映射的路径
            new_split_path: list[list[str]] = [(a_path.replace(root_path, "")).split("\\")[1:]
                                               for a_path in self.deleted_file_do]
            if not new_split_path:
                print(SHORT_INFORMATION[3])
                writeInner(self, root_dir)
                return
            # new_split_path 获得切分好key列表的被删除全部目录
            for a_path in new_split_path:
                analysisInner(self, root_dir, a_path)
            writeInner(self, root_dir)
            return

        return wrapper

    def openJson(self) -> dict:
        """
        打开当前操作目录的存根文件转换成字典存入栈内
        :return: json数据字典
        """
        with open(self.operate_log_path_do, "r", encoding="utf-8") as f:
            json_data = json.load(f)
            return json_data  # 返回json转换成的字典数据数据

    @furtherAnalysisJSON
    @writeOperateLog
    def cleanDirectory(self, *, mode: int = None, sub_mode=1) -> None:
        """
        通过模式选项选择不同删除策略
        :param mode: [
            模式 1 递归清理全部空文件夹
            模式 2 定向名字清理文件
            模式 3 定向扩展名清理文件
            模式 4 定向文件大小清理文件 获得文件清除边界
        ]
        :param sub_mode: 子项模式
        :return: 无返回值。
        """
        match mode:
            case 1:  # 1: 递归清理全部空文件夹
                self.__cleanEmptyFolders(self.operate_dir_do)
            case 2:  # 2: 定向名字清理文件
                target_name = input(DIALOGUE_TUPLE[2])
                self.__cleanTargetNameFiles(self.operate_dir_do[next(iter(self.operate_dir_do))],
                                            target_name, sub_mode)
            case 3:  # 3: 定向扩展名清理文件
                file_extensions = input(DIALOGUE_TUPLE[3]).lower()
                if file_extensions.find(".") == -1:
                    file_extensions = "." + file_extensions
                self.__cleanTargetFileExtensionsFiles(self.operate_dir_do[next(iter(self.operate_dir_do))],
                                                      file_extensions, sub_mode)
            case 4:  # 4: 定向文件大小清理文件 获得文件清除边界
                size_file: int = BYTE_SIZE(input(DIALOGUE_TUPLE[4]))
                self.__cleanTargetSizeAreaFiles(self.operate_dir_do[next(iter(self.operate_dir_do))],
                                                size_file, sub_mode)

    def __cleanEmptyFolders(self, dir_map: dict) -> None:
        """
        递归迭代 寻找清理所有空目录
        :param dir_map: 待检测目录存根字典
        :return:
        """
        for file_name in dir_map:
            if isinstance(dir_map[file_name], dict) and len(dir_map[file_name]) == 1:
                self.__cleanFilesFolders(dir_map[file_name], False, os.removedirs)
            elif isinstance(dir_map[file_name], dict):
                self.__cleanEmptyFolders(dir_map[file_name])

    def __cleanTargetNameFiles(self, dir_map: dict, target_name: str, switch: int = 1) -> None:
        """
        递归迭代 寻找待清理目标名字的文件
        :param dir_map: 待检测目录存根字典
        :param switch: [
            模式 1 默认模式 只清除目标名字的文件
            模式 2 智能模式 清除目标名字的文件夹（包括所有下属文件或文件夹）
            模式 3 强力模式 清除目标名字的文件和目标名字的文件夹（包括所有下属文件或文件夹）
            模式 4 模糊模式 清除包含该目标名称的文件和文件夹
        ]
        :return:
        """
        match switch:
            case 1:  # 1: 默认模式 只清除目标名字的文件
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        self.__cleanTargetNameFiles(dir_map[file_name], target_name, 1)
                    elif OP.splitext(dir_map[file_name])[0] == target_name:
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)

            case 2:  # 2: 智能模式 清除目标名字的文件夹（包括所有下属文件或文件夹）
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        if OP.splitext(file_name)[0] == target_name:
                            self.__cleanFilesFolders(dir_map[file_name], False, shutil.rmtree)
                        else:
                            self.__cleanTargetNameFiles(dir_map[file_name], target_name, 2)
            case 3:  # 3: 强力模式 清除目标名字的文件和目标名字的文件夹（包括所有下属文件或文件夹）
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        if OP.splitext(file_name)[0] == target_name:
                            self.__cleanFilesFolders(dir_map[file_name], False, shutil.rmtree)
                        else:
                            self.__cleanTargetNameFiles(dir_map[file_name], target_name, 3)
                    elif OP.splitext(dir_map[file_name])[0] == target_name:
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case 4:  # 2: 模糊模式 清除包含该目标名称的文件和文件夹
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        if re.search(FR"{target_name}", file_name) is not None:
                            self.__cleanFilesFolders(dir_map[file_name], False, shutil.rmtree)
                        else:
                            self.__cleanTargetNameFiles(dir_map[file_name], target_name, 4)
                    elif re.search(FR"{target_name}", OP.basename(dir_map[file_name])) is not None:
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)

    def __cleanTargetFileExtensionsFiles(self, dir_map: dict, file_extensions: str, switch: int = 1) -> None:
        """
        递归迭代 寻找待清理目标后缀的文件
        :param dir_map: 待检测目录存根字典
        :param switch: [
            模式 1 默认模式 只清除当前目录目标后缀的文件
            模式 2 增强模式 清除目标后缀的文件（包括其含有下属文件夹所有下属目标后缀文件）
        ]
        :return:
        """
        match switch:
            case 1:  # 默认模式 只清除当前目录目标后缀的文件
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        pass
                    elif OP.splitext(dir_map[file_name])[1].lower() == file_extensions:
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case 2:  # 增强模式 清除目标后缀的文件（包括其含有下属文件夹所有下属目标后缀文件）
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        self.__cleanTargetFileExtensionsFiles(dir_map[file_name], file_extensions, 2)
                    elif OP.splitext(dir_map[file_name])[1] == file_extensions:
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case _:
                print(ERROR[0])

    def __cleanTargetSizeAreaFiles(
            self,
            dir_map: dict,
            file_size: int,
            switch: int = 1,
            *,
            diffusion_boundary: int = BYTE["kb"]
    ) -> None:
        """
        递归迭代 寻找待清理目标大小的文件
        :param dir_map: 待检测目录存根字典f
        :param file_size: 目标大小(字节)
        :param: diffusion_boundary: 边界扩散距离(字节)
        :param switch: [
            模式 1 收敛默认模式 只清除当前目录小于(不包含边界大小)字节边界的文件
            模式 2 收敛加强模式 清除小于(不包含边界大小)字节边界的文件（包括其含有下属文件夹所有目标文件）
            模式 3 收敛强力模式 清除小于(包含边界大小)字节边界的文件（包括其含有下属文件夹所有目标文件）
            模式 4 扩展模式    只清除当前目录大于(不包含边界大小)字节边界的文件
            模式 5 扩展加强模式 清除大于(不包含边界大小)字节边界的文件（包括其含有下属文件夹所有目标文件）
            模式 6 扩展强力模式 清除大于(包含边界大小)字节边界的文件（包括其含有下属文件夹所有目标文件）
            模式 7 扩散局限模式 只清除当前目录接近目标边界大小的文件(包含边界大小)
            模式 8 扩散加强模式 清除接近目标边界大小的文件(包含边界大小)（包括其含有下属文件夹所有目标文件）
        ]
        :return: 无返回值
        """
        match switch:
            case 1:  # 收敛默认模式 只清除当前目录小于(不包含边界大小)字节边界的文件
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        pass
                    elif OP.getsize(dir_map[file_name]) < file_size:
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case 2:  # 收敛加强模式 清除小于(不包含边界大小)字节边界的文件（包括其含有下属文件夹所有目标文件）
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        self.__cleanTargetSizeAreaFiles(dir_map[file_name], file_size, 2)
                    elif OP.getsize(dir_map[file_name]) < file_size and not OP_ISDIR(dir_map[file_name]):
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case 3:  # 收敛强力模式 清除小于(包含边界大小)字节边界的文件（包括其含有下属文件夹所有目标文件）
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        self.__cleanTargetSizeAreaFiles(dir_map[file_name], file_size, 3)
                    elif OP.getsize(dir_map[file_name]) <= file_size and not OP_ISDIR(dir_map[file_name]):
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case 4:  # 扩展模式 只清除当前目录大于(不包含边界大小)字节边界的文件
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        pass
                    elif OP.getsize(dir_map[file_name]) > file_size and not OP_ISDIR(dir_map[file_name]):
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case 5:  # 扩展加强模式 清除大于(不包含边界大小)字节边界的文件（包括其含有下属文件夹所有目标文件）
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        self.__cleanTargetSizeAreaFiles(dir_map[file_name], file_size, 5)
                    elif OP.getsize(dir_map[file_name]) > file_size and not OP_ISDIR(dir_map[file_name]):
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case 6:  # 扩展强力模式 清除大于(包含边界大小)字节边界的文件（包括其含有下属文件夹所有目标文件）
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        self.__cleanTargetSizeAreaFiles(dir_map[file_name], file_size, 6)
                    elif OP.getsize(dir_map[file_name]) >= file_size and not OP_ISDIR(dir_map[file_name]):
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case 7:  # 扩散局限模式 只清除当前目录接近目标边界大小的文件(包含边界大小)默认最大差距为1kb
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        pass
                    elif abs(OP.getsize(dir_map[file_name]) - file_size) <= diffusion_boundary and not OP_ISDIR(
                            dir_map[file_name]):
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case 8:  # 扩散加强模式 清除接近目标边界大小的文件(包含边界大小)默认最大差距为1kb（包括其含有下属文件夹所有目标文件）
                for file_name in dir_map:
                    if isinstance(dir_map[file_name], dict):
                        self.__cleanTargetSizeAreaFiles(dir_map[file_name], file_size, 8)
                    elif abs(OP.getsize(dir_map[file_name]) - file_size) <= diffusion_boundary and not OP_ISDIR(
                            dir_map[file_name]):
                        self.__cleanFilesFolders(dir_map[file_name], True, os.remove)
            case _:
                print(ERROR[0])

    def __cleanFilesFolders(self, dir_map_value: dict | str, switch: bool, func: Callable) -> None:
        """
        递归迭代 寻找待清理的文件或文件夹
        :param dir_map_value: 待检测目录存根字典
        :param switch: [
            模式 1 清理文件模式
            模式 2 清理文件夹模式
        ]
        :param func: [
            模式 1 清理文件模式 清理文件函数
            模式 2 清理文件夹模式 清理空文件夹函数
                              清理非空文件夹函数
        ]
        :return: 无返回值
        """
        pendingPath: str
        if switch:  # 开关打开删除文件
            pendingPath = dir_map_value
        else:  # 开关关闭删除文件夹
            pendingPath = dir_map_value["path"]
        try:
            func(pendingPath)  # os.remove() 删除文件  os.removedirs() 删除空文件夹  shutil.rmtree() 删除非空文件夹
            self.deleted_file_do.append(pendingPath)
            print(SHORT_INFORMATION[2].format(pendingPath))
        except OSError:
            print(ERROR[1].format(pendingPath))


class FileProcessingRoot:
    """
    文件处理类 通用基础功能
    初始化设置 [
        重置基础日志操作更新设置。| 恢复初始化设置
        重置受保护文件日志存根设置。
        重置日志文件。
        初始化json设置与所有存根目录。
    ]
    """

    @staticmethod
    def resetSettings() -> None:
        """
        重置基础日志操作更新设置。| 恢复初始化设置
        :return: 无返回值。
        """
        with open(PATH_INNER + "\\.internalData.json", "w", encoding="utf-8") as f_json_set:
            with open(PATH_INNER + "\\.InitialState.json", "r", encoding="utf-8") as f_json_set_ori:
                json_set_ori = json.load(f_json_set_ori)
                json.dump(json_set_ori, f_json_set, ensure_ascii=False)

    @staticmethod
    def resetProtectedFiles() -> None:
        """
        重置受保护文件日志存根设置。
        :return: 无返回值。
        """
        with open(FR"{PATH_OUTPUTS}\.protectedFiles.json", "w", encoding="utf-8") as f2:
            json.dump({}, f2, ensure_ascii=False)

    @staticmethod
    def resetJsonLog() -> None:
        """
        重置日志文件。
        :return: 无返回值。
        """
        for a_path in os.listdir(PATH_JSONLOG):
            print(CONFIG_FILE()["configIndex"][0])
            if a_path == CONFIG_FILE()["configIndex"][0]:
                continue
            os.unlink(OP.join(PATH_JSONLOG, a_path))
            print(a_path, SHORT_INFORMATION[0])

    def initialization(self) -> None:
        """
        初始化json设置与所有存根目录。
        :return: 无返回值。
        """
        self.resetSettings()
        self.resetJsonLog()
        self.resetProtectedFiles()

    def __dict__(self) -> list:
        """
        获取当前类所有属性
        :return: 包含所有属性的列表
        """
        return dir(self)


@final
class AnalyticalPaper(FileProcessingRoot, DataOperation):
    """
    文件处理类 初始解析路径获取目标字典
    """
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

    def __str__(self):
        print(SHORT_INFORMATION[1])
        str_inner = ""
        for key in self.__slots__:
            str_inner += str(f"{SHORT_INFORMATION[-1][key]}: {getattr(self, key)}\n")
        return str_inner

    @catchError
    @timer(switch=True)
    def analysis(self) -> None:
        """
        解析目录启动器
        :return: 无返回值。
        """
        if self.input_path == "__path__":
            self.input_path = self.inputPath()
        self.__getAllFiles(self.input_path, True)
        self.__writeJSON()
        self.json_dict = {}

    def inputPath(self) -> str | tuple[str]:
        """
        接收需要处理的文件夹路径。
        :return: 接收到的目标文件夹路径。 [ 默认为当前路径 ]
        """
        path_ = input(DIALOGUE_TUPLE[0])
        self.input_path = fr"{path_}"
        self.cut_floor = len(self.input_path.split("\\")) - 1
        return path_ if OP_ISDIR(W_PATH(path_)) else (W_PATH(path_), input(DIALOGUE_TUPLE[1]))  # 判断输入路径是否为文件夹。

    def __getAllFiles(self, path_: str = None, switch: bool = False) -> None:
        """
        获取当前路径下所有文件夹和文件名称路径 并分别打包进列表。
        :param switch: 检测是不是的创立第一层文件目录
        :param path_: 目标路径。
        :return: 无返回值。
        """
        if switch:  # 判断是否解析的文件为第一层是即为 True 默认为 False
            self.__readPath(path_)  # 获取第一层表结构
            self.file_layers += 1
        else:
            main_dir_list = self.dir_path_list_tp
            self.dir_path_list_tp = []
            for a_dir_path in main_dir_list:
                self.__readPath(a_dir_path)
            if not self.dir_path_list_tp:
                return
            self.file_layers += 1
        self.__getAllFiles()

    def __readPath(self, path_any: str) -> None:
        """
        将该目录下所有文件夹和文件名称路径归纳进入对应总名录
        :param path_any: 目标路径。 [ 文件夹路径 后续会解析出该文件夹下属的所有文件夹和文件 ]
        :return None: 无返回值。
        """
        try:
            for a_name in os.listdir(path_any):
                full_path = OP.join(path_any, a_name)
                if OP_ISDIR(W_PATH(full_path)):
                    self.dir_path_list_tp.append(full_path)  # 将文件夹路径添加到临时列表
                    self.json_dir_path_name_tp[a_name] = {"path": full_path}  # 将文件夹名添加到临时字典
                    self.folders_number += 1  # 文件夹数量+1
                    continue
                self.json_path_name_tp[a_name] = full_path  # 将文件名添加到临字典
                self.files_number += 1  # 文件数量+1
            self.__refreshCacheJSON(path_any)
        except PermissionError:
            print(ERROR[2].format(path_any))
            self.protected_files_json[path_any] = self.file_layers
            self.protected_files_number += 1

    def __refreshCacheJSON(self, path_: str) -> None:
        """
         将缓存字典写入储存json的字典，并清除缓存
        :param path_: 母文件夹路径
        :return None: 无返回值
        """
        """ - 缓存写入点 - """
        if not self.json_dict:
            self.json_dict[NAME(self.input_path)] = {"path": path_}  # 将第一层文件添加到总文件夹路径字典
            self.json_dict[NAME(self.input_path)].update(self.json_dir_path_name_tp)  # 将第一层文件夹名添加到总文件夹路径字典
            self.json_dict[NAME(self.input_path)].update(self.json_path_name_tp)  # 将第一层文件名字典合并到总文件夹路径字典
            self.json_dir_path_name_tp, self.json_path_name_tp, = {}, {}  # 清空临时字典
        else:
            self.__searchDict(self.json_dict, path_.split("\\")[self.cut_floor::])  # 寻找对应储存点

    def __searchDict(self, dictInside: dict, cut_path_list: list) -> None | dict:
        """
        递归遍历寻找字典缓存存储点
        :param dictInside: 遍历的字典
        :param cut_path_list: 母文件夹路径
        :return None | dict: None -> 无返回值 | dict -> 返回已将缓存写入后的储存字典
        """
        if len(cut_path_list) == 1:  # 遍历结束
            dictInside[cut_path_list[0]].update(self.json_dir_path_name_tp)
            dictInside[cut_path_list[0]].update(self.json_path_name_tp)
            return
        else:
            self.__searchDict(dictInside[cut_path_list[0]], cut_path_list[1::])
        self.json_dir_path_name_tp, self.json_path_name_tp = {}, {}
        return dictInside

    def __writeJSON(self) -> None:
        """
        将数据写入json存根日志
        :return None: 无返回值。
        """
        self.save_path = DEFAULT_JSON_STORAGE_PATH()
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(self.json_dict, f, ensure_ascii=False)
        if self.protected_files_number:
            with open(FR"{PATH_OUTPUTS}\.protectedFiles.json", "r", encoding="utf-8") as f1:
                dict_: dict
                try:
                    if dict_ := json.load(f1):
                        dict_.update(self.protected_files_json)
                except json.decoder.JSONDecodeError:
                    dict_ = self.protected_files_json
            with open(FR"{PATH_OUTPUTS}\.protectedFiles.json", "w", encoding="utf-8") as f2:
                json.dump(dict_, f2, ensure_ascii=False)

    def __del__(self):
        """
        析构函数
        :return None:
        """
        pass


class FilesCompress:
    """
    文件压缩类
    待开发...
    """

    def __init__(self, _path=None):
        self.input_path: str = _path  # 输入路径 [ 默认为当前数据操作路径 ]


if __name__ == '__main__':
    ap = AnalyticalPaper()
    # ap.inputPath()
    # ap.analysis()
    ap.cleanDirectory(mode=1)
    ap.initialization()
    # print(ap)
