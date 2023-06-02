import hmac
import hashlib
import subprocess
import json
import threading
import logging
import sys
from flask import Flask, abort, request, jsonify

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

GITHUB_WEBHOOK_SECRET = 'kybR%*DK4W4hGm'

# A global variable to check if playbook is running
playbook_running = False


def run_ansible_playbook():
    global playbook_running
    try:
        completed_process = subprocess.run(
            [
                "/srv/hosting_infrastructure/venv/bin/ansible-playbook",
                "--connection", "local",
                "-u", "root",
                "-i", "/srv/hosting_infrastructure/ansible/inventory.yaml",
                "/srv/hosting_infrastructure/ansible/setup.yaml"
            ], check=True, capture_output=True, text=True)

        # Log the output
        app.logger.info(completed_process.stdout)
        app.logger.error(completed_process.stderr)
    except subprocess.CalledProcessError as e:
        app.logger.error(f'Error running Ansible playbook: {str(e)}')
    finally:
        playbook_running = False


def verify_signature(payload_body, signature_header):
    """Verify GitHub payload with the secret token."""
    if not signature_header:
        abort(403, description="x-hub-signature-256 header is missing!")

    hash_object = hmac.new(GITHUB_WEBHOOK_SECRET.encode('utf-8'),
                           msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        abort(403, description="Request signatures didn't match!")


@app.route('/github', methods=["POST"])
def gh_webhook_listener():
    # Verify GitHub signature
    verify_signature(request.data, request.headers.get('X-Hub-Signature-256'))

    # Parse the incoming payload from GitHub
    data = json.loads(request.data)

    # Check if the push was to the master branch
    global playbook_running
    if playbook_running:
        return jsonify(
            {'message': 'Webhook received, process already running'}), 409
    else:
        playbook_running = True
        threading.Thread(target=run_ansible_playbook).start()
        return jsonify(
            {'message': 'Webhook received, running process'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5009)
