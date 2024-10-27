import asyncio

import yaml


def load_yml(yml_path: str):
    with open(yml_path, encoding="UTF-8") as f:
        y = yaml.safe_load(f.read())
    return y


def save_yml(yml_path: str, data: dict):
    # YAML形式のテキストファイルに書き出す
    with open(yml_path, "w") as f:
        yaml.dump(data, f)


async def kill_all_asyncio_tasks():
    active_tasks = [task for task in asyncio.all_tasks() if not task.done()]
    for task in active_tasks:
        task.cancel()
        try:
            await task
        except BaseException:
            pass
