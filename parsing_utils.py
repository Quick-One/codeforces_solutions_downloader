import re


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out


def parse_contest_name(name):
    
    # codeforces round {} (div. {},...)
    pattern = r'codeforces round (\d+) \(div\. (\d+)'
    match = re.match(pattern, name)
    if match:
        contest_id = match.group(1)
        division = match.group(2)
        contest_name = f'{contest_id}_div{division}'
        return contest_name

    # educational codeforces round {} ...
    edu_pattern = r'educational codeforces round (\d+)'
    match = re.match(edu_pattern, name)
    if match:
        contest_id = match.group(1)
        contest_name = f'edu_{contest_id}'
        return contest_name

    # codeforces round {} ...
    pattern = r'codeforces round (\d+)'
    match = re.match(pattern, name)
    if match:
        contest_id = match.group(1)
        contest_name = f'{contest_id}'
        return contest_name

    # remove everything between the parenthesis and the parenthesis itself
    pattern = r'\(.*\)'
    name = re.sub(pattern, '', name)

    # make name folder name friendly
    name = name.strip()
    safe_name = ''
    for c in name:
        if c.isalnum():
            safe_name += c
        elif safe_name[-1] == '_':
            continue
        else:
            safe_name += '_'
    return safe_name
