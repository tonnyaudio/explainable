# 获取上下文文档

import re
import numpy as np
from openai import OpenAI
import os
import json
import _thread
import subprocess
from tqdm import tqdm
import time
import random
def write_jsonl(file_name, data_list):
    with open(file_name, "w", encoding="utf-8") as f:
        for data in data_list:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
def read_jsonl(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        data_list = [json.loads(line) for line in f.readlines()]
    return data_list
def read_json(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)  # 解析 JSON 文件内容
        return data  # 返回 JSON 数据

def get_gr_result_thread(threadName,data_list,file_path):
    # 构造命令
    for i in tqdm(range(len(data_list))):

        prompt = ""
        prompt += f"""根据已有知识，如果{data_list[i]["query"]}和{data_list[i]["i_title"]}存在什么关系？\n"""

        command = [
        'python', '-m', 'graphrag.query',
        '--root', './gr3',
        '--method', 'global',
            '--method', 'local',
        prompt
        ]
        output =""

        # 运行命令并获取输出
        while output ==""  :
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                context = result.stdout.split("*"*50)[1].split("-"*50)
                output = context if len(context) > 1 else ""
            except subprocess.CalledProcessError as e:
                output == ""

            if output == '':
                time.sleep(random.uniform(5, 20))
        data_list[i]["gr_query"] = prompt
        data_list[i]["gr_context"] = output
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data_list[i], ensure_ascii=False) + "\n")
    print("{} ok".format(threadName))



if __name__ == "__main__":

    # 1 获取数据
    data_list = read_jsonl("./data/query_item_eval.jsonl")

    # 创建n个线程,将数据分成n份，将结果输出到不同文件
    # 2.1 设置参数
    num_thread = 25
    start_num, end_num, step_num = 0, 50, 50
    part_path="./data/gr"
    try:
        file_paths = [f'{part_path}/dd_{i}.jsonl' for i in range(num_thread)]
        
        
        re_len = [0] * num_thread
        for i, file_path in enumerate(file_paths):
            if os.path.exists(file_path):
                da = read_jsonl(file_path)
                re_len[i] = len(da)
                print(re_len[i] )

        for i, file_path in enumerate(file_paths):

            if not os.path.exists(part_path):
                os.makedirs(part_path)
            # sub_data_list = data_list[start_num:end_num]
            sub_data_list = data_list[start_num+re_len[i]:end_num]

            _thread.start_new_thread(get_gr_result_thread, (f"Thread-{i}", sub_data_list, file_path))
            start_num = end_num
            end_num = end_num + step_num
    except:
        print("Error: 无法启动线程")
    while 1:
        pass