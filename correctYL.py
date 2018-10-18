#!/usr/bin/python
# coding: utf-8

#导入包
import pandas as pd
import numpy as np
import calendar 
import sys
import pylab as pl
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.externals.joblib import load
import sxtwl
import time

#引入配置文件，配置文件的路径随需要进行修改
sys.path.append("./configuration_files")
import configuration_files

#文件夹路径
file_path = configuration_files.folder_path
#预测数据文件
predict_file = file_path+"/predict_data.csv"
#夏季模型文件
summer_model_file = file_path+"/summer_model.sav"
#秋冬模型文件
other_model_file = file_path+"/other_model.sav"
#标准化文件
data_scaler_file = file_path+"/model_data.csv"
#历史放假文件
data_holiday_history = file_path+"/data_all_holiday.csv"

#绘图
def show_picture(predictions,date_data):
    date_data = pd.to_datetime(date_data)
    dates = pd.DatetimeIndex(date_data)
    data = pd.DataFrame(predictions,index=dates,columns=['YL'])
    pl.xticks(rotation=30)
    plt.title('Daily electricity consumption forecast scatter plot')
    plt.ylabel('Kilowatt hour')
    plt.scatter(data.index,data['YL'])
    plt.xlim(data.index[0],data.index[-1])
    plt.show()

#检验日期是否正确
def is_valid_date(str):
    try:
        time.strptime(str, "%Y/%m/%d")
        return 1
    except:
        print "输入日期错误,请重新输入："
        return 0

#模型数据标准化
def model_standand(data_scaler):
    try:
        data_scaler['SDATE']=pd.to_datetime(data_scaler['SDATE'])
        data_scaler_summer = pd.DataFrame()
        data_scaler_other = pd.DataFrame()
        for i in range(0, len(data_scaler['SDATE'])):
            if data_scaler['SDATE'][i].month >= 6 and data_scaler['SDATE'][i].month <= 8:
                data_scaler_summer = data_scaler_summer.append(data_scaler.iloc[i])
        for i in range(0, len(data_scaler['SDATE'])):
            if data_scaler['SDATE'][i].month < 6 or data_scaler['SDATE'][i].month > 8:
                data_scaler_other = data_scaler_other.append(data_scaler.iloc[i])
        #data_scaler_summer = data_scaler[data_scaler['SDATE']>=pd.to_datetime('2018/5/31')]
        #data_scaler_other = data_scaler[data_scaler['SDATE'] < pd.to_datetime('2018/5/31')]
        X_scaler_summer = data_scaler_summer.drop(['SDATE', 'P_MAX', 'P_MIN', 'P_AVG', 'YL_MAX'], axis=1)
        X_scaler_other = data_scaler_other.drop(['SDATE', 'P_MAX', 'P_MIN', 'P_AVG', 'YL_MAX'], axis=1)
        X_scaler_summer = X_scaler_summer[['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
        X_scaler_other = X_scaler_other[['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
        scaler_summer=StandardScaler().fit(X_scaler_summer)
        scaler_other = StandardScaler().fit(X_scaler_other)
        return scaler_summer,scaler_other
    except:
        print "模型标准化失败"
        sys.exit()


#调用模型进行预测纠正
def model_predict(model_file,data,IsSummer,data_scaler_file):
    data_scaler = pd.read_csv(data_scaler_file)
    scaler_summer,scaler_other = model_standand(data_scaler)
    X_predict = data[['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
    try:
        with open(model_file,'rb') as model_f:
            loaded_model = load(model_f)
            if IsSummer == 1:
                rescaledX_validation_summer = scaler_summer.transform(X_predict)
                predictions = loaded_model.predict(rescaledX_validation_summer)
            else:
                rescaledX_validation_other = scaler_other.transform(X_predict)
                predictions = loaded_model.predict(rescaledX_validation_other)
            return predictions
    except:
        print "模型调用失败"
        sys.exit()

#纠正空调
def update_airconditioner(data,summer_model,other_model,data_scaler_file):
    summer_result = []
    other_result = []
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    try:
        if data['SDATE'][0].month == 5 or data['SDATE'][0].month == 6:
            print "请输入打开空调的开始日期(输入日期要求:年/月/日 如:2018/6/1):"
            start_time = raw_input()
            while is_valid_date(start_time) == 0:
                start_time = raw_input()
            print "正在重新预测"
            summer_data = data[data['SDATE'] >= start_time]
            other_data = data[data['SDATE'] < start_time]
            if len(summer_data) != 0:
                summer_result = model_predict(summer_model,summer_data,1,data_scaler_file)
            if len(other_data) != 0:
                other_result = model_predict(other_model,other_data,0,data_scaler_file)
            return (np.append(summer_result,other_result))
        elif data['SDATE'][0].month == 9 or data['SDATE'][0].month == 10:
            print "请输入关闭空调的日期(输入日期要求:年/月/日 如:2018/9/1):"
            end_time = raw_input()
            while is_valid_date(end_time) == 0:
                end_time = raw_input()
            print "正在重新预测"
            summer_data = data[data['SDATE'] < end_time]
            other_data = data[data['SDATE'] >= end_time]
            if len(summer_data) != 0:
                summer_result = model_predict(summer_model,summer_data,1,data_scaler_file)
            if len(other_data) != 0:
                other_result = model_predict(other_model,other_data,0,data_scaler_file)
            return (np.append(summer_result,other_result))
    except:
        print "纠错失败"
        sys.exit()

#修改供暖时间
def correct_isHeating(data,start_date,end_date):
    result = []
    #供暖时间段
    date = pd.date_range(start_date,end_date)
    try:
        
        for temp in data['SDATE']:
            if temp in date:
                result.append(1)
            else:
                result.append(0)   
    except:
        print("是否供暖参数设置失败")
        sys.exit()
    return result

#纠正暖气
def update_heating(data,model_file,data_scaler_file):
    result = []
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    try:
        if data['SDATE'][0].month == 11 or data['SDATE'][0].month == 12:
            print "请输入供暖开始日期(输入日期要求:年/月/日 如:2018/11/1)："
            start_time = raw_input()
            while is_valid_date(start_time) == 0:
                start_time = raw_input()
            print "正在重新预测"
            end_time_day = calendar.monthrange(data['SDATE'][0].year, data['SDATE'][0].month)[1]
            end_time = str(data['SDATE'][0].year)+str(data['SDATE'][0].month)+str(end_time_day)
            data['IsHeating']=correct_isHeating(data,start_time,end_time)
            result = model_predict(model_file,data,0,data_scaler_file)
        elif data['SDATE'][0].month == 3:
            print "请输入供暖结束日期(输入日期要求:年/月/日 如:2018/3/1)："
            end_time = raw_input()
            while is_valid_date(end_time) == 0:
                end_time = raw_input()
            print "正在重新预测"
            data['IsHeating']=correct_isHeating(data,data['SDATE'][0],end_time)
            result = model_predict(model_file,data,0,data_scaler_file)
        return result
    except:
        print "纠错失败"
        sys.exit()
        
#判断是否为春节期间
def IsSpringFestival(data,date_spring):
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    for temp in data['SDATE']:
        if temp in date_spring:
            return 1
    return 0

#更新历史放假文件
def update_file(date,data_holiday_history):
    result = []
    data = pd.read_csv(data_holiday_history)
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    for temp in data['SDATE']:
        if temp in date:
            result.append(1)
        else:
            result.append(0)
    data = pd.concat([data, pd.DataFrame(columns=list('IsSpringFestival'))])
    data['IsSpringFestival'] = result
    data.to_csv(data_holiday_history,index=False)
    
#纠错IsSpringFestival设置
def update_SpringFestival(data,data_holiday_history,model_file,data_scaler_file):
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    lunar = sxtwl.Lunar()
    start_day = lunar.getDayByLunar(data['SDATE'][0].year-1, 12, 20  , False)
    end_day = lunar.getDayByLunar(data['SDATE'][0].year, 1, 15  , False)
    start_time = str(start_day.y)+'/'+str(start_day.m)+'/'+str(start_day.d)
    end_time = str(end_day.y)+'/'+str(end_day.m)+'/'+str(end_day.d)
    date = pd.date_range(start_time,end_time)
    spring_result = []
    result = []
    try:
        if IsSpringFestival(data,date) == 1:
            print "请输入本次数据中春节假期开始时间:(输入日期要求:年/月/日 如:2018/2/1):"
            start_input = raw_input()
            while is_valid_date(start_input) == 0:
                start_input = raw_input()
            print "请输入本次数据中春节假期结束时间:(输入日期要求:年/月/日 如:2018/2/1):"
            end_input = raw_input()
            while is_valid_date(end_input) == 0:
                end_input = raw_input()
            date_input = pd.date_range(start_input,end_input)
            for temp in data['SDATE']:
                if temp in date_input:
                    spring_result.append(1)
                else:
                    spring_result.append(0)
            data['IsSpringFestival']=spring_result
            result = model_predict(model_file,data,0,data_scaler_file)
            update_file(date_input,data_holiday_history)
        return result
    except:
        print "纠错失败"
        sys.exit()

#纠正程序
def correct_YL():
    print "请选择纠错项目："
    print "纠错空调1"
    print "纠错供暖2"
    print "纠错春节3"
    choose_num = input()
    if choose_num == 1:
        data = pd.read_csv(predict_file)
        print "数据载入完成"
        result = update_airconditioner(data,summer_model_file,other_model_file,data_scaler_file)
        if len(result) == 0:
            print "无需重新预测"
        else:
            print "每日用电量的预测结果："
            print result
            print "总用电量:",sum(result)
            show_picture(result,data['SDATE'])
    elif choose_num == 2:
        data = pd.read_csv(predict_file)
        result = update_heating(data,other_model_file,data_scaler_file)
        if len(result) == 0:
            print "无需重新预测"
        else:
            print "每日用电量的预测结果："
            print result
            print "总用电量:",sum(result)
            show_picture(result, data['SDATE'])
    elif choose_num == 3:
        data = pd.read_csv(predict_file)
        result = update_SpringFestival(data, data_holiday_history, other_model_file, data_scaler_file)
        if len(result) == 0:
            print "无需重新预测"
        else:
            print "每日用电量的预测结果："
            print result
            print "总用电量:", sum(result)
            show_picture(result, data['SDATE'])
    else:
        print "输入的字符有误"
        sys.exit()

if __name__ == '__main__':
    correct_YL()

