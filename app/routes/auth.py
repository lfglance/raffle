import json

import requests
from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, logout_user

from app.factory import GoogleClient, db
from app.models import User
from app import config

bp = Blueprint('auth', 'auth')


@bp.route('/login')
def login():
    r = requests.get(config.GOOGLE_DISCOVERY_URL, timeout=10)
    r.raise_for_status()
    request_uri = GoogleClient.prepare_request_uri(
        r.json()['authorization_endpoint'],
        redirect_uri=request.base_url + '/callback',
        scope=['openid', 'email', 'profile'],
    )
    return redirect(request_uri)


@bp.route('/login/callback')
def callback():
    r = requests.get(config.GOOGLE_DISCOVERY_URL, timeout=10)
    r.raise_for_status()
    token_url, headers, body = GoogleClient.prepare_token_request(
        r.json()['token_endpoint'],
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=request.args.get('code')
    )
    tr = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(config.GOOGLE_CLIENT_ID, config.GOOGLE_CLIENT_SECRET),
        timeout=10
    )
    tr.raise_for_status()
    GoogleClient.parse_request_body_response(json.dumps(tr.json()))
    uri, headers, body = GoogleClient.add_token(r.json()['userinfo_endpoint'])
    ur = requests.get(uri, headers=headers, data=body, timeout=10)
    ur.raise_for_status()
    u = None
    if ur.json().get('email_verified'):
        unique_id = ur.json()['sub']
        users_email = ur.json()['email']
        picture = ur.json()['picture']
        users_name = ur.json()['given_name']
        u = User.query.get(unique_id)
        if not u:
            u = User(
                id=unique_id,
                name=users_name,
                profile_pic=picture,
                email=users_email
            )
            db.session.add(u)
            db.session.commit()
    else:
        return 'User email not available or not verified by Google.', 400
    u.login()
    return redirect(url_for('main.index'))


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
