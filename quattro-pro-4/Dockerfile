# Quattro Pro 4.0 for DOS under DOSBox-X, headless.
#
#   docker build -t qp4 quattro-pro-4/
#   docker run --rm -v "$PWD/sheets:/work" qp4 'Q IN.WQ!'
#
# The build downloads Quattro Pro from WinWorld, so the image contains
# copyrighted software: keep it local and never push it to a public registry.
FROM debian:trixie-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl 7zip python3 dosbox-x xvfb xauth imagemagick \
    && rm -rf /var/lib/apt/lists/*

COPY setup.sh mk.py /opt/qp/
# setup.sh runs the installer under DOSBox-X, which needs a display.
RUN cd /opt/qp && xvfb-run -a ./setup.sh /opt/qp/emu \
    && mv emu/c /opt/qp/c && rm -rf emu

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
WORKDIR /work
ENTRYPOINT ["entrypoint.sh"]
CMD ["Q"]
