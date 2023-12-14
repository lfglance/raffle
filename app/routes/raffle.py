from io import BytesIO
from base64 import b64encode
from secrets import choice

from qrcode import make as qrcode_make
from flask import Blueprint, render_template, url_for, redirect, request, flash, jsonify
from flask_login import login_required

from app.models import Entry, Prize, Drawing, DrawingPrize
from app.factory import db

bp = Blueprint('raffle', 'raffle')

# Enter raffle

@bp.route('/enter')
@login_required
def enter_raffle():
    entry = Entry()
    db.session.add(entry)
    db.session.commit()
    _qr = BytesIO()
    qr = qrcode_make(url_for('raffle.show_entry', uuid=entry.uuid, _external=True)).save(_qr)
    return render_template(
        'raffle/enter.html',
        entry=entry,
        qrcode=b64encode(_qr.getvalue()).decode()
    )


@bp.route('/show/entry/<uuid>')
def show_entry(uuid):
    entry = Entry.query.filter(Entry.uuid == uuid).first()
    if not entry:
        return redirect(url_for('main.index'))
    if not entry.confirmed:
        entry.confirmed = True
        db.session.commit()
    return render_template(
        'raffle/show_entry.html',
        entry=entry
    )

# Prizes

@bp.route('/prize/manage', methods=['GET', 'POST'])
@login_required
def manage_prizes():
    if request.method == 'POST' and request.form:
        try:
            assert len(request.form.get('name')) > 3
            existing = Prize.query.filter(Prize.name == request.form.get('name')).first()
            if not existing:
                p = Prize(
                    name=request.form.get('name'),
                    image_url=request.form.get('image_url'),
                    description=request.form.get('description', '')
                )
                db.session.add(p)
                db.session.commit()
                flash('Added new prize!', 'is-success')
            else:
                flash('Prize already exists!', 'is-warning')
        except AssertionError:
            flash('Invalid prize configuration. Try again.', 'is-warning')
        except Exception as e:
            print(e)
            flash('Something went wrong. Try again.', 'is-danger')
    prizes = Prize.query.all()
    return render_template(
        'raffle/manage_prizes.html',
        prizes=prizes
    )


@bp.route('/prize/show/<id>', methods=['GET', 'POST'])
@login_required
def show_prize(id):
    prize = Prize.query.filter(Prize.id == id).first()
    if not prize:
        flash('No prize there big dawg', 'is-warning')
        return redirect(url_for('raffle.manage_prizes'))
    else:
        edited = None
        if request.method == 'POST' and request.form:
            if request.form.get('name') != prize.name:
                prize.name = request.form.get('name')
                db.session.commit()
                edited = True
            if request.form.get('image_url') != prize.image_url:
                prize.image_url = request.form.get('image_url')
                db.session.commit()
                edited = True
            if request.form.get('description') != prize.description:
                prize.description = request.form.get('description')
                db.session.commit()
                edited = True
            if request.form.get('ship') == 'no' and prize.ship_to_winner != False:
                prize.ship_to_winner = False
                db.session.commit()
                edited = True
            elif request.form.get('ship') == 'yes' and prize.ship_to_winner != True:
                prize.ship_to_winner = True
                db.session.commit()
                edited = True
            if edited:
                flash('Edited item!', 'is-success')
            else:
                flash('No changes.', 'is-info')
        drawings = Drawing.query.join(
            DrawingPrize
        ).filter(
            DrawingPrize.prize_id == id
        )
        return render_template(
            'raffle/show_prize.html', 
            prize=prize,
            drawings=drawings
        )


@bp.route('/prize/delete/<id>')
@login_required
def delete_prize(id):
    prize = Prize.query.filter(Prize.id == id).first()
    if prize:
        flash(f'You deleted prize #{prize.id} ({prize.name})', 'is-success')
        db.session.delete(prize)
        db.session.commit()
        return redirect(url_for('raffle.manage_prizes'))


# Drawing

@bp.route('/drawing/manage', methods=['GET', 'POST'])
@login_required
def manage_drawings():
    if request.method == 'POST' and request.form:
        try:
            assert len(request.form.get('name')) > 3
            existing = Drawing.query.filter(Drawing.name == request.form.get('name')).first()
            if not existing:
                d = Drawing(
                    name=request.form.get('name')
                )
                db.session.add(d)
                db.session.commit()
                flash('Added new drawing!', 'is-success')
            else:
                flash('Drawing already exists!', 'is-warning')
        except AssertionError:
            flash('Invalid drawing name. Try again.', 'is-warning')
        except Exception as e:
            print(e)
            flash('Something went wrong. Try again.', 'is-danger')
    drawings = Drawing.query.filter().order_by(Drawing.create_date.asc())
    return render_template(
        'raffle/manage_drawings.html',
        drawings=drawings
    )


