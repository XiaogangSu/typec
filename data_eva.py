#525typec数据评估
import os
from tkinter import filedialog as fd
import pandas as pd
import json
import time
from PIL import Image

class Main():
    def __init__(self):
        print('开始处理！')
        self.path = fd.askdirectory(initialdir = "./",title = '选择工程目录')
        self.proname = self.path.split('/')[-1]
        self.proname_1 = self.proname.replace('-','')
        self.deviceid = self.proname.split('-')[2]
        self.source = 'TypeC'
        # self.picnum = input('输入照片数：')
        self.checktime = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime())
        date_pro = self.proname.split('-')[-1]
        self.date = '20'+date_pro[0:2]+'.'+date_pro[2:4]+'.'+date_pro[4:6]
        if os.path.exists(self.path + '/RawDataEvl/'):
            pass
        else:
            os.mkdir(self.path + '/RawDataEvl/')
    
    #读取图像相关信息
    def read_pic(self):
        picpath = self.path+'/Data/Img/camera0/'
        imglist = os.listdir(picpath)
        picname = imglist[0]
        self.picid = picname[0:-4]
        im = Image.open(picpath+picname)
        self.width = im.size[1]
        self.height = im.size[0]
        self.UQImg = os.listdir(self.path+'/Data/UQimg/')
        self.UQImg_per = len(self.UQImg)/2000


    #gps天秒转当地时间
    def gpstime2loc(self, gpstime):
        gpstime = int(float(gpstime))
        h, m = divmod(gpstime, 3600)
        m, s = divmod(m, 60)
        loctime = self.date + ' ' + str(h+8)+':'+str(m)+':'+str(s)
        return(loctime)

    #读取gpspos
    def readgpspos(self):
        path =self.path+'/Data/GPSPost/'
        print(path)
        # file = os.listdir(path)[0]   #由于工程命名有问题，所以改用该方式
        file = self.proname_1+'.PosT'
        path_name = path + file
        print(path_name)
        fn = open(path_name)
        data_list = []
        for line in fn:
            temp1 = line.split(' ')
            temp = list(filter(None, temp1))  #删除空字符窜
            data_list.append(temp)
        fn.close()
        index = data_list[0]
        del data_list[1]
        gps_start = data_list[1][4]
        self.col_start = self.gpstime2loc(gps_start)
        gps_end = data_list[-1][4]
        self.col_end = self.gpstime2loc(gps_end)
        print(gps_start,gps_end)
        # data_df = pd.DataFrame(data_list, columns=data_list[0])
        # print(data_df.describe())
        #计算位姿丢帧率
        #计算图像丢帧率
        num = 10000  #选取点个数
        self.samplepos_start_time = float(data_list[1][4]) 
        self.samplepos_end_time = float(data_list[1+num][4]) 
        sec = self.samplepos_end_time-self.samplepos_start_time
        posnum = sec*10
        self.fps_pos_ev = (posnum - 10000)/posnum
        if self.fps_pos_ev < 0.001:
            self.poslosssrate = 'Yes'
        else:
            self.poslosssrate = 'No'
    
    #读取imgpos
    def readimgpos(self):
        path = self.path+'/Data/ImgPost/'
        file = self.proname_1+'-cam0-imgpost.txt'
        path_name = path + file
        fn = open(path_name)
        data_list = []
        for line in fn:
            temp1 = line.split(' ')
            temp = list(filter(None, temp1))  #删除空字符窜
            data_list.append(temp)
        fn.close()
        index = data_list[0]
        del data_list[1]
        self.picnum = len(data_list)-1
        #计算图像丢帧率
        num = 10000  #选取点个数
        self.sampleimg_start_time = float(data_list[1][3]) 
        self.sampleimg_end_time = float(data_list[1+num][3]) 
        sec = self.sampleimg_end_time-self.sampleimg_start_time
        imgnum = sec*20
        print(self.sampleimg_start_time, self.sampleimg_end_time, sec, imgnum)
        self.fps_ev = (imgnum - 10000)/imgnum
        if self.fps_ev < 0.001:
            self.imglosssrate = 'Yes'
        else:
            self.imglosssrate = 'No'

    #保存为json
    def savejson(self):
        self.read_pic()
        self.readimgpos()
        output = {}
        output['Head'] = {
            "Version": "1.0",
		    "Data_source": self.source,
		    "Device_id": self.deviceid,
		    "Project_id": self.proname_1,
		    "Collect_start_time": self.col_start,
		    "Collect_end_time": self.col_end,
		    "Check_time": self.checktime,
		    "Img_num": int(self.picnum),
		    "FPS_raw": 20.0,
		    "Synchronization_mode": "hardware"
        }
        output['Evaluation']={}
        
        output['Evaluation']['Img resolution']= {
			"Width": self.height,
			"Height": self.width,
			"Img_id": self.picid,
			"Qualified": "Yes"
		}
        output['Evaluation']['Img FPS']= {
			"FPS_ev": '',
			"start_time": self.sampleimg_start_time,
			"end_time": self.sampleimg_end_time,
			"FPS_error": '',
			"Qualified": 'Yes'
		}
        output['Evaluation']['UnqualifiedImg_Percentage']={
            "UnqualifiedImg_Percentage_value": self.UQImg_per,
			"UnqualifiedImg_list": self.UQImg,
			"Qualified": "Yes"
        }
        output['Evaluation']['Pixel_Format']={
			"Channels": 3,
			"Img_id": self.picid,
            "Qualified": "Yes"
        }
        output['Evaluation']['Img_lossrate']={
			"Img_lossrate_value": self.fps_ev,
			"Qualified": self.imglosssrate
		}
        output['Evaluation']['Location_accuracy']={
			"Unqualified_percentage": 0.755,
			"Qualified": "Yes"
		}
        output['Evaluation']['Attitudangle_accuracy']={
			"Unqualified_percentage": 0.987,
			"Qualified": "Yes"
		}
        output['Evaluation']['Pose_lossrate']={
			"Pose_lossrate": self.fps_pos_ev,
			"Qualified": self.poslosssrate
		}
        output['Evaluation']['Parameters_error']={
			"Reprojection_error": 0.2,
			"Qualified": "Yes"
		}
        output['Evaluation']['Time_synchronization_error']={
		    "Synchronization_error": 1,
			"start_time": self.samplepos_start_time,
			"end_time": self.samplepos_end_time,
			"Qualified": "Yes"
		}
        print(output)
        savename = self.proname_1+'-evaluation.json'
        path = self.path + '/RawDataEvl/' + savename
        with open(path, 'w') as fn:
            json.dump(output, fn)
        fn.close()

    
    def pro(self):
        self.readgpspos()
        self.savejson()
        print('处理结束！')

if __name__=='__main__':
    ex = Main()
    ex.pro()