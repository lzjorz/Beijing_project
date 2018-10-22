#!/usr/bin/python
# -*- coding: UTF-8 -*-

#导入包
import sys
import pandas as pd
from pandas import read_csv
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.externals.joblib import dump
import os
import requests
import demjson
import datetime as dt

#引入配置文件，配置文件的路径随需要进行修改
sys.path.append("./configuration_files")
import configuration_files

#历史温度数据的年月
years=configuration_files.years
months=configuration_files.months
#文件夹路径
folder_path=configuration_files.folder_path
file_path=folder_path+"/"
folder_all_data_path=folder_path+"/all_data"
file_split_path=folder_path+"/new_Data/split/"
file_temperature_path=folder_path+"/temperature/"
file_level2_split_hour_path=folder_path+"/new_Data\split_hour\level_2_device/"
file_level4_split_hour_path=folder_path+"/new_Data\split_hour\level_4_device/"
file_level5_split_hour_path=folder_path+"/new_Data\split_hour\level_5_device/"
file_level2_split_day_path=folder_path+"/new_Data\split_day\level_2_device/"
file_level4_split_day_path=folder_path+"/new_Data\split_day\level_4_device/"
file_level5_split_day_path=folder_path+"/new_Data\split_day\level_5_device/"
device = pd.read_csv(folder_path+"/device.csv", encoding='GBK')
device_node = set(device['device_code'].unique())
level_2_device = device[device['level'] == 2]['device_code']
level_4_device = device[device['level'] == 4]['device_code']
level_5_device = device[device['level'] == 5]['device_code']
#与暖气开放有关的设备
heating_file_list = ['K0bjcxa5023822']


#获取指定文件夹中所有文件名
def file_name(file_dir):
    file_list=[]
    try:
        for root, dirs, files in os.walk(file_dir):
    #         print(type(root)) #当前目录路径
    #         print(dirs) #当前路径下所有子目录
            for temp in files:
                file_list.append(root+'/'+temp)
        print "获取指定文件夹中的文件名成功"
        #print file_list[-1]
    except:
        print("获取指定文件夹中文件名失败")
    return file_list

#读取文件并将文件合并为一个文件
def file_read():
    file_list=file_name(folder_all_data_path)
    bjcx_list=[]
    for file_path in file_list:
        try:
            bjcx_list.append(read_csv(file_path))
        except:
            print "文件"+file_path+"读取失败"
            sys.exit()
    bjcx = pd.concat(bjcx_list, axis=0,sort=False)
    #print bjcx.tail(5)
    print "数据合并完毕"
    return bjcx

#数据切分与处理
#切分为每五分钟的数据文件
def data_original_segmentation(bjcx):
    data_temp = bjcx.groupby('DEVICE_CODE')
    for name, group in data_temp:
        #if not os.path.exists(file_split_path + str(name) + '.csv'):
        try:
            group.to_csv(file_split_path + str(name) + '.csv', index=False)
        except:
            print name,"分割失败"
            sys.exit()
    return 1


# 1.读取第二等级的数据,将第二等级的数据分开为每一个小时存储
def split_level_2_hour():
    for device in level_2_device:
        data = pd.read_csv(file_split_path + str(device) + '.csv')
        ##获取年月日信息
        data['S_Year'] = pd.DatetimeIndex(data.SDATE).year
        data['S_Month'] = pd.DatetimeIndex(data.SDATE).month
        data['S_Day'] = pd.DatetimeIndex(data.SDATE).day
        data['S_Hour'] = pd.DatetimeIndex(data.SDATE).hour
        ##删除‘S_MINUTE’数据信息
        df = data.drop(['S_MINUTE'], axis=1)
        ##统计每一小时的功率数据
        p_max = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['P_MAX'].max()
        p_max = p_max.reset_index()
        p_min = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['P_MIN'].min()
        p_min = p_min.reset_index()
        p_avg = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['P_AVG'].mean()
        p_avg = p_avg.reset_index()
        ##统计每一小时的用电量数据
        YL_max = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['YL_MAX'].max()
        # YL_max = YL_max.reset_index()
        YL_min = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['YL_MAX'].min()
        # YL_min = YL_min.reset_index()
        result = YL_max - YL_min
        result = result.reset_index()
        temp = pd.DataFrame()
        temp = pd.merge(p_max, p_min)
        temp = pd.merge(temp, p_avg)
        temp = pd.merge(temp, result)
        temp.to_csv(file_level2_split_hour_path + str(device) + '_hour.csv', index=False)
    return 1


