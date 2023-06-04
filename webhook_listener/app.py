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


def run_playbook(repo_name):
    ansible_args = [
        "/srv/hosting_infrastructure/venv/bin/ansible-playbook",
        "-c=local",
        "-u", "root",
        "-i", "/srv/hosting_infrastructure/ansible/inventory.yaml",
        "--extra-vars", f"env={ENVIRONMENT}"
    ]

    if repo_name == "hosting_infrastructure":
        ansible_args += ["--extra-vars", "install_type=full"]
    else:
        ansible_args += ["--extra-vars", "install_type=update",
                         "--extra-vars", f"project_update={repo_name}"]

    subprocess.run(ansible_args, check=True, capture_output=True, text=True)


def update_repository():
    repo_dir = f"{INSTALL_DIR}/hosting_infrastructure"
    subprocess.run(['git', 'fetch', '--depth', '1', 'origin', 'main'],
                   check=True, capture_output=True, text=True, cwd=repo_dir)
    subprocess.run(['git', 'reset', '--hard', 'FETCH_HEAD'],
                   check=True, capture_output=True, text=True, cwd=repo_dir)


def run_ansible_playbook():
    try:
        post_data = request.get_json()
        repo_name = post_data.get('repository', {}).get('name')
        if not repo_name:
            app.logger.error('Invalid JSON data')
            return

        # Update the repository
        update_repository()

        # Run the Ansible playbook
        run_playbook(repo_name)

    except (subprocess.CalledProcessError, KeyError) as e:
        app.logger.error(f'Error: {str(e)}')


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
