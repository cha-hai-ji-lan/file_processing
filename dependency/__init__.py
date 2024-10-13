"""
临时存放工具
"""
from tempConstant import *
import os


def getFilesAndFoldersPathList(path_l: list[str], switch: bool = False) -> list[str]:
    """
    获取当前路径下所有文件夹的名录列表。
    :param switch: (
        控制输出的目录列表 是文件夹目录列表 还是文件目录列表
        switch=False 输出文件目录列表。 [ 默认输出文件目录列表 ]
        switch=True 输出文件夹目录列表。
    )
    :param path_l: 待检测已打包文件路径。
    :return: 只储存 文件/文件夹 路径的列表。 [ 默认为空 ]
    """
    list_temp_f: list = []
    list_temp_ff: list = []
    for file in path_l:
        if OP_ISDIR(W_PATH(file)):
            list_temp_ff += [file]
        else:
            list_temp_f += [file]
    if switch:
        return list_temp_ff
    return list_temp_f



