import os

# Ensure default region is set to avoid NoRegionError during imports
if 'AWS_DEFAULT_REGION' not in os.environ:
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

from app.app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5041))
    app.run(host='0.0.0.0', port=port, debug=True)