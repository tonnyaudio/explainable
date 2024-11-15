

## Environment Description

Several major dependencies:

- python=3.10.15 
- pytorch=2.4
- transformers=4.46.1
- datasets
- vllm=0.6.3
- graphrag=0.3.6
- wandb
- modelscope

## Overall Framework
    目录
    1 相关性模型
        1 数据构造
            1.1 qwen72B 生成标签与推理过程
            1.2 qwen72B 反向验证数据
        2 模型训练
            2.1 样本评估器
            2.2 训练调度器
            2.3 lora fine-tune
    2 BehaviorRAG 
        1 GraphRAG构建
        2 用户意图获取
        3 获取相关知识
    3 生成相关性可解释理由



1 相关性模型

    1 数据构造
        1.1 qwen72B 生成标签与推理过程
            为了使用qwen2-72B模型构建相关性模型的训练数据:
            运行以下代码：get_train_data_by_qwen2-72B.py

        1.2 qwen72B 反向验证数据
            为了对生成的训练数据进行筛选验证:
            运行以下代码：verify_train_data_by_qwen2-72B.py
    
    2 模型训练
        本代码使用了LLaMA-Factory 框架用于训练 qwen2-7B模型，因此首先需要安装LLaMA-Factory：
        具体细节：https://github.com/hiyouga/LLaMA-Factory/blob/main/README_zh.md
        为了使用训练数据训练相关性模型:
            实现以下功能
                2.1 样本评估器
                2.2 训练调度器
                2.3 lora fine-tune
            运行以下代码 run_fintune.sh

    
2 BehaviorRAG 
    
    1 GraphRAG构建
        本代码使用了GraphRAG 用用将非结构化文本转换Graph，因此首先需要安装graphrag
        具体细节：https://github.com/microsoft/graphrag
        
    2 用户意图获取
        运行代码  get_user_q_i.py
    3 获取相关知识
        运行代码  get_gr_result.py
3 生成相关性可解释理由

    运行以下代码 get_rule_experiment_data_qwen.py


