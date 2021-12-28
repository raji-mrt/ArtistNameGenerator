import json
import boto3
from boto3.dynamodb.conditions import Key
import random
from names_dataset import NameDataset

m = NameDataset()


def get_meaningful_name(name1, name2):
    best_word = ""
    best_score = 0.0
    for i in range(1, len(name1)):
        for j in range(1, len(name2)):
            new_name = name1[:i] + name2[j:]
            score_for_the_name = m.search_first_name(new_name)
            if score_for_the_name > best_score:
                best_word = new_name
                best_score = score_for_the_name
    for i in range(1, len(name2)):
        for j in range(1, len(name1)):
            new_name = name2[:i] + name1[j:]
            score_for_the_name = m.search_first_name(new_name)
            if score_for_the_name > best_score:
                best_word = new_name
                best_score = score_for_the_name

    return best_word


def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    first_names = dynamodb.Table('first_names')
    last_names = dynamodb.Table('last_names')
    # first_names_count = first_names.Item_count
    first_names_count = 1219
    last_names_count = 20172
    print(first_names_count)
    print(last_names_count)

    random_names = []

    while len(random_names) <= 10:
        response = first_names.query(
            KeyConditionExpression=Key('id').eq(random.randint(1, first_names_count))
        )
        first_name1 = response['Items'][0]['name']
        response = last_names.query(
            KeyConditionExpression=Key('id').eq(random.randint(1, last_names_count))
        )
        first_name2 = response['Items'][0]['name']
        new_name = get_meaningful_name(first_name1, first_name2)
        if new_name:
            random_names.append(new_name)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(random_names)
    }
