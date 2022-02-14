import csv
import json
import netrc
import os
import re
from urllib.parse import urlparse
from string import Template
from numpy.lib.polynomial import _binary_op_dispatcher
import pandas

import requests
import xnat

from knee_marker_analysis import knee_marker_analysis


TASKMANAGER = 'https://bigr-tracr.erasmusmc.nl:5001'
XNAT = 'https://bigr-genr-xnat.erasmusmc.nl'


COPY_FIELDS = [
]


def download_latest_file(path, xnat_connection):
    if path.startswith(XNAT):
        path = path.replace(XNAT, '')

    if '{timestamp}' in path:
        resource, filename = path.split('/files/')
        pattern = filename.format(timestamp=r'(_?(?P<timestamp>\d\d\d\d\-\d\d\-\d\dT\d\d:\d\d:\d\d)_?)?') + '$'
        pattern = pattern.replace(' ', '%20')

        # Query all files and sort by timestamp
        print('{}/files'.format(resource))
        files = xnat_connection.get_json('{}/files'.format(resource))
        files = [x['Name'] for x in files['ResultSet']['Result']]
        print('Found file candidates {}, pattern is {}'.format(files, pattern))
        files = {re.match(pattern, x): x for x in files}
        files = {k.group('timestamp'): v for k, v in files.items() if k is not None}
        print('Found files: {}'.format(files))

        if len(files) == 0:
            return None

        # None is the first, timestamp come after that, so last one is highest timestamp
        files = sorted(files.items())
        latest_timestamp = files[-1][0]
        latest_file = files[-1][1]
        print('Select {} as being the latest file'.format(latest_file))

        # Construct the correct path again
        path = '{}/files/{}'.format(resource, latest_file)

        data = xnat_connection.get_json(path)

        data['__timestamp__'] = latest_timestamp

        return data


