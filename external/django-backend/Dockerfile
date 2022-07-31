FROM python:3.8

# Copy all the sources to the container.
COPY . .

# Install uWSGI and other dependencies.
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir uwsgi && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt && \
    mkdir -p config

# Indicates that this container exposes its 80 port.
EXPOSE 80

# It takes a few steps to run the program, so write them in a shell script.
CMD ["/bin/sh", "start.sh"]
