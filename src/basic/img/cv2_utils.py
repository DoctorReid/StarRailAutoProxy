import math
from typing import Union, List

import cv2
import numpy as np
import os
from PIL.Image import Image

from basic.img import ImageLike, MatchResult, MatchResultList
from basic.log_utils import log


def read_image(file_path: str) -> cv2.typing.MatLike:
    """
    读取图片
    :param file_path: 图片路径
    :param show_result: 是否显示结果
    :return:
    """
    if not os.path.exists(file_path):
        return None
    image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
    return image


def convert_source(source_image: ImageLike, src_x_scale: float = 1, src_y_scale: float = 1):
    """
    将原图转化成适合使用的cv2格式，会转化成RGBA
    :param source_image: 原图
    :param src_x_scale: 原图缩放比例x
    :param src_y_scale: 原图缩放比例y
    :return: 转化图
    """
    source: cv2.typing.MatLike = None
    if type(source_image) == Image:
        if source_image.mode == 'RGBA':
            source = cv2.cvtColor(np.array(source_image), cv2.COLOR_RGBA2BGRA)
        else:
            source = cv2.cvtColor(np.array(source_image.convert('RGBA')), cv2.COLOR_RGBA2BGRA)
    elif type(source_image) == str:
        source = cv2.imread(source_image)
    else:
        source = source_image
    if src_x_scale != 1 or src_y_scale != 1:
        source = cv2.resize(source, (0, 0), fx=src_x_scale, fy=src_y_scale)
    return source


def show_image(img: cv2.typing.MatLike,
               rects: Union[MatchResult, MatchResultList] = None,
               win_name='DEBUG',
               wait=1):
    """
    显示一张图片
    :param img: 图片
    :param rects: 需要画出来的框
    :param win_name:
    :param wait:
    :return:
    """
    to_show = img

    if rects is not None:
        to_show = img.copy()
        if type(rects) == MatchResult:
            cv2.rectangle(to_show, (rects.x, rects.y), (rects.x + rects.w, rects.y + rects.h), (255, 0, 0), 1)
        elif type(rects) == MatchResultList:
            for i in rects:
                cv2.rectangle(to_show, (i.x, i.y), (i.x + i.w, i.y + i.h), (255, 0, 0), 1)

    cv2.imshow(win_name, to_show)
    cv2.waitKey(wait)


def image_rotate(img: cv2.typing.MatLike, angle: int, show_result: bool = False):
    """
    对图片按中心进行旋转
    :param img: 原图
    :param angle: 逆时针旋转的角度
    :param show_result: 显示结果
    :return: 旋转后图片
    """
    height, width = img.shape[:2]
    center = (width // 2, height // 2)

    # 获取旋转矩阵
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # 应用旋转矩阵来旋转图像
    rotated_image = cv2.warpAffine(img, rotation_matrix, (width, height))

    if show_result:
        cv2.imshow('Result', rotated_image)

    return rotated_image


def convert_png_and_save(image_path: str, save_path: str):
    """
    将原图转化成png格式保存
    :param image_path: 原图路径
    :param save_path: 目标路径
    """
    img = read_image(image_path)
    img.save(save_path)


def mark_area_as_transparent(image: cv2.typing.MatLike, pos: Union[List, np.ndarray], outside: bool = False):
    """
    将图片的一个区域变成透明 然后返回新的图片
    :param image: 原图
    :param pos: 区域坐标 如果是矩形 传入 [x,y,w,h] 如果是圆形 传入 [x,y,r]。其他数组长度不处理
    :param outside: 是否将区域外变成透明
    :return: 新图
    """
    # 创建一个与图像大小相同的掩膜，用于指定要变成透明的区域
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    if not type(pos) is np.ndarray:
        pos = np.array([pos])
    for p in pos:
        if len(p) == 4:
            x, y, w, h = p[0], p[1], p[2], p[3]
            # 非零像素表示要变成透明的区域
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
        if len(p) == 3:
            x, y, r = p[0], p[1], p[2]
            # 非零像素表示要变成透明的区域
            cv2.circle(mask, (x, y), r, 255, -1)
    # 合并
    return cv2.bitwise_and(image, image, mask=mask if outside else cv2.bitwise_not(mask))


def mark_area_as_color(image: cv2.typing.MatLike, pos: List, color, new_image: bool = False):
    """
    将图片的一个区域变颜色 然后返回新的图片
    :param image: 原图
    :param pos: 区域坐标 如果是矩形 传入 [x,y,w,h] 如果是圆形 传入 [x,y,r]。其他数组长度不处理
    :param new_image: 是否返回一张新的图
    :return: 新图
    """
    to_paint = image.copy() if new_image else image
    if not type(pos) is np.ndarray:
        pos = np.array([pos])
    for p in pos:
        if len(p) == 4:
            x, y, w, h = p[0], p[1], p[2], p[3]
            cv2.rectangle(to_paint, pt1=(x, y), pt2=(x + w, y + h), color=color, thickness=-1)
        if len(p) == 3:
            x, y, r = p[0], p[1], p[2]
            cv2.circle(to_paint, (x, y), r, color, -1)
    return to_paint


def match_template(source: cv2.typing.MatLike, template: cv2.typing.MatLike, threshold,
                   mask: np.ndarray = None, ignore_inf: bool = False) -> MatchResultList:
    """
    在原图中匹配模板
    :param source: 原图
    :param template: 模板
    :param threshold: 阈值
    :param mask: 掩码
    :param ignore_inf: 是否忽略无限大的结果
    :return: 所有匹配结果
    """
    ty, tx = template.shape[1], template.shape[0]
    # 进行模板匹配
    result = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED, mask=mask)

    match_result_list = MatchResultList()
    filtered_locations = np.where(np.logical_and(
        result >= threshold,
        np.isfinite(result) if ignore_inf else np.ones_like(result))
    )  # 过滤低置信度的匹配结果

    # 遍历所有匹配结果，并输出位置和置信度
    for pt in zip(*filtered_locations[::-1]):
        confidence = result[pt[1], pt[0]]  # 获取置信度
        match_result_list.append(MatchResult(confidence, pt[0], pt[1], tx, ty))

    return match_result_list


