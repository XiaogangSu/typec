#评价报告提取
import os
import shutil
def main():
    path = 'D:/had/data/525POC/allpro_wuhan'
    save = 'D:/had/data/525POC/all_wuhan_eva/'
    for var in os.listdir(path):
        if os.path.isdir(path+'/'+var):
            os.mkdir(save+var)
            shutil.copytree(path+'/'+var+'/'+'RawDataEvl',save+var+'/'+'RawDataEvl')
    print('处理完成！')

main()
