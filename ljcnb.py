import numpy as np
import math

def RotationMatrixToEulerAngles(R):
    sy = math.sqrt(R[2, 0] * R[2, 0] + R[2, 2] * R[2, 2])
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(R[2, 1], sy)
        y = math.atan2(-R[2, 0], R[2, 2])
        z = math.atan2(-R[0, 1], R[1, 1])   # 矩阵按Z-X-Y的顺序计算角度 yxz
    # else:
    #     x = math.atan2(-R[1, 2], R[1, 1])
    #     y = math.atan2(-R[2, 0], sy)
    #     z = 0
    return(np.array([x, y, z]) * 180 / math.pi)  # 输出pitch、roll、heading

def a(theta):   #旋转顺序 
    # [R_x, R_y, R_z] = theta
    R_x = np.array([[1, 0, 0],
                    [0, math.cos(theta[0]), -math.sin(theta[0])],
                    [0, math.sin(theta[0]), math.cos(theta[0])]
                    ])
    R_y = np.array([[math.cos(theta[1]), 0, math.sin(theta[1])],
                    [0, 1, 0],
                    [-math.sin(theta[1]), 0, math.cos(theta[1])]
                    ])
    R_z = np.array([[math.cos(theta[2]), -math.sin(theta[2]), 0],
                    [math.sin(theta[2]), math.cos(theta[2]), 0],
                    [0, 0, 1]
                    ])
    R_zxy = np.dot(np.dot(R_z, R_x), R_y)   #绕轴顺序为Z-X-Y  
    R_zyx = np.dot(np.dot(R_z, R_y), R_x)   #绕轴顺序为Z-X-Y
    # R1=np.array([[0,     1,          0],
    #     [0,     0,  1],
    #     [1,     0,   0]])
    # R_NED_ENU = np.array([[1,      0,          0],
    #                       [0,     0.01745241,  0.9998477],
    #                       [0,     -0.9998477,   0.01745241]])
    
    # R3 = np.dot(R1,R)
    # print('R:',R)
    return((R_zxy,R_zyx))

# cam2f9k = np.array([82.78,1.88,0]) * np.pi / 180
# cam2f9k = np.array([84.427,2.025,0]) * np.pi / 180

#lvx到相机旋转顺序：ZXY
def finalcom(A1,A2):  #A1转到A2的欧拉角
    cam2f9k = np.array(A2) * np.pi / 180
    R =a(cam2f9k)
    # lvx2cam = np.array([-82.0207,0.173103,0.306117]) * np.pi / 180
    lvx2cam = np.array(A1) * np.pi / 180
    A =a(lvx2cam)
    final=np.dot(R,A)
    prh = RotationMatrixToEulerAngles(np.array(final))
    return(prh)  #pitch\roll\heading

def finalcom_1(A1,A2):  
    cam2f9k = np.array(A2) * np.pi / 180
    R =a(cam2f9k)
    R_ni = np.linalg.inv(R)
    # lvx2cam = np.array([-82.0207,0.173103,0.306117]) * np.pi / 180
    lvx2cam = np.array(A1) * np.pi / 180
    A =a(lvx2cam)
    final=np.dot(A,R_ni)
    prh = RotationMatrixToEulerAngles(np.array(final))
    return(prh)  #pitch\roll\heading
