import pandas as pd
import matplotlib.pyplot as plt
import re
import folium
import requests
import time
from requests.utils import quote

def load_data(file_path):
    """Загружает данные из CSV-файла."""
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
        print("Данные загружены успешно.")
        print("Названия столбцов:", df.columns.tolist())  # Выводим названия всех столбцов
        return df
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        return None

def extract_postal_codes(df):
    """Извлекает почтовые индексы из столбца адресов."""
    postal_codes = []
    
    # Удаляем лишние пробелы из названий столбцов
    df.columns = df.columns.str.strip()
    
    if 'AddressLegal' not in df.columns:
        print("Столбец 'AddressLegal' не найден. Проверьте названия столбцов.")
        return df
    
    for address in df['AddressLegal']:  # Используем правильное имя столбца
        # Ищем почтовый индекс (предполагается, что он состоит из 6 цифр)
        match = re.search(r'\b(\d{6})\b', address)
        if match:
            postal_codes.append(match.group(1))  # Добавляем найденный индекс
        else:
            postal_codes.append('Неизвестно')  # Если индекс не найден
    
    df['postal_code'] = postal_codes  # Добавляем новый столбец с почтовыми индексами
    return df

def visualize_distribution(df):
    """Создает визуализацию распределения адресов по почтовым индексам."""
    postal_code_counts = df['postal_code'].value_counts()
    
    plt.figure(figsize=(10, 6))
    postal_code_counts.plot(kind='bar', color='skyblue')
    plt.title('Распределение адресов по почтовым индексам')
    plt.xlabel('Почтовые индексы')
    plt.ylabel('Количество адресов')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def geocode_postal_codes_nominatim(df):
    """Геокодирует почтовые индексы с использованием Nominatim."""
    
    latitudes = []
    longitudes = []
    
    for postal_code in df['postal_code']:
        try:
            # Кодируем почтовый индекс для URL
            encoded_postal_code = quote(postal_code)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded_postal_code}&format=json&addressdetails=1"
            
            headers = {
                'User-Agent': 'YourAppName/1.0 (your.email@example.com)'  # Замените на ваше имя приложения и контактный email
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    latitudes.append(data[0]['lat'])
                    longitudes.append(data[0]['lon'])
                else:
                    latitudes.append(None)
                    longitudes.append(None)
                    print(f"Не удалось найти координаты для почтового индекса: {postal_code}")
            else:
                latitudes.append(None)
                longitudes.append(None)
                print(f"Ошибка при запросе: {response.status_code} для почтового индекса '{postal_code}'")
            
            time.sleep(1)  # Задержка в 1 секунду между запросами
            
        except Exception as e:
            latitudes.append(None)
            longitudes.append(None)
            print(f"Ошибка при геокодировании почтового индекса '{postal_code}': {e}")

    df['latitude'] = latitudes
    df['longitude'] = longitudes
    return df

def create_map(df):
    """Создает карту с маркерами для каждого адреса."""
    m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=12)  # Центр карты
    
    for idx, row in df.iterrows():
        if row['latitude'] is not None and row['longitude'] is not None:
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=row['postal_code'],
                icon=folium.Icon(color='blue')
            ).add_to(m)

    m.save('map.html')  # Сохранение карты в HTML файл

def main():
    file_path = 'D:/adress.csv'  # Путь к файлу
    df_addresses = load_data(file_path)
    
    if df_addresses is not None:
        df_addresses = extract_postal_codes(df_addresses)  # Извлекаем почтовые индексы
        visualize_distribution(df_addresses)  # Визуализируем распределение
        
        # Геокодируем почтовые индексы и создаем карту с использованием Nominatim
        df_addresses = geocode_postal_codes_nominatim(df_addresses)  
        create_map(df_addresses)

if __name__ == "__main__":
    main()