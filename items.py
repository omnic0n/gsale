
from flask import Blueprint


mod = Blueprint('items', __name__)

@mod.route('/items/bought',methods=["POST","GET"])
def bought_items():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,name FROM groups ORDER BY id ASC")
    groups = list(cur.fetchall())
    cur.execute("SELECT * FROM location ORDER BY id ASC")
    locations = list(cur.fetchall())

    form = PurchaseForm()
    form.group.choices = [(group['id'], group['name']) for group in groups]
    form.location.choices = [(location['id'], location['long_name']) for location in locations]
    if not form.validate_on_submit():
        return render_template('items_purchased.html',form=form)
    return render_template('items_purchased.html', form=form)
