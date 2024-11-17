# 

This repository contains the source code for the paper: **Towards Explainable Search Results in E-commerce** WWW Industry 2025.

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

## Project Structure

    1 Relevance Model
        1.1Training data construction
            1.1.1 Qwen2-72B generates label and reasoning processes
            1.1.2 qwen2-72B Reverse validation of training data
        1.2 Model training
            1.2.1 difficulty measurer
            1.2.2 training scheduler
            1.2.3 lora fine-tune
    2 BehaviorRAG 
        2.1 process with GraphRA
        2.2 QueryIntent and ItemIntent
        2.3 explainable information
    3 Generating the final explainable reason

- `Relevance Model`:   Model training data construction and model fine-tuning
- `BehaviorRAG `:  Process with GraphRA  QueryIntent and ItemIntent Explainable information


    



## Pre-trained Language Models

The generation model：[Qwen2-7B](https://www.modelscope.cn/models/Qwen/Qwen2-7B-Instruct)
The embedding model: [bge](https://www.modelscope.cn/models/BAAI/bge-m3)

Download the weights and put them in `./`.

The public dataset: [amazon](https://amazon-reviews-2023.github.io/)



## How to use

### 1. Relevance Model

#### 1.1 Model training

1.1.1 Qwen2-72B generates label and reasoning processes

To build the correlation model training data using the QWEN2-72B model:            

The codes are in `get_train_data_by_qwen2-72B.py`:

```Run the following code：
python get_train_data_by_qwen2-72B.py
```

1.1.2 qwen2-72B Reverse validation of training data

To filter validation of generated training data

```Run the following code：
python verify_train_data_by_qwen2-72B.py
```

#### 1.2 Model training

This code uses the LLaMA-Factory framework to train the qwen2-7B model, so you need to install LLaMA-Factory first:

Details：[LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory/blob/main/README_zh.md)

To train the correlation model using training data:

Implement the following functions

1.2.1 difficulty measurer

1.2.2 training scheduler

1.2.3 lora fine-tune

```Run the following code：
sh run_fintune.sh
```
-  Note that the path can be changed under different settings. The format of dataset is: `[src, target]`


### 2. BehaviorRAG 

#### 2.1 process with GraphRA

This code uses GraphRAG to convert unstructured text into Graph, so you need to install graphrag first.

Details：[GraphRAG](https://github.com/microsoft/graphrag)

#### 2.2 QueryIntent and ItemIntent

```Run the following code：
python get_user_q_i.py
```
#### 2.3 explainable information

```Run the following code：
python get_gr_result.py
```

        
### 3 Generating the final explainable reason
```Run the following code：
python get_rule_experiment_data_qwen.py
```

