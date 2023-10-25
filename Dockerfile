FROM python:3.11-alpine
LABEL MAINTAINER KBase Developer

COPY ./ /kb/module/
ENV PYTHONPATH="/kb/module/lib:$PYTHONPATH"
WORKDIR /kb/module

RUN mkdir -p /kb/module/work && \
    chmod -R a+rw /kb/module && \
    # set executable bit on script files
    chmod a+x scripts/*.sh && \
    chmod a+x bin/*.sh && \
    # copy compile_report to the work directory
    cp compile_report.json work/ && \
    # update pip
    pip install --upgrade pip && \
    # install python modules one at a time so that all deps get resolved properly
    cat requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    cat requirements-test.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD []
