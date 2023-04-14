from flask import Blueprint, current_app
from flask_session import Session

report_api = Blueprint('report_api', __name__)

@report_api.route('/reports/profit',methods=["GET", "POST"])
def reports_profit():
    if not 'loggedin' in session:
        return redirect(url_for('login'))  

    form = ReportsForm()

    if request.method == "POST":
        details = request.form
        start_date, end_date = function.set_dates(details)
        sold_dates = get_data.get_group_sold_from_date(start_date, end_date)
        purchased_dates = get_data.get_purchased_from_date(start_date, end_date)
        expenses= get_data.get_all_from_expenses_date(start_date, end_date)
        return render_template('reports_profit.html', form=form, sold_dates=sold_dates, purchased_dates=purchased_dates, expenses=expenses,type_value=details['type'])
    return render_template('reports_profit.html', form=form)
