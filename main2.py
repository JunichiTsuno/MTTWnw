import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import gspread
from google.auth import impersonated_credentials
# from oauth2client.service_account import ServiceAccountCredentials
import re
import requests
import json
import matplotlib.pyplot as plt


st.sidebar.title('MTTW不動産サービス')
st.sidebar.write('あなたの不動産価値は？')
st.sidebar.write('所有不動産の価値をかんたんに査定します')
st.sidebar.markdown("---")
st.sidebar.header('STEP1')
st.sidebar.header('所有している物件のエリアを選んでください')
url = "http://zipcloud.ibsnet.co.jp/api/search"
zipcode = st.sidebar.text_input('郵便番号')
params = {"zipcode": zipcode}
res = requests.get(url, params=params)

# APIからの応答が正常ならば結果を表示
if res.status_code == 200:
    result = res.json()

    # 'results' フィールドが存在し、かつ結果が1つ以上ある場合に住所情報を表示
    if 'results' in result and result['results']:
        address1 = result['results'][0]['address1']
        address2 = result['results'][0]['address2']
        address3 = result['results'][0]['address3']
        st.sidebar.write(f'調べる物件の住所: {address1} {address2} {address3}')
    else:
        st.sidebar.write('エラー: 結果がありません')
else:
    st.sidebar.write(f'エラー: {res.status_code}')

st.sidebar.header('STEP2')
st.sidebar.header('所有している物件の特徴を選んでください')
selected_type = st.sidebar.selectbox('物件の種類',['一戸建て','マンション・アパート'])

size = st.sidebar.text_input('専有面積(m2)')
age = st.sidebar.text_input('築年数(年)')

button = st.sidebar.button('査定をはじめる',type="primary")
if button:
    st.header('査定結果')
    st.write(f'物件: {address1} {address2} {address3}')
    st.markdown("---")

    # size と age を数値に変換
    size = float(size)
    age = float(age)
    
    st.subheader('賃貸経営の場合')
    # 家賃の算出 家賃 = 面積×0.2930 - 築年数×0.0982 + 4.0223
    rent = size * 0.2930 - age * 0.0982 + 4.0223
    rent_rounded = round(rent, 1)
    st.write('想定家賃',rent_rounded,'万円')
    
    #収入
    income = rent_rounded * 12 * 20
    #支出
    expense = rent_rounded * 0.5
    #収益
    profit = income - expense
    profit_rounded = round(profit,0)
    
    st.write('20年運用した場合')
    st.write('収益', profit_rounded, '万円')
    st.markdown("---")
    
    st.subheader('売却の場合')
    if selected_type == "一戸建て":
        profit_sold = size * 129.6015 - 5447.7748 
        profit_sold_rounded = round(profit_sold, 1)
    elif selected_type == "マンション・アパート":
        profit_sold = size * 74.8310 + age * -75.5728 + 3423.3659
        profit_sold_rounded = round(profit_sold, 1)        
    
    st.write('売却時の収益')
    st.write('収益',profit_sold_rounded,'万円')
    st.markdown("---")    
    
    # 収益の比較
    if profit_rounded > profit_sold:
        st.info('賃貸経営が売却よりも収益が高いです。')
    elif profit_rounded < profit_sold:
        st.info('売却が賃貸経営よりも収益が高いです。')
    else:
        st.info('賃貸と売却の収益は同じです。')
    
    st.markdown("---")
    st.subheader('損益分岐点のグラフ')

    # 賃貸経営の損益関数
    def rental_profit_function(years):
        income = rent_rounded * 12 * years
        expense = rent_rounded * 0.5 * years
        profit = income - expense
        return profit

    # 売却の損益関数（こちらは20年で確定と仮定）
    def sale_profit_function():
        if selected_type == "一戸建て":
            return size * 129.6015 - 5447.7748
        elif selected_type == "マンション・アパート":
            return size * 74.8310 + age * -75.5728 + 3423.3659

    # グラフ描画用のデータ
    years_range = np.arange(1, 21)  # 1年から20年まで
    rental_profit_values = [rental_profit_function(year) for year in years_range]
    sale_profit_value = sale_profit_function()

    # グラフ描画
    fig, ax = plt.subplots()
    plt.rcParams['font.family'] = 'MS Gothic'
    ax.plot(years_range, rental_profit_values, label='賃貸経営')
    ax.axhline(y=sale_profit_value, color='red', linestyle='--', label='売却')

    ax.set_xlabel('年数')
    ax.set_ylabel('収益')
    ax.legend()
    st.pyplot(fig)

    # 損益分岐点の表示
    break_even_year = np.argmin(np.abs(np.array(rental_profit_values) - sale_profit_value)) + 1
    st.write(f'損益分岐点: {break_even_year} 年')
    
    st.markdown("---")   
    button2 = st.button('問い合わせ',type="primary")
        