@bp.route('/drawing/show/<id>', methods=['GET', 'POST'])
@login_required
def show_drawing(id):
    drawing = Drawing.query.filter(Drawing.id == id).first()
    if not drawing:
        flash('No drawing there', 'is-warning')
        return redirect(url_for('raffle.manage_drawings'))
    elif drawing.has_concluded:
        flash('That drawing has concluded and cannot be changed', 'is-warning')
        return redirect(url_for('raffle.manage_drawings'))
    else:
        edited = None
        if request.method == 'POST' and request.form:
            if request.form.get('name') != drawing.name:
                drawing.name = request.form.get('name')
                db.session.commit()
                edited = True
            if edited:
                flash('Edited item!', 'is-success')
            else:
                flash('No changes.', 'is-info')
        elif request.method == 'GET' and request.args:
            if request.args.get('add'):
                to_add = DrawingPrize(
                    prize_id=request.args.get('add'),
                    drawing_id=drawing.id
                )
                db.session.add(to_add)
                db.session.commit()
                flash(f'Added prize #{request.args.get("add")}', 'is-success')
                return redirect(url_for('raffle.show_drawing', id=drawing.id))
            elif request.args.get('remove'):
                to_remove = DrawingPrize.query.filter(DrawingPrize.id == request.args.get('remove')).first()
                if to_remove:
                    db.session.delete(to_remove)
                    db.session.commit()
                    flash(f'Removed drawing prize #{to_remove.id} from {drawing.name}', 'is-success')
                    return redirect(url_for('raffle.show_drawing', id=drawing.id))
        all_prizes = Prize.query.all()
        drawing_prizes = DrawingPrize.query.filter(
            DrawingPrize.drawing_id == drawing.id
        ).order_by(DrawingPrize.create_date.asc())
        return render_template(
            'raffle/show_drawing.html', 
            drawing=drawing,
            all_prizes=all_prizes,
            drawing_prizes=drawing_prizes
        )


@bp.route('/drawing/delete/<id>')
@login_required
def delete_drawing(id):
    drawing = Drawing.query.get(id)
    if not drawing:
        flash('That drawing does not exist', 'is-warning')
        return redirect(url_for('raffle.manage_drawings'))
    
    if drawing.has_concluded:
        flash('That drawing has concluded, you cannot delete it', 'is-warning')
        return redirect(url_for('raffle.manage_drawings'))
    
    db.session.delete(drawing)
    db.session.commit()
    flash(f'You deleted drawing #{drawing.id} ({drawing.name})', 'is-success')
    return redirect(url_for('raffle.manage_drawings'))


@bp.route('/drawing/start/<id>')
@login_required
def start_drawing(id):
    drawing = Drawing.query.get(id)
    if not drawing:
        flash('There is no drawing there', 'is-warning')
        return redirect(url_for('raffle.manage_drawings'))
    
    if drawing.has_concluded:
        flash('That drawing has concluded, you cannot start it', 'is-warning')
        return redirect(url_for('raffle.manage_drawings'))
    
    ongoing = Drawing.query.filter(Drawing.is_active == True).first()
    if ongoing:
        flash(f'There is already an active raffle (#{ongoing.id})')
        return redirect(url_for('raffle.now'))

    drawing.start()
    return redirect(url_for('raffle.now'))

@bp.route('/raffle')
def now():
    drawing = Drawing.query.filter(Drawing.is_active == True).first()
    if not drawing:
        flash(f'There is no active raffle right now. Check back later.', 'is-warning')
        return redirect(url_for('main.index'))

    prize = drawing.get_next_prize()
    if not prize:
        drawing.end()
        flash('There are no more prizes to be raffled')
        return redirect(url_for('main.index'))

    if prize.selected_entry == None:
        potentials = Entry.query.filter(Entry.has_won == False).all()
        selected = choice(potentials)
        prize.selected_entry_id = selected.id
        db.session.commit()
    
    return render_template(
        'raffle/raffling.html',
        drawing=drawing,
        prize=prize
    )

@bp.route('/raffle/reselect')
@login_required
def reselect():
    drawing = Drawing.query.filter(Drawing.is_active == True).first()
    if not drawing:
        flash(f'There is no active raffle right now. Check back later.', 'is-warning')
        return redirect(url_for('main.index'))
    
    prize = drawing.get_next_prize()
    if not prize:
        flash(f'There is no active raffle right now. Check back later.', 'is-warning')
        return redirect(url_for('main.index'))
    
    potentials = Entry.query.filter(Entry.has_won == False).all()
    selected = choice(potentials)
    prize.selected_entry_id = selected.id
    db.session.commit()
    return redirect(url_for('raffle.now'))

@bp.route('/raffle/confirm')
@login_required
def confirm():
    drawing = Drawing.query.filter(Drawing.is_active == True).first()
    if not drawing:
        flash(f'There is no active raffle right now. Check back later.', 'is-warning')
        return redirect(url_for('main.index'))
    
    prize = drawing.get_next_prize()
    if not prize:
        flash(f'There is no active raffle right now. Check back later.', 'is-warning')
        return redirect(url_for('main.index'))
    
    prize.confirmed_winner_id = prize.selected_entry_id
    db.session.commit()
    return redirect(url_for('raffle.now'))

@bp.route('/raffle/check')
def check():
    drawing = Drawing.query.filter(Drawing.is_active == True).first()
    if drawing:
        return jsonify({'active': True})
    else:
        return jsonify({'active': False})