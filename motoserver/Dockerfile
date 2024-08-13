FROM motoserver/moto:5.0.12

# Install AWS CLI
RUN apt-get install -y awscli && rm -rf /var/lib/apt/lists/*

COPY main.py ./
ENTRYPOINT python3 -m main
