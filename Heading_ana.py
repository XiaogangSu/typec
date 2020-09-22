#heading 分析
import os
import sxg_python.myfun as myfun
import pdb
import math
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
import pandas as pd
import numpy as np

def ana():
    path='D:/had/data/bmwpoc/20200920'
    file = '20200920-25hz-vel.txt'
    data_list = myfun.readtxt(file, path, ' ')
    index = data_list[0]
    del data_list[0]
    Heading_output=[]
    for var in data_list:
        try:
            Heading1=float(var[4])
            v_n = float(var[2])
            v_e = float(var[1])
            v = float(var[3])
        except:
            pass
        
        if v>15:
        # try:
            if v_n ==0 and v_e>0:
                # print('test1')
                Heading2 = 90.0
            elif v_n ==0 and v_e<0:
                print('test2')
                Heading2 = 270.0
            elif v_e==0 and v_n>0:
                Heading2 = 0
            elif v_e==0 and v_n<0:
                Heading2 = 180
            elif v_n<0 and v_e<0: 
                Heading2 = 180 + 180 * math.atan(v_e/v_n)/math.pi
            elif v_n>0 and v_e>0:
                Heading2 = 180 * math.atan(v_e/v_n)/math.pi
            elif v_n>0 and v_e<0:
                Heading2 = 360 + 180 * math.atan(v_e/v_n)/math.pi
            elif v_n<0 and v_e>0:
                Heading2 = 180 + 180 * math.atan(v_e/v_n)/math.pi
            dis = Heading1-Heading2 #航向-航迹
            if dis>300:
                dis = dis-360
        # except:
        #     print(v_n)
            temp=[float(var[0]),float(var[1]),float(var[2]),float(var[3]),float(var[4]),Heading2,dis]
            Heading_output.append(temp)
        
        # print(Heading1,Heading2)
        # pdb.set_trace()
        
    # index = ['gpstime','Hgt','lat','lon','Heading1','v_e','v_n','v','Heading2','dis']
    index = ['gpstime','v_e','v_n','v','Heading1','Heading2','dis']
    data_df = pd.DataFrame(Heading_output, columns=index)
    print('航向角-航迹角均值=',data_df['dis'].mean())
    # print(data_df['dis'].describe())
    # print(data_df)
    plt.figure(1, figsize=(20, 8))
    plt.rcParams['axes.unicode_minus'] = False 
    # plt.subplot(3,1,3)
    plt.ylabel('航向角', fontdict={'size':22})
    plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
    plt.title('航向角对比', fontdict={'size':30})
    # plt.plot(data_df['gpstime'].values, data_df['Heading1'].values, color='b',label='双天线') 
    # plt.plot(data_df['gpstime'].values, data_df['Heading2'].values, color='r', label='单天线')
    plt.plot(np.arange(len(Heading_output)), data_df['dis'].values, color='r', label='航向角差') 
    plt.tick_params(labelsize=23)   #设置刻度大小
    plt.legend(prop = {'size':25})
    # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
    plt.savefig(path+'航向角.jpg',bbox_inches='tight')
    print('航向角.jpg 保存成功！')
    
    plt.figure(2, figsize=(8, 10))
    plt.rcParams['axes.unicode_minus'] = False 
    plt.ylabel('航向角误差', fontdict={'size':22})
    plt.title('航向角差', fontdict={'size':30})
    plt.boxplot([data_df['dis']],labels=['速度航向-Heading'])
    plt.tick_params(labelsize=23)   #设置刻度大小
    plt.savefig(path+'航向角箱线图.jpg',bbox_inches='tight')

    Heading_output.insert(0,index)
    myfun.savecsv(Heading_output,'output.csv', path)

ana()