def collect_info(connection, xnat_connection):
    possible_tasks = []
    for user_id in range(9, 19):
        response = connection.get(f'{TASKMANAGER}/api/v1/users/{user_id}/tasks')
        print(f'response = [{response.status_code}] {response.text}')
        user_tasks = response.json()['tasks']
        possible_tasks.extend(x for x in user_tasks if x['status'] != 'aborted')
        
    result = []

    print(f"Found {len(possible_tasks)} tasks to check")

    for task in possible_tasks:
        response = connection.get('{}{}'.format(TASKMANAGER, task['uri']))
        task_data = response.json()
        task_content = json.loads(task_data['content'])
        xnat_experiment = task_content['_vars']['EXPERIMENT_ID']
        xnat_experiment = xnat_connection.create_object('/data/experiments/{}'.format(xnat_experiment))

        # Get latest FIELDS dat from XNAT
        field_data = download_latest_file(task_content['fields_file'], xnat_connection)

        if field_data is None:
            continue

        rater = field_data['__raters__'][-1]
        if rater == 'wvanderheijden' and 'wvanderheijden2' in task_content['fields_file']:
            rater = 'wvanderheijden2'

        print(f"Got field data: {json.dumps(field_data)}")
        (i_s_R, lt_R, tttg_R, pt_R, lpt_R, bo_R, sa_R, lat_incl_R, med_incl_R, td_R, mis_R, cd_R, bp_R, ta_R,
         i_s_L, lt_L, tttg_L, pt_L, lpt_L, bo_L, sa_L, lat_incl_L, med_incl_L, td_L, mis_L, cd_L, bp_L, ta_L
         ) = knee_marker_analysis(field_data)

        print(f"Calculated i_s R: {i_s_R}")
        print(f"Calculated lt R: {lt_R}")
        print(f"Calculated tttg R: {tttg_R}")
        print(f"Calculated pt R: {pt_R}")
        print(f"Calculated lpt_R: {lpt_R}")
        print(f"Calculated bo_R: {bo_R}")
        print(f"Calculated sa_R: {sa_R}")
        print(f"Calculated lat_incl_R: {lat_incl_R}")
        print(f"Calculated med_incl_R: {med_incl_R}")
        print(f"Calculated td_R: {td_R}")
        print(f"Calculated mis_R: {mis_R}")
        print(f"Calculated cd_R: {cd_R}")
        print(f"Calculated bp_R: {bp_R}")
        print(f"Calculated ta_R: {ta_R}")
        print(f"Calculated i_s L: {i_s_L}")
        print(f"Calculated lt L: {lt_L}")
        print(f"Calculated tttg L: {tttg_L}")
        print(f"Calculated pt L: {pt_L}")
        print(f"Calculated lpt_L: {lpt_L}")
        print(f"Calculated bo_L: {bo_L}")
        print(f"Calculated sa_L: {sa_L}")
        print(f"Calculated lat_incl_L: {lat_incl_L}")
        print(f"Calculated med_incl_L: {med_incl_L}")
        print(f"Calculated td_L: {td_L}")
        print(f"Calculated mis_L: {mis_L}")
        print(f"Calculated cd_L: {cd_L}")
        print(f"Calculated bp_L: {bp_L}")
        print(f"Calculated ta_L: {ta_L}")

        # Collect results
        row = {
            'label': task_content['_vars']['LABEL'],
            'id': task_content['_vars']['EXPERIMENT_ID'],
            'user': rater['username'],
            'timestamp': rater['timestamp'],
            'i_s_R': i_s_R,
            'lt_R': lt_R,
            'tttg_R': tttg_R,
            'pt_R': pt_R,
            'lpt_R': lpt_R,
            'bo_R': bo_R,
            'sa_R': sa_R,
            'lat_incl_R': lat_incl_R,
            'med_incl_R': med_incl_R,
            'td_R': td_R,
            'mis_R': mis_R,
            'cd_R': cd_R,
            'bp_R': bp_R,
            'ta_R': ta_R,
            'i_s_L': i_s_L,
            'lt_L': lt_L,
            'tttg_L': tttg_L,
            'pt_L': pt_L,
            'lpt_L': lpt_L,
            'bo_L': bo_L,
            'sa_L': sa_L,
            'lat_incl_L': lat_incl_L,
            'med_incl_L': med_incl_L,
            'td_L': td_L,
            'mis_L': mis_L,
            'cd_L': cd_L,
            'bp_L': bp_L,
            'ta_L': ta_L
        }

        result.append(row)

    return result


def write_info(info, filename):
    fieldnames = (
            [
                'label', 'id', 'user', 'timestamp',
                'i_s_R', 'lt_R', 'tttg_R', 'pt_R', 'lpt_R',
                'bo_R', 'sa_R', 'lat_incl_R', 'med_incl_R',
                'td_R', 'mis_R', 'cd_R', 'bp_R', 'ta_R',
                'i_s_L', 'lt_L', 'tttg_L', 'pt_L', 'lpt_L',
                'bo_L', 'sa_L', 'lat_incl_L', 'med_incl_L',
                'td_L', 'mis_L', 'cd_L', 'bp_L', 'ta_L'
            ]
    )

    data = pandas.DataFrame(info)
    data.to_excel(filename, columns=fieldnames, index=False)


def main():
    with xnat.connect(XNAT) as xnat_connection:
        taskman_connection = requests.Session()

        parsed_taskman = urlparse(TASKMANAGER)

        try:
            netrc_file = os.path.join('~', '_netrc' if os.name == 'nt' else '.netrc')
            netrc_file = os.path.expanduser(netrc_file)
            username, _, password = netrc.netrc(netrc_file).authenticators(parsed_taskman.netloc)
            taskman_connection.auth = (username, password)
        except (TypeError, IOError):
            print('[INFO] Could not find login for {}, continuing without login'.format(parsed_taskman.netloc))

        info = collect_info(taskman_connection, xnat_connection)
    write_info(info, './knee_newIS.xlsx')


if __name__ == '__main__':
    main()