def find_max_circle(image, show_result: bool = False):
    """
    在图形中找到最大的圆
    :param image: 原图
    :param show_result: 是否显示结果
    :return: 圆的坐标半径
    """
    # 对图像进行预处理
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100, minRadius=160, maxRadius=200)

    # 如果找到了圆
    if circles is None:
        log.debug('没找到圆')
        return 0, 0, 0

    circles = np.uint16(np.around(circles))
    tx, ty, tr = 0, 0, 0

    # 保留半径最大的圆
    for circle in circles[0, :]:
        if show_result:
            cv2.circle(gray, (circle[0], circle[1]), circle[2], (0, 255, 0), 1)
        if circle[2] > tr:
            tx, ty, tr = circle[0], circle[1], circle[2]
    log.debug('匹配圆结果: %d %d %d', tx, ty, tr)

    if show_result:
        to_show = image.copy()
        cv2.circle(to_show, (tx, ty), tr, (0, 255, 0), 1)
        show_image(to_show)
        show_image(gray)
    return tx, ty, tr


def concat_vertically(img: cv2.typing.MatLike, next_img: cv2.typing.MatLike, decision_height: int = 200):
    """
    垂直拼接图片。
    假设两张图片是通过垂直滚动得到的，即宽度一样，部分内容重叠
    :param img: 图
    :param next_img: 下一张图
    :decision_height: 用第二张图的多少高度来判断重叠部分
    :return:
    """
    # 截取一个横截面用来匹配
    next_part = next_img[0: decision_height, :]
    result = match_template(img, next_part, 0.5)
    # 找出置信度最高的结果
    r = None
    for i in result:
        if r is None or i.confidence > r.confidence:
            r = i
    h, w, _ = img.shape
    overlap_h = h - r.y
    extra_part = next_img[overlap_h+1:,:]
    # 垂直拼接两张图像
    return cv2.vconcat([img, extra_part])


def is_same_image(i1, i2, threshold: float = 1) -> bool:
    """
    简单使用均方差判断两图是否一致
    :param i1: 图1
    :param i2: 图2
    :param threshold: 低于阈值认为是相等
    :return: 是否同一张图
    """
    return np.mean((i1 - i2) ** 2) < threshold



def binary_with_white_alpha(image, thresh: int = 70):
    """"""
    # 提取透明通道
    alpha_channel = image[:, :, 3]
    # 将图像转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 将透明通道中的非零值设置为白色
    gray[alpha_channel == 0] = 255
    # 二值化模板图像
    _, binary = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)
    return binary


def show_overlap(source, template, x, y, template_scale: float = 1, win_name: str = 'DEBUG', wait: int = 1):
    to_show_source = source.copy()

    if template_scale != 1:
        # 缩放后的宽度和高度
        scaled_width = int(template.shape[1] * template_scale)
        scaled_height = int(template.shape[0] * template_scale)

        # 缩放小图
        to_show_template = cv2.resize(template, (scaled_width, scaled_height))
    else:
        to_show_template = template

    # 获取要覆盖图像的宽度和高度
    overlay_height, overlay_width = to_show_template.shape[:2]

    # 覆盖图在原图上的坐标
    sx_start = int(x)
    sy_start = int(y)
    sx_end = sx_start + overlay_width
    sy_end = sy_start + overlay_height

    # 覆盖图要用的坐标
    tx_start = 0
    ty_start = 0
    tx_end = to_show_template.shape[1]
    ty_end = to_show_template.shape[0]

    # 覆盖图缩放后可以超出了原图的范围
    if sx_start < 0:
        tx_start -= sx_start
        sx_start -= sx_start
    if sx_end > to_show_source.shape[1]:
        tx_end -= sx_end - to_show_source.shape[1]
        sx_end -= sx_end - to_show_source.shape[1]

    if sy_start < 0:
        ty_start -= sy_start
        sy_start -= sy_start
    if sx_end > to_show_source.shape[0]:
        ty_end -= sy_end - to_show_source.shape[0]
        sy_end -= sy_end - to_show_source.shape[0]

    # 将覆盖图像放置到底图的指定位置
    to_show_source[sy_start:sy_end, sx_start:sx_end] = to_show_template[ty_start:ty_end, tx_start:tx_end]
    show_image(to_show_source, win_name=win_name, wait=wait)