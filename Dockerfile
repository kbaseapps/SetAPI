FROM kbase/kbase:sdkbase.latest
MAINTAINER KBase Developer
# -----------------------------------------

# Insert apt-get instructions here to install
# any required dependencies for your module.

# RUN apt-get update

# -----------------------------------------

RUN pip install --upgrade ndg-httpsclient

# update installed WS client (will now include get_objects2)
RUN mkdir -p /kb/module && \
    cd /kb/module && \
    git clone https://github.com/kbase/workspace_deluxe && \
    cd workspace_deluxe && \
    git checkout 837ad4c && \
    rm -rf /kb/deployment/lib/biokbase/workspace && \
    cp -vr lib/biokbase/workspace /kb/deployment/lib/biokbase/workspace


COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod 777 /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
