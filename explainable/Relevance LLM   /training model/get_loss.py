import random
import argparse
import json
from tqdm import tqdm
import torch
from modelscope import AutoModelForCausalLM, AutoTokenizer,GenerationConfig

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)  # 解析 JSON 文件内容
        return data  # 返回 JSON 数据
def write_jsonl(file_name, data_list):
    with open(file_name, "w", encoding="utf-8") as f:
        for data in data_list:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

def get_input(data_list):
    input_list = []
    for data in data_list:
        messages = [
            {"role": "system", "content": data["instruction"]+data["input"]},
            {"role": "user", "content": data["output"]},
            # {"role": "system", "content": data["output"]},
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        input_list.append(text)

    return input_list

def choose_data(data_list,t,level_num ):

    x1 = 0.9
    x2 = 0.9
    data_count = len(data_list)
    level_dic = {}
    for level in range(1,level_num+1):
        level_dic[level] = {"s":int((level-1)*(data_count/level_num)), 'e':int(level*(data_count/level_num))}

    if t == 1:
        choosed_data = data_list[level_dic[t]['s']:level_dic[t]['e']].copy()
        random.shuffle(choosed_data)
        len_choosed_data = len(choosed_data)
        choosed_data = choosed_data[ :int(len_choosed_data*x1)]

        return choosed_data

    if 1 < t and t < level_num + 1:

        choosed_data = []
        for i in range(1,t):
            level_data = data_list[level_dic[i]['s']:level_dic[i]['e']].copy()
            random.shuffle(level_data)
            len_level_data = len(level_data)
            level_data = level_data[ :int(len_level_data*x1*(x2**(i)))]
            choosed_data.extend(level_data)


        level_data = data_list[level_dic[t]['s']:level_dic[t]['e']].copy()
        random.shuffle(level_data)
        len_level_data = len(level_data)
        level_data = level_data[ :int(len_level_data*x1)]
        choosed_data.extend(level_data)

        return choosed_data

    if t == level_num+1:
        return  data_list




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--epoch', type=int, default=1)
    args = parser.parse_args()
    print(args.epoch)

    model_name = "../models/qwen/Qwen2-7B-Instruct"
    print(model_name)
    device = "cuda" # the device to load the model onto

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto",
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("model loead")

    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    epoch = args.epoch
    level_num = 5
    all_epoch = level_num + 1


    #1 获取query数据
    # 需要修改
    data_list = read_json("./data/qwen_data/qwen2_train_lf_g4o0826.json")[:]
    #2 设置batch_size
    batch_size = 1
    #3 构建大模型 input
    input_list = get_input(data_list)[:]



    model.eval()
    with torch.no_grad():
        with torch.autocast("cuda"):
            #4 获取response
            output_list = []
            loss_score=[]
            for i in tqdm(range(0, len(input_list), batch_size)):
                encoded = tokenizer(input_list[i:i + batch_size], return_tensors='pt', add_special_tokens=False ).to(device)
                loss = model(input_ids=encoded["input_ids"],labels=encoded["input_ids"]).loss
                loss_score.append( float(loss.cpu().detach().numpy()) )
    sorted_indices = sorted(range(len(loss_score)), key=lambda i: loss_score[i])
    chose_data = [data_list[index]   for index in sorted_indices[:]]
    chose_data = choose_data(chose_data, epoch, level_num  )

    random.shuffle(chose_data)
    write_jsonl(f"./data/qwen_data/cl_data/qwen_train_epoch{epoch}.json",chose_data)


