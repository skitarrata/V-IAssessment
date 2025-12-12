from flask import Flask, render_template_string, request, jsonify
import requests
import json
import re
import os
from urllib.parse import urlparse

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Assessment - Webhook Interface</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #000000;
            color: #ffffff;
            min-height: 100vh;
            line-height: 1.6;
        }

        .header {
            background-color: #000000;
            padding: 15px 0;
            border-bottom: 1px solid #333;
        }

        .nav {
            display: flex;
            align-items: center;
            justify-content: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #bf00ff;
        }

        .hero-section {
            background: linear-gradient(135deg, #bf00ff 0%, #8b00cc 100%);
            padding: 60px 20px;
            text-align: center;
        }

        .hero-title {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #ffffff;
        }

        .hero-subtitle {
            font-size: 20px;
            color: rgba(255, 255, 255, 0.9);
            max-width: 600px;
            margin: 0 auto;
        }

        .main-content {
            max-width: 1200px;
            margin: 80px auto;
            padding: 0 20px;
        }

        .webhook-card {
            background: linear-gradient(145deg, #1a1a1a, #2a2a2a);
            border-radius: 16px;
            padding: 50px;
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
            border: 2px solid #bf00ff;
            box-shadow: 0 20px 40px rgba(191, 0, 255, 0.15);
        }

        .webhook-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 6px;
            height: 100%;
            background: linear-gradient(to bottom, #bf00ff, #8b00cc);
        }

        .webhook-card::after {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #bf00ff, #8b00cc, #bf00ff);
            border-radius: 16px;
            z-index: -1;
            opacity: 0.3;
            animation: pulse 3s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.6; }
        }

        .section-label {
            color: #bf00ff;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 20px;
            position: relative;
        }

        .section-label::after {
            content: '';
            position: absolute;
            left: 0;
            bottom: -8px;
            width: 40px;
            height: 2px;
            background-color: #bf00ff;
        }

        .card-title {
            font-size: 36px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 30px;
            line-height: 1.2;
        }

        .card-description {
            font-size: 18px;
            color: #cccccc;
            margin-bottom: 40px;
            line-height: 1.6;
        }

        .form-group {
            margin-bottom: 30px;
        }

        .form-label {
            display: block;
            color: #ffffff;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
        }

        .form-input {
            width: 100%;
            padding: 18px 20px;
            background-color: #2a2a2a;
            border: 2px solid #333333;
            border-radius: 8px;
            color: #ffffff;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .form-input:focus {
            outline: none;
            border-color: #bf00ff;
            box-shadow: 0 0 0 3px rgba(191, 0, 255, 0.1);
        }

        .form-input::placeholder {
            color: #888888;
        }

        .submit-button {
            background: linear-gradient(135deg, #bf00ff, #8b00cc);
            color: #ffffff;
            border: none;
            padding: 18px 40px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }

        .submit-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(191, 0, 255, 0.3);
        }

        .submit-button:active {
            transform: translateY(0);
        }

        .submit-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .submit-button::after {
            content: '→';
            font-size: 18px;
            transition: transform 0.3s ease;
        }

        .submit-button:hover::after {
            transform: translateX(5px);
        }

        .loading {
            display: none;
            margin-left: 10px;
        }

        .loading.show {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #ffffff;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .status-message {
            margin-top: 30px;
            padding: 20px;
            border-radius: 8px;
            font-size: 16px;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
        }

        .status-message.show {
            opacity: 1;
            transform: translateY(0);
        }

        .status-message.success {
            background-color: rgba(191, 0, 255, 0.1);
            border: 1px solid #bf00ff;
            color: #bf00ff;
        }

        .status-message.error {
            background-color: rgba(255, 0, 100, 0.1);
            border: 1px solid #ff0064;
            color: #ff0064;
        }

        .downloads-section {
            margin-top: 40px;
            padding: 30px;
            background-color: #1a1a1a;
            border-radius: 12px;
            border: 2px solid #bf00ff;
            display: none;
        }

        .downloads-section.show {
            display: block;
            animation: fadeInUp 0.5s ease;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .downloads-title {
            font-size: 24px;
            font-weight: 700;
            color: #bf00ff;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .downloads-title::before {
            content: '📄';
            font-size: 20px;
        }

        .download-item {
            background-color: #2a2a2a;
            border: 1px solid #333333;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.3s ease;
        }

        .download-item:hover {
            border-color: #bf00ff;
            transform: translateY(-2px);
        }

        .download-info {
            flex: 1;
        }

        .download-name {
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 5px;
        }

        .download-url {
            font-size: 14px;
            color: #888888;
            word-break: break-all;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 400px;
        }

        .download-button {
            background: linear-gradient(135deg, #bf00ff, #8b00cc);
            color: #ffffff;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .download-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(191, 0, 255, 0.3);
        }

        .download-button::after {
            content: '⬇';
            font-size: 12px;
        }

        .info-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 60px;
        }

        .info-card {
            background-color: #1a1a1a;
            border-radius: 12px;
            padding: 40px;
            position: relative;
            overflow: hidden;
        }

        .info-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, #bf00ff, #8b00cc);
        }

        .info-card-title {
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 15px;
        }

        .info-card-text {
            color: #cccccc;
            font-size: 16px;
            line-height: 1.6;
        }

        /* Mobile Responsiveness */
        @media screen and (max-width: 768px) {
            .hero-title {
                font-size: 32px;
            }

            .hero-subtitle {
                font-size: 18px;
            }

            .webhook-card {
                padding: 30px 20px;
            }

            .card-title {
                font-size: 28px;
            }

            .card-description {
                font-size: 16px;
            }

            .info-cards {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .info-card {
                padding: 30px 20px;
            }

            .download-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 15px;
            }

            .download-button {
                align-self: flex-end;
            }
        }

        @media screen and (max-width: 480px) {
            .hero-section {
                padding: 40px 20px;
            }

            .hero-title {
                font-size: 24px;
            }

            .main-content {
                margin: 40px auto;
            }

            .webhook-card {
                padding: 25px 15px;
            }

            .card-title {
                font-size: 24px;
            }

            .downloads-section {
                padding: 20px 15px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav">
            <div class="logo">SecureTest</div>
        </nav>
    </header>

    <section class="hero-section">
        <h1 class="hero-title">Penetration Testing</h1>
        <p class="hero-subtitle">Valuta la sicurezza della tua infrastruttura con i nostri strumenti avanzati di assessment</p>
    </section>

    <main class="main-content">
        <div class="webhook-card">
            <div class="section-label">Security Assessment</div>
            <h2 class="card-title">Avvia scansione di sicurezza</h2>
            <p class="card-description">
                Inserisci l'indirizzo IP o il dominio del target da analizzare. Il nostro sistema avvierà 
                una valutazione completa della superficie di attacco e delle vulnerabilità potenziali.
            </p>

            <form id="securityForm">
                <div class="form-group">
                    <label class="form-label" for="target">Target IP/Dominio</label>
                    <input 
                        type="text" 
                        id="target" 
                        class="form-input" 
                        placeholder="es. 192.168.1.1 o example.com"
                        required
                    >
                </div>

                <button type="submit" class="submit-button" id="submitBtn">
                    Avvia Assessment
                    <div class="loading" id="loadingSpinner"></div>
                </button>
            </form>

            <div id="statusMessage" class="status-message"></div>
            
            <div id="downloadsSection" class="downloads-section">
                <div class="downloads-title">Report Disponibili</div>
                <div id="downloadsList"></div>
            </div>
        </div>

        <div class="info-cards">
            <div class="info-card">
                <div class="section-label">Automazione</div>
                <h3 class="info-card-title">Orchestratore Intelligente</h3>
                <p class="info-card-text">
                    Il nostro orchestratore AI coordina automaticamente agenti specializzati 
                    per ogni fase del penetration testing, garantendo un approccio sistematico e completo.
                </p>
            </div>

            <div class="info-card">
                <div class="section-label">Multi-Agent</div>
                <h3 class="info-card-title">Agenti Specializzati</h3>
                <p class="info-card-text">
                    Ogni agente AI è specializzato in specifiche fasi di testing: 
                    reconnaissance, network scan, enumeration, vulnerability scan, exploitation e post exploitation.
                </p>
            </div>

            <div class="info-card">
                <div class="section-label">Reporting</div>
                <h3 class="info-card-title">Report Dettagliati</h3>
                <p class="info-card-text">
                    Ricevi report completi con analisi dettagliate, prioritizzazione dei rischi 
                    e raccomandazioni per la remediation generate dall'orchestratore.
                </p>
            </div>

            <div class="info-card">
                <div class="section-label">Conformità</div>
                <h3 class="info-card-title">Standard Internazionali</h3>
                <p class="info-card-text">
                    I nostri test seguono gli standard OWASP, NIST e altre best practice 
                    riconosciute nel settore della cybersecurity attraverso workflow automatizzati.
                </p>
            </div>
        </div>
    </main>

    <script>
        document.getElementById('securityForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const target = document.getElementById('target').value.trim();
            const statusMessage = document.getElementById('statusMessage');
            const submitBtn = document.getElementById('submitBtn');
            const loadingSpinner = document.getElementById('loadingSpinner');
            const downloadsSection = document.getElementById('downloadsSection');
            
            if (!target) {
                showStatus('Inserisci un target valido per procedere', 'error');
                return;
            }

            // Validazione formato IP/dominio
            const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
            const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/;
            
            if (!ipRegex.test(target) && !domainRegex.test(target)) {
                showStatus('Formato non valido. Inserisci un IP valido (es. 192.168.1.1) o un dominio (es. example.com)', 'error');
                return;
            }

            // Mostra loading
            submitBtn.disabled = true;
            loadingSpinner.classList.add('show');
            downloadsSection.classList.remove('show');
            showStatus('Invio richiesta al sistema di scanning...', 'success');

            try {
                const response = await fetch('/scan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ target: target })
                });

                const data = await response.json();

                if (response.ok) {
                    if (data.downloads && data.downloads.length > 0) {
                        showStatus('Scansione completata! Report disponibili per il download.', 'success');
                        displayDownloads(data.downloads);
                    } else {
                        showStatus('Scansione completata, ma nessun report disponibile.', 'success');
                    }
                } else {
                    showStatus(data.error || 'Errore durante la scansione', 'error');
                }
            } catch (error) {
                showStatus('Errore di connessione: ' + error.message, 'error');
            } finally {
                submitBtn.disabled = false;
                loadingSpinner.classList.remove('show');
            }
        });

        function showStatus(message, type) {
            const statusElement = document.getElementById('statusMessage');
            statusElement.textContent = message;
            statusElement.className = `status-message ${type} show`;
            
            setTimeout(() => {
                if (type === 'error') {
                    statusElement.classList.remove('show');
                }
            }, 6000);
        }

        function displayDownloads(downloads) {
            const downloadsSection = document.getElementById('downloadsSection');
            const downloadsList = document.getElementById('downloadsList');
            
            downloadsList.innerHTML = '';
            
            downloads.forEach((download, index) => {
                const downloadItem = document.createElement('div');
                downloadItem.className = 'download-item';
                
                const fileName = extractFileName(download.url) || `Report_${index + 1}.pdf`;
                
                downloadItem.innerHTML = `
                    <div class="download-info">
                        <div class="download-name">${fileName}</div>
                        <div class="download-url" title="${download.url}">${download.url}</div>
                    </div>
                    <a href="${download.url}" class="download-button" target="_blank">
                        Scarica
                    </a>
                `;
                
                downloadsList.appendChild(downloadItem);
            });
            
            downloadsSection.classList.add('show');
        }

        function extractFileName(url) {
            try {
                const urlObj = new URL(url);
                const pathParts = urlObj.pathname.split('/');
                return pathParts[pathParts.length - 1] || null;
            } catch (error) {
                return null;
            }
        }

        // Smooth scroll per eventuali link interni
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });
    </script>
