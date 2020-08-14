import os
import requests
import json
import uuid

from installed_clients.DataFileUtilClient import DataFileUtil

class SamplesSearchUtils():

    def __init__(self, token, search_url):
        self.token = token
        self.search_url = search_url
        self.debug = False

    def _parse_inputs(self, params):
        if params.get('sort_by'):
            sort_by = params['sort_by']
        else:
            # we sort by "name" by default
            sort_by = [("name", 1)]
        if params.get('query'):
            # get fields to search on
            fields = params.get("query_fields",
                # need to sort out how to get all relevant fields
                ["name", "description", "location"]
            )
            extra_must = [
                {"match": {field: params['query']}}
                for field in fields
            ]
        else:
            extra_must = []
        start = params.get('start', 0)
        limit = params.get('limit', 10)

        return sort_by, extra_must, start, limit

    def sample_set_to_samples_info(self, params, aggs=None, track_total_hits=False):
        """
        """
        sample_set_ref = params['ref']
        sort_by, extra_must, start, limit = self._parse_inputs(params)

        (workspace_id, object_id, version) = sample_set_ref.split('/')
        # we use namespace 'WSVER' for versioned elasticsearch index.
        ss_id = f'WS::{workspace_id}:{object_id}'

        headers = {"Authorization": self.token}
        query_data = {
            "method": "search_objects",
            "params": {
                "query": {
                    "bool": {
                        "must": [{"term": {"parent_id": ss_id}}] + extra_must
                    }
                },
                "indexes": ["sample"],
                "from": start,
                "size": limit,
                "sort": [{s[0]: {"order": "asc" if s[1] else "desc"}} for s in sort_by]
            },
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4())
        }
        if aggs:
            query_data['params']['aggs'] = aggs
        if track_total_hits:
            query_data['params']['track_total_hits'] = True
        if self.debug:
            print(f"querying {self.search_url}, with params: {json.dumps(query_data)}")
        resp = requests.post(self.search_url, headers=headers, data=json.dumps(query_data))
        if not resp.ok:
            raise Exception(f"Not able to complete search request against {self.search_url} "
                            f"with parameters: \n{json.dumps(query_data)} \nResponse body:\n{resp.text}")
        respj = resp.json()
        if respj.get('error'):
            raise Exception(f"Error from Search API with parameters\n{json.dumps(query_data)}\n response:\n{respj}")
        return self._process_sample_set_resp(respj['result'], start, query_data)

    def _process_sample_set_resp(self, resp, start, query):
        """
        """
        if resp.get('hits'):
            hits = resp['hits']
            return {
                "num_found": int(resp['count']),
                "start": start,
                # "query": query,
                # this should handle empty results list of hits, also sort by feature_id
                "samples": [self._process_sample(h['doc'], h['id']) for h in hits]
            }
        # empty list in reponse for hits
        elif 'hits' in resp:
            return {
                "num_found": int(resp['count']),
                "start": start,
                # "query": query,
                "samples": []
            }
        else:
            # only raise if no hits found at highest level.
            raise RuntimeError(f"no 'hits' with params {json.dumps(params)}\n in http response: {resp}")

    def _process_sample(self, sample_doc, sample_id):
        # return as is
        remove_fields = [
            "node_id",
            "creator", 
            "access_group",
            "obj_name",
            "shared_users",
            "timestamp",
            "creation_date",
            "is_public",
            "version",
            "obj_id",
            "copied",
            "tags",
            "obj_type_version",
            "obj_type_module",
            "obj_type_name",
            "parent_id",
            "save_date"
        ]
        for field in remove_fields:
            if sample_doc.get(field):
                sample_doc.pop(field)
        sample_doc['kbase_sample_id'] = sample_id.split('::')[1].split(":")[0]
        return sample_doc
