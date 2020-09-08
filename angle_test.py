import ljcnb as lj
import numpy as np
import math
import cmath

def ola2arr(theta):   #旋转顺序 
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
    R_xyz = np.dot(np.dot(R_x, R_y), R_z)   #xyz
    return(R_zxy)

def main():
    arr1 = [-81.8176,-0.657773,3.82069]
    # arr1 = [30,0,0]
    # arr1 = [0,0,30]
    arr1 = np.array(arr1) * np.pi / 180
    R1 = ola2arr(arr1)
    X_axis = [1,0,0]
    Y_axis = [0,1,0]
    Z_axis = [0,0,1]
    x_o = np.dot(X_axis,R1) 
    y_o = np.dot(Y_axis,R1) 
    z_o = np.dot(Z_axis,R1) 
    print(x_o,y_o,z_o)
    x_abs=math.sqrt(pow(x_o[0],2)+pow(x_o[1],2)+pow(x_o[2],2))
    y_abs=math.sqrt(pow(y_o[0],2)+pow(y_o[1],2)+pow(y_o[2],2)) 
    z_abs=math.sqrt(pow(z_o[0],2)+pow(z_o[1],2)+pow(z_o[2],2)) 
    xz_a=np.dot(x_o,np.transpose(z_o))/(x_abs*z_abs)
    print('xz_a=',xz_a)
    yz_a=np.dot(y_o,np.transpose(z_o))/(y_abs*z_abs)
    print('yz_a=',yz_a)
    # var=-1
    # test = math.atan(var)*180/math.pi
    # print('testatan=',test)
    pitchvar1 = y_o[2]/(math.sqrt(math.pow(y_o[0],2)+math.pow(y_o[1],2)))
    pitchvar2 = z_o[1]/(math.sqrt(math.pow(z_o[0],2)+math.pow(z_o[2],2)))
    print('var=',pitchvar1,pitchvar2)
    pitch = math.atan(pitchvar1)*180/math.pi
    pitch2 = math.atan(pitchvar2)*180/math.pi
    roll = math.atan(x_o[2]/(math.sqrt(math.pow(x_o[0],2)+math.pow(x_o[1],2))))*180/math.pi
    roll2 = math.atan(z_o[0]/(math.sqrt(math.pow(z_o[2],2)+math.pow(z_o[1],2))))*180/math.pi
    roll3 = math.atan(x_o[0]/(math.sqrt(math.pow(z_o[2],2)+math.pow(z_o[1],2))))*180/math.pi
    heading = math.atan(y_o[0]/(math.sqrt(math.pow(y_o[1],2)+math.pow(y_o[2],2))))*180/math.pi
    heading2 = math.atan(x_o[1]/(math.sqrt(math.pow(y_o[0],2)+math.pow(y_o[2],2))))*180/math.pi
    print('pitch1=%f,pitch2=%f,roll1=%f,roll2=%f,roll3=%f,heading1=%f,heading2=%f' %(pitch,pitch2,roll,roll2,heading,heading2))  #LVX==>相机
    
    

    typeC_ex=[98.7,-0.03, -3.85] #右后下==》相机
    #右前上==》相机
    pitch,roll,heading = [-81.3,0.03,3.85]


main()