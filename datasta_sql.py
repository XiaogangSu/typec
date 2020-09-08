# 从sql中获取数据
import math
import os
import pandas as pd
import numpy as np
import sqlite3 as sq
import math
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']


class main():
    def __init__(self):
        print('开始处理')
        # dbname = input('输入dbname:')
        dbname = 'DB-0522'
        try:
            self.conn = sq.connect('./'+dbname+'.db')
            print('连接数据库成功！')
        except:
            print('连接失败！')
        self.cur = self.conn.cursor()
    


    def getdata(self):
        # sql = '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.GPS,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12 FROM lvx_1014001C00002200522 lvx, gps_1014002C00002200522 gps WHERE lvx.daysec = gps.GPS AND lvx.daysec > 10622.2 AND lvx.daysec < 10772.6;'''
        sql = '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvx_1014001C00002200522 lvx, gps_1014002C00002200522 gps WHERE lvx.daysec = gps.GPS and lvx.daysec > 11705.1 AND lvx.daysec < 11848.1 and rolldis<10 and rolldis>-10 and pitchdis<10 and pitchdis>-10 and headingdis>-10 and headingdis<10;'''
        a=self.cur.execute(sql)
        outputlist1 = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist1.append(var_list)
        # print(outputlist[0:2])
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','H_dis','roll_dis','pitch_dis','heading_dis']
        data_df1 = pd.DataFrame(outputlist1, columns=index)
        RMS1_h12 = math.sqrt((np.square(data_df1['h12']).sum())/len(outputlist1))
        print('RMS1_h12=', RMS1_h12)
        RMS1_H_dis = math.sqrt((np.square(data_df1['H_dis']).sum())/len(outputlist1))
        print('RMS1_H_dis=', RMS1_H_dis)
        RMS1_roll_dis = math.sqrt((np.square(data_df1['roll_dis']).sum())/len(outputlist1))
        print('RMS1_roll_dis=', RMS1_roll_dis)
        RMS1_pitch_dis = math.sqrt((np.square(data_df1['pitch_dis']).sum())/len(outputlist1))
        print('RMS1_pitch_dis=', RMS1_pitch_dis)
        RMS1_heading_dis = math.sqrt((np.square(data_df1['heading_dis']).sum())/len(outputlist1))
        print('RMS1_Heading_dis=', RMS1_heading_dis)
        
        sql = '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvx_1014001C00002200522 lvx, gps_1014002C00002200522 gps WHERE lvx.daysec = gps.GPS and lvx.daysec > 11548.4 AND lvx.daysec < 11607.4 and rolldis<10 and rolldis>-10 and pitchdis<10 and pitchdis>-10 and headingdis>-10 and headingdis<10;'''
        b=self.cur.execute(sql)
        outputlist2 = []
        for var in b:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist2.append(var_list)
        # print(outputlist[0:2])
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','H_dis','roll_dis','pitch_dis','heading_dis']
        data_df2 = pd.DataFrame(outputlist2, columns=index)
        print(np.square(data_df2['h12']).sum(),len(outputlist2))
        RMS2_h12 = math.sqrt((np.square(data_df2['h12']).sum())/len(outputlist2))
        print('RMS2_h12=', RMS2_h12)
        RMS2_H_dis = math.sqrt((np.square(data_df2['H_dis']).sum())/len(outputlist2))
        print('RMS2_H_dis=', RMS2_H_dis)
        RMS2_roll_dis = math.sqrt((np.square(data_df2['roll_dis']).sum())/len(outputlist2))
        print('RMS2_roll_dis=', RMS2_roll_dis)
        RMS2_pitch_dis = math.sqrt((np.square(data_df2['pitch_dis']).sum())/len(outputlist2))
        print('RMS2_pitch_dis=', RMS2_pitch_dis)
        RMS2_heading_dis = math.sqrt((np.square(data_df2['heading_dis']).sum())/len(outputlist2))
        print('RMS2_Heading_dis=', RMS2_heading_dis)

        sql = '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvx_1014001C00002200522 lvx, gps_1014002C00002200522 gps WHERE lvx.daysec = gps.GPS and lvx.daysec > 11193.0 AND lvx.daysec < 11267.5 and rolldis<10 and rolldis>-10 and pitchdis<10 and pitchdis>-10 and headingdis>-10 and headingdis<10;'''
        c=self.cur.execute(sql)
        outputlist3 = []
        for var in c:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist3.append(var_list)
        # print(outputlist[0:2])
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','H_dis','roll_dis','pitch_dis','heading_dis']
        data_df3 = pd.DataFrame(outputlist3, columns=index)
        print(np.square(data_df3['h12']).sum(),len(outputlist3))
        RMS3_h12 = math.sqrt((np.square(data_df3['h12']).sum())/len(outputlist3))
        print('RMS3_h12=', RMS3_h12)
        RMS3_H_dis = math.sqrt((np.square(data_df3['H_dis']).sum())/len(outputlist3))
        print('RMS3_H_dis=', RMS3_H_dis)
        RMS3_roll_dis = math.sqrt((np.square(data_df3['roll_dis']).sum())/len(outputlist3))
        print('RMS3_roll_dis=', RMS3_roll_dis)
        RMS3_pitch_dis = math.sqrt((np.square(data_df3['pitch_dis']).sum())/len(outputlist3))
        print('RMS3_pitch_dis=', RMS3_pitch_dis)
        RMS3_heading_dis = math.sqrt((np.square(data_df3['heading_dis']).sum())/len(outputlist3))
        print('RMS3_Heading_dis=', RMS3_heading_dis)
        # print(data_df3['h12'].describe())

        #绘制高程图
        plt.figure(1, figsize=(20, 25))
        plt.tight_layout()
        # figure,ax=plt.subplots(3,1)
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.boxplot([data_df1['roll_dis'],data_df2['roll_dis'],data_df3['roll_dis']],labels=['直路','弯路','坡道'])
        # plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.title('Roll误差分布', fontdict={'size':30})
        # plt.ylabel('Roll误差(°)', fontdict={'size':25})
        # plt.ylim(-0.5, 0.5)
        # plt.subplot(3,1,1)
        # plt.ylabel('椭球高(m)', fontdict={'size':25})
        # plt.title('1014001C00002200522高程分布', fontdict={'size':30})
        # x_range = np.arange(len(outputlist1))
        # # data_df['gps_del'].plot(kind='line')
        # plt.plot(x_range, data_df1['he1'].values, color='b',label='lvx') 
        # plt.plot(x_range, data_df1['he2'].values, color='r',label='m8l') 
        # plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.legend(prop = {'size':25})
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.98, bottom=0.1)
        
        sql = '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvx_1014001C00002200522 lvx, gps_1014002C00002200522 gps WHERE lvx.daysec = gps.GPS;'''
        c=self.cur.execute(sql)
        outputlist_h = []
        for var in c:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist_h.append(var_list)
        # print(outputlist[0:2])
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','H_dis','roll_dis','pitch_dis','heading_dis']
        data_df2 = pd.DataFrame(outputlist_h, columns=index)
        
        #绘制姿态角误差
        # plt.subplot(3,1,1)
        # plt.ylabel('角度误差(°)', fontdict={'size':45})
        # plt.title('Roll', fontdict={'size':50})
        # # x_range = np.arange(len(outputlist2))
        # # data_df['gps_del'].plot(kind='line')
        # plt.plot(data_df2['daysec'], data_df2['roll_dis'].values, color='b',label='lvx') 
        # # plt.plot(data_df2['daysec'], data_df2['he2'].values, color='r',label='m8l') 
        # plt.tick_params(labelsize=33)   #设置刻度大小
        # # plt.legend(prop = {'size':45})
        # plt.axvline(x=11848.1, ls='--', color='y', linewidth=3)
        # plt.axvline(x=11705.1, ls='--', color='y', linewidth=3)
        # plt.axvline(x=11548.4, ls='--', color='c', linewidth=3)
        # plt.axvline(x=11607.4, ls='--', color='c', linewidth=3)
        # plt.axvline(x=11193.1, ls='--', color='r', linewidth=3)
        # plt.axvline(x=11267.1, ls='--', color='r', linewidth=3)
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        
        # plt.subplot(3,1,2)
        # plt.ylabel('角度误差(°)', fontdict={'size':45})
        # plt.title('Pitch', fontdict={'size':50})
        # x_range = np.arange(len(outputlist2))
        # plt.ylim(5,-5)
        # # data_df['gps_del'].plot(kind='line')
        # plt.plot(data_df2['daysec'], data_df2['pitch_dis'].values, color='r',label='lvx') 
        # # plt.plot(x_range, data_df2['he2'].values, color='r',label='m8l') 
        # plt.tick_params(labelsize=33)   #设置刻度大小
        # # plt.legend(prop = {'size':25})
        # plt.axvline(x=11848.1, ls='--', color='y', linewidth=3)
        # plt.axvline(x=11705.1, ls='--', color='y', linewidth=3)
        # plt.axvline(x=11548.4, ls='--', color='c', linewidth=3)
        # plt.axvline(x=11607.4, ls='--', color='c', linewidth=3)
        # plt.axvline(x=11193.1, ls='--', color='r', linewidth=3)
        # plt.axvline(x=11267.1, ls='--', color='r', linewidth=3)
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1)
        
        # plt.subplot(3,1,3)
        # plt.ylabel('角度误差(°)', fontdict={'size':45})
        # plt.title('Heading', fontdict={'size':50})
        # x_range = np.arange(len(outputlist2))
        # # data_df['gps_del'].plot(kind='line')
        # plt.plot(data_df2['daysec'], data_df2['heading_dis'].values, color='darkorchid',label='lvx') 
        # # plt.plot(x_range, data_df2['he2'].values, color='r',label='m8l') 
        # plt.tick_params(labelsize=33)   #设置刻度大小
        # # plt.legend(prop = {'size':25})
        # plt.axvline(x=11848.1, ls='--', color='y', linewidth=3)
        # plt.axvline(x=11705.1, ls='--', color='y', linewidth=3)
        # plt.axvline(x=11548.4, ls='--', color='c', linewidth=3)
        # plt.axvline(x=11607.4, ls='--', color='c', linewidth=3)
        # plt.axvline(x=11193.1, ls='--', color='r', linewidth=3)
        # plt.axvline(x=11267.1, ls='--', color='r', linewidth=3)
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1)
        
        #绘制定位误差
        plt.subplot(3,1,1)
        plt.ylabel('椭球高(m)', fontdict={'size':45})
        plt.title('Roll', fontdict={'size':50})
        # x_range = np.arange(len(outputlist2))
        # data_df['gps_del'].plot(kind='line')
        plt.plot(data_df2['daysec'], data_df2['he1'].values, color='#E33E33',label='lvx') 
        plt.plot(data_df2['daysec'], data_df2['he2'].values, color='#050F1A',label='m8l') 
        plt.tick_params(labelsize=33)   #设置刻度大小
        plt.legend(prop = {'size':45})
        plt.axvline(x=11848.1, ls='--', color='y', linewidth=3)
        plt.axvline(x=11705.1, ls='--', color='y', linewidth=3)
        plt.axvline(x=11548.4, ls='--', color='c', linewidth=3)
        plt.axvline(x=11607.4, ls='--', color='c', linewidth=3)
        plt.axvline(x=11193.1, ls='--', color='r', linewidth=3)
        plt.axvline(x=11267.1, ls='--', color='r', linewidth=3)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        
        plt.subplot(3,1,2)
        plt.ylabel('椭球高差(m)', fontdict={'size':45})
        plt.title('Pitch', fontdict={'size':50})
        x_range = np.arange(len(outputlist2))
        # plt.ylim(5,-5)
        # data_df['gps_del'].plot(kind='line')
        plt.plot(data_df2['daysec'], data_df2['h12'].values, color='#050F1A') 
        # plt.plot(x_range, data_df2['he2'].values, color='r',label='m8l') 
        plt.tick_params(labelsize=33)   #设置刻度大小
        # plt.legend(prop = {'size':25})
        plt.axvline(x=11848.1, ls='--', color='y', linewidth=3)
        plt.axvline(x=11705.1, ls='--', color='y', linewidth=3)
        plt.axvline(x=11548.4, ls='--', color='c', linewidth=3)
        plt.axvline(x=11607.4, ls='--', color='c', linewidth=3)
        plt.axvline(x=11193.1, ls='--', color='r', linewidth=3)
        plt.axvline(x=11267.1, ls='--', color='r', linewidth=3)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1)
        
        plt.subplot(3,1,3)
        plt.ylabel('水平定位误差(m)', fontdict={'size':45})
        plt.title('Heading', fontdict={'size':50})
        x_range = np.arange(len(outputlist2))
        # data_df['gps_del'].plot(kind='line')
        plt.plot(data_df2['daysec'], data_df2['H_dis'].values, color='darkorchid') 
        # plt.plot(x_range, data_df2['he2'].values, color='r',label='m8l') 
        plt.tick_params(labelsize=33)   #设置刻度大小
        # plt.legend(prop = {'size':25})
        plt.axvline(x=11848.1, ls='--', color='y', linewidth=3)
        plt.axvline(x=11705.1, ls='--', color='y', linewidth=3)
        plt.axvline(x=11548.4, ls='--', color='c', linewidth=3)
        plt.axvline(x=11607.4, ls='--', color='c', linewidth=3)
        plt.axvline(x=11193.1, ls='--', color='r', linewidth=3)
        plt.axvline(x=11267.1, ls='--', color='r', linewidth=3)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.1)

        # plt.subplot(3,1,3)
        # plt.ylabel('椭球高(m)', fontdict={'size':25})
        # plt.title('1014003C00002200522高程分布', fontdict={'size':30})
        # x_range = np.arange(len(outputlist3))
        # # data_df['gps_del'].plot(kind='line')
        # plt.plot(x_range, data_df3['he1'].values, color='b',label='lvx') 
        # plt.plot(x_range, data_df3['he2'].values, color='r',label='m8l') 
        # plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.legend(prop = {'size':25})
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        
        
        plt.savefig('./定位误差统计.jpg',bbox_inches='tight')
        

    def pro(self):
        self.getdata()
        print('处理结束！')


if __name__ == '__main__':
    ex = main()
    ex.pro()
