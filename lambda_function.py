import json
import boto3
from boto3.dynamodb.conditions import Key
import random
from names_dataset import NameDataset

m = NameDataset()

dynamodb = boto3.resource('dynamodb')
male_first_names_db = dynamodb.Table('artist_first_names_male')
female_first_names_db = dynamodb.Table('artist_first_names_female')
last_names_db = dynamodb.Table('artist_last_names')
table_blacklisted = dynamodb.Table('blacklisted_words')
# first_names_count = first_names.Item_count
male_first_names_count = 1219
female_first_names_count = 4275
last_names_count = 88799


def validate_name(name):
    if len(name) < 4:
        return False
    # Check in blacklisted words
    response = table_blacklisted.query(
        KeyConditionExpression=Key('word').eq(name)
    )
    if response['Count'] > 0:
        print('Found in table_blacklisted ' + name)
        return False

    # Check in names db
    response = male_first_names_db.query(
        IndexName='name-index',
        KeyConditionExpression=Key('name').eq(name)
    )
    if response['Count'] > 0:
        print('Found in male_first_names_db ' + name)
        return False

    response = female_first_names_db.query(
        IndexName='name-index',
        KeyConditionExpression=Key('name').eq(name)
    )
    if response['Count'] > 0:
        print('Found in female_first_names_db ' + name)
        return False

    response = last_names_db.query(
        IndexName='name-index',
        KeyConditionExpression=Key('name').eq(name)
    )
    if response['Count'] > 0:
        print('Found in last_names_db ' + name)
        return False
    print('Validation passed for ' + name)
    return True


def get_meaningful_name(name1, name2):
    best_word = ""
    best_score = 0.0
    for i in range(1, len(name1)):
        for j in range(1, len(name2)):
            new_name = name1[:i] + name2[j:]
            score_for_the_name = m.search_first_name(new_name)
            if score_for_the_name > best_score and validate_name(new_name):
                best_word = new_name
                best_score = score_for_the_name
    for i in range(1, len(name2)):
        for j in range(1, len(name1)):
            new_name = name2[:i] + name1[j:]
            score_for_the_name = m.search_first_name(new_name)
            if score_for_the_name > best_score and validate_name(new_name):
                best_word = new_name
                best_score = score_for_the_name

    print(best_word + " scored " + str(best_score))
    return best_word


def generate_names(db, count, item_count):
    names = []
    while len(names) <= count:
        response = db.query(
            KeyConditionExpression=Key('id').eq(random.randint(1, item_count))
        )
        name1 = response['Items'][0]['name']
        response = db.query(
            KeyConditionExpression=Key('id').eq(random.randint(1, item_count))
        )
        name2 = response['Items'][0]['name']
        new_name = get_meaningful_name(name1, name2)
        if len(new_name) > 3:
            names.append(new_name)
    return names


def lambda_handler(event, context):
    male_first_names = generate_names(male_first_names_db, 5, male_first_names_count)
    female_first_names = generate_names(female_first_names_db, 5, female_first_names_count)
    last_names = generate_names(last_names_db, 6, last_names_count)

    random_names = []
    for i in range(2):
        random_names.append(male_first_names[i].capitalize())
    for i in range(2, 5):
        random_names.append(male_first_names[i].capitalize() + " " + last_names[i - 2].capitalize())
    for i in range(2):
        random_names.append(female_first_names[i].capitalize())
    for i in range(2, 5):
        random_names.append(female_first_names[i].capitalize() + " " + last_names[i + 1].capitalize())

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(random_names)
    }
