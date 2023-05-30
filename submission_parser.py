from html.parser import HTMLParser

import requests


class CFSubmissionResponseParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.code = ''
        self.is_code = False

    def handle_starttag(self, tag, attrs):
        if tag == 'pre' and ('id', 'program-source-text') in attrs:
            self.is_code = True

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.is_code = False

    def handle_data(self, data):
        if self.is_code:
            self.code += data


class CFSubmission:
    def __init__(self, contest_id, submission_id):
        self.contest_id = contest_id
        self.submission_id = submission_id
        self.code = ''

    def get_code(self):
        if self.code:
            return self.code
        URL = f'https://codeforces.com/contest/{self.contest_id}/submission/{self.submission_id}'
        response = requests.get(URL)
        parser = CFSubmissionResponseParser()
        parser.feed(response.text)
        parser.close()
        self.code = parser.code
        return self.code

    def save(self, filename):
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            f.write(self.get_code())


if __name__ == '__main__':
    CONTEST_ID = 1805
    SUBMISSION_ID = 200532587
    submission = CFSubmission(CONTEST_ID, SUBMISSION_ID)
    # submission.save('submission.py')
