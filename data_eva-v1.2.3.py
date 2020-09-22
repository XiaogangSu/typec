#525typec数据评估
import os
from tkinter import filedialog as fd
import pandas as pd
import numpy as np
import json
import time
from PIL import Image
import sqlite3 as sq
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
import math
import pdb
# import sxg_python.myfun as myfun
from pyproj import Transformer, transform
from osgeo import gdal
from osgeo import ogr
from osgeo import osr

class Main():
    def __init__(self):
        print('初始化！')
        # print(projectname)
        self.path = fd.askdirectory(initialdir = "D:/had/data/",title = '选择工程目录')
        self.savepath = self.path+'_anaoutput/'
        # prolist = os.listdir(path)
        if os.path.isdir(self.savepath):
            pass
        else:
            os.mkdir(self.savepath)
        if os.path.exists(self.path + '/'+'Evaluation.csv'):
            os.remove(self.path + '/'+'Evaluation.csv')
        self.dbname = 'DB-'+self.path.split('/')[-1]+'.db'
        # self.proname_1 = self.proname.replace('-','')
        # self.deviceid = self.proname.split('-')[2]
        self.source = 'TypeC'
        # self.picnum = input('输入照片数：')
        self.checktime = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime())
        # dbname = input('输入dbname:')
        try:
            self.conn = sq.connect(self.savepath + self.dbname)
            print('连接数据库成功！')
        except:
            print('连接失败！')
        self.gps_fps_raw = 25  #gps理论帧率
        self.img_fps_raw = 20 #img理论帧率
        self.tar_epsg = 4547 #投影坐标系
        self.src_epsg = 4326 #原始坐标系
        self.cur = self.conn.cursor()
        self.grs80 = (6378137, 298.257222100882711)
        self.wgs84 = (6378137, 298.257223563)
        # date_pro = self.proname.split('-')[-1]
        # self.date = '20'+date_pro[0:2]+'.'+date_pro[2:4]+'.'+date_pro[4:6]
        # if os.path.exists(self.path + '/RawDataEvl/'):
        #     pass
        # else:
        #     os.mkdir(self.path + '/RawDataEvl/')
    
    #经纬度转空间直角坐标系  "print(geodetic_to_geocentric(wgs84, lat, lon, hell))"
    def geodetic_to_geocentric(self, ellps, lat, lon, h):
        a, rf = ellps
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        N = a / math.sqrt(1 - (1 - (1 - 1 / rf) ** 2) * (math.sin(lat_rad)) ** 2)
        X = (N + h) * math.cos(lat_rad) * math.cos(lon_rad)
        Y = (N + h) * math.cos(lat_rad) * math.sin(lon_rad)
        Z = ((1 - 1 / rf) ** 2 * N + h) * math.sin(lat_rad)
        return([X, Y, Z])
    
    #坐标投影
    def cor_pro(self, src_epsg, tar_epsg, lon, lat):
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(src_epsg)
        sr_tar = osr.SpatialReference()
        sr_tar.ImportFromEPSG(tar_epsg)
        temppoint = ogr.Geometry(ogr.wkbPoint)
        temppoint.AssignSpatialReference(sr)
        temppoint.AddPoint(lon, lat, 0)
        # print(temppoint)
        temppoint.TransformTo(sr_tar)
        X=temppoint.GetX()
        Y=temppoint.GetY()
        Z=temppoint.GetZ()
        return([X,Y,Z])

    #读取图像相关信息
    def read_pic(self, proname):
        # print('proname:===', proname)
        picpath = self.path+'/'+proname+'/Data/Img/camera0/'
        self.proname = proname
        #将部分init中的定义挪到此处
        self.proname_1 = proname.replace('-','')
        self.deviceid = proname.split('-')[0]
        date_pro = proname.split('-')[-1]
        self.date = '20'+date_pro[0:2]+'.'+date_pro[2:4]+'.'+date_pro[4:6]
        if os.path.exists(self.path +'/'+proname+ '/RawDataEvl/'):
            pass
        else:
            os.mkdir(self.path +'/'+proname+ '/RawDataEvl/')
        if os.path.exists(picpath):
            imglist = os.listdir(picpath)
            picname = imglist[0]
            self.picid = picname[0:-4]
            im = Image.open(picpath+picname)
            self.width = im.size[1]
            self.height = im.size[0]
        else:
            self.picid = ''
            self.width = ''
            self.height = ''
        if os.path.exists(self.path+'/'+proname+'/Data/UQimg/'):
            self.UQImg = os.listdir(self.path+'/'+proname+'/Data/UQimg/')
            self.UQImg_per = len(self.UQImg)/2000
        else:
            os.mkdir(self.path+'/'+proname+'/Data/UQimg/')
            self.UQImg = ''
            self.UQImg_per = ''

    #gps天秒转当地时间
    def gpstime2loc(self, gpstime):
        gpstime = int(float(gpstime))
        h, m = divmod(gpstime, 3600)
        m, s = divmod(m, 60)
        loctime = self.date + ' ' + str(h+8)+':'+str(m)+':'+str(s)
        return(loctime)

    #读取gpspos
    def readgpspos(self):
        path =self.path+'/'+self.proname+'/Data/GPSPost/'
        # print(path)
        # file = os.listdir(path)[0]   #由于工程命名有问题，所以改用该方式
        file = self.proname_1+'.PosT'
        path_name = path + file
        # print(path_name)
        fn = open(path_name)
        data_list = []
        # for line in fn:
        #     temp1 = line.split(' ')
        #     temp = list(filter(None, temp1))  #删除空字符窜
        #     data_list.append(temp)
        for line in fn:
            temp1 = line.split(' ')
            temp = list(filter(None, temp1))  #删除空字符窜
            data_list.append(temp)
        fn.close()
        index = data_list[0]
        del data_list[1]
        # print(data_list)
        # print(len(data_list[1]))
        self.gps_start = data_list[1][4]
        self.col_start = self.gpstime2loc(self.gps_start)
        self.gps_end = data_list[-1][4]
        self.col_end = self.gpstime2loc(self.gps_end)
        # print(gps_start,gps_end)
        # data_df = pd.DataFrame(data_list, columns=data_list[0])
        # print(data_df.describe())
        #计算位姿丢帧率
        num = 5000  #选取点个数
        self.samplepos_start_time = float(data_list[1][4]) 
        self.samplepos_end_time = float(data_list[-1][4]) 
        sec = self.samplepos_end_time-self.samplepos_start_time
        self.posfps = (len(data_list)-1)/sec
        posnum = sec*25
        self.fps_pos_ev = (posnum - len(data_list)+1)/posnum
        if self.fps_pos_ev < 0.001:
            self.poslosssrate = 'Yes'
        else:
            self.poslosssrate = 'No'
    
    #计算并统计位姿输出情况
    def gps_pos_sta(self):
        path =self.path+'/'+self.proname+'/Data/GPSPost/'
        file = self.proname_1+'.PosT'
        tbname = 'gps_'+self.proname_1
        a = self.cur.execute("SELECT COUNT(*) FROM sqlite_master where type='table' and name='%s';" %(tbname))
        # a = self.cur.execute('''SELECT COUNT(*) FROM sqlite_master where type='table' and name='node';''')
        for row in a:
            exist_bool = row[0]
        if exist_bool == 1:
            self.cur.execute('drop table %s' %(tbname))
            print('表%s已删除' %(tbname))
        path_name = path + file
        # print(path_name)
        fn = open(path_name)
        data_list = []
        for line in fn:
            temp1 = line.split(' ')
            temp = list(filter(None, temp1))  #删除空字符窜
            # gps = temp[4]
            del temp[0:4]
            temp[-1] = temp[-1].replace('\n', '')
            data_list.append(temp)
        fn.close()
        
        index = data_list[0]+['X1','Y1','Z1']
        # print('index:',index)
        del data_list[0:2]
        datalist_float = []
        transformer = Transformer.from_proj(self.src_epsg, self.tar_epsg)
        for var in data_list:
            temp = [float(i) for i in var]
            # print(temp)
            # [x,y,z] = self.geodetic_to_geocentric(self.wgs84, temp[1], temp[2], temp[4]) #z转为ecef坐标
            # [x,y] = myfun.cor_proj2(self.src_epsg, self.tar_espg, temp[2], temp[1]) #转为投影坐标系
            # [y,x] = transform(self.src_epsg, self.tar_epsg, temp[1], temp[2])  #输入输出为 Y，X ，lat ,lon
            # z=0
            [x,y,z] = self. cor_pro(self.src_epsg, self.tar_epsg, temp[2], temp[1])
            # print([x,y,z])
            # pdb.set_trace()
            temp = temp+[x,y,z]
            datalist_float.append(temp)
       
        data_df = pd.DataFrame(datalist_float, columns=index)
        # data_df.sort_values(by=['GPS'])  #排序
        # data_df.drop(['SrcId', 'DevNum', 'Freq','Ver','CoorType'], axis=1, inplace=True) 
        # print(data_df.columns)
        # pd.io.sql.to_sql(data_df, tbname, con=self.conn, if_exists='replace')  #pandas写入数据库
        gps_1 = data_df['gps_time'].values
        # print(type(gps_1))
        gps_2 = np.delete(gps_1, 0, axis=0)
        gps_1 = np.delete(gps_1, len(gps_1)-1, axis=0)
        gps_del = gps_2-gps_1
        del_list = gps_del.tolist()
        del_num = []
        del_in = 1/self.gps_fps_raw  #理论时间间隔
        for var in del_list:
            temp = int(var/del_in)
            if temp >= 2:
                del_num.append(temp-1)
            else:
                del_num.append(0)
        del_arr = np.array(del_num)
        max_index = np.argmax(del_arr) #丢帧最大位置
        self.max_poseloss = del_arr[max_index]
        # max_index = np.argmax(gps_del) #丢帧最大位置
        # self.max_poseloss = int(gps_del[max_index]*10)-1
        # dellist = gps_del.tolist()
        # for i in range(len(dellist)):
        #     if dellist[i]<0:
        #         print('*******',i,' ',dellist[i])
        gps_del = np.insert(gps_del,len(gps_del)-1,values=0.1,axis=0)
        del_arr = np.insert(del_arr,len(del_arr)-1,values=0,axis=0)
        data_df['gps_del'] = gps_del
        data_df['del_arr'] = del_arr
        self.pose_maxloss_gpstime = data_df['gps_time'][max_index]
        # print(data_df.dtypes)
        data_df.to_sql(tbname,con=self.conn, if_exists='replace')
        #绘图
        plt.figure(1, figsize=(25, 5))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.ylim(-0.5, 0.5)
        # plt.ylabel('相临帧时间间隔(s)', fontdict={'size':25})
        plt.ylabel('丢帧数', fontdict={'size':50})
        plt.title('位姿丢帧统计'+'(丢帧率：'+str(self.fps_pos_ev)+')', fontdict={'size':30})
        # x_range = np.arange(len(datalist_float))
        # data_df['gps_del'].plot(kind='line')
        # plt.plot(x_range, data_df['gps_del'].values, color='b') 
        plt.plot(data_df['gps_time'], data_df['del_arr'].values, color='b') 
        plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.xticks(fontdict={'size': 10})
        # plt.yticks(fontdict={'size': 10})
        picname = self.proname_1+'_gpsloss.jpg'
        plt.savefig(path+picname, bbox_inches='tight')
        plt.clf()
    
    #读取lvx数据
    def read_lvx(self):
        path =self.path+'/'+self.proname+'/Data/GPSPost/'
        file = 'lvx.txt'
        tbname = 'lvx_'+self.proname_1
        a = self.cur.execute("SELECT COUNT(*) FROM sqlite_master where type='table' and name='%s';" %(tbname))
        # a = self.cur.execute('''SELECT COUNT(*) FROM sqlite_master where type='table' and name='node';''')
        for row in a:
            exist_bool = row[0]
        if exist_bool == 1:
            self.cur.execute('drop table %s' %(tbname))
            print('表%s已删除' %(tbname))
        path_name = path + file
        # print(path_name)
        fn = open(path_name)
        data_list = []
        for line in fn:
            try:
                temp1 = line.split(' ')
                temp = list(filter(None, temp1))  #删除空字符窜
                temp[-1] = temp[-1].replace('\n', '')
                del temp[-2:]
                data_list.append(temp)
            except:
                print('错误列：',temp)
        fn.close()
        # print('a:',data_list[0:3])
        # pdb.set_trace()
        del data_list[0]
        del data_list[-1]
        # print(data_list[0:2])
        index = ['daysec','northing','easting','hell','lat','lon','north_v','roll','pitch','heading','X1','Y1','Z1']
        # print('index:',index)
        del data_list[0:2]
        data_list = [var for var in data_list if float(var[0])>float(self.gps_start)-10 and float(var[0])<float(self.gps_end)+10]
        datalist_float = []
        for var in data_list:
            # print(var)
            # if float(var[0])>float(self.gps_start)-10 and float(var[0])<float(self.gps_end)+10:
                temp = [float(i) for i in var]
            # [x,y,z] = self.geodetic_to_geocentric(self.wgs84, temp[4], temp[5], temp[3])
            # [x,y] = myfun.cor_proj(self.tar_espg, temp[5], temp[4]) #转为投影坐标系
            # z=0
            # [x,y] = myfun.cor_proj2(self.src_epsg, self.tar_epsg, temp[5], temp[4]) #转为投影坐标系
            # z=0
                temp[0] = round(temp[0],2)
                [x,y,z] = self.cor_pro(self.src_epsg, self.tar_epsg, temp[5], temp[4])
                temp = temp+[x,y,z]
                datalist_float.append(temp)
        data_df = pd.DataFrame(datalist_float, columns=index)
        data_df.to_sql(tbname,con=self.conn, if_exists='replace')

    #读取imgpos
    def readimgpos(self):
        path = self.path+'/'+self.proname+'/Data/ImgPost/'
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
        self.sampleimg_end_time = float(data_list[-1][3]) 
        sec = self.sampleimg_end_time-self.sampleimg_start_time
        imgnum = sec*self.img_fps_raw
        # print(self.sampleimg_start_time, self.sampleimg_end_time, sec, imgnum)
        self.fps_ev = (imgnum - len(data_list)+1)/imgnum
        if self.fps_ev < 0.001:
            self.imglosssrate = 'Yes'
        else:
            self.imglosssrate = 'No'
     
    #计算并统计图像位姿信息
    def imgpos_sta(self):
        path = self.path+'/'+self.proname+'/Data/ImgPost/'
        file = self.proname_1+'-cam0-imgpost.txt'
        tbname = 'img_'+self.proname_1
        a = self.cur.execute("SELECT COUNT(*) FROM sqlite_master where type='table' and name='%s';" %(tbname))

        # a = self.cur.execute('''SELECT COUNT(*) FROM sqlite_master where type='table' and name='node';''')
        for row in a:
            exist_bool = row[0]
        if exist_bool == 1:
            self.cur.execute('drop table %s' %(tbname))
            print('表%s已删除' %(tbname))
        
        path_name = path + file
        fn = open(path_name)
        data_list = []
        for line in fn:
            temp1 = line.split(' ')
            temp = list(filter(None, temp1))  #删除空字符窜
            temp[-1] = temp[-1].replace('\n', '')
            data_list.append(temp)
        fn.close()
        index = data_list[0]
        del data_list[0:2]
        datalist_float = []
        for i in range(len(data_list)):
            temp = data_list[i]
            imgname = temp[1]
            del temp[1]
            # print('temp:',temp)
            temp_1 = [float(var) for var in temp]
            # print('temp_1:',temp_1)
            temp_1.insert(1,imgname)
            # print('temp_0:', temp_1)
            datalist_float.append(temp_1)
        # print(datalist_float[0:2])
        data_df = pd.DataFrame(datalist_float, columns=index)
        # data_df.sort_values(by=['GpsTime'])  #排序
        # print(data_df.dtypes)
        gps_1 = data_df['GpsTime'].values
        # print(type(gps_1))
        gps_2 = np.delete(gps_1, 0, axis=0)
        gps_1 = np.delete(gps_1, len(gps_1)-1, axis=0)
        gps_del = gps_2-gps_1
        del_list = gps_del.tolist()
        del_num = []
        del_in = 1/self.img_fps_raw
        for var in del_list:
            temp = int(var/del_in)
            if temp >= 2:
                del_num.append(temp-1)
            else:
                del_num.append(0)
        del_arr = np.array(del_num)
        # max_index = np.argmax(gps_del) #丢帧最大位置
        # self.max_imgloss = int(gps_del[max_index]*15)-1
        max_index = np.argmax(del_arr) #丢帧最大位置
        self.max_imgloss = del_arr[max_index]
        # dellist = gps_del.tolist()
        # for i in range(len(dellist)):
        #     if dellist[i]<0:
        #         print('*******',i,' ',dellist[i])
        gps_del = np.insert(gps_del,len(gps_del)-1,values=0.05,axis=0)
        del_arr = np.insert(del_arr,len(del_arr)-1,values=0,axis=0)
        data_df['gps_del'] = gps_del
        data_df['del_arr'] = del_arr
        # print(gps_del)
        self.img_maxloss_gpstime = data_df['GpsTime'][max_index]
        data_df.to_sql(tbname,con=self.conn, if_exists='replace')
        # print('test:',data_df['gps_del'].max())
        #绘图
        plt.figure(2, figsize=(25, 5))
        plt.rcParams['axes.unicode_minus'] = False 
        # plt.ylim(-1, 1)
        # plt.ylabel('相临帧时间间隔(s)', fontdict={'size':25})
        plt.ylabel('图像丢帧数', fontdict={'size':50})
        plt.title('图像丢帧统计'+'(丢帧率：'+str(self.fps_ev)+')', fontdict={'size':30})
        # x_range = np.arange(len(datalist_float))
        # data_df['gps_del'].plot(kind='line')
        # plt.plot(x_range, data_df['gps_del'].values, color='b') 
        plt.plot(data_df['GpsTime'], data_df['del_arr'].values, color='b') 
        plt.tick_params(labelsize=23)   #设置刻度大小
        # plt.xticks(fontdict={'size': 10})
        # plt.yticks(fontdict={'size': 10})
        picname = self.proname_1+'_imgloss.jpg'
        plt.savefig(path+picname, bbox_inches='tight')
        plt.clf()

    #保存为json
    def savejson(self):
        # self.read_pic()
        # self.readimgpos()
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
        # print(output)
        savename = self.proname_1+'-evaluation.json'
        path = self.path + '/'+self.proname+'/RawDataEvl/' + savename
        with open(path, 'w') as fn:
            json.dump(output, fn)
        fn.close()
  
    def pro(self):
        print('开始处理。。。')
        # path = fd.askdirectory(initialdir = "./",title = '选择工程目录')
        prolist_raw = os.listdir(self.path)
        prolist=[]
        for var in prolist_raw:
            if os.path.isdir(self.path+'/'+var):
                prolist.append(var)
        output = []
        index = ['pro_name','img_lossrate','img_maxloss','img_maxloss_gpstime','pose_lossrate','pose_maxloss','pose_maxloss_gpstime','posefps']
        for var in prolist:
            # try:
                print('处理工程：', var)
                self.read_pic(var)
                self.readgpspos()
                self.gps_pos_sta()

                if os.path.exists(self.path+'/'+self.proname+'/Data/GPSPost/lvx.txt'):
                    print('读取lvx...')
                    self.read_lvx()
                imgpostname = var.replace('-','')+'-cam0-imgpost.txt'
                if os.path.exists(self.path+'/'+self.proname+'/Data/ImgPost/'+imgpostname):
                    print('读取imgpos...')
                    self.readimgpos()
                    self.imgpos_sta()
                    self.savejson()
                # self.readimgpos()
                # self.imgpos_sta()
                # self.savejson()
                # output[var]={
                #     '图像丢帧率': self.fps_ev,
                #     '位姿丢帧率': self.fps_pos_ev
                # }
                output.append([var, self.fps_ev,self.max_imgloss, self.img_maxloss_gpstime,self.fps_pos_ev,self.max_poseloss, self.pose_maxloss_gpstime,self.posfps])
            # except:
            #     print(var,'处理出错')
            #     pass
        # print(output)
        output.insert(0, index)
        path = self.path + '/'+'Evaluation.csv'
        savedata_df = pd.DataFrame(output)
        savedata_df.to_csv(path, index=True, header=False)
        print('处理结束！')

if __name__=='__main__':
    ex = Main()
    ex.pro()