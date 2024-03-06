#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import json, requests, datetime
import pandas as pd


def get_price_day_tx(code, end_date='', count=10, frequency='1d'):
    unit = 'week' if frequency in '1w' else 'month' if frequency in '1M' else 'day'
    if end_date:
        end_date = end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime.date) else end_date.split(' ')[0]
    end_date = '' if end_date == datetime.datetime.now().strftime('%Y-%m-%d') else end_date
    URL = f'http://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={code},{unit},,{end_date},{count},qfq'
    st = json.loads(requests.get(URL).content)
    ms = 'qfq'+unit
    stk = st['data'][code]
    buf = stk[ms] if ms in stk else stk[unit]
    df = pd.DataFrame(buf, columns=['time','open','close','high','low','volume'], dtype='float')
    df.time = pd.to_datetime(df.time)
    df.set_index(['time'], inplace=True)
    df.index.name = ''
    return df

def get_price_min_tx(code, end_date=None, count=10, frequency='1d'):
    ts = int(frequency[:-1]) if frequency[:-1].isdigit() else 1
    if end_date:
        end_date = end_date.strftime('%Y-%m-%d') if isinstance(end_date, datetime.date) else end_date.split(' ')[0]
    URL=f'http://ifzq.gtimg.cn/appstock/app/kline/mkline?param={code},m{ts},,{count}'
    st = json.loads(requests.get(URL).content)
    buf = st['data'][code]['m'+str(ts)]
    df = pd.DataFrame(buf, columns=['time','open','close','high','low','volume','n1','n2'])
    df = df[['time','open','close','high','low','volume']]
    df[['open','close','high','low','volume']] = df[['open','close','high','low','volume']].astype('float')
    df.time = pd.to_datetime(df.time)
    df.set_index(['time'], inplace=True)
    df.index.name = ''
    df['close'][-1] = float(st['data'][code]['qt'][code][3])
    return df

def get_price_sina(code, end_date='', count=10, frequency='60m'):
    frequency = frequency.replace('1d', '240m').replace('1w', '1200m').replace('1M', '7200m')
    mcount=count
    ts = int(frequency[:-1]) if frequency[:-1].isdigit() else 1
    if end_date != '' and frequency in ['240m','1200m','7200m']:
        end_date = pd.to_datetime(end_date) if not isinstance(end_date, datetime.date) else end_date
        unit = 4 if frequency == '1200m' else 29 if frequency == '7200m' else 1
        count = count + (datetime.datetime.now() - end_date).days // unit
    URL = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale={ts}&ma=5&datalen={count}'
    dstr = json.loads(requests.get(URL).content)
    df = pd.DataFrame(dstr, columns=['day','open','high','low','close','volume'])
    df[['open','close','high','low','volume']] = df[['open','close','high','low','volume']].astype('float')
    df.day = pd.to_datetime(df.day)
    df.set_index(['day'], inplace=True)
    df.index.name = ''
    if end_date != '' and frequency in ['240m','1200m','7200m']:
        return df[df.index<=end_date][-mcount:]
    return df

def get_price(code, end_date='',count=10, frequency='1d', fields=[]):
    xcode = code.replace('.XSHG', '').replace('.XSHE', '')
    xcode = 'sh' + xcode if 'XSHG' in code else 'sz' + xcode if 'XSHE' in code else code
    if frequency in ['1m']:
        return get_price_min_tx(xcode, end_date=end_date, count=count, frequency=frequency)
    elif frequency in ['1m','5m','15m','30m','60m','1d','1w','1M']:
         try:
             return get_price_sina(xcode, end_date=end_date, count=count, frequency=frequency)
         except:
             return get_price_day_tx(xcode, end_date=end_date, count=count, frequency=frequency)

