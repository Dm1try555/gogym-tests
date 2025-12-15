#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов с разными ролями.
Сначала запускает тесты с ролью coach, затем с ролью customer.
Результаты Allure накапливаются (не перезаписываются).
"""
import subprocess
import sys
import os
import shutil

def clean_allure_results():
    """Очищает результаты Allure перед первым запуском (только файлы, не директорию)"""
    allure_dir = "allure-results"
    try:
        if os.path.exists(allure_dir):
            print(f"Очистка файлов в директории {allure_dir}...")
            # Удаляем только файлы внутри директории, а не саму директорию
            # Это безопаснее для Docker volumes
            files_cleaned = 0
            for filename in os.listdir(allure_dir):
                file_path = os.path.join(allure_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        files_cleaned += 1
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        files_cleaned += 1
                except Exception as e:
                    print(f"Предупреждение: не удалось удалить {file_path}: {e}")
            if files_cleaned > 0:
                print(f"Очищено файлов: {files_cleaned}")
        else:
            os.makedirs(allure_dir, exist_ok=True)
            print(f"Создана директория {allure_dir}")
    except Exception as e:
        print(f"Предупреждение: не удалось очистить {allure_dir}: {e}")
        print("Продолжаем выполнение без очистки...")
        # Создаём директорию, если её нет
        try:
            os.makedirs(allure_dir, exist_ok=True)
        except:
            pass

def run_tests(role: str, markers: str = None, clean_alluredir: bool = False):
    """Запускает тесты с указанной ролью"""
    cmd = ["pytest", "-v", f"--role={role}", "--alluredir=allure-results"]
    
    # Очищаем результаты только при первом запуске
    if clean_alluredir:
        cmd.append("--clean-alluredir")
    
    if markers:
        cmd.extend(["-m", markers])
    
    print(f"\n{'='*60}")
    print(f"Запуск тестов с ролью: {role}")
    if markers:
        print(f"Маркеры: {markers}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(cmd)
    return result.returncode

def main():
    """Основная функция запуска всех тестов"""
    exit_code = 0
    
    # Очищаем результаты Allure только один раз в начале
    clean_allure_results()
    
    # Запускаем тесты коуча (с очисткой результатов)
    coach_exit = run_tests("coach", "coach", clean_alluredir=True)
    if coach_exit != 0:
        exit_code = coach_exit
    
    # Запускаем тесты клиента (БЕЗ очистки, чтобы результаты накапливались)
    customer_exit = run_tests("customer", "customer", clean_alluredir=False)
    if customer_exit != 0:
        exit_code = customer_exit
    
    print(f"\n{'='*60}")
    if exit_code == 0:
        print("Все тесты завершены успешно!")
    else:
        print(f"Некоторые тесты завершились с ошибками (код: {exit_code})")
    print(f"Результаты Allure сохранены в allure-results/")
    print(f"Для просмотра отчёта выполните: allure serve allure-results")
    print(f"{'='*60}\n")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

