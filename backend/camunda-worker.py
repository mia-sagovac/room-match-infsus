import time
import requests


CAMUNDA_URL = 'http://localhost:8080/engine-rest'
FLASK_URL   = 'http://localhost:5000'
WORKER_ID   = 'roommatch-worker'




def fetch_and_lock(topic, count=1):
    response = requests.post(
        f'{CAMUNDA_URL}/external-task/fetchAndLock',
        json={
            'workerId': WORKER_ID,
            'maxTasks': count,
            'topics': [{'topicName': topic, 'lockDuration': 10000}]
        }
    )
    return response.json() if response.ok else []




def complete_task(task_id, variables={}):
    requests.post(
        f'{CAMUNDA_URL}/external-task/{task_id}/complete',
        json={'workerId': WORKER_ID, 'variables': variables}
    )




def fail_task(task_id, message):
    requests.post(
        f'{CAMUNDA_URL}/external-task/{task_id}/failure',
        json={
            'workerId': WORKER_ID,
            'errorMessage': message,
            'retries': 0,
            'retryTimeout': 0
        }
    )


def handle_provjeri_profil(task):
    token = task['variables']['token']['value']
    headers = {'Authorization': f'Bearer {token}'}


    try:
        r = requests.get(f'{FLASK_URL}/api/profil', headers=headers)
        profil = r.json() if r.ok else {}
        popunjen = bool(profil.get('grad'))
        complete_task(task['id'], {
            'profil_popunjen': {'value': popunjen, 'type': 'Boolean'}
        })
    except Exception as e:
        fail_task(task['id'], str(e))




def handle_dohvati_preporuke(task):
    token = task['variables']['token']['value']
    headers = {'Authorization': f'Bearer {token}'}

    params = {}
    vars_ = task.get('variables', {})
    if 'filter_grad' in vars_:
        params['grad'] = vars_['filter_grad']['value']
    if 'filter_ritam' in vars_:
        params['ritam'] = vars_['filter_ritam']['value']
    if 'filter_min_postotak' in vars_:
        params['min_postotak'] = vars_['filter_min_postotak']['value']


    try:
        r = requests.get(
            f'{FLASK_URL}/api/match/preporuke',
            headers=headers,
            params=params
        )
        rezultati = r.json() if r.ok else []
        complete_task(task['id'], {
            'broj_preporuka': {'value': len(rezultati), 'type': 'Integer'},
            'ima_preporuka': {'value': len(rezultati) > 0, 'type': 'Boolean'}
        })
    except Exception as e:
        fail_task(task['id'], str(e))




def handle_kreiraj_match(task):
    token = task['variables']['token']['value']
    odabrani_id = task['variables']['odabrani_korisnik_id']['value']
    headers = {'Authorization': f'Bearer {token}'}


    try:
        r = requests.post(
            f'{FLASK_URL}/api/match',
            json={'korisnik_id': odabrani_id},
            headers=headers
        )
        match = r.json()
        complete_task(task['id'], {
            'match_id': {'value': match.get('match_id'), 'type': 'Integer'},
            'match_status': {'value': match.get('status', 'predlozen'), 'type': 'String'}
        })
    except Exception as e:
        fail_task(task['id'], str(e))

def handle_otvori_chat(task):
    match_id = task['variables'].get('match_id', {}).get('value')
    complete_task(task['id'], {
        'razgovor_otvoren': {'value': True, 'type': 'Boolean'}
    })


HANDLERI = {
    'provjeri-profil':      handle_provjeri_profil,
    'dohvati-preporuke':    handle_dohvati_preporuke,
    'kreiraj-match':        handle_kreiraj_match,
    'otvori-chat':          handle_otvori_chat,
}

if __name__ == '__main__':
    print('Camunda worker pokrenut — ceka na zadatke...')
    print(f'Camunda: {CAMUNDA_URL}')
    print(f'Flask:   {FLASK_URL}')
    print('---')
    while True:
        for topic, handler in HANDLERI.items():
            for task in fetch_and_lock(topic):
                try:
                    handler(task)
                    print(f'[OK]  {topic} | task {task["id"][:8]}...')
                except Exception as e:
                    print(f'[ERR] {topic}: {e}')
        time.sleep(2)
