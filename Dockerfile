FROM kbase/sdkbase2:python
LABEL MAINTAINER KBase Developer

COPY ./ /kb/module/
ENV PYTHONPATH="/kb/module/lib:$PYTHONPATH"
WORKDIR /kb/module
# install python modules one at a time so that all deps get resolved properly
RUN pip install --upgrade pip && \
    cat requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    cat requirements-test.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    mkdir -p /kb/module/work && \
    chmod -R a+rw /kb/module && \
    cp compile_report.json work/ && \
    make set-executable

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD []
