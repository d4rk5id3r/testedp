FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY readflag.c .
RUN gcc -o /readflag -static readflag.c && \
    chown root:root /readflag && \
    chmod +s /readflag && \
    rm readflag.c

RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app

COPY --chown=root:root pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml

# Cache embedding model
ENV HOME=/home/appuser
RUN mkdir -p /home/appuser/.cache/chroma/onnx_models && \
    python3 -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()(['test'])" && \
    chown -R root:root /home/appuser/.cache && \
    chmod -R 755 /home/appuser/.cache

COPY --chown=root:root flag.txt /flag.txt
RUN chmod 400 /flag.txt

COPY --chown=root:root src/*.py ./
COPY --chown=root:root src/static ./static

RUN mkdir -p /chroma-data /docs && \
    chown appuser:appuser /chroma-data /docs && \
    chmod 777 /chroma-data /docs

RUN chown -R root:root /app && \
    chmod 444 /app/pyproject.toml /app/*.py && \
    chmod 555 /app /app/static

USER appuser
EXPOSE 8000
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
