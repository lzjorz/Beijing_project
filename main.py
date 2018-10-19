#!/usr/bin/python
# -*- coding: UTF-8 -*-

#导入包
import sys
from pandas import read_csv
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import pylab as pl
import pandas as pd
import numpy as np
from sklearn.externals.joblib import load

#引入配置文件，配置文件的路径随需要进行修改
sys.path.append("./configuration_files")
import configuration_files


#入秋与入夏时间，在此依据温度来规定
temperature_summer_to_autumn=configuration_files.temperature_summer_to_autumn
temperature_spring_to_summer=configuration_files.temperature_spring_to_summer
date_summer_to_autumn=configuration_files.date_summer_to_autumn
date_spring_to_summer=configuration_files.date_spring_to_summer
month_summer_to_autumn=configuration_files.month_summer_to_autumn
month_spring_to_summer=configuration_files.month_spring_to_summer

#文件夹路径
folder_path=configuration_files.folder_path
rebuild_model_python_path=folder_path+"/Model_reconstruction.py"
Preprocessed_data_python_path=folder_path+"/Preprocessed_data.py"
correct_YL_path=folder_path+"/correctYL.py"
sys.path.append(rebuild_model_python_path)
sys.path.append(Preprocessed_data_python_path)
sys.path.append(correct_YL_path)
import Model_reconstruction
import Preprocessed_data
import correctYL
summer_model_file=folder_path+"/summer_model.sav"
other_model_file=folder_path+"/other_model.sav"
file_path_run_model=folder_path+"/predict_data.csv"
data_scaler_file=folder_path+"/model_data.csv"
result_file = folder_path+"/result_data.csv"

#得到对应月份的最大功率
def get_month_p_max(month_number):
	if month_number==9:
		return 1626.01
	elif month_number==10:
		return 860.27
	else:
		try:
			data_all = pd.read_csv('d://Beijing_project/code/data_all.csv')
		except:
			print "读取功率总文件失败"
		data_all['SDATE'] = pd.to_datetime(data_all['SDATE'])
		month = []
		year = []
		for i in range(0, len(data_all['SDATE'])):
			month.append(data_all['SDATE'][i].month)
			year.append(data_all['SDATE'][i].year)
		data_all['month'] = month
		data_all['year'] = year
		grouped = data_all['P_MAX'].groupby([data_all['month'], data_all['year']])
		grouped_p_max_month_year = grouped.max()
		grouped_p_max_month = grouped_p_max_month_year.groupby('month').mean()
		return round(grouped_p_max_month[month_number]+np.random.random(),2)

#根据温度来判断日期
def temperature_judge_sdate(data):
	data['SDATE'] = pd.to_datetime(data['SDATE'])
	if data['SDATE'][0].month in month_summer_to_autumn:
		return temperature_judge_sdate_summer_to_autumn(data)
	elif data['SDATE'][0].month in month_spring_to_summer:
		return temperature_judge_sdate_spring_to_summer(data)

#根据温度来判断日期，针对夏季到秋季的换季
def temperature_judge_sdate_summer_to_autumn(data):
	judge = 0
	count = 0
	# data['SDATE']=pd.to_datetime(data['SDATE'])
	for i in range(0, len(data['temperature_max'])):
		if data['temperature_max'][i] < temperature_summer_to_autumn:
			count = count + 1
			if count == date_summer_to_autumn:
				if judge == 0:
					judge = 1
					return data['SDATE'][i - date_summer_to_autumn + 1]
		elif data['temperature_max'][i] >= temperature_summer_to_autumn:
			count = 0

#根据温度来判断日期，针对春季到夏季的换季
def temperature_judge_sdate_spring_to_summer(data):
	judge = 0
	count = 0
	# data['SDATE']=pd.to_datetime(data['SDATE'])
	for i in range(0, len(data['temperature_avg'])):
		if data['temperature_avg'][i] >= temperature_spring_to_summer:
			count = count + 1
			if count == date_spring_to_summer:
				if judge == 0:
					judge = 1
					return data['SDATE'][i - date_spring_to_summer + 1]
		elif data['temperature_avg'][i] < temperature_spring_to_summer:
			count = 0

#夏季模型载入
def load_summer_model():
	try:
		with open(summer_model_file,'rb') as summer_model_f:
			run_model=load(summer_model_f)
		print "夏季模型载入成功"
	except:
		print "夏季模型载入失败"
	return run_model

#秋冬春模型载入
def load_other_model():
	try:
		with open(other_model_file,'rb') as other_model_f:
			run_model=load(other_model_f)
		print "春冬模型载入成功"
	except:
		print "春冬模型载入失败"
	return run_model

