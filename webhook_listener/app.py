import hmac
import hashlib
import subprocess
import logging
import sys
import os
import threading
from flask import Flask, abort, request, jsonify
from flask.logging import default_handler

app = Flask(__name__)
app.logger.removeHandler(default_handler)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)
app.logger.info("Starting Github listener")

GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')

def verify_signature(payload_body, signature_header):
    """Verify GitHub payload with the secret token."""
    if not signature_header:
        abort(403, description="x-hub-signature-256 header is missing!")

    hash_object = hmac.new(GITHUB_WEBHOOK_SECRET.encode('utf-8'),
                           msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        abort(403, description="Request signatures didn't match!")


def run_ansible_playbook():
    completed_process = subprocess.run(
        ["/srv/hosting_infrastructure/venv/bin/ansible-playbook",
         "-c=local", "-u", "root", "-i",
         "/srv/hosting_infrastructure/ansible/inventory.yaml",
         "/srv/hosting_infrastructure/ansible/setup.yaml",
         "--extra-vars", f"env={ENVIRONMENT}"],
        check=True, capture_output=True, text=True)

    # Log the output
    app.logger.info(completed_process.stdout)
    app.logger.error(completed_process.stderr)


@app.route('/github', methods=["POST"])
def gh_webhook_listener():
    # Verify GitHub signature
    verify_signature(request.data, request.headers.get('X-Hub-Signature-256'))

    # Start ansible-playbook in a separate thread
    threading.Thread(target=run_ansible_playbook).start()

    return jsonify(
        {'message': 'Webhook received, running process'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5009)
