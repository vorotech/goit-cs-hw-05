import asyncio
from aiopath import AsyncPath
from aioshutil import copyfile
import os
from argparse import ArgumentParser
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def copy_file(file_path: AsyncPath, target_folder: AsyncPath):
    """
    Копіює файл до відповідної папки на основі розширення.
    """
    try:
        extension = file_path.suffix[1:] or "unknown"
        target_dir = target_folder / extension
        await target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file_path.name

        await copyfile(file_path, target_path)
        logger.info(f"Файл {file_path} скопійовано до {target_path}")
    except Exception as e:
        logger.error(f"Помилка під час копіювання файлу {file_path}: {e}")

async def read_folder(source_folder: AsyncPath, target_folder: AsyncPath):
    """
    Рекурсивно читає файли у вихідній папці та сортує їх.
    """
    try:
        tasks = []
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = AsyncPath(root) / file
                tasks.append(copy_file(file_path, target_folder))

        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Помилка під час читання папки {source_folder}: {e}")

async def main():
    """
    Головна функція програми.
    """
    parser = ArgumentParser(description="Асинхронне сортування файлів за розширеннями.")
    parser.add_argument("source", type=str, help="Шлях до вихідної папки.")
    parser.add_argument("target", type=str, help="Шлях до цільової папки.")
    args = parser.parse_args()

    source_folder = AsyncPath(args.source)
    target_folder = AsyncPath(args.target)

    if not await source_folder.is_dir():
        logger.error(f"Вихідна папка {source_folder} не існує або це не папка.")
    else:
        await read_folder(source_folder, target_folder)

if __name__ == "__main__":
    asyncio.run(main())
