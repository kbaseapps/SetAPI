FROM kbase/sdkbase2:python
LABEL MAINTAINER KBase Developer

COPY ./ /kb/module/
ENV PYTHONPATH="/kb/module/lib:$PYTHONPATH"
WORKDIR /kb/module

RUN pip install --upgrade pip && \
    # install python modules one at a time so that all deps get resolved properly
    cat requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    cat requirements-test.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    mkdir -p /kb/module/work && \
    chmod -R a+rw /kb/module && \
    # set executable bit on script files
    chmod a+x scripts/*.sh && \
    chmod a+x bin/*.sh && \
    # copy compile_report to the work directory
    cp compile_report.json work/

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD []
