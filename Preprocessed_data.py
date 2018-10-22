#!/usr/bin/python
# -*- coding: UTF-8 -*-

#导入包
import requests
import json
import sys
import pandas as pd
from datetime import datetime
import datetime as dt
import sxtwl

#引入配置文件，配置文件的路径随需要进行修改
sys.path.append("./configuration_files")
import configuration_files

#文件夹路径
folder_path=configuration_files.folder_path
# 设置季度转化的温度
temperature_autumn_to_winter = configuration_files.temperature_autumn_to_winter
temperature_winter_to_spring = configuration_files.temperature_winter_to_spring
date_autumn_to_winter = configuration_files.date_autumn_to_winter
date_winter_to_spring = configuration_files.date_winter_to_spring
month_autumn_to_winter = configuration_files.month_autumn_to_winter
month_winter_to_spring = configuration_files.month_winter_to_spring
#以下文件路径可以无需修改

#全局变量方便修改天气预报的信息
file_all_holiday_path=folder_path+"/data_all_holiday.csv"
file_holiday_path=folder_path+"/isHoliday.csv"
file_path=folder_path+"/predict_data.csv"
file_temperature_path=folder_path+"/weather_report.csv"
df_temperature_report = pd.DataFrame([], columns=['SDATE', 'temperature_max', 'temperature_min', 'temperature_avg'])

#获取jason请求
def get_datejson(year,month):
    # 请求连接
    # url = 'http://d1.weather.com.cn/calendar_new/2018/101010200_201809.html?_=1535598982101'
    url = 'http://d1.weather.com.cn/calendar_new/'+year+'/101010200_'+ year + month+'.html?_=1535598982101'
    # 请求头： Referer：通过Referer告诉服务器我是从哪个页面链接过来的，有些网站会对这个做验证，防止别人盗链
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
        'Referer': 'http://www.weather.com.cn/weather40d/101010200.shtml'
    }
    # 发送requests请求，对得到的数据进行切片，得到json字符串
    content  = requests.get(url=url, headers=headers).content[11:]
    date_json = json.loads(content)
    # print(date_json)
    return date_json

#获取日期中的温度
def get_date(year, month):
    date_json = get_datejson(year, month)
    date_items = []
    for date in date_json:
        item = {}
        # 格式化日期
        theDate = date.get('date')
        dataObj = datetime.strptime(theDate, '%Y%m%d')
        dataStr = datetime.strftime(dataObj, '%Y/%m/%d')
        item['SDATE'] = dataStr
        item['temperature_max'] = date.get('hmax')
        item['temperature_min'] = date.get('hmin')
        item['temperature_avg'] = str((int(item['temperature_max']) + int(item['temperature_min']))/2)
        date_items.append(item)
	new_df_temperature_report = pd.DataFrame(date_items)
	#定义全局变量df,每次合并新的DataFrame
	global df_temperature_report
	df_temperature_report = pd.concat([df_temperature_report, new_df_temperature_report], sort=False, ignore_index=True)
	df_temperature_report.drop_duplicates(inplace=True)
	df_temperature_report.to_csv(file_temperature_path,index=False)

#爬虫主体函数
def crawler(years,months):
	for year in years:
		for month in months:
			try:
				get_date(year,month)
			except:
				print "未爬下来的年为", year, "月为", month

#获取当前日期以用以爬虫的时间获取
def crawler_time():
	now_time = datetime.now()
	years = []
	years.append(str(now_time.year))
	months = []
	if now_time.month < 9 and now_time > 1:
		months.append(str(now_time.month - 1))
		months.append(str(now_time.month))
		months.append(str(now_time.month + 1))
	elif now_time.month == 9:
		months.append(str('08'))
		months.append(str('09'))
		months.append(str('10'))
	elif now_time.month == 10:
		months.append(str('09'))
		months.append(str('10'))
		months.append(str('11'))
	elif now_time.month == 11:
		months.append(str('10'))
		months.append(str('11'))
		months.append(str('12'))
	elif now_time.month == 12:
		months.append(str('11'))
		months.append(str('12'))
		months.append(str('01'))
		years.append(str(now_time.year + 1))
	elif now_time.month == 1:
		months.append(str('12'))
		months.append(str('01'))
		months.append(str('02'))
		years.append(str(now_time.year+1))
	return years,months
#爬虫结束

##设置week_year参数
def set_week_year(data):
	result = []
	data['SDATE'] = pd.to_datetime(data['SDATE'])
	for temp in data['SDATE']:
		result.append(dt.date(temp.year,temp.month,temp.day).isocalendar()[1])
	return result

#设置weekday参数
def set_weekday(data):
    result = []
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    for temp in data['SDATE']:
        result.append(dt.date.isoweekday(dt.datetime(temp.year,temp.month,temp.day)))
    return result



# 根据温度确认季节
def temperature_judge_sdate(data):
	data['SDATE'] = pd.to_datetime(data['SDATE'])
	if data['SDATE'][0].month in month_autumn_to_winter:
		return temperature_judge_sdate_autumn_to_winter(data)
	elif data['SDATE'][0].month in month_winter_to_spring:
		return temperature_judge_sdate_winter_to_spring(data)

def temperature_judge_sdate_autumn_to_winter(data):
	judge = 0
	count = 0
	# data['SDATE']=pd.to_datetime(data['SDATE'])
	for i in range(0, len(data['temperature_avg'])):
		if data['temperature_avg'][i] <= temperature_autumn_to_winter:
			count = count + 1
			if count == date_autumn_to_winter:
				if judge == 0:
					judge = 1
					return data['SDATE'][i - date_autumn_to_winter + 1]
		elif data['temperature_avg'][i] > temperature_autumn_to_winter:
			count = 0


