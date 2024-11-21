#!/bin/bash


int_epoch=1

python get_loss.py --epoch=$int_epoch
echo "数据epoch$int_epoch 已构建"
llamafactory-cli train yaml/qwen2_7b_lora_sft_cl.yaml
echo "模型epoch$int_epoch 已训练"
llamafactory-cli export yaml/qwen2_7b_lora_merge_cl.yaml
echo "模型epoch$int_epoch 已merge"


load_train_model_o="./models/Qwen2-7B-Instruct"
save_train_model_o="saves/qwen2-7b/lora/sft/cl_qwen2_72B/train_qwen_epoch$((int_epoch - 1))"
train_data_o="qwen2_exp_train_epoch$((int_epoch - 1))"

load_merge_model_o=$load_train_model_o
load_train_merge_model_o=$save_train_model_o
save_merge_model_o="saves/qwen2-7b/lora/merge/cl_qwen2_72B/train_qwen_epoch$((int_epoch - 1))"

load_train_model_r=$save_merge_model_o
save_train_model_r="saves/qwen2-7b/lora/sft/cl_qwen2_72B/train_qwen_epoch$int_epoch"
train_data_r="qwen2_exp_train_epoch$int_epoch"


load_merge_model_r=$load_train_model_r
load_train_merge_model_r=$save_train_model_r
save_merge_model_r="saves/qwen2-7b/lora/merge/cl_qwen2_72B/train_qwen_epoch$int_epoch"


FILE1="yaml/qwen2_7b_lora_sft_cl.yaml"
# # 使用 sed 进行字符串替换
sed -i "s|model_name_or_path: $load_train_model_o|model_name_or_path: $load_train_model_r|g" "$FILE1"
sed -i "s|output_dir: $save_train_model_o|output_dir: $save_train_model_r|g" "$FILE1"
sed -i "s|dataset: $train_data_o|dataset: $train_data_r|g" "$FILE1"
echo "文件1内容已更新"

FILE2="yaml/qwen2_7b_lora_merge_cl.yaml"
# # 使用 sed 进行字符串替换
sed -i "s|model_name_or_path: $load_merge_model_o|model_name_or_path: $load_merge_model_r|g" "$FILE2"
sed -i "s|adapter_name_or_path: $load_train_merge_model_o|adapter_name_or_path: $load_train_merge_model_r|g" "$FILE2"
sed -i "s|export_dir: $save_merge_model_o|export_dir: $save_merge_model_r|g" "$FILE2"
echo "文件2内容已更新"

llamafactory-cli train yaml/qwen2_7b_lora_sft_cl.yaml
echo "模型epoch$int_epoch 已训练"
llamafactory-cli export yaml/qwen2_7b_lora_merge_cl.yaml
echo "模型epoch$int_epoch 已merge"




