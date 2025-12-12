FROM kalilinux/kali-rolling

ENV NVM_DIR=/root/.nvm
ENV NODE_VERSION=22

ENV N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
ENV N8N_RUNNERS_ENABLED=true
# Aggiorna il sistema e installa le dipendenze necessarie
RUN apt update -y

RUN apt install -y \
    curl \
    wget \
    git \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    sudo

RUN apt install -y \
     nmap \
     masscan \
     # Web application testing
     sqlmap \
     nikto \
     dirb \
     dirbuster \
     gobuster \
     wfuzz \
     burpsuite \
     # Exploitation frameworks
     metasploit-framework \
     # Password attacks
     hydra \
     john \
     hashcat \
     rdesktop \
     tnftp \
     ssh-audit \
     rpcbind \
     smtp-user-enum \
     telnet \
     mariadb-client \
     mariadb-server \
     crunch \
     cewl \
     # Wireless tools
     aircrack-ng \
     reaver \
     kismet \
     # Forensics
     binwalk \
     theharvester \
     sublist3r \
     # Reverse engineering
     radare2 \
     gdb \
     # Social engineering
     set \
     # Additional utilities
     netcat-traditional \
     socat \
     ncat \
     wireshark \
     tcpdump \
     enum4linux \
     smbclient \
     nbtscan \
     onesixtyone \
     whatweb \
     dnsenum \
     wafw00f \
     snmp \
     fierce \
     dnsrecon \
     dnsutils \
     whois \
     # Python tools
     python3-impacket \
     python3-scapy \
     # Additional pentesting tools
     responder \
     enum4linux-ng \
     seclists \
     wordlists

WORKDIR /home

# Copia lo script nel container
COPY server-shell.py /home/server-shell.py

RUN python3 -m venv .venv
RUN bash -c 'source .venv/bin/activate && pip install flask flask-cors pexpect'

# Installa Node.js via NVM e n8n
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && \
    . "$NVM_DIR/nvm.sh" && \
    nvm install $NODE_VERSION && \
    nvm use $NODE_VERSION && \
    npm install -g n8n

RUN mkdir -p /home/n8n_workflows
COPY workflows /home/n8n_workflows

RUN echo '#!/bin/bash' > /start.sh && \
    echo 'source /home/.venv/bin/activate' >> /start.sh && \
    echo 'python3 /home/server-shell.py &' >> /start.sh && \
    echo 'export NVM_DIR="$NVM_DIR"' >> /start.sh && \
    echo '. "$NVM_DIR/nvm.sh"' >> /start.sh && \
    echo 'nvm use $NODE_VERSION' >> /start.sh && \
    echo 'if [ -d "/home/n8n_workflows" ]; then' >> /start.sh && \
    echo '  echo "Importazione workflow da /home/n8n_workflows...";' >> /start.sh && \
    echo '  n8n import:workflow --separate --input=/home/n8n_workflows || true;' >> /start.sh && \
    echo 'fi' >> /start.sh && \
    echo 'exec n8n' >> /start.sh && \
    chmod +x /start.sh

# Comando di avvio
CMD ["/bin/bash", "/start.sh"]
