import os
import json
import re
from datetime import datetime

__all__ = [
    "SHORT_INFORMATION", "DIALOGUE_TUPLE", "ERROR", "PATH_NOW", "PATH_INNER", "PATH_OUTPUTS",
    "PATH_JSONLOG", "OP", "OP_ISDIR", "W_PATH", "NAME", "PROJECT_NAME", "DEFAULT_JSON_STORAGE_PATH",
    "BYTE", "BYTE_SIZE", "CONFIG_FILE"
]
BYTE: dict[str, int] = {
    "b": 1,  # 字节
    "kb": 1024,
    "mb": 1048576,
    "gb": 1073741824,
    "tb": 1099511627776,
    "__default__": 2004_08_14,  # 默认字节大小
}
OP = os.path  # 路径操作
OP_ISDIR = os.path.isdir  # 判断是否为文件夹
W_PATH = os.path.normpath  # 路径规范
NAME = os.path.basename  # 获取当前路径文件名

__SWITCH__: bool = False


def findDir():
    absolute_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径。
    # __file__ 是一个特殊变量，表示当前脚本文件的路径。综上，这行代码返回当前脚本的绝对路径。
    current_dir = os.path.dirname(absolute_path)  # 通过传入的绝对路径，获取其所在的目录名称.
    return os.path.dirname(current_dir)  # 该函数获取current_dir的父目录路径。 返回 fileProcessing 所在磁盘中的绝对路径


def timeData(part: int = 3, connector: str = "_") -> str:
    """
    获取当前时间戳最精确可到微秒
    当前年份: now.year          part = 1
    当前月份: now.month         part = 2
    当前日期: now.day           part = 3
    当前小时: now.hour          part = 4
    当前分钟: now.minute        part = 5
    当前秒: now.second         part = 6
    当前微妙: now.microsecond   part = 7
    :param part: 启用几个组件构成时间戳 默认为3个
    :param connector: 时间组件连接符
    :return str: 构建好的时间戳
    """
    if part > 7 or part < -6:
        print("参数错误采取默认输出")
        part, connector = 3, "_"
    now = datetime.now()
    now_time = [now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond]
    return connector.join(str(i) for i in now_time[:part])


def sizeData(size: str = "1kb") -> int | None:
    if size == "0":
        return BYTE["__default__"]
    elif size == "生日":
        birthday = input("请输入您生日：")
        if birthday[0] == "0":
            return int(re.findall(r'\d+', birthday)[0], 8)
        return int(re.findall(r'\d+', birthday)[0])
    num = int(re.findall(r'\d+', size)[0])
    byte_symbol = re.findall(r'[a-zA-Z]+', size)[0].lower()
    try:
        return BYTE[byte_symbol] * num
    except KeyError:
        print(ERROR[4])
        return None


def getPathInner() -> str:
    """
    调用管理文件数的 json文件进行路径与时间戳整合
    :return str: 写好的 json文件保存的路径
    """
    global __SWITCH__
    with open(FR"{PATH_NOW}\.inner\.internalData.json", "r", encoding="utf-8") as f:
        internal_data: dict = json.load(f)  # 读取内部数据将json格式转化为字典
        if internal_data["writeCountJSON"] > 10:  # 如果文件超过10个，进入存根清理模式
            internal_data["writeCountJSON"] = 1  # 重置文件序列号
        if internal_data["deleteCountJSON"] > 10:
            try:
                os.remove(internal_data["fileStub"][next(iter(internal_data["fileStub"]))])  # 删除第一个文件
                del internal_data["fileStub"][next(iter(internal_data["fileStub"]))]  # 删除第一个键值对即清理最早存根
            except FileNotFoundError:
                del internal_data["fileStub"][next(iter(internal_data["fileStub"]))]  # 删除第一个键值对即清理最早存根
                print(F"{internal_data["fileStub"][next(iter(internal_data["fileStub"]))]}文件不存在")
        a_path = FR"{PATH_NOW}\.outputs\jsonLog\{internal_data["writeCountJSON"]}_{timeData(5)}.json"  # 构建文件名及路径
        operate_name: str = FR"{timeData(7, "-")}"
        internal_data["writeCountJSON"] += 1
        internal_data["deleteCountJSON"] += 1
        internal_data["fileStub"][operate_name] = a_path
        internal_data["currentDirectory"] = operate_name
    with open(FR"{PATH_NOW}\.inner\.internalData.json", "w", encoding="utf-8") as f:
        json.dump(internal_data, f, ensure_ascii=False)
    return a_path


def configSearch():
    with open(FR"{PATH_NOW}\.inner\.internalData.json", "r", encoding="utf-8") as f:
        internal_data: dict = json.load(f)
        return internal_data


SHORT_INFORMATION: tuple = (
    "已删除",  # index 0
    "当前类属性>",  # index 1
    "{}删除成功",  # index 2
    "无删除文件",  # index 3
    {
        "input_path": "输入路径：",
        "file_layers": "文件层级：",
        "cut_floor": "初始路径所停靠的文件(夹)层数：",
        "files_number": "文件数量：",
        "folders_number": "文件夹数量：",
        "protected_files_number": "受保护文件数量："
    }  # index -1
)
DIALOGUE_TUPLE: tuple = (
    "请输入文件夹/文件路径：",  # index 0
    "需要对此文件 删除[1] 压缩[2]：",  # index 1
    "请输入待清理文件名称：",  # index 2
    "请输入文件待清理文件扩展名：",  # index 3
    "请输入文件大小边界 默认[0]：",  # index 4
)
ERROR: tuple = (
    "-!-子项模式错误，已忽略本次删除操作-!-",  # index 0
    "-!-{}删除失败-!-",  # index 1
    "-!-对于{} 您的权限不够,无法访问。-!-"  # index 2
    "-!-找不到目标键-!-",  # index 3
    "-!-参数错误__文件字节异常__-!-"  # index 4

)

PATH_NOW = findDir()  # 当前项目路径
PATH_INNER = FR"{PATH_NOW}\.inner"
PATH_OUTPUTS = FR"{PATH_NOW}\.outputs"
PATH_JSONLOG = FR"{PATH_NOW}\.outputs\jsonLog"
PROJECT_NAME = NAME(PATH_NOW)  # 项目名
DEFAULT_JSON_STORAGE_PATH = getPathInner  # 默认的json存根文件存储路径
BYTE_SIZE = sizeData
CONFIG_FILE = configSearch

if __name__ == '__main__':
    pass
