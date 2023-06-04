import hmac
import hashlib
import subprocess
import os
import threading
from flask import Flask, abort, request, jsonify

app = Flask(__name__)

GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
ENVIRONMENT = os.getenv('ENVIRONMENT')
INSTALL_DIR = os.getenv('INSTALL_DIR')


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
    try:
        post_data = request.get_json()

        # Navigate to the repository's directory
        os.chdir(f"{INSTALL_DIR}/hosting_infrastructure")

        # Fetch the latest shallow commit and reset to it
        # Need to do this before running playbook to ensure we're
        # running latest version of playbook
        fetch_process = subprocess.run(
            ['git', 'fetch', '--depth', '1', 'origin', 'main'],
            check=True, capture_output=True, text=True)
        reset_process = subprocess.run(
            ['git', 'reset', '--hard', 'FETCH_HEAD'],
            check=True, capture_output=True, text=True)

        # Run the Ansible playbook
        ansible_args = [
            "/srv/hosting_infrastructure/venv/bin/ansible-playbook",
            "-c=local",
            "-u", "root",
            "-i", "/srv/hosting_infrastructure/ansible/inventory.yaml",
            "--extra-vars", f"env={ENVIRONMENT}"
        ]

        if post_data.repository.name == "hosting_infrastructure":
            ansible_args += ["--extra-vars", "install_type=full"]
        else:
            ansible_args += ["--extra-vars",
                             f"project_update={post_data.repository.name}"]

        ansible_process = subprocess.run(
            ansible_args,
            check=True, capture_output=True, text=True)

    except subprocess.CalledProcessError as e:
        # If a CalledProcessError is raised, it means that either git
        # pull or ansible-playbook returned a non-zero exit status.
        # Log the error message and return from the function.
        app.logger.error(f'Error: {str(e)}')
        return


@app.route('/github', methods=["POST"])
def gh_webhook_listener():
    # Verify GitHub signature
    verify_signature(request.data, request.headers.get('X-Hub-Signature-256'))

    # Start ansible-playbook in a separate thread
    threading.Thread(target=run_ansible_playbook).start()

    return jsonify(
        {'message': 'Webhook received, running process'}), 200


if __name__ == '__main__':
    app.run(debug=False, port=5009)
