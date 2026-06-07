import requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity


bp = Blueprint('proces', __name__, url_prefix='/api/proces')
CAMUNDA = 'http://localhost:8080/engine-rest'

PROCESS_KEY = 'pronalazak-cimera'




@bp.post('/pokreni')
@jwt_required()
def pokreni_proces():
    korisnik_id = get_jwt_identity()
    token = request.headers.get('Authorization', '').replace('Bearer ', '')


    r = requests.post(
        f'{CAMUNDA}/process-definition/key/{PROCESS_KEY}/start',
        json={
            'variables': {
                'korisnik_id': {'value': korisnik_id,  'type': 'String'},
                'token':       {'value': token,        'type': 'String'},
            }
        }
    )


    if not r.ok:
        return jsonify(error='Ne mogu pokrenuti Camunda proces.'), 500


    instance = r.json()
    return jsonify({'process_instance_id': instance['id']}), 201




@bp.get('/stanje/<instance_id>')
@jwt_required()
def stanje_procesa(instance_id):
    r_inst = requests.get(f'{CAMUNDA}/process-instance/{instance_id}')


    if r_inst.status_code == 404:
        return jsonify({'status': 'zavrsen', 'aktivan_korak': None})

    r_act = requests.get(
        f'{CAMUNDA}/activity-instance',
        params={'processInstanceId': instance_id}
    )
    aktivnosti = r_act.json() if r_act.ok else []


    aktivan_korak = None
    if aktivnosti:
        aktivan_korak = aktivnosti[0].get('activityName', 'Nepoznato')


    return jsonify({
        'status': 'aktivan',
        'aktivan_korak': aktivan_korak,
        'process_instance_id': instance_id
    })




@bp.post('/korak/odaberi-cimera')
@jwt_required()
def odaberi_cimera():
    data = request.get_json() or {}
    instance_id = data.get('process_instance_id')
    odabrani_id = data.get('odabrani_korisnik_id')


    if not instance_id or not odabrani_id:
        return jsonify(error='Nedostaju process_instance_id ili odabrani_korisnik_id.'), 400

    r = requests.get(f'{CAMUNDA}/task',
                     params={'processInstanceId': instance_id})
    tasks = r.json() if r.ok else []


    if not tasks:
        return jsonify(error='Nema aktivnog zadatka za ovu instancu.'), 404


    task_id = tasks[0]['id']
    requests.post(
        f'{CAMUNDA}/task/{task_id}/complete',
        json={
            'variables': {
                'odabrani_korisnik_id': {'value': odabrani_id, 'type': 'Integer'},
                'nastavi_traziti':      {'value': False,       'type': 'Boolean'}
            }
        }
    )
    return jsonify({'ok': True})




@bp.post('/korak/promijeni-filtere')
@jwt_required()
def promijeni_filtere():
    data = request.get_json() or {}
    instance_id = data.get('process_instance_id')


    r = requests.get(f'{CAMUNDA}/task',
                     params={'processInstanceId': instance_id})
    tasks = r.json() if r.ok else []


    if not tasks:
        return jsonify(error='Nema aktivnog zadatka.'), 404


    task_id = tasks[0]['id']
    variables = {
        'nastavi_traziti': {'value': True, 'type': 'Boolean'}
    }
    if data.get('filter_grad'):
        variables['filter_grad'] = {'value': data['filter_grad'], 'type': 'String'}
    if data.get('filter_ritam'):
        variables['filter_ritam'] = {'value': data['filter_ritam'], 'type': 'String'}
    if data.get('filter_min_postotak'):
        variables['filter_min_postotak'] = {
            'value': float(data['filter_min_postotak']), 'type': 'Double'
        }


    requests.post(
        f'{CAMUNDA}/task/{task_id}/complete',
        json={'variables': variables}
    )
    return jsonify({'ok': True})
