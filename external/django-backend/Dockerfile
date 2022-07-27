FROM python:3.8

COPY . .

RUN pip install uwsgi && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 80

CMD ["/bin/sh", "start.sh"]
