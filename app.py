from flask import Flask, render_template, request, redirect
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
import Quandl

app = Flask(__name__)

api_key = 'LiHdpPDKZas3fSfA5-LJ'
start_date = '2000-01-01'
colors = ['blue', 'red', 'green', 'purple']


def get_stock_data(ticker):
    df = Quandl.get('WIKI/%s' % ticker.upper(), collapse='weekly',
                    trim_start=start_date, authtoken=api_key)
    df['Datetime'] = pd.to_datetime(df.index)
    return df


def get_plot_components(df, columns):
    p = figure(title="Data from Quandle WIKI set", x_axis_label="Date",
               y_axis_label="Price ($)", x_axis_type='datetime')
    for i, col in enumerate(columns):
        p.line(df.Datetime, df[col], legend=col, color=colors[i])
    return components(p)


def save_html_plot(ticker, columns):
    ticker = ticker.upper()
    df = get_stock_data(ticker)
    script, div = get_plot_components(df, columns)
    html_text = '''
    <!doctype html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>%s Stock</title>
            <link rel="stylesheet"
            href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap-theme.min.css">
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
            <link href="http://cdn.pydata.org/bokeh/release/bokeh-0.11.0.min.css" rel="stylesheet" type="text/css">
            <script src="http://cdn.pydata.org/bokeh/release/bokeh-0.11.0.min.js"></script>
            %s
        </head>
        <body>
            <div class=page>
                <h1>Generated graph for %s<br><a href="/index">Back</a></h1>
                %s
            </div>
        </body>
    </html>
    ''' % (ticker, script, ticker, div)
    html_path = '%s_%s.html' % (ticker,
                                '_'.join(columns).replace('. ', ''))
    with open('templates/%s' % html_path, 'w') as f:
        f.write(html_text)
    return html_path


@app.route('/')
def main():
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        ticker = request.form['ticker']
        columns = request.form.getlist('check')
        try:
            html_path = save_html_plot(ticker, columns)
        except Quandl.Quandl.DatasetNotFound:
            return render_template('error-quandle.html')
        return render_template(html_path)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    # app.run(port=33507)
    # app.run(debug=True)
