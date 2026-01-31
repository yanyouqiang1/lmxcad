import math
import array
from pyautocad import Autocad, APoint

def create_stairs_drawing():
    # 1. 连接到 AutoCAD
    acad = Autocad(create_if_not_exists=True)
    print(f"已连接到 AutoCAD: {acad.doc.Name}")

    # 数据源 [a(步高), b(步宽), c(右边多余), d(左边多余), h(总高度), n(顶点个数)]
    data = [
        [151.2, 250, 60, 70, 290, 14],
        [151.2, 253.3, 70, 60, 280, 10],
        [156, 253.3, 70, 60, 260, 10],
        [155, 253.3, 30, 60, 260, 10]
    ]

    # 绘图参数
    base_x = 0.0
    base_y = 0.0
    gap = 1000.0  # 图形垂直间距
    
    # 标注偏移距离
    dim_offset = 50.0 

    for i, (a, b, c, d, h, n) in enumerate(data):
        print(f"正在绘制第 {i+1} 个图形 (a={a}, b={b})...")
        
        points = [] # 用于存储所有顶点坐标 (x, y)
        
        # --- 计算几何参数 ---
        angleA = math.atan(a / b)
        angleB = math.pi / 2 - angleA
        f1 = b / math.sin(angleB)

        # --- 生成顶点 ---
        
        # 1. 左侧小边 (d)
        # A: 左上
        pt_A = (base_x + 0, base_y + math.sin(angleA) * d)
        if d != 0:
            points.append(pt_A)
        
        # B: 左下
        pt_B = (base_x + math.cos(angleA) * d, base_y + 0)
        if d != 0:
            points.append(pt_B)
        else:
            # 如果d=0，起点B就是(0,0)偏移位置
            pt_B = (base_x, base_y)
            # A点不存在，但为了后续逻辑，可以将A视为B
            pt_A = pt_B

        # 2. 锯齿部分
        # 我们需要记录最后几个点用于标注
        last_C = None     # 最后一个齿尖
        last_C1 = None    # 最后一个齿谷 (倒数第二个点)
        second_last_C = None # 倒数第二个齿尖

        # 当前参考点 (初始为B的x坐标，但要在局部坐标系计算)
        current_x_rel = pt_B[0] - base_x
        
        for k in range(n):
            # C: 齿尖 (向上)
            # 相对B的偏移计算
            cx = current_x_rel + math.cos(angleB) * a + k * f1
            cy = math.sin(angleB) * a
            C = (base_x + cx, base_y + cy)
            
            points.append(C)
            
            # 更新关键点记录
            second_last_C = last_C
            last_C = C

            # C1: 齿谷 (向下回到 y=0)
            if k != n - 1:
                c1x = current_x_rel + f1 * (k + 1)
                c1y = 0
                C1 = (base_x + c1x, base_y + c1y)
                points.append(C1)
                last_C1 = C1

        # 3. 右侧小边 (c)
        # D: 右下
        # D点连接在最后一个C点之后
        dx = math.cos(angleA) * c + (last_C[0] - base_x)
        dy = (last_C[1] - base_y) - math.sin(angleA) * c
        pt_D = (base_x + dx, base_y + dy)
        points.append(pt_D)

        # 4. 顶部闭合
        # E: 右上
        f2 = h - (pt_D[1] - base_y)
        ex = f2 / math.tan(angleB) + (pt_D[0] - base_x)
        ey = h
        pt_E = (base_x + ex, base_y + ey)
        points.append(pt_E)

        # F: 左上
        f3 = h - math.sin(angleA) * d
        fx = math.tan(angleA) * f3
        fy = h
        pt_F = (base_x + fx, base_y + fy)
        points.append(pt_F)

        # --- 绘制多段线 ---
        flat_points = []
        for p in points:
            flat_points.extend([p[0], p[1]])
        
        poly = acad.model.AddLightWeightPolyline(array.array('d', flat_points))
        poly.Closed = True

        # --- 添加标注 ---
        
        # 转换坐标为 APoint 对象
        ap_A = APoint(*pt_A)
        ap_B = APoint(*pt_B)
        ap_D = APoint(*pt_D)
        ap_E = APoint(*pt_E)
        ap_F = APoint(*pt_F)
        ap_last_C = APoint(*last_C)
        
        # 1. 顶部总长 (红色)
        dim_top = acad.model.AddDimAligned(ap_F, ap_E, APoint((pt_F[0]+pt_E[0])/2, pt_F[1] + 100))
        dim_top.Color = 1 # Red

        # 2. 右侧总高度 (垂直线性标注)
        # 使用 AddDimRotated 替代 AddDimLinear
        # 参数: (点1, 点2, 标注线位置, 旋转角度)
        # 角度: math.pi/2 表示垂直标注
        dim_h_pos = APoint(pt_E[0] + 100, base_y + h/2)
        pt_E_bottom = APoint(pt_E[0], base_y) # E在底部的投影点
        dim_h = acad.model.AddDimRotated(pt_E_bottom, ap_E, dim_h_pos, math.pi/2)
        dim_h.Color = 1

        # 3. 左侧小边 d (如果存在)
        if d != 0:
            dim_d = acad.model.AddDimAligned(ap_A, ap_B, APoint(pt_A[0] - 40, pt_A[1] - 20))
            dim_d.Color = 1

        # 4. 右侧小边 c
        # 对应最后一段 C -> D
        dim_c = acad.model.AddDimAligned(ap_last_C, ap_D, APoint(pt_D[0] + 40, pt_D[1] - 20))
        dim_c.Color = 1

        # 5. 锯齿细节 (a 和 b)
        # 我们标注倒数第二个完整的齿，避免和c边冲突
        # 需要点: second_last_C (上一个齿尖) -> last_C1 (齿谷) -> last_C (当前齿尖)
        if last_C1 and second_last_C:
            ap_sec_C = APoint(*second_last_C)
            ap_last_C1 = APoint(*last_C1)
            
            # 标注 b (下坡长边): second_last_C -> last_C1
            dim_b = acad.model.AddDimAligned(ap_sec_C, ap_last_C1, APoint((pt_D[0]+pt_A[0])/2, base_y - 150))
            # 为了让标注线好看，通常放在线条外侧。因为是锯齿，放在内部容易重叠，这里尝试放在斜线下方
            dim_b.TextPosition = APoint((second_last_C[0]+last_C1[0])/2 + 20, (second_last_C[1]+last_C1[1])/2 + 20)
            dim_b.Color = 1

            # 标注 a (上坡短边): last_C1 -> last_C
            dim_a = acad.model.AddDimAligned(ap_last_C1, ap_last_C, APoint((last_C1[0]+last_C[0])/2 - 20, (last_C1[1]+last_C[1])/2 + 20))
            dim_a.Color = 1
        
        # --- 添加编号文字 ---
        label_text = f"{i + 1}号" # 2号, 3号...
        label_pos = APoint(base_x - 400, base_y + h/2)
        text_obj = acad.model.AddText(label_text, label_pos, 80) # 字高80
        text_obj.Color = 7 # White

        # 更新下一次绘制的Y轴基准 (向下移动)
        base_y -= (h + gap)

    print("绘制完成！")

if __name__ == "__main__":
    try:
        create_stairs_drawing()
    except Exception as e:
        print("发生错误:", e)