# 2.读取第4等级的数据,将第4等级的数据分开为每一个小时存储
def split_level_4_hour():
    for device in level_4_device:
        data = pd.read_csv(file_split_path + str(device) + '.csv')
        ##获取年月日信息
        data['S_Year'] = pd.DatetimeIndex(data.SDATE).year
        data['S_Month'] = pd.DatetimeIndex(data.SDATE).month
        data['S_Day'] = pd.DatetimeIndex(data.SDATE).day
        data['S_Hour'] = pd.DatetimeIndex(data.SDATE).hour
        ##删除‘S_MINUTE’数据信息
        df = data.drop(['S_MINUTE'], axis=1)
        ##统计每一小时的功率数据
        p_max = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['P_MAX'].max()
        p_max = p_max.reset_index()
        p_min = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['P_MIN'].min()
        p_min = p_min.reset_index()
        p_avg = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['P_AVG'].mean()
        p_avg = p_avg.reset_index()
        ##统计每一小时的用电量数据
        YL_max = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['YL_MAX'].max()
        # YL_max = YL_max.reset_index()
        YL_min = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['YL_MAX'].min()
        # YL_min = YL_min.reset_index()
        result = YL_max - YL_min
        result = result.reset_index()
        temp = pd.DataFrame()
        temp = pd.merge(p_max, p_min)
        temp = pd.merge(temp, p_avg)
        temp = pd.merge(temp, result)
        temp.to_csv(file_level4_split_hour_path + str(device) + '_hour.csv', index=False)
    return 1

# 3.读取第5等级的数据,将第5等级的数据分开为每一个小时存储
def split_level_5_hour():
    for device in level_5_device:
        data = pd.read_csv(file_split_path + str(device) + '.csv')
        ##获取年月日信息
        data['S_Year'] = pd.DatetimeIndex(data.SDATE).year
        data['S_Month'] = pd.DatetimeIndex(data.SDATE).month
        data['S_Day'] = pd.DatetimeIndex(data.SDATE).day
        data['S_Hour'] = pd.DatetimeIndex(data.SDATE).hour
        ##删除‘S_MINUTE’数据信息
        df = data.drop(['S_MINUTE'], axis=1)
        
        ##统计每一小时的功率数据
        p_max = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['P_MAX'].max()
        p_max = p_max.reset_index()
        p_min = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['P_MIN'].min()
        p_min = p_min.reset_index()
        p_avg = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['P_AVG'].mean()
        p_avg = p_avg.reset_index()
        ##统计每一小时的用电量数据
        YL_max = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['YL_MAX'].max()
        # YL_max = YL_max.reset_index()
        YL_min = df.groupby(['S_Year', 'S_Month', 'S_DAY', 'S_Hour'])['YL_MAX'].min()
        # YL_min = YL_min.reset_index()
        result = YL_max - YL_min
        result = result.reset_index()
        temp = pd.DataFrame()
        temp = pd.merge(p_max, p_min)
        temp = pd.merge(temp, p_avg)
        temp = pd.merge(temp, result)
        temp.to_csv(file_level5_split_hour_path + str(device) + '_hour.csv', index=False)
    return 1

# 1.第2等级设备（天）
def split_level_2_day():
    for device in level_2_device:
        data = pd.read_csv(file_split_path + str(device) + '.csv')
        ##获取年月日信息
        data['S_Year'] = pd.DatetimeIndex(data.SDATE).year
        data['S_Month'] = pd.DatetimeIndex(data.SDATE).month
        data['S_Day'] = pd.DatetimeIndex(data.SDATE).day
        data['S_Hour'] = pd.DatetimeIndex(data.SDATE).hour
        ##删除‘S_MINUTE’数据信息
        df = data.drop(['S_MINUTE'], axis=1)
        
        ##统计每一小时的功率数据
        p_max = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['P_MAX'].max()
        p_max = p_max.reset_index()
        p_min = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['P_MIN'].min()
        p_min = p_min.reset_index()
        p_avg = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['P_AVG'].mean()
        p_avg = p_avg.reset_index()
        ##统计每一小时的用电量数据
        YL_max = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['YL_MAX'].max()
        # YL_max = YL_max.reset_index()
        YL_min = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['YL_MAX'].min()
        # YL_min = YL_min.reset_index()
        result = YL_max - YL_min
        result = result.reset_index()
        temp = pd.DataFrame()
        temp = pd.merge(p_max, p_min)
        temp = pd.merge(temp, p_avg)
        temp = pd.merge(temp, result)
        temp.to_csv(file_level2_split_day_path + str(device) + '_day.csv', index=False)
    return 1
    
