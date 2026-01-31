import ezdxf
import math

def draw_single(a, b, c, d, h, n):
    """
    计算图形顶点坐标。
    """
    points = []

    angleA = math.atan(a / b)
    angleB = math.pi / 2 - angleA

    # Point A (左上角凸起起点)
    # 只有当 d != 0 时，才会有 A 点
    if d != 0:
        A = (0, math.sin(angleA) * d)
        points.append(A)

    # Point B (左下角转折点 / 起始点)
    # 无论 d 是否为 0，B 点都是锯齿开始上升的基准点
    # 如果 d=0, B 就是 (0,0)
    B = (math.cos(angleA) * d, 0)
    points.append(B) 

    # 生成中间的锯齿
    C = ()
    for i in range(n):
        f1 = b / math.sin(angleB)

        # 峰顶点 (C)
        # 从 B 点开始推算
        C = (B[0] + math.cos(angleB) * a + i * f1, math.sin(angleB) * a)
        points.append(C)
        
        # 谷底点 (C1) - 只要不是最后一个峰，就需要加谷底
        if i != n - 1:
            C1 = (B[0] + f1 * (i + 1), 0)
            points.append(C1)

    # Point D (右侧倒数第二个转折)
    D = (math.cos(angleA) * c + C[0], C[1] - math.sin(angleA) * c)
    points.append(D)

    # Point E (右上)
    f2 = h - D[1]
    E = (f2 / math.tan(angleB) + D[0], h)
    points.append(E)

    # Point F (左上)
    f3 = h - math.sin(angleA) * d
    F = (math.tan(angleA) * f3, h)
    points.append(F)

    return points

def setup_dimstyle(doc):
    """设置红色标注样式"""
    if "RED_DIM" not in doc.dimstyles:
        dimstyle = doc.dimstyles.new("RED_DIM")
        dimstyle.dxf.dimclrt = 1  # 红色文字
        dimstyle.dxf.dimclrd = 1  # 红色尺寸线
        dimstyle.dxf.dimclre = 1  # 红色尺寸界线
        dimstyle.dxf.dimtxt = 12.0  # 文字高度
        dimstyle.dxf.dimasz = 8.0   # 箭头大小
        dimstyle.dxf.dimexe = 5.0   # 超出量
        dimstyle.dxf.dimexo = 3.0   # 偏移量
        dimstyle.dxf.dimdec = 4     # 精度

def draw_all_in_one(data, output_filename="result.dxf"):
    doc = ezdxf.new()
    setup_dimstyle(doc)
    msp = doc.modelspace()

    # 定义中文字体
    if "SimSun" not in doc.styles:
        doc.styles.new("SimSun", dxfattribs={"font": "simsun.ttc"})

    current_offset_y = 0
    spacing = 400  # 图形垂直间距

    for idx, (a, b, c, d, h, n) in enumerate(data):
        # 1. 计算点并应用垂直偏移
        raw_points = draw_single(a, b, c, d, h, n)
        points = [(p[0], p[1] + current_offset_y) for p in raw_points]

        # 2. 绘制多段线
        msp.add_lwpolyline(points, close=True)

        # 3. 添加序号文字
        text_x = points[0][0] - 250
        text_y = points[0][1] + h / 2
        msp.add_text(
            f"{idx + 1}号", 
            dxfattribs={'style': 'SimSun', 'height': 60, 'color': 7}
        ).set_placement((text_x, text_y))

        # === 智能判断索引位置 ===
        has_left_stub = (d != 0)
        idx_B = 1 if has_left_stub else 0
        idx_Peak1 = idx_B + 1
        idx_Valley1 = idx_B + 2

        # --- 标注 1: 左边 (d) ---
        if has_left_stub:
            # 标注 A -> B
            msp.add_aligned_dim(
                p1=points[0], p2=points[1], distance=30,
                dimstyle="RED_DIM"
            ).set_text_format(user_text=f"{d:.4f}")  # 修改处：text -> user_text

        # --- 标注 2: 步高 (a) ---
        # 标注 B -> Peak1
        if idx_Peak1 < len(points):
            dim_a = msp.add_aligned_dim(
                p1=points[idx_B], p2=points[idx_Peak1], distance=30,
                dimstyle="RED_DIM"
            )
            dim_a.set_text_format(user_text=f"{a:.4f}") # 修改处：text -> user_text

        # --- 标注 3: 步宽 (b) ---
        # 标注 Peak1 -> Valley1 (如果存在谷底)
        if idx_Valley1 < len(points) - 3: 
            dim_b = msp.add_aligned_dim(
                p1=points[idx_Peak1], p2=points[idx_Valley1], distance=30,
                dimstyle="RED_DIM"
            )
            dim_b.set_text_format(user_text=f"{b:.4f}") # 修改处：text -> user_text

        # --- 标注 4: 右边 (c) ---
        # D点是倒数第3个点 points[-3]
        # 连接D点的是 points[-4]
        if len(points) > 4:
            p_D = points[-3]
            p_pre_D = points[-4]
            dim_c = msp.add_aligned_dim(
                p1=p_pre_D, p2=p_D, distance=30,
                dimstyle="RED_DIM"
            )
            dim_c.set_text_format(user_text=f"{c:.4f}") # 修改处：text -> user_text

        # --- 标注 5: 总高 (h) ---
        # 使用线性标注 (add_linear_dim)
        x_max = points[-2][0]
        base_x = x_max + 150
        
        msp.add_linear_dim(
            base=(base_x, current_offset_y + h/2), 
            p1=(x_max, current_offset_y),          
            p2=(x_max, current_offset_y + h),      
            dimstyle="RED_DIM",
            angle=90 
        ).set_text_format(user_text=f"{h:.4f}") # 修改处：text ->                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         

        # --- 标注 6: 版宽 (顶部宽度) ---
        p_F = points[-1]
        p_E = points[-2]
        
        msp.add_linear_dim(
            base=(0, current_offset_y + h + 80), 
            p1=p_F,
            p2=p_E,
            dimstyle="RED_DIM"
        ) # 版宽不需要强制文字，默认显示真实距离

        # 更新下一张图的位置
        current_offset_y -= (h + spacing)

    doc.saveas(output_filename)
    print(f"成功生成文件: {output_filename}")

# 数据测试
data = [
  [190, 230, 110, 50, 260, 3], 
  [198, 230, 30, 0, 260, 5]    
]

if __name__ == '__main__':
    draw_all_in_one(data, "output_shapes.dxf")