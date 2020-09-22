import os
import pdb
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
plt.rcParams['font.sans-serif'] = ['SimHei']

class main():
    def __init__(self):
        self.path = 'D:/had/data/bmwpoc/roll_ana/'

    def readgpspos(self,name):
        path = self.path
        # print(path)
        # file = os.listdir(path)[0]   #由于工程命名有问题，所以改用该方式
        path_name = path + name
        fn = open(path_name)
        data_list = []
        # for line in fn:
        #     temp1 = line.split(' ')
        #     temp = list(filter(None, temp1))  #删除空字符窜
        #     data_list.append(temp)
        for line in fn:
            temp1 = line.split(' ')
            temp = list(filter(None, temp1))  #删除空字符窜
            del temp[0:4]
            data_list.append(temp)            
        fn.close()
        index = data_list[0]
        del data_list[0:2]
        data_list_f = []
        for var in data_list:
            temp_f = [float(i) for i in var]
            data_list_f.append(temp_f)
        datadf = pd.DataFrame(data_list_f,columns=index)
        return(datadf)
    
    def pro(self):
        path='D:/had/data/bmwpoc/roll_ana'
        file = os.listdir(path)
        # print(file)
        plt.figure(1, figsize=(23, 18))
        plt.rcParams['axes.unicode_minus'] = False 
        plt.grid(axis="y")
        y_major_locator=MultipleLocator(0.5)
        ax=plt.gca()
        ax.yaxis.set_major_locator(y_major_locator)
        i=0
        for var in file:
            if var[-4:] == 'PosT':
                datadf = self.readgpspos(var)
                # print(datadf.head())
                # pdb.set_trace()
                labelvar = var[2:4]+'C'+var[8:10]+var[12:16]
                plt.ylabel('roll分布(°)', fontdict={'size':22})
                plt.boxplot([datadf['Roll']], positions=[i], widths=0.7, showmeans=True,labels=[labelvar])
                plt.tick_params(labelsize=23)   #设置刻度大小
                plt.savefig(self.path+'/'+'姿态角分布箱线图.jpg',bbox_inches='tight')
                i=i+1
            # plt.cla()

if __name__=='__main__':
    ex = main()
    ex.pro()