</body>
</html>
"""

def extract_urls_from_response(response_text):
    """
    Estrae URL da una risposta che può essere JSON o plain text
    """
    urls = []
    
    # Prima prova a parsare come JSON
    try:
        data = json.loads(response_text)
        
        # Se è un dizionario, cerca le chiavi comuni per URL
        if isinstance(data, dict):
            url_keys = ['url', 'download_url', 'pdf_url', 'file_url', 'urls', 'downloads']
            for key in url_keys:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and value.startswith('http'):
                        urls.append(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and item.startswith('http'):
                                urls.append(item)
                            elif isinstance(item, dict):
                                # Se è un oggetto, cerca URL dentro
                                for subkey in ['url', 'download_url', 'pdf_url', 'file_url']:
                                    if subkey in item and isinstance(item[subkey], str) and item[subkey].startswith('http'):
                                        urls.append(item[subkey])
        
        # Se è una lista, controlla ogni elemento
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str) and item.startswith('http'):
                    urls.append(item)
                elif isinstance(item, dict):
                    for key in ['url', 'download_url', 'pdf_url', 'file_url']:
                        if key in item and isinstance(item[key], str) and item[key].startswith('http'):
                            urls.append(item[key])
    
    except json.JSONDecodeError:
        # Se non è JSON, cerca semplicemente qualsiasi cosa che inizia con http
        # Dividi per spazi e cerca le stringhe che iniziano con http
        words = response_text.split()
        for word in words:
            if word.startswith('http'):
                # Rimuovi eventuali caratteri finali non validi
                clean_url = word.rstrip('.,;:)"\'')
                urls.append(clean_url)
    
    # Rimuovi duplicati
    urls = list(set(urls))
    
    # Filtra solo URL validi
    valid_urls = []
    for url in urls:
        try:
            parsed = urlparse(url)
            if parsed.scheme in ['http', 'https'] and parsed.netloc:
                valid_urls.append(url)
        except:
            continue
    
    return valid_urls

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()
        target = data.get('target')
        
        if not target:
            return jsonify({'error': 'Target mancante'}), 400
        
        # Invia richiesta al webhook
        hostname = os.getenv("HOSTNAME")
        webhook_url = f'https://{hostname}/webhook/scan'
        webhook_data = {'target': target}
        
        try:
            response = requests.post(webhook_url, json=webhook_data)
            
            if response.status_code == 200:
                # Estrae URL dalla risposta
                urls = extract_urls_from_response(response.text)
                
                if urls:
                    downloads = [{'url': url} for url in urls]
                    return jsonify({
                        'success': True,
                        'message': 'Scansione completata',
                        'downloads': downloads
                    })
                else:
                    return jsonify({
                        'success': True,
                        'message': 'Scansione completata ma nessun file disponibile',
                        'downloads': []
                    })
            else:
                return jsonify({
                    'error': f'Errore dal webhook: {response.status_code}'
                }), 500
                
        except requests.exceptions.RequestException as e:
            return jsonify({
                'error': f'Errore di connessione al webhook: {str(e)}'
            }), 500
    
    except Exception as e:
        return jsonify({
            'error': f'Errore interno: {str(e)}'
        }), 500

if __name__ == '__main__':
    host = os.getenv("HOSTNAME")
    print("🚀 Avviando server Security Assessment...")
    print("📡 Server disponibile su: http://localhost:8080")
    print(f"🔗 Webhook endpoint: https://{host}/webhook/scan")
    print("⚡ Pronto per ricevere richieste di scansione!")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
