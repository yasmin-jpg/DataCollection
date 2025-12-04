# airflow_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import sys
import os

# Добавляем путь к src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # dags -> airflow
src_path = os.path.join(project_root, '..', 'src')  # airflow -> project root -> src
sys.path.insert(0, src_path)

# Аргументы DAG
default_args = {
    'owner': 'student',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 4),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,  # Количество повторений при ошибке
    'retry_delay': timedelta(minutes=5),
}

# Создание DAG
dag = DAG(
    'hm_scraping_pipeline',
    default_args=default_args,
    description='H&M Product Scraping and Processing Pipeline',
    schedule_interval=timedelta(days=1),  # Раз в сутки
    catchup=False,
    tags=['hm', 'scraping', 'data_pipeline']
)

# Функция для скрапинга
def run_scraper():
    from scraper import scrape_data
    print("Starting scraper...")
    df = scrape_data()
    print(f"Scraping completed. Collected {len(df)} products")
    return True

# Функция для очистки
def run_cleaner():
    from cleaner import new_data as clean_data
    print("Starting data cleaning...")
    clean_data()
    print("Data cleaning completed")
    return True

# Функция для загрузки в БД
def run_loader():
    from loader import load_data
    print("Starting database loading...")
    load_data()
    print("Database loading completed")
    return True

# Начальная задача
start_task = DummyOperator(
    task_id='start_pipeline',
    dag=dag,
)

# Задача скрапинга
scrape_task = PythonOperator(
    task_id='scrape_data',
    python_callable=run_scraper,
    dag=dag,
)

# Задача очистки
clean_task = PythonOperator(
    task_id='clean_data',
    python_callable=run_cleaner,
    dag=dag,
)

# Задача загрузки в БД
load_task = PythonOperator(
    task_id='load_to_database',
    python_callable=run_loader,
    dag=dag,
)

# Конечная задача
end_task = DummyOperator(
    task_id='end_pipeline',
    dag=dag,
)

# Настройка зависимостей (последовательность выполнения)
start_task >> scrape_task >> clean_task >> load_task >> end_task

# Функция для тестирования
if __name__ == "__main__":
    # Тестируем локально
    print("Testing DAG locally...")
    
    # Создаем контекст для тестирования
    test_context = {
        'ds': '2025-12-04',
        'run_id': 'test_run'
    }
    
    # Тестируем задачи по очереди
    try:
        print("\n=== Testing scrape_task ===")
        run_scraper()
        
        print("\n=== Testing clean_task ===")
        run_cleaner()
        
        print("\n=== Testing load_task ===")
        run_loader()
        
        print("\nAll tasks completed successfully!")
    except Exception as e:
        print(f"\n Error during testing: {e}")