import pexpect
from flask import Flask, request, jsonify
import threading
import time
import os
import re

app = Flask(__name__)
shell_manager_lock = threading.Lock()
shell_instances = {}

# Regex per rimuovere sequenze ANSI (colori, stili, ecc.)
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def clean_output(output):
    # Rimuove sequenze ANSI
    cleaned = ANSI_ESCAPE.sub('', output)
    # Rimuove caratteri di controllo eccetto newline e tab
    cleaned = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', cleaned)
    # Sostituisce ritorni carrello e form feed
    return cleaned.replace('\r\n', '\n').replace('\r', '\n').replace('\f', '\n').strip()

def create_shell_session(shell_id):
    """Crea una nuova sessione shell per un ID specifico"""
    # Crea nuova sessione con prompt univoco
    session = pexpect.spawn(
        '/bin/bash --norc',
        encoding=None,
        timeout=15,
        env={
            'TERM': 'dumb',
            'PS1': f'SHELL_{shell_id}$ ',  # Prompt univoco per shell
            **os.environ
        }
    )
    session.expect_exact(f'SHELL_{shell_id}$ ')
    return session

def get_shell_instance(shell_id):
    """Ottiene o crea un'istanza shell con lock dedicato"""
    with shell_manager_lock:
        if shell_id not in shell_instances:
            # Crea nuova istanza se non esiste
            shell_instances[shell_id] = {
                'session': create_shell_session(shell_id),
                'lock': threading.Lock(),
                'last_used': time.time()
            }
        return shell_instances[shell_id]

def execute_command(shell_id, command):
    """Esegue un comando su una shell specifica"""
    instance = get_shell_instance(shell_id)
    
    with instance['lock']:
        session = instance['session']
        instance['last_used'] = time.time()
        
        # Riavvia la sessione se è chiusa o non attiva
        if session.closed or not session.isalive():
            session = create_shell_session(shell_id)
            instance['session'] = session

        if command in ('0x03', '\x03'):
            session.sendintr()
        else:
            session.sendline(command)
        
        try:
            session.expect_exact(f'SHELL_{shell_id}$ ')
            output = session.before
            if isinstance(output, bytes):
                output = output.decode('utf-8', errors='replace')
            status = "completed"
        except pexpect.TIMEOUT:
            output = session.before
            if isinstance(output, bytes):
                output = output.decode('utf-8', errors='replace')
            status = "waiting_input"
        except pexpect.EOF:
            output = session.before
            if isinstance(output, bytes):
                output = output.decode('utf-8', errors='replace')
            status = "restarted"
            # Ricrea la sessione dopo EOF
            session = create_shell_session(shell_id)
            instance['session'] = session
        
        return clean_output(output), status

@app.route('/execute/<shell_id>', methods=['POST'])
def execute_endpoint(shell_id):
    """Endpoint per eseguire comandi su una shell specifica"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({"error": "Empty command"}), 400

    try:
        output, status = execute_command(shell_id, command)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({
        "output": output,
        "status": status,
        "shell_id": shell_id,
        "timestamp": int(time.time())
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint per verificare lo stato del servizio"""
    with shell_manager_lock:
        count = len(shell_instances)
    return jsonify({
        "status": "active",
        "shell_instances": count
    })

@app.route('/reset/<shell_id>', methods=['DELETE'])
def reset_shell(shell_id):
    """Resetta una shell specifica"""
    try:
        with shell_manager_lock:
            if shell_id in shell_instances:
                instance = shell_instances[shell_id]
                if not instance['session'].closed:
                    instance['session'].close()
                del shell_instances[shell_id]
        return jsonify({"status": "reset", "shell_id": shell_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reset_all', methods=['DELETE'])
def reset_all_shells():
    """Resetta tutte le shell"""
    try:
        with shell_manager_lock:
            for shell_id, instance in list(shell_instances.items()):
                if not instance['session'].closed:
                    instance['session'].close()
                del shell_instances[shell_id]
        return jsonify({"status": "all shells reset"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
