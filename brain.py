import os
import webbrowser
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from forms import Find, Epi
from heart import Heart

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['secret_key']  # secret_key in environmental variables
Bootstrap(app)

heart = Heart()


@app.route("/", methods=['POST', 'GET'])
def home():
    form_find = Find()
    if request.method == 'POST':
        name = form_find.movie.data
        return redirect(url_for('select', name=name))
    return render_template("index.html", form_find=form_find, data=heart.home_pg())


@app.route('/select')
def select():
    movie_name = request.args.get('name')
    data = heart.search(movie_name)
    return render_template('select.html', movies=data, name=movie_name)


@app.route('/select_episodes', methods=['POST', 'GET'])
def select_episodes():
    form = Epi()
    movie_name = request.args.get('name')
    movie_url = request.args.get('url')
    movie_img = request.args.get('img')
    data = heart.get_all_ep_pg(movie_url)
    if len(data) == 1:
        download_links = heart.get_ep_download_links(data)
        heart.download(download_links)
        return redirect(url_for('home'))

    elif request.method == 'POST':
        ep = form.episode.data
        if '-' in ep:
            ep_numbers = ep.split('-')
            ep_numbers = [i - 1 for i in range(int(ep_numbers[0]), int(ep_numbers[1]) + 1)]
        else:
            ep_numbers = [int(i) - 1 for i in ep.split(',')]
        download_links = heart.get_ep_download_links([data[i] for i in ep_numbers])
        heart.download(download_links)
        return redirect(url_for('home'))

    return render_template('episodes.html', form=form, data=data, name=movie_name, img=movie_img)


if __name__ == '__main__':
    webbrowser.open_new('http://127.0.0.1:5000')
    app.run(port=5000)
