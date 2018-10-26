#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
#文件夹路径，只需要修改此路径即可
folder_path=sys.path[0]
# 设置季度转化的温度
#夏入秋的临界温度
temperature_summer_to_autumn=28
#春入夏的临界温度
temperature_spring_to_summer=22
#秋入冬的临界温度
temperature_autumn_to_winter = 5
#冬入春的临界温度
temperature_winter_to_spring = 5
#夏入秋的判断天数
date_summer_to_autumn=3
#春入夏的判断天数
date_spring_to_summer=5
#秋入冬的判断天数
date_autumn_to_winter = 5
#冬入春的判断天数
date_winter_to_spring = 5
#夏入秋的判断月份
month_summer_to_autumn=[9,10]
#春入夏的判断月份
month_spring_to_summer=[5,6]
#秋入冬的判断月份
month_autumn_to_winter = [11, 12]
#冬入春的判断月份
month_winter_to_spring = [3, 4]
#历史温度数据的年月标志,该标志在到新的一年中需要修改，且仅需要添加年份，方便在数据遗失时对历史温度数据进行重爬取
years=[2016,2017,2018]
months=['01','02','03','04','05','06','07','08','09','10','11','12']
#过年开始放假时间
#农历的月份
springfestival_start_month=12
#农历的日期
springfestival_start_date=28
#过年放假结束时间
#农历的月份
springfestival_end_month=1
#农历的日期
springfestival_end_date=10