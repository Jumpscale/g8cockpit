from flask import Blueprint, jsonify, request, current_app
from JumpScale import j


cockpit_api = Blueprint('cockpit_api', __name__)


@cockpit_api.route('/cockpit/update', methods=['POST'])
def update():
    '''
    endpoint that update the cockpit to the last version
    It is handler for POST /cockpit/update
    '''
    try:
        current_app.ays_bot.update()
        return jsonify(msg='update done'), 200
    except j.exceptions.NotFound as e:
        return jsonify(msg=e.message), 404
    except j.exceptions.AYSNotFound as e:
        return jsonify(msg=e.message), 404
