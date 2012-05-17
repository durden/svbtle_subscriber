"""
Little wrapper to kick off web interface
"""

import os
import svbtle_subscriber as subscriber
from flask import Flask, request, render_template

app = Flask(__name__)


def allowed_file(filename):
    """Return True if file has allowed extension (xml only)"""

    return '.' in filename and  filename.rsplit('.', 1)[1] in set(['xml'])


def run_web(host, port):
    """Run web interface"""

    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

    app.run(host=host, port=port)


@app.route('/')
def home():
    """homepage"""

    return render_template('index.html')


@app.route('/all_available')
def available():
    """Show all available writers on svbtle.com"""

    writers = subscriber.get_writers(False)
    return render_template('subscriptions.html', writers=writers)


@app.route('/missing_subscriptions', methods=['POST'])
def missing():
    """Show missing author subscriptions based on uploaded file"""

    missing_authors = []
    file_obj = request.files['reader_xml']

    if file_obj and allowed_file(file_obj.filename):
        writers = subscriber.get_writers(False)

        greader_feed_urls = subscriber.get_greader_subscription_urls(
                                                                file_obj)
        if greader_feed_urls:
            missing_authors = subscriber.diff_subscriptions(
                                                        greader_feed_urls,
                                                        writers)

    return render_template('subscriptions.html', writers=missing_authors,
                            heading='Missing Svbtle Authors')


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    run_web(host='0.0.0.0', port=port)
