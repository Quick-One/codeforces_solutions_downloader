import pandas
import requests
import json
from parsing_utils import flatten_json, parse_contest_name
from pathlib import Path
from submission_parser import CFSubmission
from time import sleep

USER_NAME = 'Quick-One'

### Get submissions
submissions_URL = f'https://codeforces.com/api/user.status?handle={USER_NAME}&from=1&count=100000'
response = requests.get(submissions_URL).json()

if response['status'] != 'OK':
    raise Exception('Could not get submissions from codeforces API')

submissions = response['result']
submissions = [flatten_json(submission) for submission in submissions]
submissions = pandas.DataFrame(submissions)
# Drop non contest submissions
submissions = submissions.dropna(subset=['contestId'])
# Consider only accepted submissions
submissions = submissions[submissions['verdict'] == 'OK']
# remove multiple submissions of the same problem
submissions = submissions.drop_duplicates(subset=['contestId', 'problem_index', 'programmingLanguage'])
submissions['contestId'] = submissions['contestId'].astype(int)
submissions_cols = ['id', 'contestId', 'problem_index', 'programmingLanguage']
submissions = submissions[submissions_cols]


### Get contests
contests_URL = r'https://codeforces.com/api/contest.list?gym=false'
response = requests.get(contests_URL).json()

if response['status'] != 'OK':
    raise Exception('Could not get contests from codeforces API')

contests = response['result']
contests = [flatten_json(contest) for contest in contests]
contests = pandas.DataFrame(contests)
contests_cols =['id', 'name', 'type']
contests = contests[contests_cols]
contests['name'] = contests['name'].str.lower()

### Merge submissions and contests
merged = submissions.merge(contests, left_on='contestId', right_on='id')
merged = merged.drop(columns=['id_y'])
coulmn_rename = {
    'id_x': 'submissionId',
    'problem_index': 'problemIndex',
    'name': 'contestName'
}
merged = merged.rename(columns=coulmn_rename)
merged['folderName'] = merged['contestName'].apply(parse_contest_name)

with open('file_extensions.json', 'r') as f:
    file_extensions = json.load(f)

p = Path.cwd() / f'CF_{USER_NAME}'
for index, row in merged.iterrows():
    path_soln = p / row['folderName']
    path_soln.mkdir(exist_ok=True, parents=True)

    extension = file_extensions[row['programmingLanguage']]

    file_path = path_soln / f'{row["problemIndex"]}.{extension}'
    if file_path.exists():
        continue
    CFSubmission(row['contestId'], row['submissionId']).save(file_path)
    print(f'Saved {file_path}')
    sleep(0.1)
