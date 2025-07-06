import os
import shutil
import math
import ezdxf

def draw_single(a, b, c, d, h, n):
    """Draws a single shape with specified parameters."""
    points = []

    angleA = math.atan(a / b)
    angleB = math.pi/2 - angleA

    # 初始点
    A = (0, math.sin(angleA)*d)
    points.append(A)
    B = (math.cos(angleA)*d, 0)
    points.append(B)

    # 生成中间点
    f1 = b / math.sin(angleB)
    for i in range(n):
        Cx = B[0] + math.cos(angleB)*a + i*f1
        Cy = math.sin(angleB)*a
        points.append((Cx, Cy))
        
        if i != n-1:
            C1x = B[0] + f1*(i+1)
            points.append((C1x, 0))

    # 右侧结构
    last_point = points[-1]
    Dx = math.cos(angleA)*c + last_point[0]
    Dy = last_point[1] - math.sin(angleA)*c
    points.append((Dx, Dy))

    # 顶部结构
    f2 = h - Dy
    Ex = Dx + f2/math.tan(angleB)
    points.append((Ex, h))

    # 最后闭合点
    f3 = h - math.sin(angleA)*d
    Fx = math.tan(angleA)*f3
    points.append((Fx, h))

    return points

def draw_multiple(data, output_dir="dxf"):
    """Draws multiple shapes into a single DXF file with labels."""
    # 创建输出目录并清空旧文件
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    doc = ezdxf.new()
    msp = doc.modelspace()
    current_x_offset = 0
    spacing = 100  # 图形间距

    for idx, (a, b, c, d, h, n) in enumerate(data):
        # 生成图形坐标
        points = draw_single(a, b, c, d, h, n)
        if not points:
            continue

        # 计算图形尺寸
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        max_x = max(x_coords)
        min_y = min(y_coords)

        # 平移坐标
        translated = [(x + current_x_offset, y) for x, y in points]
        msp.add_lwpolyline(translated, close=True)

        # 添加标签（位于图形左下角下方）
        label_pos = (current_x_offset, min_y - 30)  # 向下偏移30单位
        msp.add_text(f"{idx+1}号", 
                    dxfattribs={
                        'height': 25,
                        'style': 'Standard'
                    }).set_pos(label_pos, align='LEFT')

        # 更新偏移量
        current_x_offset += (max_x + spacing)

    # 保存最终文件
    output_path = os.path.join(output_dir, "lmx.dxf")
    doc.saveas(output_path)

# 示例数据
data = [
    (162.36, 231.42, 0, 0, 280, 8),  # Shape 1 parameters
    (162.36, 230, 290, 0, 230, 6),  # Shape 2 parameters
    (161, 230, 0, 0, 230, 8),  # Shape 3 parameters
    (161, 232, 0, 30, 230, 6)
]

draw_multiple(data)
