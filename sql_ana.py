# 从sql中获取数据
import math
import os
import pandas as pd
import numpy as np
import sqlite3 as sq
import math
import matplotlib.pyplot as plt
import pdb
import ljcnb as lj
from tkinter import filedialog as fd
plt.rcParams['font.sans-serif'] = ['SimHei']

class main():
    def __init__(self):
        print('开始处理')
        # dbname = input('输入dbname:')
        # self.path = 'E:/920POC/pro/'   #工程所在目录
        path_1=fd.askdirectory(initialdir = "D:/had/data/",title = '选择工程目录')
        self.savepath = path_1+'_anaoutput/'
        
        self.path = path_1+'/'
        # print(self.path)
        # self.path = 'F:/810POC/0006-C00001-200807'
        # dbname = 'DB-0006-C00001-200807'
        proname_all=self.path.split('/')[-2]
        # print(proname_all)
        dbname = 'DB-'+proname_all
        # dbname = 'DB-wuhan_ceshi'
        # typeC_ex = [82.78,1.88,0]  #自研设备本身的外参 pitch\roll\heading
        # typeC_ex=[81.3,-0.03, -3.85]
        typeC_ex=[98.7,-0.03, -3.85]
        
        #-0.0317144 -80.9005 3.8597
        # typeC_ex=[0,-0.03,0]
        # lvx_ex = [-82.8613,0.129664,0.665626]  #lvx到相机的外参 pitch\roll\heading
        # lvx_ex = [-82.82561,0.13345,0.43481]
        # lvx_ex = [-84.1138,-0.0663615,1.61433]
        lvx_ex = [-81.8176,-0.657773,3.82069]
        # lvx_ex = [0,-0.0663615,0]
        # lvx_ex = [-82.8283,0.0503643,0.466366]
        # arr1 = lj.finalcom_1(lvx_ex,typeC_ex)
        # print('arr1:',arr1)
        # zaiti_arr = [180,0,0]
        # arr2 = lj.finalcom(arr1,zaiti_arr)
        # print('arr2:',arr2)

        # self.sys_prh = lj.finalcom(lvx_ex,typeC_ex)  #输出 pitch\roll\heading
        # self.sys_prh = [0.66475, 0.8507,0]
        # self.sys_prh = [9.957097,2.219587,-3.3297] #5号车第一次
        self.sys_prh = [10.90996, -0.2109, -0.7789]
        print('self.sysprh:',self.sys_prh)
        # self.sys_rph = [1.89611357,-0.08131809,0.53698999]  #roll\pitch\heading
        # self.savepath = './'+dbname
        self.RMS = []
        # if os.path.isdir(self.savepath):
        #     pass
        # else:
        #     os.mkdir(self.savepath)
        try:
            self.conn = sq.connect(self.savepath+dbname+'.db')
            print('连接数据库成功！')
        except:
            print('连接失败！')
        # pdb.set_trace()
        self.cur = self.conn.cursor()
    
    #绘制所有工程的gps与真值高程图
    def h12(self, proname_raw):
        proname = proname_raw.replace('-','')
        gpstab = 'gps_'+proname
        lvxtab = 'lvx_'+proname
        sql= '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS;'''
        sql = sql.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab)
        a=self.cur.execute(sql)
        outputlist = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist.append(var_list)
        # print(outputlist[0:2])
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','H_dis']
        data_df = pd.DataFrame(outputlist, columns=index)
        plt.figure(1, figsize=(20, 8))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.subplot(3,1,3)
        plt.ylabel('椭球高(m)', fontdict={'size':22})
        plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        plt.title(proname+'-高程分布', fontdict={'size':30})
        plt.plot(data_df['daysec'].values, data_df['he1'].values, color='b',label='lvx') 
        plt.plot(data_df['daysec'].values, data_df['he2'].values, color='r',label='F9K') 
        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.legend(prop = {'size':25})
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        plt.savefig(self.savepath+'/'+proname+'椭球高与真值对比图.jpg',bbox_inches='tight')
        print(proname+'椭球高与真值对比图.jpg 保存成功！')
        # h12_RMS = math.sqrt((np.square(data_df['H_dis']).sum())/len(outputlist))
        plt.cla()
        # return(h12_RMS)

    #绘制误差分布与参考指标之间的关系
    def locrelation_rms(self, proname_raw):
        proname = proname_raw.replace('-','')
        print('处理工程：',proname_raw)
        gpstab = 'gps_'+proname
        lvxtab = 'lvx_'+proname
        sql= 'SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, abs(lvx.hell - gps.[H-Ell]) AS h12,lvx.roll - gps.Roll - (%f) AS rolldis,lvx.pitch - gps.Pitch- (%f) AS pitchdis,lvx.heading - gps.Heading- (%f) AS headingdis, gps.acc,gps.speed,gps.star,gps.locmode,gps.locacc/100,gps.rollacc,gps.pitchacc,gps.hdingacc FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS;' %(self.sys_prh[1],self.sys_prh[0],self.sys_prh[2])
        sql = sql.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab)
        a=self.cur.execute(sql)
        outputlist = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))
            var_list.append(H_dis)
            outputlist.append(var_list)
        # print(outputlist[0:2])
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','ACC','SPEED','Star','LocMode','LocAcc','RollAcc','PitchAcc','HdingAcc','H_dis']
        data_df = pd.DataFrame(outputlist, columns=index)
        # print(data_df['ACC'].head())
        # pdb.set_trace()
        data_locre = pd.DataFrame(data_df, columns=['h12','H_dis','LocAcc','ACC'])
        data_locre.corr().to_csv(os.path.join(self.path,proname+'_locrelation.csv'), index=True, header=True)
        # data_angre = pd.DataFrame(data_df, columns=['roll_dis','pitch_dis','heading_dis','LocAcc','ACC','RollAcc','PitchAcc','HdingAcc'])
        # data_angre.corr().to_csv(os.path.join(self.path,proname+'_anglocrelation.csv'), index=True, header=True)
        # print(type(data_re.corr()))
        ylabelsize=40
        xlabelsize=30
        ticksize=30
        figsize=(25,60)

        fig = plt.figure(1, figsize=figsize)
        plt.rcParams['axes.unicode_minus'] = False 
        plt.title(proname, fontdict={'size': 30})
        # plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        # plt.tick_params(labelsize=23)   #设置刻度大小

        # ax1=fig.add_subplot(8,1,1)
        # ax1.set_ylabel('椭球高(m)', fontdict={'size':ylabelsize})
        # ax1.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # ax1.set_title(proname, fontdict={'size':30})
        # ax1.plot(data_df['daysec'].values, data_df['he1'].values, color='b',label='lvx') 
        # ax1.plot(data_df['daysec'].values, data_df['he2'].values, color='r',label='m8l') 
        # ax1.legend(prop = {'size':ticksize})
        # ax1.tick_params(labelsize=30)
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        
        # 椭球高差
        # ax2=fig.add_subplot(8,1,2)
        # ax2.set_title(proname, fontdict={'size':30})
        # ax2.set_ylabel('椭球高差', fontdict={'size':ylabelsize,'color':'b'})
        # ax2.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # # plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        # # plt.title(proname+'-高程分布', fontdict={'size':30})
        # ax2.plot(data_df['daysec'].values, data_df['h12'].values, color='b',label='高差') 
        # # ax2.plot(data_df['daysec'].values, data_df['LocAcc'].values, color='r',linewidth=3,label='LocAcc') 
        # # ax2.legend()
        # ax2.tick_params(labelsize=ticksize)   #设置刻度大小
        
        ax3=fig.add_subplot(8,1,3)
        ax3.set_title(proname, fontdict={'size':30})
        ax3.set_ylabel('水平定位误差', fontdict={'size':ylabelsize,'color':'b'})
        ax3.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        ax3.plot(data_df['daysec'].values, data_df['H_dis'].values, color='b',label='水平定位误差') 
        # ax2.plot(data_df['daysec'].values, data_df['LocAcc'].values, color='r',linewidth=3,label='LocAcc')
        # ax3.legend()
        ax3.tick_params(labelsize=ticksize)
        
        # ax4=ax2.twinx()
        # # ax4=fig.add_subplot(8,1,4)
        # ax4.set_ylabel('LocACC', fontdict={'size':ylabelsize,'color':'red'})
        # # ax4.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # ax4.plot(data_df['daysec'].values, data_df['LocAcc'].values, color='r', linewidth=3) 
        # ax4.tick_params(labelsize=ticksize)

        ax4=ax3.twinx()
        # ax4=fig.add_subplot(8,1,4)
        ax4.set_ylabel('hacc', fontdict={'size':ylabelsize,'color':'red'})
        # ax4.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        ax4.plot(data_df['daysec'].values, data_df['LocAcc'].values, color='r', linewidth=3) 
        ax4.tick_params(labelsize=ticksize)

        plt.subplot(8,1,4)
        plt.ylabel('收星数', fontdict={'size':ylabelsize})
        plt.xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # plt.title(proname+'-高程分布', fontdict={'size':30})
        plt.plot(data_df['daysec'].values, data_df['Star'].values, color='b') 
        plt.tick_params(labelsize=ticksize)   #设置刻度大小

        # plt.subplot(8,1,6)
        # plt.ylabel('SPEED', fontdict={'size':22})
        # plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        # # plt.title(proname+'-高程分布', fontdict={'size':30})
        # plt.plot(data_df['daysec'].values, data_df['SPEED'].values, color='b') 
        # plt.tick_params(labelsize=23)   #设置刻度大小
     
        plt.subplot(8,1,5)
        plt.ylabel('定位模式', fontdict={'size':ylabelsize})
        plt.xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # plt.title(proname+'-高程分布', fontdict={'size':30})
        plt.plot(data_df['daysec'].values, data_df['LocMode'].values, color='b') 
        plt.tick_params(labelsize=ticksize)   #设置刻度大小

        # plt.subplot(8,1,6)
        # plt.ylabel('ACC', fontdict={'size':ylabelsize})
        # plt.xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # # plt.ylim(0.4,2)
        # # plt.title(proname+'-高程分布', fontdict={'size':30})
        # plt.plot(data_df['daysec'].values, data_df['ACC'].values, color='b') 
        # plt.tick_params(labelsize=ticksize)   #设置刻度大小
        
        plt.savefig(self.savepath+'/'+proname+'误差相关性分析.jpg',bbox_inches='tight')
        print(proname+'误差相关性分析.jpg 保存成功！')
        # h12_RMS = math.sqrt((np.square(data_df['H_dis']).sum())/len(outputlist))
        # return(h12_RMS)
        plt.clf()

     #绘制姿态角误差与参考指标之间的关系
    
    def angrelation_rms(self, proname_raw):
        proname = proname_raw.replace('-','')
        print('处理工程：',proname_raw)
        gpstab = 'gps_'+proname
        lvxtab = 'lvx_'+proname
        sql= 'SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll - (%f) AS rolldis,lvx.pitch - gps.Pitch- (%f) AS pitchdis,lvx.heading - gps.Heading- (%f) AS headingdis, gps.acc,gps.speed,gps.star,gps.locmode,gps.locacc,gps.rollacc,gps.pitchacc,gps.hdingacc FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS;' %(self.sys_prh[1],self.sys_prh[0],self.sys_prh[2])
        sql = sql.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab)
        a=self.cur.execute(sql)
        outputlist = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist.append(var_list)
        # print(outputlist[0:2])
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','ACC','SPEED','Star','LocMode','LocAcc','RollAcc','PitchAcc','HdingAcc','H_dis']
        data_df = pd.DataFrame(outputlist, columns=index)
        data_df = data_df[(data_df['heading_dis']<10)&(data_df['heading_dis']>-10)]
        # data_locre = pd.DataFrame(data_df, columns=['h12','H_dis','LocAcc','ACC'])
        # data_locre.corr().to_csv(os.path.join(self.path,proname+'_locrelation.csv'), index=True, header=True)
        
        data_angre = pd.DataFrame(data_df, columns=['roll_dis','pitch_dis','heading_dis','LocAcc','ACC','RollAcc','PitchAcc','HdingAcc'])
        data_angre.corr().to_csv(os.path.join(self.path,proname+'_anglocrelation.csv'), index=True, header=True)
        # print(type(data_re.corr()))
        ylabelsize=80
        xlabelsize=60
        ticksize=60
        figsize=(60,60)

        fig = plt.figure(1, figsize=figsize)
        plt.rcParams['axes.unicode_minus'] = False 
        plt.title(proname, fontdict={'size': 60})
        # plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        # plt.tick_params(labelsize=23)   #设置刻度大小

        # ax1=fig.add_subplot(8,1,1)
        # ax1.set_ylabel('椭球高(m)', fontdict={'size':ylabelsize})
        # ax1.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # ax1.set_title(proname, fontdict={'size':30})
        # ax1.plot(data_df['daysec'].values, data_df['he1'].values, color='b',label='lvx') 
        # ax1.plot(data_df['daysec'].values, data_df['he2'].values, color='r',label='m8l') 
        # ax1.legend(prop = {'size':ticksize})
        # ax1.tick_params(labelsize=30)
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        
        ax2=fig.add_subplot(3,1,1)
        # ax2.set_title(proname, fontdict={'size':30})
        ax2.set_ylabel('roll', fontdict={'size':ylabelsize,'color':'blue'})
        ax2.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        # plt.title(proname+'-高程分布', fontdict={'size':30})
        ax2.plot(data_df['daysec'].values, data_df['roll_dis'].values, color='b') 
        ax2.tick_params(labelsize=ticksize)   #设置刻度大小

        ax2_1 = ax2.twinx()
        ax2_1.plot(data_df['daysec'].values, data_df['RollAcc'].values, color='r', linewidth=3) 
        ax2_1.set_ylabel('RollAcc', fontdict={'size':ylabelsize,'color':'red'})
        ax2_1.tick_params(labelsize=ticksize)   #设置刻度大小
        
        ax3=fig.add_subplot(3,1,2)
        ax3.set_ylabel('pitch', fontdict={'size':ylabelsize,'color':'blue'})
        ax3.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        ax3.plot(data_df['daysec'].values, data_df['pitch_dis'].values, color='b') 
        ax3.tick_params(labelsize=ticksize)
        
        ax3_1=ax3.twinx()
        ax3_1.plot(data_df['daysec'].values, data_df['PitchAcc'].values, color='r',linewidth=3) 
        ax3_1.set_ylabel('PitchAcc', fontdict={'size':ylabelsize,'color':'red'})
        ax3_1.tick_params(labelsize=ticksize)


        ax4=fig.add_subplot(3,1,3)
        ax4.set_ylabel('heading', fontdict={'size':ylabelsize,'color':'blue'})
        ax4.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        ax4.plot(data_df['daysec'].values, data_df['heading_dis'].values, color='b') 
        ax4.tick_params(labelsize=ticksize)

        ax4_1=ax4.twinx()
        ax4_1.plot(data_df['daysec'].values, data_df['HdingAcc'].values, color='r',linewidth=3) 
        ax4_1.set_ylabel('HdingAcc', fontdict={'size':ylabelsize,'color':'red'})
        ax4_1.tick_params(labelsize=ticksize)

        # ax5=fig.add_subplot(5,1,4)
        # ax5.set_ylabel('LocACC', fontdict={'size':ylabelsize})
        # ax5.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # ax5.plot(data_df['daysec'].values, data_df['LocAcc'].values, color='b') 
        # # ax5.plot(data_df['daysec'].values, data_df['HdingAcc'].values, color='r') 
        # ax5.tick_params(labelsize=ticksize)

        # ax6=fig.add_subplot(4,1,4)
        # ax6.set_ylabel('ACC', fontdict={'size':ylabelsize})
        # ax6.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # ax6.plot(data_df['daysec'].values, data_df['ACC'].values, color='b') 
        # ax6.set_ylim(0.4,2)
        # ax6.tick_params(labelsize=ticksize)        
        
        plt.savefig(self.savepath+'/'+proname+'姿态角误差相关性分析.jpg',bbox_inches='tight')
        print(proname+'姿态角误差相关性分析.jpg 保存成功！')
        # h12_RMS = math.sqrt((np.square(data_df['H_dis']).sum())/len(outputlist))
        # return(h12_RMS)
        plt.clf()
        

    def dis_sta(self, proname_raw):
        proname = proname_raw.replace('-','')
        gpstab = 'gps_'+proname
        lvxtab = 'lvx_'+proname
        # sql= '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch  AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS and abs(lvx.X1-gps.X1)<15 and abs(lvx.Y1-gps.Y1)<15;'''

        sql= 'SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll - (%f) AS rolldis,lvx.pitch - gps.Pitch- (%f) AS pitchdis,lvx.heading - gps.Heading- (%f) AS headingdis FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS and abs(lvx.hell - gps.[H-Ell])<15 and (gps.X1-lvx.X1)*(gps.X1-lvx.X1)+(gps.Y1-lvx.Y1)*(gps.Y1-lvx.Y1)<225;' %(self.sys_prh[1],self.sys_prh[0],self.sys_prh[2])
        # sql= 'SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2,gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll - 0.66475 AS rolldis,lvx.pitch -gps.Pitch -0.8507  AS pitchdis, lvx.heading - gps.Heading AS headingdis FROM lvxtabname lvx,gpstabname gps WHERE lvx.daysec = gps.GPS and abs(lvx.X1-gps.X1)<15 and abs(lvx.Y1-gps.Y1)<15;' 
        sql = sql.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab)
        print(sql)
        # print(sql)
        # pdb.set_trace()
        a=self.cur.execute(sql)
        outputlist = []
        for var in a:
            # print('1')
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist.append(var_list)
        print('行数：',len(outputlist))
        
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','H_dis']
        data_df = pd.DataFrame(outputlist, columns=index)
        plt.figure(1, figsize=(20, 8))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.subplot(3,1,3)
        plt.ylabel('定位误差(m)', fontdict={'size':22})
        plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        plt.title(proname, fontdict={'size':30})
        plt.plot(data_df['daysec'].values, data_df['h12'].values, color='b',label='高程误差') 
        plt.plot(data_df['daysec'].values, data_df['H_dis'].values, color='r', label='水平定位误差') 
        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.legend(prop = {'size':25})
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        plt.savefig(self.savepath+'/'+proname+'定位误差.jpg',bbox_inches='tight')
        print(proname+'定位误差.jpg 保存成功！')
        plt.cla()
        h12_RMS = math.sqrt((np.square(data_df['h12']).sum())/len(outputlist))
        
        # plt.figure(2, figsize=(20, 8))
        # plt.rcParams['axes.unicode_minus'] = False 
        # # plt.subplot(3,1,3)
        # plt.ylabel('水平定位误差(m)', fontdict={'size':22})
        # plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        # plt.title(proname, fontdict={'size':30})
        # plt.plot(data_df['daysec'].values, data_df['H_dis'].values, color='b') 
        # plt.tick_params(labelsize=23)   #设置刻度大小
        # # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        # plt.savefig(self.savepath+'/'+proname+'水平定位误差.jpg',bbox_inches='tight')
        # print(proname+'水平定位误差.jpg 保存成功！')
        # plt.cla()
        Hdis_RMS = math.sqrt((np.square(data_df['H_dis']).sum())/len(outputlist))
        
        plt.figure(3, figsize=(20, 8))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.subplot(3,1,3)
        plt.ylabel('姿态角误差(m)', fontdict={'size':22})
        plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        plt.title(proname, fontdict={'size':30})
        data_df_roll = data_df[(data_df['roll_dis']<10)&(data_df['roll_dis']>-10)]
        data_df_pitch = data_df[(data_df['pitch_dis']<10)&(data_df['pitch_dis']>-10)]
        data_df_heading = data_df[(data_df['heading_dis']<10)&(data_df['heading_dis']>-10)]
        plt.plot(data_df_roll['daysec'].values, data_df_roll['roll_dis'].values, color='#0A0A0A', label='Roll') 
        plt.plot(data_df_pitch['daysec'].values, data_df_pitch['pitch_dis'].values, color='r', label='Pitch')
        plt.plot(data_df_heading['daysec'].values, data_df_heading['heading_dis'].values, color='b', label='Heading')
        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.legend(prop = {'size':25})
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        plt.savefig(self.savepath+'/'+proname+'姿态角误差.jpg',bbox_inches='tight')
        print(proname+'姿态角误差.jpg 保存成功！')
        plt.cla()
        roll_RMS = math.sqrt((np.square(data_df_roll['roll_dis']).sum())/data_df_roll.shape[0])
        pitch_RMS = math.sqrt((np.square(data_df_pitch['pitch_dis']).sum())/data_df_pitch.shape[0])
        heading_RMS = math.sqrt((np.square(data_df_heading['heading_dis']).sum())/data_df_heading.shape[0])
        
        plt.figure(4, figsize=(8, 10))
        plt.rcParams['axes.unicode_minus'] = False 
        plt.ylabel('姿态角误差(m)', fontdict={'size':22})
        plt.title(proname, fontdict={'size':30})
        plt.boxplot([data_df_roll['roll_dis'],data_df_pitch['pitch_dis'],data_df_heading['heading_dis']],labels=['Roll','Pitch','Heading'])
        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.savefig(self.savepath+'/'+proname+'姿态角误差箱线图.jpg',bbox_inches='tight')
        print(proname+'姿态角误差箱线图.jpg 保存成功！')
        plt.cla()
        return([proname, h12_RMS, Hdis_RMS, roll_RMS, pitch_RMS, heading_RMS])
    
    def dis_sta_time(self, proname_raw, mingpstime,maxgpstime):
        proname = proname_raw.replace('-','')
        gpstab = 'gps_'+proname
        lvxtab = 'lvx_'+proname
        sql= '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS and lvx.daysec<maxgpstime and lvx.daysec>mingpstime;'''
        sql = sql.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab).replace('maxgpstime', str(maxgpstime)).replace('mingpstime', str(mingpstime))
        a=self.cur.execute(sql)
        outputlist = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist.append(var_list)
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','H_dis']
        data_df = pd.DataFrame(outputlist, columns=index)

        h12_RMS = math.sqrt((np.square(data_df['h12']).sum())/len(outputlist))

        Hdis_RMS = math.sqrt((np.square(data_df['H_dis']).sum())/len(outputlist))

        data_df_roll = data_df[(data_df['roll_dis']<10)&(data_df['roll_dis']>-10)]
        data_df_pitch = data_df[(data_df['pitch_dis']<10)&(data_df['pitch_dis']>-10)]
        data_df_heading = data_df[(data_df['heading_dis']<10)&(data_df['heading_dis']>-10)]

        roll_RMS = math.sqrt((np.square(data_df_roll['roll_dis']).sum())/data_df_roll.shape[0])
        pitch_RMS = math.sqrt((np.square(data_df_pitch['pitch_dis']).sum())/data_df_pitch.shape[0])
        heading_RMS = math.sqrt((np.square(data_df_heading['heading_dis']).sum())/data_df_heading.shape[0])
        

        return([proname, mingpstime, maxgpstime, h12_RMS, Hdis_RMS, roll_RMS, pitch_RMS, heading_RMS])

    #椭球高绘制，添加scene时间段
    def scene_plot1(self,proname_raw):
        proname = proname_raw.replace('-','')
        gpstab = 'gps_'+proname
        lvxtab = 'lvx_'+proname
        sql= '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS;'''
        sql = sql.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab)
        a=self.cur.execute(sql)
        outputlist = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist.append(var_list)
        # print(outputlist[0:2])
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','H_dis']
        data_df = pd.DataFrame(outputlist, columns=index)
        plt.figure(1, figsize=(20, 8))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.subplot(3,1,3)
        plt.ylabel('椭球高(m)', fontdict={'size':22})
        plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        plt.title(proname+'-高程分布', fontdict={'size':30})
        plt.plot(data_df['daysec'].values, data_df['he1'].values, color='b',label='lvx') 
        plt.plot(data_df['daysec'].values, data_df['he2'].values, color='r',label='F9K') 
        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.legend(prop = {'size':25})
        [9500, 9750],[10372,10429],[9880,10000]
        plt.axvline(x=9500, ls='--', color='y', linewidth=3)
        plt.axvline(x=9750, ls='--', color='y', linewidth=3)
        plt.axvline(x=10372, ls='--', color='c', linewidth=3)
        plt.axvline(x=10429, ls='--', color='c', linewidth=3)
        plt.axvline(x=9800, ls='--', color='#d242d8', linewidth=3)
        plt.axvline(x=10000, ls='--', color='#d242d8', linewidth=3)
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        plt.savefig(self.savepath+'/'+proname+'椭球高与真值对比图-scene.jpg',bbox_inches='tight')
        print(proname+'椭球高与真值对比图-scene.jpg 保存成功！')
        # h12_RMS = math.sqrt((np.square(data_df['H_dis']).sum())/len(outputlist))
        plt.cla()
        # return(h12_RMS)
        
    def scene_plot2(self,proname_raw, scene1,scene2,scene3):
        proname = proname_raw.replace('-','')
        gpstab = 'gps_'+proname
        lvxtab = 'lvx_'+proname
        #场景1数据提取
        sql1= '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS and lvx.daysec<maxgpstime and lvx.daysec>mingpstime;'''
        sql1 = sql1.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab).replace('maxgpstime', str(scene1[1])).replace('mingpstime', str(scene1[0]))
        a=self.cur.execute(sql1)
        outputlist1 = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist1.append(var_list)
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','H_dis']
        data_df1 = pd.DataFrame(outputlist1, columns=index)
        #场景2数据提取
        sql2= '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS and lvx.daysec<maxgpstime and lvx.daysec>mingpstime;'''
        sql2 = sql2.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab).replace('maxgpstime', str(scene2[1])).replace('mingpstime', str(scene2[0]))
        a=self.cur.execute(sql2)
        outputlist2 = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist2.append(var_list)
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','H_dis']
        data_df2 = pd.DataFrame(outputlist2, columns=index)
        #场景3数据提取
        sql3= '''SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll AS rolldis,lvx.pitch - gps.Pitch AS pitchdis,lvx.heading - gps.Heading AS headingdis FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS and lvx.daysec<maxgpstime and lvx.daysec>mingpstime;'''
        sql3 = sql3.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab).replace('maxgpstime', str(scene3[1])).replace('mingpstime', str(scene3[0]))
        a=self.cur.execute(sql3)
        outputlist3 = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))-0.15
            var_list.append(H_dis)
            outputlist3.append(var_list)
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','H_dis']
        data_df3 = pd.DataFrame(outputlist3, columns=index)
        
        plt.figure(1, figsize=(35, 8))
        plt.rcParams['axes.unicode_minus'] = False 
        plt.subplots_adjust(wspace =0.2, hspace =0)
        # plt.suptitle('ProjectId:'+proname, fontdict={'size':40})

        plt.subplot(1,5,1)
        plt.title('椭球高差(m)', fontdict={'size':22})
        plt.boxplot([data_df1['h12'],data_df2['h12'],data_df3['h12']],labels=['直路','弯路','坡道'])
        plt.ylabel('ProjectId:'+proname, fontdict={'size':20})
        plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        # plt.savefig(self.savepath+'/'+proname+'椭球高差箱图-scene.jpg',bbox_inches='tight')
        # print(proname+'椭球高差箱图-scene.jpg 保存成功！')
        # plt.cla()
        
        plt.subplot(1,5,2)
        plt.title('水平定位误差(m)', fontdict={'size':22})
        plt.boxplot([data_df1['H_dis'],data_df2['H_dis'],data_df3['H_dis']],labels=['直路','弯路','坡道'])
        # plt.title(proname, fontdict={'size':20})
        plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        
        #航向角筛选
        data_df_heading1 = data_df1[(data_df1['heading_dis']<10)&(data_df1['heading_dis']>-10)]
        data_df_heading2 = data_df2[(data_df2['heading_dis']<10)&(data_df2['heading_dis']>-10)]
        data_df_heading3 = data_df3[(data_df3['heading_dis']<10)&(data_df3['heading_dis']>-10)]

        plt.subplot(1,5,3)
        plt.title('Roll误差(°)', fontdict={'size':22})
        plt.boxplot([data_df1['roll_dis'],data_df2['roll_dis'],data_df3['roll_dis']],labels=['直路','弯路','坡道'])
        # plt.title(proname, fontdict={'size':20})
        plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)

        plt.subplot(1,5,4)
        plt.title('Pitch误差(°)', fontdict={'size':22})
        plt.boxplot([data_df1['pitch_dis'],data_df2['pitch_dis'],data_df3['pitch_dis']],labels=['直路','弯路','坡道'])
        # plt.title(proname, fontdict={'size':20})
        plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)

        plt.subplot(1,5,5)
        plt.title('Heading误差(°)', fontdict={'size':22})
        plt.boxplot([data_df_heading1['heading_dis'],data_df_heading2['heading_dis'],data_df_heading3['heading_dis']],labels=['直路','弯路','坡道'])
        # plt.title(proname, fontdict={'size':20})
        plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        
        plt.savefig(self.savepath+'/'+proname+'场景误差箱图-scene.jpg',bbox_inches='tight')
        print(proname+'场景误差箱图-scene.jpg 保存成功！')
        plt.clf()
    
    #计算参考指标与误差相关性
    def relation(self,proname_raw):
        proname = proname_raw.replace('-','')
        gpstab = 'gps_'+proname
        lvxtab = 'lvx_'+proname
        sql= 'SELECT lvx.daysec,lvx.X1, lvx.Y1,lvx.Z1,lvx.hell AS he1,gps.X1 AS X2,gps.Y1 AS Y2,gps.Z1 AS Z2, gps.[H-Ell] AS he2, lvx.hell - gps.[H-Ell] AS h12,lvx.roll - gps.Roll - (%f) AS rolldis,lvx.pitch - gps.Pitch- (%f) AS pitchdis,lvx.heading - gps.Heading- (%f) AS headingdis, gps.acc,gps.speed,gps.star,gps.locmode,gps.locacc,gps.rollacc,gps.pitchacc,gps.hdingacc FROM lvxtabname lvx, gpstabname gps WHERE lvx.daysec = gps.GPS and abs(lvx.X1-gps.X1)<15 and abs(lvx.Y1-gps.Y1)<15;' %(self.sys_prh[1],self.sys_prh[0],self.sys_prh[2])
        sql = sql.replace('gpstabname', gpstab).replace('lvxtabname', lvxtab)
        a=self.cur.execute(sql)
        outputlist = []
        for var in a:
            var_list = list(var)
            H_dis =math.sqrt(math.pow((var_list[1]-var_list[5]),2) + math.pow((var_list[2]-var_list[6]),2))
            var_list.append(H_dis)
            outputlist.append(var_list)
        index = ['daysec','X1','Y1','Z1','he1','X2','Y2','Z2','he2','h12','roll_dis','pitch_dis','heading_dis','ACC','speed','star','locmode','locacc','rollacc','pitchacc','hdingacc','H_dis']
        print(outputlist[0])
        # pdb.set_trace()
        data_df = pd.DataFrame(outputlist, columns=index)
        Hdis_in = [1.0,1.5,2.0,2.5]
        data01 = data_df[data_df['H_dis']<=Hdis_in[0]]
        data12 = data_df[(data_df['H_dis']>Hdis_in[0])&(data_df['H_dis']<=Hdis_in[1])]
        data23 = data_df[(data_df['H_dis']>Hdis_in[1])&(data_df['H_dis']<=Hdis_in[2])]
        data34 = data_df[(data_df['H_dis']>Hdis_in[2])&(data_df['H_dis']<=Hdis_in[3])]
        data4 = data_df[data_df['H_dis']>Hdis_in[3]]
        plt.figure(1, figsize=(8, 10))
        plt.rcParams['axes.unicode_minus'] = False 
        plt.ylabel('LocAcc', fontdict={'size':22})
        plt.title(proname+'_水平定位误差', fontdict={'size':30})
        plt.boxplot([data01['locacc'],data12['locacc'],data23['locacc'],data34['locacc'],data4['locacc']],labels=['0-'+str(Hdis_in[0]),str(Hdis_in[0])+'-'+str(Hdis_in[1]),str(Hdis_in[1])+'-'+str(Hdis_in[2]),str(Hdis_in[2])+'-'+str(Hdis_in[3]),str(Hdis_in[3])+'-'])
        # plt.boxplot([data_df_roll['roll_dis'],data_df_pitch['pitch_dis'],data_df_heading['heading_dis']],labels=['Roll','Pitch','Heading'])

        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.savefig(self.savepath+'/'+proname+'水平定位误差区段.jpg',bbox_inches='tight')
        print(proname+'水平定位误差区段.jpg 保存成功！')
        plt.cla()
        pdb.set_trace()

        #h12
        data_h01 = data_df[data_df['h12']<=1]
        data_h12 = data_df[(data_df['h12']>1)&(data_df['h12']<=2)]
        data_h23 = data_df[(data_df['h12']>2)&(data_df['h12']<=3)]
        data_h34 = data_df[(data_df['h12']>3)&(data_df['h12']<=4)]
        data_h4 = data_df[data_df['h12']>4]
        plt.figure(2, figsize=(8, 10))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.ylabel('LocAcc', fontdict={'size':22})
        plt.ylabel('locacc', fontdict={'size':22})
        plt.title(proname+'_椭球高误差', fontdict={'size':30})
        plt.boxplot([data_h01['locacc'],data_h12['locacc'],data_h23['locacc'],data_h34['locacc'],data_h4['locacc']],labels=['0-1','1-2','2-3','3-4','4-'])
        # plt.boxplot([data_df_roll['roll_dis'],data_df_pitch['pitch_dis'],data_df_heading['heading_dis']],labels=['Roll','Pitch','Heading'])

        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.savefig(self.savepath+'/'+proname+'椭球高差分阶段.jpg',bbox_inches='tight')
        print(proname+'椭球高差分阶段.jpg 保存成功！')
        plt.cla()

        #roll
        data_roll01 = data_df[data_df['roll_dis']<=0.5]
        data_roll12 = data_df[(data_df['roll_dis']>0.5)&(data_df['roll_dis']<=1)]
        data_roll23 = data_df[(data_df['roll_dis']>1)&(data_df['roll_dis']<=1.5)]
        data_roll34 = data_df[(data_df['roll_dis']>1.5)&(data_df['roll_dis']<=2)]
        data_roll4 = data_df[data_df['roll_dis']>2]
        plt.figure(3, figsize=(8, 10))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.ylabel('LocAcc', fontdict={'size':22})
        plt.ylabel('rollacc', fontdict={'size':22})
        plt.title(proname+'_roll误差', fontdict={'size':30})
        plt.boxplot([data_roll01['rollacc'],data_roll12['rollacc'],data_roll23['rollacc'],data_roll34['rollacc'],data_roll4['rollacc']],labels=['0-0.5','0.5-1','1-1.5','1.5-2','2-'])
        # plt.boxplot([data_df_roll['roll_dis'],data_df_pitch['pitch_dis'],data_df_heading['heading_dis']],labels=['Roll','Pitch','Heading'])

        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.savefig(self.savepath+'/'+proname+'roll误差分阶段.jpg',bbox_inches='tight')
        print(proname+'heading误差分阶段.jpg 保存成功！')
        plt.cla()
        
        #heading
        data_heading01 = data_df[data_df['heading_dis']<=0.2]
        data_heading12 = data_df[(data_df['heading_dis']>0.2)&(data_df['heading_dis']<=1)]
        data_heading23 = data_df[(data_df['heading_dis']>1)&(data_df['heading_dis']<=1.5)]
        data_heading34 = data_df[(data_df['heading_dis']>1.5)&(data_df['heading_dis']<=2)]
        data_heading4 = data_df[(data_df['heading_dis']>2)&(data_df['heading_dis']<3)]
        plt.figure(4, figsize=(8, 10))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.ylabel('LocAcc', fontdict={'size':22})
        plt.ylabel('hdingacc', fontdict={'size':22})
        plt.title(proname+'_heading误差', fontdict={'size':30})
        plt.boxplot([data_heading01['hdingacc'],data_heading12['hdingacc'],data_heading23['hdingacc'],data_heading34['hdingacc'],data_heading4['hdingacc']],labels=['0-0.2','0.2-1','1-1.5','1.5-2','2-'])
        # plt.boxplot([data_df_roll['roll_dis'],data_df_pitch['pitch_dis'],data_df_heading['heading_dis']],labels=['Roll','Pitch','Heading'])

        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.savefig(self.savepath+'/'+proname+'hding误差分阶段.jpg',bbox_inches='tight')
        print(proname+'roll误差分阶段.jpg 保存成功！')
        plt.cla()

        #pitch
        data_pitch01 = data_df[data_df['pitch_dis']<=0.3]
        data_pitch12 = data_df[(data_df['pitch_dis']>0.3)&(data_df['pitch_dis']<=1)]
        data_pitch23 = data_df[(data_df['pitch_dis']>1)&(data_df['pitch_dis']<=1.5)]
        data_pitch34 = data_df[(data_df['pitch_dis']>1.5)&(data_df['pitch_dis']<=2)]
        data_pitch4 = data_df[(data_df['pitch_dis']>2)&(data_df['pitch_dis']<3)]
        plt.figure(5, figsize=(8, 10))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.ylabel('LocAcc', fontdict={'size':22})
        plt.ylabel('pitchacc', fontdict={'size':22})
        plt.title(proname+'_pitch误差', fontdict={'size':30})
        plt.boxplot([data_pitch01['pitchacc'],data_pitch12['pitchacc'],data_pitch23['pitchacc'],data_pitch34['pitchacc'],data_pitch4['pitchacc']],labels=['0-0.3','0.3-1','1-1.5','1.5-2','2-'])
        # plt.boxplot([data_df_roll['roll_dis'],data_df_pitch['pitch_dis'],data_df_heading['heading_dis']],labels=['Roll','Pitch','Heading'])

        plt.tick_params(labelsize=23)   #设置刻度大小
        plt.savefig(self.savepath+'/'+proname+'pitch误差分阶段.jpg',bbox_inches='tight')
        print(proname+'pitch误差分阶段.jpg 保存成功！')
        plt.cla()
        

    def pro1(self):
        for var in os.listdir(self.path):
            print('工程：',var)
            # print(self.path+var)
            if os.path.isdir(self.path+var):
                # print('test')
                # try:
                    self.h12(var)   
                    rms = self.dis_sta(var)
                    self.RMS.append(rms)
                # except:
                #     pass
        index = ['name','Height_RMS','Loc_RMS','Roll_RMS','Pitch_RMS','Heading_RMS']
        self.RMS.insert(0, index)
        savedata_df = pd.DataFrame(self.RMS)
        # print(savedata_df)
        # pdb.set_trace()
        savedata_df.to_csv(self.path+'Evaluation_sql.csv', index=True, header=False)
    
    #按照时间段输出RMS
    def pro2(self):
        pro={}
        proname = os.listdir(self.path)
        pronamelist = []
        for var in proname:
            if os.path.isdir(self.path+var):
                for i in range(3):
                    pronamelist.append(var)
        # print(pronamelist)
        time = [[9500, 9750],[10372,10429],[9880,10000],[11486,11710],[12239,12283],[11826,11923],[13198,13400],[13889,13929],[13515,13609],[28030,28271],[28778,28820],[28376,28478]]
        scene_rms = []
        for i in range(len(pronamelist)):
            # print(time[i][0])
            rms = self.dis_sta_time(pronamelist[i],time[i][0],time[i][1])
            scene_rms.append(rms)                
        savedata_df = pd.DataFrame(scene_rms)
        savedata_df.to_csv(self.path+'Evaluation-scene.csv', index=True, header=False)
        print('处理结束！')
    def pro3(self):
        proname = os.listdir(self.path)[0]
        self.scene_plot1(proname)
    def pro4(self):
        scene = [[[9500, 9750],[10372,10429],[9880,10000]],[[11486,11710],[12239,12283],[11826,11923]],[[13198,13400],[13889,13929],[13515,13609]],[[28030,28271],[28778,28820],[28376,28478]]]
        # scene = [9500, 9750],[10372,10429],[9880,10000]
        i=0
        for var in os.listdir(self.path):
            if os.path.isdir(self.path+var):
                # proname = os.listdir(self.path)[0]
                self.scene_plot2(var,scene[i][0],scene[i][1],scene[i][2])
                i=i+1
    def pro5(self):  #定位与姿态角相关性分析
       for var in os.listdir(self.path):
           if os.path.isdir(self.path+var):
            #    self.locrelation_rms(var)   #定位
               self.angrelation_rms(var)   #姿态角
               
            #    rms = self.dis_sta(var)
            #    self.RMS.append(rms)
    #    savedata_df = pd.DataFrame(self.RMS)
    #    savedata_df.to_csv(self.path+'Evaluation.csv', index=True, header=False)
    def pro6(self):
        for var in os.listdir(self.path):
            if os.path.isdir(self.path+var):
                self.relation(var)
    

if __name__ == '__main__':
    ex = main()
    ex.pro1()
    # ex.pro2()
    # ex.pro3()
    # ex.pro4()
    # ex.pro5() #计算相关系数
    # ex.pro6()
