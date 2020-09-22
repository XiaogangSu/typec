#计算roll\pitch标定结果
import sxg_python.myfun as myfun
import pdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']

class main():
    def __init__(self):
        print('开始处理。。。')
        self.path = 'D:/had/data/bmwpoc/20200920'
        # self.name = 'export_Mission-b2-200hz.txt'
        # self.name = 'export_Mission-b1-200hz.txt'
        # self.time1 = [[23900,24180],[24720,24900]] #5号车第一次
        self.name = '20200920-200hz.txt'
        self.time = [[26040,26340],[26520,26700]]  #5号车第二次
        # self.time2 = [[28560,28800],[28920,29100]] 

    def readrawdata(self):
        data = myfun.readtxt(self.name, self.path, ' ')
        del data[0]
        dataoutput = []
        for var in data:
            del var[-2:]
            temp = [float(i) for i in var]
            dataoutput.append(temp)
        index = ['daysec','X','Y','hgt','lat','lon','speed','roll','pitch','heading']
        # dataoutput.insert(0,index)
        self.alldata = pd.DataFrame(dataoutput,columns=index)
    
    def ana(self,time): #time指正反停车的时间节点[[start1,end1],[start2,end2]]
        f1_time = time[0]
        f2_time = time[1]
        print(self.alldata.shape[0])
        f1_data = self.alldata[(self.alldata['daysec']<=f1_time[1])&(self.alldata['daysec']>=f1_time[0])]
        f2_data = self.alldata[(self.alldata['daysec']<=f2_time[1])&(self.alldata['daysec']>=f2_time[0])]
        
        ylabelsize=80
        xlabelsize=60
        ticksize=60
        figsize=(60,60)
        fig = plt.figure(1, figsize=figsize)
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.title(proname, fontdict={'size': 60})
        ax1=fig.add_subplot(2,1,1)
        # ax2.set_title(proname, fontdict={'size':30})
        ax1.set_ylabel('roll', fontdict={'size':ylabelsize,'color':'blue'})
        ax1.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        # plt.title(proname+'-高程分布', fontdict={'size':30})
        ax1.plot(f1_data['daysec'].values, f1_data['roll'].values, color='b') 
        
        ax1.tick_params(labelsize=ticksize)   #设置刻度大小
        
        ax1_1 = ax1.twinx()
        ax1.plot(f1_data['daysec'].values, f1_data['pitch'].values, color='r')  
        ax1_1.set_ylabel('pitch', fontdict={'size':ylabelsize,'color':'red'})
        ax1_1.tick_params(labelsize=ticksize)   #设置刻度大小

        ax2=fig.add_subplot(2,1,2)
        # ax2.set_title(proname, fontdict={'size':30})
        ax2.set_ylabel('roll', fontdict={'size':ylabelsize,'color':'blue'})
        ax2.set_xlabel('GpsTime(天秒)', fontdict={'size':xlabelsize})
        # plt.xlabel('GpsTime(天秒)', fontdict={'size':22})
        # plt.title(proname+'-高程分布', fontdict={'size':30})
        ax2.plot(f2_data['daysec'].values, f2_data['roll'].values, color='b') 
        ax2.tick_params(labelsize=ticksize)   #设置刻度大小
        
        ax2_1 = ax2.twinx()
        ax2.plot(f2_data['daysec'].values, f2_data['pitch'].values, color='r') 
        ax2_1.set_ylabel('pitch', fontdict={'size':ylabelsize,'color':'red'})
        ax2_1.tick_params(labelsize=ticksize)   #设置刻度大小

        plt.savefig(self.path+'/'+self.name[0:-4]+'_'+str(f1_time[0])+'-'+str(f1_time[1])+'_.jpg',bbox_inches='tight')
        # print(proname+'姿态角误差相关性分析.jpg 保存成功！')
        # h12_RMS = math.sqrt((np.square(data_df['H_dis']).sum())/len(outputlist))
        # return(h12_RMS)
        plt.clf()
        roll1_avg = f1_data['roll'].mean()
        roll2_avg = f2_data['roll'].mean()
        pitch1_avg = f1_data['pitch'].mean()
        pitch2_avg = f2_data['pitch'].mean()
        roll_syserr = (roll1_avg+roll2_avg)/2
        pitch_syserr = (pitch1_avg+pitch2_avg)/2
        print('roll1=%f,roll2=%f \npitch1=%f,pitch2=%f \nroll_err=%f,pitch_err=%f' %(roll1_avg,roll2_avg,pitch1_avg,pitch2_avg,roll_syserr,pitch_syserr))


    def pro(self):
        self.readrawdata()
        self.ana(self.time)
        # self.ana(self.time2)
        print('处理结束！')

if  __name__=='__main__':
    ex=main()
    ex.pro()