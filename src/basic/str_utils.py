import re
from typing import Optional

from basic.log_utils import log


def find(source: str, target: str, ignore_case: bool = False) -> int:
    """
    字符串find的封装 在原目标串中招目标字符串
    :param source: 原字符串
    :param target: 目标字符串
    :param ignore_case: 是否忽略大小写
    :return:
    """
    if source is None or target is None:
        return -1
    if ignore_case:
        return source.lower().find(target.lower())
    else:
        return source.find(target)


def find_by_lcs(source: str, target: str, percent: float = 0.3,
                ignore_case: bool = True) -> bool:
    """
    根据最长公共子序列长度和一定阈值 判断字符串是否有包含关系。
    用于OCR结果和目标的匹配
    :param source: OCR目标
    :param target: OCR结果
    :param percent: 最长公共子序列长度 需要占 source长度 的百分比
    :param ignore_case: 是否忽略大小写
    :return: 是否包含
    """
    if source is None or target is None:
        return False
    source_usage = source.lower() if ignore_case else source
    target_usage = target.lower() if ignore_case else target

    common_length = longest_common_subsequence_length(source_usage, target_usage)

    return common_length >= len(source) * percent


def longest_common_subsequence_length(str1: str, str2: str):
    """
    找两个字符串的最长公共子序列长度
    :param str1:
    :param str2:
    :return: 长度
    """
    m = len(str1)
    n = len(str2)

    # 创建一个二维数组用于存储中间结果
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # 动态规划求解
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


def get_positive_digits(v: str, err: Optional[int] = 0) -> Optional[int]:
    """
    返回字符串中的数字部分 不包含符号
    :param v: 字符串
    :param err: 原字符串中没有数字的话返回的值
    :return: 字符串中的数字
    """
    try:
        return int(re.sub(r"\D", "", v))
    except Exception:
        log.error('目标字符串中没有数字 %s', v)
        return err
