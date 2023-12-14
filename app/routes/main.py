from flask import Blueprint, render_template

from app.models import Entry, Drawing, DrawingPrize, Prize

bp = Blueprint('main', 'main')


@bp.route('/')
def index():
    return render_template(
        'main/index.html',
        entries=Entry.query.filter(Entry.confirmed == True).count(),
        prizes=Prize.query.filter().count(),
        drawings=Drawing.query.filter().count(),
        winners=DrawingPrize.query.filter(DrawingPrize.confirmed_winner != None).count()
    )
