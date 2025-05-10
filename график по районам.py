import pandas as pd
import matplotlib.pyplot as plt
import re

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

def extract_districts(df):
    """Извлекает районы из столбца адресов."""
    districts = []
    
    # Удаляем лишние пробелы из названий столбцов
    df.columns = df.columns.str.strip()
    
    if 'AddressLegal' not in df.columns:
        print("Столбец 'AddressLegal' не найден. Проверьте названия столбцов.")
        return df
    
    for address in df['AddressLegal']:  # Используем правильное имя столбца
        # Ищем район после слов "район" или "р-н"
        match = re.search(r'(?:район|р-н)\s*([^\s]+)', address, re.IGNORECASE)
        if match:
            districts.append(match.group(1))  # Добавляем найденный район
        else:
            districts.append('Неизвестно')  # Если район не найден
    
    df['district'] = districts  # Добавляем новый столбец с районами
    return df

def visualize_distribution(df):
    """Создает визуализацию распределения адресов по районам."""
    district_counts = df['district'].value_counts()
    
    plt.figure(figsize=(10, 6))
    district_counts.plot(kind='bar', color='skyblue')
    plt.title('Распределение адресов по районам')
    plt.xlabel('Районы')
    plt.ylabel('Количество адресов')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    file_path = 'D:/adress.csv'  # Путь к файлу
    df_addresses = load_data(file_path)
    
    if df_addresses is not None:
        df_addresses = extract_districts(df_addresses)  # Извлекаем районы
        visualize_distribution(df_addresses)  # Визуализируем распределение

if __name__ == "__main__":
    main()