# 2.第4等级设备（天）
def split_level_4_day():
    for device in level_4_device:
        data = pd.read_csv(file_split_path + str(device) + '.csv')
        ##获取年月日信息
        data['S_Year'] = pd.DatetimeIndex(data.SDATE).year
        data['S_Month'] = pd.DatetimeIndex(data.SDATE).month
        data['S_Day'] = pd.DatetimeIndex(data.SDATE).day
        data['S_Hour'] = pd.DatetimeIndex(data.SDATE).hour
        ##删除‘S_MINUTE’数据信息
        df = data.drop(['S_MINUTE'], axis=1)
        
        ##统计每一小时的功率数据
        p_max = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['P_MAX'].max()
        p_max = p_max.reset_index()
        p_min = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['P_MIN'].min()
        p_min = p_min.reset_index()
        p_avg = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['P_AVG'].mean()
        p_avg = p_avg.reset_index()
        ##统计每一小时的用电量数据
        YL_max = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['YL_MAX'].max()
        # YL_max = YL_max.reset_index()
        YL_min = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['YL_MAX'].min()
        # YL_min = YL_min.reset_index()
        result = YL_max - YL_min
        result = result.reset_index()
        temp = pd.DataFrame()
        temp = pd.merge(p_max, p_min)
        temp = pd.merge(temp, p_avg)
        temp = pd.merge(temp, result)
        temp.to_csv(file_level4_split_day_path + str(device) + '_day.csv', index=False)
    return 1
    
# 3.第5等级设备（天）
def split_level_5_day():
    for device in level_5_device:
        data = pd.read_csv(file_split_path + str(device) + '.csv')
        ##获取年月日信息
        data['S_Year'] = pd.DatetimeIndex(data.SDATE).year
        data['S_Month'] = pd.DatetimeIndex(data.SDATE).month
        data['S_Day'] = pd.DatetimeIndex(data.SDATE).day
        data['S_Hour'] = pd.DatetimeIndex(data.SDATE).hour
        ##删除‘S_MINUTE’数据信息
        df = data.drop(['S_MINUTE'], axis=1)
        
        ##统计每一小时的功率数据
        p_max = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['P_MAX'].max()
        p_max = p_max.reset_index()
        p_min = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['P_MIN'].min()
        p_min = p_min.reset_index()
        p_avg = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['P_AVG'].mean()
        p_avg = p_avg.reset_index()
        ##统计每一小时的用电量数据
        YL_max = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['YL_MAX'].max()
        # YL_max = YL_max.reset_index()
        YL_min = df.groupby(['S_Year', 'S_Month', 'S_DAY'])['YL_MAX'].min()
        # YL_min = YL_min.reset_index()
        result = YL_max - YL_min
        result = result.reset_index()
        temp = pd.DataFrame()
        temp = pd.merge(p_max, p_min)
        temp = pd.merge(temp, p_avg)
        temp = pd.merge(temp, result)
        temp.to_csv(file_level5_split_day_path + str(device) + '_day.csv', index=False)
    return 1
    
#爬虫爬取温度数据
def crawler():
    global years
    global months
    for year in years:
        for month in months:
            try:
                date = str(year) + str(month)
                # print date
                url = 'http://tianqi.2345.com/t/wea_history/js/' + str(date) + '/71144_' + str(date) + '.js'
                content = requests.get(url).text
                # re.search('({[\s\S]}*)',content).group()
                content = content[16:-1]
                # content_json=json.dumps(dict(content),ensure_ascii=False,encoding='utf-8')
                content.encode('unicode-escape').decode('string_escape')
                content_demjson = demjson.decode(content)
                dict_all = content_demjson['tqInfo']
                sdate = []
                temperature_min = []
                temperature_max = []
                try:
                    for i in range(0, len(dict_all)):
                        # print dict_all[i].keys()
                        dict_temp = dict_all[i]
                        # print type(dict_temp['ymd'])
                        sdate.append(dict_temp['ymd'.encode('string_escape').decode('unicode-escape')])
                        temperature_max.append(dict_all[i]['bWendu'][:-1])
                        temperature_min.append(dict_all[i]['yWendu'][:-1])
                except:
                    i=1
                new_df = pd.DataFrame()
                new_df['SDATE'] = sdate
                new_df['temperature_min'] = temperature_min
                new_df['temperature_max'] = temperature_max
                #print new_df.tail(5)
                filename = "data_temperature_" + str(date) + ".csv"
                new_df.to_csv(file_temperature_path +str(filename), index=False)
                print date,"温度数据爬取成功"
            except:
                print date,"温度数据爬取失败"
    # 温度数据的综合
    data = []
    for year in years:
        for month in months:
            try:
                date = str(year) + str(month)
                filename = "data_temperature_" + str(date) + ".csv"
                data.append(pd.read_csv(file_temperature_path +str(filename)))
            except:
                print date,"温度数据合并失败"
    df = pd.DataFrame()
    for i in range(0, len(data)):
        df = df.append(data[i])
        df.reset_index(inplace=True)
        del df['index']
    df['temperature_avg'] = (df['temperature_max'] + df['temperature_min']) / 2
    df.to_csv(file_path+"data_temperature.csv", index=False)
    return df


