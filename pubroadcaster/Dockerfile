FROM arm32v7/python:3
ADD . /
RUN pip install -U discord.py
RUN pip install -U tabulate
CMD [ "python", "./__init__.py"]