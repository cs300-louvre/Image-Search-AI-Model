import re
import os
import base64
from io import BytesIO
from PIL import Image
from flask import Flask, render_template, send_file, request
from core import SearchEngine
from argparse import ArgumentParser


def try_catch(func):
    ''' Decorator for try catch '''
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)
    return wrapper


app = Flask(__name__)

seach_engine = SearchEngine(model_path='ViT-B/32')


@app.route('/')
def main():
    '''Main page'''
    return render_template('index.html')


@app.route('/assets/<file_name>', methods=['GET'])
def get_assets(file_name):
    return send_file(os.path.join('templates', 'assets', file_name))


@app.route('/images/<file_name>', methods=['GET'])
def get_images(file_name):
    return send_file(os.path.join('images', file_name))


@try_catch
@app.route('/api', methods=['GET', 'POST'])
def search():
    JSON_sent = request.get_json()
    image_query = JSON_sent.get('image', None)
    text_query = JSON_sent.get('search_text', None)
    if image_query is not None:
        # remove the header
        image_query = re.sub('^data:image/.+;base64,', '', image_query)
        # decode the image
        image = Image.open(BytesIO(base64.b64decode(image_query)))
        result_topk = seach_engine.search_image(image, top_k=5)
        results = ["/images/" + result['image_name'] for result in result_topk]
    elif text_query is not None:
        result_topk = seach_engine.search_text(text_query, top_k=5)
        results = ["/images/" + result['image_name'] for result in result_topk]
    else:
        results = []
        print('No query')
    return {'results': results}


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=80)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