#将S_Year等数据转化为SDATE
def convert_date(data):
    result = []
    try:
        for year,month,day in zip(data['S_Year'],data['S_Month'],data['S_DAY']):
            result.append(str(int(year))+'/'+str(int(month))+'/'+str(int(day)))
    except:
        print("日期数据转化为SDATE失败")
    return result

#判断文件名中是否包含某个名称
def find_str(str_1,str_list):
    for temp in str_list:
        if temp in str_1:
            return 1
    return 0

#获取到与暖气相关设备的数据
def get_device_heating(path,file_list):
    all_file = file_name(path)
    result_data_len = pd.read_csv(all_file[0])
    result_data = pd.DataFrame()
    result_data['S_Year'] = result_data_len['S_Year']
    result_data['S_Month'] = result_data_len['S_Month']
    result_data['S_DAY'] = result_data_len['S_DAY']
    result_data['YL_MAX'] = [0]*len(result_data_len)
    result_data['SDATE'] = convert_date(result_data)
    for temp_file in all_file:
        data = pd.read_csv(temp_file)
        if find_str(temp_file,file_list) == 1:
            #print(1)
            result_data['YL_MAX'] +=  data['YL_MAX']
    del result_data['S_Year']
    del result_data['S_Month']
    del result_data['S_DAY']
    return result_data

#设置isHeating参数
def set_isHeating(path,file_list):
    result = []
    YL_data = get_device_heating(path,file_list)
    YL_data['SDATE'] = pd.to_datetime(YL_data['SDATE'])
    i = 0
    for temp in YL_data['SDATE']:
        if temp.month in [11,12,1,2,3]:
            if YL_data['YL_MAX'][i] > 1700:
                result.append(1)
            elif YL_data['YL_MAX'][i] > 900:
                result.append(0.6)
            else:
                result.append(0)
        else:
            result.append(0)
        i+=1
    return result

##设置week_year参数
def set_week_year(data):
	result = []
	data['SDATE'] = pd.to_datetime(data['SDATE'])
	for temp in data['SDATE']:
		result.append(dt.date(temp.year,temp.month,temp.day).isocalendar()[1])
	return result

#设置weekday
def set_weekday(data):
    result = []
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    for temp in data['SDATE']:
        result.append(dt.date.isoweekday(dt.datetime(temp.year,temp.month,temp.day)))
    return result

# 4级设备每天数据的合并
def merge_all_data(df_temperature):
    all_file = [file_level4_split_day_path + 'K0bjcxd4010111_day.csv',
                file_level4_split_day_path + 'K0bjcxd4020222_day.csv',
                file_level4_split_day_path + 'K0bjcxd4030313_day.csv']
    data_all = pd.read_csv(file_level4_split_day_path + 'K0bjcxm4010411_day.csv')
    for temp_file in all_file:
        data = pd.read_csv(temp_file)
        data_all['P_MAX'] += data['P_MAX']
        data_all['P_MIN'] += data['P_MIN']
        data_all['P_AVG'] += data['P_AVG']
        data_all['YL_MAX'] += data['YL_MAX']
    data_all['SDATE'] = convert_date(data_all)
    data_all['week_year'] = set_week_year(data_all)
    data_all['IsHeating'] = set_isHeating(file_level5_split_day_path,heating_file_list)
    data_all['weekday'] = set_week_year(data_all)
    df_temperature['SDATE'] = pd.to_datetime(df_temperature['SDATE'])
    data_temp = pd.merge(data_all,df_temperature,on=['SDATE'])
    data_all['temperature_max'] = data_temp['temperature_max']
    data_all['temperature_min'] = data_temp['temperature_min']
    data_all['temperature_avg'] = data_temp['temperature_avg']
    data_holiday = pd.read_csv(file_path+"data_all_holiday.csv")
    data_holiday['SDATE'] = pd.to_datetime(data_holiday['SDATE'])
    data_all = pd.merge(data_all,data_holiday,on=['SDATE'])
    del data_all['S_Year']
    del data_all['S_Month']
    del data_all['S_DAY']
    data_all.to_csv(file_path + 'data_all.csv', index=False)
    #sys.exit()
    return 1