def temperature_judge_sdate_winter_to_spring(data):
	judge = 0
	count = 0
	# data['SDATE']=pd.to_datetime(data['SDATE'])
	for i in range(0, len(data['temperature_avg'])):
		if data['temperature_avg'][i] >= temperature_winter_to_spring:
			count = count + 1
			if count == date_winter_to_spring:
				if judge == 0:
					judge = 1
					return data['SDATE'][i - date_winter_to_spring + 1]
		elif data['temperature_avg'][i] < temperature_winter_to_spring:
			count = 0


# 设置isHeating参数
def set_isHeating(data):
	data['SDATE'] = pd.to_datetime(data['SDATE'])
	date_autumn_to_winter = dt.datetime(data['SDATE'][0].year, 11, 1)
	date_winter_to_spring = dt.datetime(data['SDATE'][0].year, 4, 30)
	if data['SDATE'][0].month in month_autumn_to_winter:
		date_autumn_to_winter = temperature_judge_sdate(data)
		if date_autumn_to_winter is None:
			if data['SDATE'][0].month == 12:
				date_autumn_to_winter = dt.datetime(data['SDATE'][0].year + 1, 1, 1)
			else:
				date_autumn_to_winter = dt.datetime(data['SDATE'][0].year, data['SDATE'][0].month + 1, 1)
		else:
			print "供暖开始日期：", date_autumn_to_winter
	elif data['SDATE'][0].month in month_winter_to_spring:
		date_winter_to_spring = temperature_judge_sdate(data)
		if date_winter_to_spring is None:
			date_winter_to_spring = dt.datetime(data['SDATE'][0].year, data['SDATE'][0].month + 1, 1)
		else:
			print "供暖结束日期：", date_winter_to_spring
	
	# 供暖月份
	heating_month_list = []
	if date_autumn_to_winter.year != date_winter_to_spring.year:
		for month in range(date_autumn_to_winter.month, date_winter_to_spring.month + 1):
			heating_month_list.append(month)
	else:
		for month in range(date_autumn_to_winter.month, date_winter_to_spring.month + 13):
			if month <= 12:
				heating_month_list.append(month)
			else:
				heating_month_list.append(month - 12)
	# 供暖开始日
	start_day = date_autumn_to_winter.day
	# 供暖结束日
	end_day = date_winter_to_spring.day
	result = []
	try:
		data['SDATE'] = pd.to_datetime(data['SDATE'])
		for temp in data['SDATE']:
			if temp.month in heating_month_list:
				if temp.month == heating_month_list[0] and temp.day < start_day:
					result.append(0)
				elif temp.month == heating_month_list[-1] and temp.day >= end_day:
					result.append(0)
				else:
					result.append(1)
			else:
				result.append(0)
	except:
		print("是否供暖参数设置失败")
	return result

#判断是否为在过年期间
def IsSpringFestival(data,date_spring):
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    for temp in data['SDATE']:
        if temp in date_spring:
            return 1
    return 0

#设置IsSpringFestival参数
def set_SpringFestival(data):
    data['SDATE'] = pd.to_datetime(data['SDATE'])
    lunar = sxtwl.Lunar()
    start_day = lunar.getDayByLunar(data['SDATE'][0].year-1, configuration_files.springfestival_start_month, configuration_files.springfestival_start_date  , False)
    end_day = lunar.getDayByLunar(data['SDATE'][0].year, configuration_files.springfestival_end_month, configuration_files.springfestival_end_date  , False)
    start_time = str(start_day.y)+'/'+str(start_day.m)+'/'+str(start_day.d)
    end_time = str(end_day.y)+'/'+str(end_day.m)+'/'+str(end_day.d)
    date = pd.date_range(start_time,end_time)
    result = []
    if IsSpringFestival(data,date) == 1:
        for temp in data['SDATE']:
            if temp in date:
                result.append(1)
            else:
                result.append(0)
		print "本次数据中春节放假开始日期:",start_time
		print "本次数据中春节放假结束日期:",end_time
        return result
    else:
        return [0] * len(data['SDATE'])

def preprocfessed_data():
	try:
		years=[]
		months=[]
		years,months=crawler_time()
		crawler(years,months)
		print "爬取温度数据成功"
	except:
		print "爬取温度预报数据失败"
	print "数据载入"
	holiday_df=pd.read_csv(file_holiday_path)
	holiday_df['IsSpringFestival'] = set_SpringFestival(holiday_df)
	try:
		holiday_all_df=pd.read_csv(file_all_holiday_path)
		holiday_all_df['SDATE']=pd.to_datetime(holiday_all_df['SDATE'])
		holiday_all_df=pd.concat([holiday_all_df,holiday_df],axis=0)
		holiday_all_df.drop_duplicates(inplace=True)
		holiday_all_df.to_csv(file_all_holiday_path,index=False)
	except:
		print "新节假日数据粘贴失败"
	print "数据载入完毕，开始进行数据合并"
	holiday_df['SDATE']=pd.to_datetime(holiday_df['SDATE'])
	df_temperature_report['SDATE']=pd.to_datetime(df_temperature_report['SDATE'])
	final_df=pd.merge(holiday_df,df_temperature_report,on=['SDATE'])
	final_df['IsHeating']=set_isHeating(final_df)
	final_df['week_year']=set_week_year(final_df)
	final_df['weekday']=set_weekday(final_df)
	print "数据合并完毕"
	final_df.to_csv(file_path,index=False)
	print "数据输出完毕"

if __name__ == '__main__':
	preprocfessed_data()