import os
import math
import ezdxf
from ezdxf.math import Matrix44

def draw_single(a, b, c, d, h, n):
    """
    根据指定的参数绘制单个形状。

    参数:
        a (float): 步高
        b (float): 步宽
        c (float): 右边多余
        d (float): 左边多余
        h (float): 总高度
        n (int): 顶点个数

    返回:
        list: 构成形状的点列表
    """
    points = []

    # 防止 a 或 b 为零导致数学错误
    if b == 0 or a == 0:
        print(f"警告: 参数 a 或 b 为零，跳过计算。")
        return []

    angleA = math.atan(a / b)
    angleB = math.pi / 2 - angleA

    # 防止 angleB 接近零导致 sin(angleB) 为零
    if math.isclose(math.sin(angleB), 0):
        print(f"警告: 计算出的角度无效 (b/a 太小)，跳过计算。")
        return []

    A = (0, math.sin(angleA) * d)
    points.append(A)

    B = (math.cos(angleA) * d, 0)
    points.append(B)

    C = () # 初始化C
    for i in range(n):
        f1 = b / math.sin(angleB)

        C = (B[0] + math.cos(angleB) * a + i * f1, math.sin(angleB) * a)
        points.append(C)
        C1 = (B[0] + f1 * (i + 1), 0)
        if i != n - 1:
            points.append(C1)

    # 确保C已被定义
    if not C:
        C = B # 如果循环未执行，将C设置为B

    D = (math.cos(angleA) * c + C[0], C[1] - math.sin(angleA) * c)
    points.append(D)

    # 防止 tan(angleB) 为零
    if math.isclose(math.tan(angleB), 0):
        E = (D[0], h)
    else:
        f2 = h - D[1]
        E = (f2 / math.tan(angleB) + D[0], h)
    points.append(E)

    # 防止 tan(angleA) 为零
    if math.isclose(math.tan(angleA), 0):
         F = (0, h)
    else:
        f3 = h - math.sin(angleA) * d
        # 确保分母不为零
        if math.isclose(math.tan(angleA), 0):
             F = (0, h)
        else:
             F = (f3 / math.tan(angleA), h)
    points.append(F)


    return points


def draw_multiple_in_one_file(data, output_file="all_shapes.dxf", x_offset=5000, y_offset=0, text_height=100):
    """
    将多个图形绘制到单个DXF文件中，并在每个图形旁边添加编号。

    参数:
        data (list): 包含多个图形参数的列表
        output_file (str): 输出的DXF文件名
        x_offset (float): 每个图形在x轴上的间距
        y_offset (float): 每个图形在y轴上的间距
        text_height (float): 编号文本的高度
    """
    doc = ezdxf.new()
    msp = doc.modelspace()

    # 初始偏移量
    current_x = 0
    current_y = 0

    for i, params in enumerate(data):
        # 解包参数
        a, b, c, d, h, n = params

        # 绘制单个图形
        points = draw_single(a, b, c, d, h, n)

        if not points:
            print(f"跳过第 {i + 1} 个图形，因为参数无效。")
            continue

        # 为当前图形创建平移矩阵
        transform = Matrix44.translate(current_x, current_y, 0)

        # 平移图形的点并添加到模型空间
        transformed_points = list(transform.transform_vertices(points))
        msp.add_lwpolyline(transformed_points, close=True)

        # 在图形旁边添加编号
        # **这里是修正的部分**
        text_position = (current_x, current_y - text_height * 2) # 将文本放在图形下方
        msp.add_text(
            f"{i + 1}号",
            dxfattribs={
                'style': 'Standard',
                'height': text_height,
                'insert': text_position  # 使用 'insert' 属性直接指定位置
            }
        )

        # 更新下一个图形的偏移量
        current_x += x_offset
        current_y += y_offset

    # 保存到单个DXF文件
    doc.saveas(output_file)
    print(f"所有图形已成功保存到 {output_file}")


# a 步高
# b 步宽
# c 右边多余
# d 左边多余
# h 总高度
# n 顶点个数
# 示例数据:
data = [
  [
    164.44,
    252.22,
    30,
    70,
    250,
    10
  ],
  [
    173,
    251,
    0,
    70,
    250,
    13
  ],
  [
    173,
    251,
    70,
    70,
    250,
    13
  ]
]

# 调用优化后的函数
draw_multiple_in_one_file(data, output_file="lmx_combined.dxf")