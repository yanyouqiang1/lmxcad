import os
import shutil
import math
import ezdxf


def draw_single(a, b, c, d, h, n):
    # 调整顶点个数
    if c==0:
        n=n+1
    if d==0:
        n=n+1
    """Draws a single shape with specified parameters and y-offset."""
    points = []

    angleA = math.atan(a / b)
    angleB = math.pi / 2 - angleA

    A = (0, math.sin(angleA) * d)
    if d!=0:
        points.append(A)



    B = (math.cos(angleA) * d, 0)
    if d!=0:
        points.append(B)

    C = ()
    for i in range(n):
        f1 = b / math.sin(angleB)

        C = (B[0] + math.cos(angleB) * a + i * f1, math.sin(angleB) * a)
        points.append(C)
        C1 = (B[0] + f1 * (i + 1), 0)
        if i != n - 1:
            points.append(C1)

    D = (math.cos(angleA) * c + C[0], C[1] - math.sin(angleA) * c)
    points.append(D)

    f2 = h - D[1]
    E = (f2 / math.tan(angleB) + D[0], h)
    points.append(E)

    f3 = h - math.sin(angleA) * d
    F = (math.tan(angleA) * f3, h)
    points.append(F)

    return points


def draw_multiple(data, output_dir="dxf"):
    """Draws multiple shapes, saving each to a separate DXF file in a specified directory.
       Clears the directory before saving.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Clear the contents of the output directory
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        try:
            if os.path.isfile(file_path):  # Only delete files, not directories
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    for i, (a, b, c, d, h, n) in enumerate(data):
        doc = ezdxf.new()
        msp = doc.modelspace()
        points = draw_single(a, b, c, d, h, n)
        msp.add_lwpolyline(points, close=True)
        filename = os.path.join(output_dir, f"lmx{i + 1}.dxf")

        doc.saveas(filename)


# a 步高
# b 步宽
# c 右边多余
# d 左边多余
# h 总高度
# n 顶点个数
# Example usage with multiple sets of parameters:
data = [
  [
    167.8,
    260,
    20,
    50,
    280,
    8
  ],
  [
    167.8,
    250,
    30,
    15,
    260,
    5
  ],
  [
    167.2,
    242.5,
    20,
    30,
    250,
    5
  ],
  [
    167.2,
    257.1,
    20,
    30,
    250,
    8
  ],
  [
    167.2,
    252,
    20,
    15,
    245,
    5
  ],
  [
    166.1,
    245,
    30,
    20,
    250,
    5
  ],
  [
    166.1,
    257.1,
    20,
    0,
    270,
    8
  ],
  [
    166.1,
    253.5,
    30,
    0,
    250,
    5
  ]
]

draw_multiple(data)