def deal_data(data,df_temperature):
    if data_original_segmentation(data)==1:
        print "原始文件切分完毕"
    if split_level_2_hour()==1:
        print "2级设备文件的每小时的分类完毕"
    else:
        print "2级设备文件的每小时的分类失败"
        sys.exit()
    if split_level_4_hour()==1:
        print "4级设备文件的每小时的分类完毕"
    else:
        print "4级设备文件的每小时的分类失败"
        sys.exit()
    if split_level_5_hour()==1:
        print "5级设备文件的每小时的分类完毕"
    else:
        print "5级设备文件的每小时的分类失败"
        sys.exit()
    if split_level_2_day()==1:
        print "2级设备文件的每天的分类完毕"
    else:
        print "2级设备文件的每天的分类失败"
        sys.exit()
    if split_level_4_day()==1:
        print "4级设备文件的每天的分类完毕"
    else:
        print "4级设备文件的每天的分类失败"
        sys.exit()
    if split_level_5_day()==1:
        print "5级设备文件的每天的分类完毕"
    else:
        print "5级设备文件的每天的分类失败"
        sys.exit()
    if merge_all_data(df_temperature)==1:
        print "4级设备每天数据合并完毕"
    else:
        print "4级设备每天数据合并失败"
        sys.exit()



#对数据进行处理，得到模型所使用的数据

