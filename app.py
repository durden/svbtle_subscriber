"""
Little wrapper to kick off web interface
"""

import os
import svbtle_subscriber as subscriber


def run_web(host, port):
    """Run web interface"""

    from flask import Flask, request, render_template
    from werkzeug import secure_filename

    app = Flask(__name__)
    app.debug = True

    def allowed_file(filename):
        """Return True if file has allowed extension (xml only)"""

        return '.' in filename and  filename.rsplit('.', 1)[1] in set(['xml'])

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
            filename = secure_filename(file_obj.filename)
            xml = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_obj.save(xml)

            writers = subscriber.get_writers(False)

            greader_feed_urls = subscriber.get_greader_subscription_urls(xml)
            if greader_feed_urls:
                missing_authors = subscriber.diff_subscriptions(
                                                            greader_feed_urls,
                                                            writers)
                os.remove(xml)

        return render_template('subscriptions.html', writers=missing_authors,
                               heading='Missing Svbtle Authors')

    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

    app.run(host=host, port=port)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    run_web(host='0.0.0.0', port=port)