#载入模型并预测数据
def run_the_model():
	print "正在加载模型"
	#print "Please input the file path"
	#file_path=input()
	#print file_path
	print "正在载入数据"
	try:
		dataset=read_csv(file_path_run_model)
		data_scaler=read_csv(data_scaler_file)
		# print dataset.head(5)
		print "数据载入成功"
	except:
		print "数据载入失败"
		
	#数据的标准化
	data_scaler['SDATE']=pd.to_datetime(data_scaler['SDATE'])
	data_scaler_summer=pd.DataFrame()
	data_scaler_other=pd.DataFrame()
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
	X_scaler_summer = X_scaler_summer[
		['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
	X_scaler_other = X_scaler_other[
		['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
	scaler_summer=StandardScaler().fit(X_scaler_summer)
	scaler_other = StandardScaler().fit(X_scaler_other)
	validation=dataset
	X_validation = validation[
		['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
	
	print "夏季模型请输入1"
	print "春冬模型请输入2"
	print "夏秋换季模型请输入3"
	print "春夏换季模型请输入4"

	#输入选择
	choose_model_number=input()
	if choose_model_number == 1:
		rescaledX_validation_summer = scaler_summer.transform(X_validation)
		model=load_summer_model()
		predictions = model.predict(rescaledX_validation_summer)
	elif choose_model_number == 2:
		rescaledX_validation_other = scaler_other.transform(X_validation)
		model=load_other_model()
		predictions = model.predict(rescaledX_validation_other)
	elif choose_model_number == 3:
		summer_to_autumn_date=temperature_judge_sdate(dataset)
		print "夏季到秋季关空调的时间为", summer_to_autumn_date
		validation['SDATE'] = pd.to_datetime(validation['SDATE'])
		validation_summer = validation[validation['SDATE'] <= pd.to_datetime(summer_to_autumn_date)]
		validation_other = validation[validation['SDATE'] > pd.to_datetime(summer_to_autumn_date)]
		X_summer_validation = validation_summer[
			['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
		X_other_validation = validation_other[
			['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
		model_summer=load_summer_model()
		rescaledX_validation_summer = scaler_summer.transform(X_summer_validation)
		predictions_summer=model_summer.predict(rescaledX_validation_summer)
		model_other=load_other_model()
		rescaledX_validation_other = scaler_other.transform(X_other_validation)
		predictions_other=model_other.predict(rescaledX_validation_other)
		predictions=np.append(predictions_summer,predictions_other)
	elif choose_model_number == 4:
		spring_to_summer_date=temperature_judge_sdate(dataset)
		print "春季到夏季开空调的时间为",spring_to_summer_date
		validation['SDATE'] = pd.to_datetime(validation['SDATE'])
		validation_summer = validation[validation['SDATE'] >= pd.to_datetime(spring_to_summer_date)]
		validation_other = validation[validation['SDATE'] < pd.to_datetime(spring_to_summer_date)]
		X_summer_validation = validation_summer[
			['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
		X_other_validation = validation_other[
			['IsHoliday', 'temperature_min', 'temperature_max', 'temperature_avg', 'IsHeating', 'week_year','IsSpringFestival']]
		model_summer=load_summer_model()
		rescaledX_validation_summer = scaler_summer.transform(X_summer_validation)
		predictions_summer=model_summer.predict(rescaledX_validation_summer)
		model_other=load_other_model()
		rescaledX_validation_other = scaler_other.transform(X_other_validation)
		predictions_other=model_other.predict(rescaledX_validation_other)
		predictions=np.append(predictions_summer,predictions_other)
	else:
		print "输入数字错误，系统退出"
		sys.exit()
	
	#得到功率最大值
	dataset['SDATE']=pd.to_datetime(dataset['SDATE'])
	p_max=get_month_p_max(dataset['SDATE'][5].month)
	
	print "最大功率为",p_max,"KW"
	print "每日用电量的预测结果"
	print predictions
	print "总电量为",predictions.sum()
	
	#将预测结果写入文件中
	new_df=pd.DataFrame()
	new_df['SDATE'] = dataset['SDATE']
	new_df['YL'] = predictions
	new_df.ix[-1] = pd.Series(['YL_SUM',predictions.sum()],index=new_df.columns)
	new_df.to_csv(result_file,index=False)
	#画图
	date_data = dataset['SDATE']
	dates = pd.DatetimeIndex(date_data)
	data = pd.DataFrame(predictions, index=dates, columns=['YL'])
	pl.xticks(rotation=30)
	plt.title('Daily electricity consumption forecast scatter plot')
	plt.ylabel('Kilowatt hour')
	plt.scatter(data.index, data['YL'])
	plt.xlim(data.index[0], data.index[-1])
	plt.show()

#显示界面
def show_print():
	print "欢迎使用电力预测系统，请输入对应得字符来选择相应的功能"
	print "1,预测数据处理（请自行设置放假时间，在IsHoliday.csv文件中，工作日为0，周六周日为1，三天及以上的假期为2，七天及以上的假期为3，过年期间的为4）"
	print "2,使用数据载入模型并得到用电量的结果"
	print "3,重载模型"
	print "4,模型纠错"
	print "5,系统退出"
	

if __name__ == '__main__':
	while 1:
		show_print()
		choose_number=input()
		if choose_number==1:
			Preprocessed_data.preprocfessed_data()
		elif choose_number==3:
			Model_reconstruction.model_reconstruction()
		elif choose_number==2:
			run_the_model()
		elif choose_number == 4:
			correctYL.correct_YL()
		elif choose_number==5:
			sys.exit()
		else:
			print "输入的数字有问题，请重新输入"

	#print choose_number
	#print type(choose_number)