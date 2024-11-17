

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
    1 Relevance Model
        1Training data construction
            1.1 Qwen2-72B generates label and reasoning processes
            1.2 qwen2-72B Reverse validation of training data
        2 Model training
            2.1 difficulty measurer
            2.2 training scheduler
            2.3 lora fine-tune
    2 BehaviorRAG 
        1 process with GraphRA
        2 QueryIntent and ItemIntent
        3 explainable information
    3 Generating the final explainable reason



1 Relevance Model

    1 Training data construction
        1.1 Qwen2-72B generates label and reasoning processes
            To build the correlation model training data using the QWEN2-72B model:
            Run the following code：get_train_data_by_qwen2-72B.py

        1.2 qwen2-72B Reverse validation of training data
            To filter validation of generated training data
            Run the following code：verify_train_data_by_qwen2-72B.py
    
    2 Model training
        This code uses the LLaMA-Factory framework to train the qwen2-7B model, so you need to install LLaMA-Factory first:
        Details：https://github.com/hiyouga/LLaMA-Factory/blob/main/README_zh.md
        To train the correlation model using training data:
            Implement the following functions
                2.1 difficulty measurer
                2.2 training scheduler
                2.3 lora fine-tune
            Run the following code： run_fintune.sh

    
2 BehaviorRAG 
    
    1 process with GraphRA
        This code uses GraphRAG to convert unstructured text into Graph, so you need to install graphrag first.
        Details：https://github.com/microsoft/graphrag
    2 QueryIntent and ItemIntent
        Run the following code： get_user_q_i.py
    3 explainable information
        Run the following code：  get_gr_result.py
        
3 Generating the final explainable reason
    
    Run the following code： get_rule_experiment_data_qwen.py