#建模与调参
def model_select():
    data=pd.read_csv(file_path+'data_all.csv')
    X_train = data.drop(['SDATE', 'P_MAX', 'P_MIN', 'P_AVG', 'YL_MAX'], axis=1)
    Y_train = data['YL_MAX']
    # 评估算法 - 评估标准
    num_folds = 10
    seed = 7
    scoring = 'neg_mean_absolute_error'
    start_time=dt.datetime.now()
    # 集成算法GradientBoostingRegressor - 调参
    scaler = StandardScaler().fit(X_train)
    rescaledX = scaler.transform(X_train)
    param_grid = {'n_estimators': [5, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800, 900],
                  'min_samples_leaf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                  'min_samples_split': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                  'learning_rate': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                    0.7, 0.8, 0.9, 1.0]}
    model = GradientBoostingRegressor()
    kfold = KFold(n_splits=num_folds, random_state=seed)
    print "算法开始调参，采用10折交叉验证"
    grid = GridSearchCV(estimator=model, param_grid=param_grid, scoring=scoring, cv=kfold)
    grid_result = grid.fit(X=rescaledX, y=Y_train)
    print('总模型中GBDT最优：%s 使用%s' % (grid_result.best_score_, grid_result.best_params_))
    end_time=dt.datetime.now()
    time=end_time-start_time
    print "调参结束,耗时",time
    print "进行总模型的训练"
    # 训练模型
    scaler = StandardScaler().fit(X_train)
    rescaledX = scaler.transform(X_train)
    gbr = GradientBoostingRegressor(n_estimators=grid_result.best_params_['n_estimators'], min_samples_leaf=grid_result.best_params_['min_samples_leaf'], min_samples_split=grid_result.best_params_['min_samples_split'], learning_rate=grid_result.best_params_['learning_rate'])
    gbr.fit(X=rescaledX, y=Y_train)
    print "总模型训练完毕"
    model_file = file_path+"all_model.sav"
    with open(model_file, 'wb') as model_f:
        dump(gbr, model_f)
    print "总模型保存完毕"

def summer_model_select():
    data=pd.read_csv(file_path+'data_all.csv')
    data['SDATE']=pd.to_datetime(data['SDATE'])
    new_df = pd.DataFrame()
    for i in range(0, len(data['SDATE'])):
        if data['SDATE'][i].month >= 6 and data['SDATE'][i].month <= 8:
            new_df = new_df.append(data.iloc[i])
    X_train = new_df.drop(['SDATE', 'P_MAX', 'P_MIN', 'P_AVG', 'YL_MAX'], axis=1)
    Y_train = new_df['YL_MAX']
    # 评估算法 - 评估标准
    num_folds = 10
    seed = 7
    scoring = 'neg_mean_absolute_error'
    start_time=dt.datetime.now()
    # 集成算法GradientBoostingRegressor - 调参
    scaler = StandardScaler().fit(X_train)
    rescaledX = scaler.transform(X_train)
    param_grid = {'n_estimators': [5, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800, 900],
                  'min_samples_leaf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                  'min_samples_split': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                  'learning_rate': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                    0.7, 0.8, 0.9, 1.0]}
    model = GradientBoostingRegressor()
    kfold = KFold(n_splits=num_folds, random_state=seed)
    print "算法开始调参，采用10折交叉验证"
    grid = GridSearchCV(estimator=model, param_grid=param_grid, scoring=scoring, cv=kfold)
    grid_result = grid.fit(X=rescaledX, y=Y_train)
    print('夏季模型中GBDT最优：%s 使用%s' % (grid_result.best_score_, grid_result.best_params_))
    end_time=dt.datetime.now()
    time=end_time-start_time
    print "调参结束,耗时",time
    print "进行夏季模型的训练"
    # 训练模型
    scaler = StandardScaler().fit(X_train)
    rescaledX = scaler.transform(X_train)
    gbr = GradientBoostingRegressor(n_estimators=grid_result.best_params_['n_estimators'], min_samples_leaf=grid_result.best_params_['min_samples_leaf'], min_samples_split=grid_result.best_params_['min_samples_split'], learning_rate=grid_result.best_params_['learning_rate'])
    gbr.fit(X=rescaledX, y=Y_train)
    print "夏季模型训练完毕"
    model_file = file_path+"summer_model_new.sav"
    with open(model_file, 'wb') as model_f:
        dump(gbr, model_f)
    print "夏季模型保存完毕"

def other_model_select():
    data=pd.read_csv(file_path+'data_all.csv')
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    new_df = pd.DataFrame()
    for i in range(0, len(data['SDATE'])):
        if data['SDATE'][i].month < 6 or data['SDATE'][i].month > 8:
            new_df = new_df.append(data.iloc[i])
    X_train = new_df.drop(['SDATE', 'P_MAX', 'P_MIN', 'P_AVG', 'YL_MAX'], axis=1)
    Y_train = new_df['YL_MAX']
    # 评估算法 - 评估标准
    num_folds = 10
    seed = 7
    scoring = 'neg_mean_absolute_error'
    start_time=dt.datetime.now()
    # 集成算法GradientBoostingRegressor - 调参
    scaler = StandardScaler().fit(X_train)
    rescaledX = scaler.transform(X_train)
    param_grid = {'n_estimators': [5, 10, 20, 30, 40, 50, 60, 70, 80, 100, 200, 300, 400, 500, 600, 700, 800, 900],
                  'min_samples_leaf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                  'min_samples_split': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                  'learning_rate': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,
                                    0.7, 0.8, 0.9, 1.0]}
    model = GradientBoostingRegressor()
    kfold = KFold(n_splits=num_folds, random_state=seed)
    print "算法开始调参，采用10折交叉验证"
    grid = GridSearchCV(estimator=model, param_grid=param_grid, scoring=scoring, cv=kfold)
    grid_result = grid.fit(X=rescaledX, y=Y_train)
    print('秋冬模型中GBDT最优：%s 使用%s' % (grid_result.best_score_, grid_result.best_params_))
    end_time=dt.datetime.now()
    time=end_time-start_time
    print "调参结束,耗时",time
    print "进行秋冬模型的训练"
    # 训练模型
    scaler = StandardScaler().fit(X_train)
    rescaledX = scaler.transform(X_train)
    gbr = GradientBoostingRegressor(n_estimators=grid_result.best_params_['n_estimators'], min_samples_leaf=grid_result.best_params_['min_samples_leaf'], min_samples_split=grid_result.best_params_['min_samples_split'], learning_rate=grid_result.best_params_['learning_rate'])
    gbr.fit(X=rescaledX, y=Y_train)
    print "秋冬模型训练完毕"
    model_file = file_path+"other_model_new.sav"
    with open(model_file, 'wb') as model_f:
        dump(gbr, model_f)
    print "秋冬模型保存完毕"

def model_reconstruction():
    data = file_read()
    try:
        df_temperature = crawler()
    except:
        print "爬虫失败"
    deal_data(data, df_temperature)
    # summer_model_select()
    # other_model_select()
    #model_select()

if __name__ == '__main__':
    model_reconstruction()
