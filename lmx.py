import math
import ezdxf

def draw(a,b,c,d,h,n):
    points = []

    angleA = math.atan(a / b)
    angleB = math.pi/2-angleA

    A = (0,math.sin(angleA)*d)
    points.append(A)

    B = (math.cos(angleA)*d,0)
    points.append(B)

    C = ()
    for i in range(n):
        f1 = b/math.sin(angleB)
    
        C = (B[0]+math.cos(angleB)*a+i*f1,math.sin(angleB)*a)
        points.append(C)
        C1 = (B[0]+f1*(i+1),0)
        if i!=n-1:
            points.append(C1)

    D = (math.cos(angleA)*c+C[0],C[1]-math.sin(angleA)*c)
    points.append(D)

    f2 = h-D[1]
    E = (f2/math.tan(angleB)+D[0],h)
    points.append(E)

    f3 = h - math.sin(angleA)*d
    F = (math.tan(angleA)*f3,h)
    points.append(F)

    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_lwpolyline(points, close=True)
    doc.saveas('lmx.dxf')

# 三角形高度
a = 187
# 三角形宽度
b = 244
# 右边多余
c=40
# 左边多余
d=340
# 三角形顶点个数
n=8
# 高度
h=260

data = [
    (181, 217.5, 120, 50, 240, 5),  # Shape 1 parameters
    (177.5, 140, 0, 140, 240, 2),  # Shape 2 parameters
    (180, 220, 30, 110, 230, 5) # Shape 3 parameters
]



draw(a,b,c,d,h,n)
