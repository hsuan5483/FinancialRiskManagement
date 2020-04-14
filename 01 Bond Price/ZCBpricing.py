#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Pei-Hsuan Hsu
"""

import os
from os.path import join
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from business_calendar import Calendar
from dateutil.relativedelta import relativedelta
from scipy.interpolate import interp1d

#%% day count convention
def DayCount30_360(start_date, end_date):
    """Returns number of days between start_date and end_date, using Thirty/360 convention"""
    d1 = min(30, start_date.day)
    d2 = min(30, end_date.day) if d1 == 30 else end_date.day
    
    days = 360*(end_date.year - start_date.year) + 30*(end_date.month - start_date.month) + d2 - d1
    return days / 360

#%% Bond Pricing
# 債券發行日
issue = datetime(2014,2,26)
# 債券發行期限 
N = 30
# 計息日期
accuralDates = [issue+relativedelta(years=i+1) for i in range(N)]
# 債券到期日
matirity = accuralDates[-1]
# 票面利率
coupon = 2.125 * 0.01
# 面額
FaceValue = 1e9
# 每期現金流
cashflow = FaceValue * coupon

# 評價日
valuation = datetime(2017, 12, 29)
date = valuation.strftime("%Y%m%d")

# 已計息天數 (annual)
accDays = DayCount30_360([x for x in accuralDates if x.date() < valuation.date()][-1], valuation)

#!!! yield curve data
yc = pd.read_excel(date+' yield curve.xlsx')

# 使用cubic spline配適yield curve
fitCurve = interp1d(yc.iloc[:, 0], yc.iloc[:, 1])

accuralDates = [x for x in accuralDates if x.date() > valuation.date()]
accT = [DayCount30_360(valuation, x) for x in accuralDates]
R = fitCurve(accT)

# 計算債券價格
V = FaceValue * np.exp(-R[-1]*accT[-1])
for i in range(len(accT)):
    V += cashflow * np.exp(-R[i]*accT[i])

# Accrued Interest
accI = round(accDays * cashflow, 0)

print('value =', round(V - accI, 0))
MTM = 1147710000
print('error =', abs(MTM-V)/MTM)

'''
MTM=1147710000

value = 1149918167.0
error = 0.017507544325801306
'''

