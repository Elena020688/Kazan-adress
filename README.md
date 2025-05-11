# Установка необходимых библиотек
!pip install pandas geopandas folium geopy

import pandas as pd
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from IPython.display import display, HTML

# Загрузка данных
from google.colab import files
uploaded = files.upload()

# Чтение данных
df = pd.read_csv('temp_d.csv')

# Функция для очистки адресов
def clean_address(address):
    if pd.isna(address) or address in ['неизвестно', 'без регистрации', 'БЕЗ ПРОПИСКИ', 'без прописки']:
        return None
    address = re.sub(r'\[.*?\]', '', str(address))
    address = re.sub(r'"', '', address)
    address = re.sub(r'РОССИЯ', 'Российская Федерация', address)
    address = re.sub(r'Респ\.Татарстан', 'Республика Татарстан', address)
    return address.strip() if address else None

# Очистка адресов
df['AddressLegal'] = df['AddressLegal'].apply(clean_address)
df = df.dropna(subset=['AddressLegal'])

# Настройка геокодера
geolocator = Nominatim(user_agent="tatarstan_address_analysis", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Функция геокодирования с обработкой ошибок
def geocode_address(address):
    try:
        location = geocode(address + ', Республика Татарстан, Россия')
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Ошибка геокодирования для адреса {address}: {str(e)}")
    return (None, None)

# Применяем геокодирование к первым 30 адресам (для демонстрации)
sample_size = 30
sample_df = df.head(sample_size).copy()
sample_df['coordinates'] = sample_df['AddressLegal'].apply(geocode_address)
sample_df[['latitude', 'longitude']] = pd.DataFrame(sample_df['coordinates'].tolist(), index=sample_df.index)
sample_df = sample_df.dropna(subset=['latitude', 'longitude'])

# Создаем карту Folium
m = folium.Map(location=[55.796289, 49.108795], zoom_start=7)

# Добавляем маркеры на карту
for idx, row in sample_df.iterrows():
    tooltip_text = row['AddressLegal'][:50] + '...' if len(row['AddressLegal']) > 50 else row['AddressLegal']
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=row['AddressLegal'],
        tooltip=tooltip_text
    ).add_to(m)

# Сохраняем карту в HTML
map_html = m._repr_html_()

# Создаем HTML для дашборда (без f-строки с обратными слешами)
top_locations = sample_df['AddressLegal'].str.extract(r'(г\..*?|с\..*?|пгт\..*?|д\..*?)(?:,|$)')[0].value_counts().head(5).index.tolist()
top_locations_html = "".join(f"<li>{loc}</li>" for loc in top_locations)

dashboard_html = f"""
<div style="font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto;">
    <h1 style="text-align: center; color: #2c3e50;">Адреса в Республике Татарстан</h1>
    
    <div style="margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; overflow: hidden;">
        {map_html}
    </div>
    
    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
        <h3 style="color: #2c3e50;">Статистика по адресам</h3>
        <p><strong>Всего адресов в файле:</strong> {len(df)}</p>
        <p><strong>Обработано адресов:</strong> {sample_size}</p>
        <p><strong>Успешно геокодировано:</strong> {len(sample_df)} ({(len(sample_df)/sample_size)*100:.1f}%)</p>
        
        <h4 style="margin-top: 20px;">Топ 5 населенных пунктов:</h4>
        <ul>
            {top_locations_html}
        </ul>
    </div>
</div>
"""

display(HTML(dashboard_html))
