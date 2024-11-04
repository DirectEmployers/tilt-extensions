FROM motoserver/moto:5.0.19

ENV AWS_ACCESS_KEY_ID="test" \
    AWS_SECRET_ACCESS_KEY="test" \
    AWS_DEFAULT_REGION="us-east-1" \
    AWS_ENDPOINT_URL="http://localhost:3000" \
    AWS_DEFAULT_OUTPUT="json" \
    AWS_PAGER=""

RUN pip --no-cache-dir install awscli-local[ver1]

COPY main.py ./
ENTRYPOINT python3 -m main
