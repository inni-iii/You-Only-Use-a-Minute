from datasets import Dataset, DatasetDict, concatenate_datasets
from typing import Dict, List

import json
import pandas as pd
import torch


# json 형식 파일을 불러오는 함수
def load_json(path: str) -> Dict[str, str]:
    with open(path) as f:
        data = json.load(f)

    return data


# 대화ID, 대화, 요약 정보 추출
def load_data(path: Dict) -> List[str]:
    data = load_json(path)
    dialogueID = []
    dialogue = []
    summary = []
    for text in data['data']:
        dialogueID.append(text['header']['dialogueInfo']['dialogueID'])
        summary.append(text['body']['summary'])

        utterances = []
        participantID = ''
        person_dialogue = ''
        for utterance in text['body']['dialogue']:
            if participantID == utterance['participantID']:
                person_dialogue += ' ' + utterance['utterance']
            else:
                if person_dialogue:
                    utterances.append(person_dialogue)
                participantID = utterance['participantID']
                person_dialogue = utterance['utterance']
        if person_dialogue:
            utterances.append(person_dialogue)
        dialogue.append(' '.join(utterances))

    data = {}
    data['ID'] = dialogueID
    data['dialogue'] = dialogue
    data['summary'] = summary
    data = Dataset.from_pandas(pd.DataFrame(data))

    return data


# 모든 dataset을 합치고 Dataset 형태로 반환
def load_and_concat_dataset(path: str):
    train_path = path + 'train/'
    valid_path = path + 'valid/'
    data_list = ['개인및관계', '미용과건강', '상거래(쇼핑)', '시사교육', '식음료', '여가생활', '일과직업', '주거와생활', '행사']
    train_datasets = load_data(train_path + data_list[0] + '.json')
    valid_datasets = load_data(valid_path + data_list[0] + '.json')
    for text in data_list[1:]:
        prev_train_data = load_data(train_path + text + '.json')
        prev_valid_data = load_data(valid_path + text + '.json')
        train_datasets = concatenate_datasets([train_datasets, prev_train_data])
        valid_datasets = concatenate_datasets([valid_datasets, prev_valid_data])
    datasets = DatasetDict({'train' : train_datasets, 'validation' : valid_datasets})

    return datasets