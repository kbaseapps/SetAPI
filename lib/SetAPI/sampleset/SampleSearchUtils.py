import requests
import json
import uuid


class SamplesSearchUtils():

    def __init__(self, token, search_url):
        self.token = token
        self.search_url = search_url
        self.debug = False

    def _parse_inputs(self, params):
        # we sort by "name" by default
        sort_by = [("name", 1)]
        extra_must = []
        if params.get('sort_by'):
            sort_by = params['sort_by']
        if params.get('query'):
            # use default all_sample_metadata_field as specified in the index_runner spec
            query_data = {
                "multi_match": {
                    "fields": ["all_sample_metadata_field"],
                    "query": str(params['query']),
                    "operator": "or",
                    "type": "phrase_prefix"
                }
            }
            extra_must.append(query_data)
        start = params.get('start', 0)
        limit = params.get('limit', 10)

        return sort_by, extra_must, start, limit

    def sample_set_to_samples_info(self, params, aggs=None, track_total_hits=False):
        """
        params - input parameters for "sample_set_to_samples_info" function, see spec file for contents
        aggs - elasticsearch aggregation, see elasticsearch documentation for formatting
        track_total_hits - True/False - Whether to track the total number of hits past the elasticsearch limit
        """
        sample_set_ref = params['ref']
        sort_by, extra_must, start, limit = self._parse_inputs(params)

        (workspace_id, object_id, version) = sample_set_ref.split('/')
        # we use namespace 'WSVER' for versioned elasticsearch index.
        ss_id = f'WSVER::{workspace_id}:{object_id}:{version}'

        headers = {"Authorization": self.token}
        query_data = {
            "method": "search_objects",
            "params": {
                "query": {
                    "bool": {
                        "must": [{"term": {"sample_set_ids": ss_id}}] + extra_must
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
        if self.debug:
            print(f"queried {self.search_url} with data {json.dumps(query_data)}")
        if not resp.ok:
            raise Exception(f"Not able to complete search request against {self.search_url} "
                            f"with parameters: \n{json.dumps(query_data)} \nResponse body:\n{resp.text}")
        respj = resp.json()
        if self.debug:
            print(f'response from query: {respj}')
        if respj.get('error'):
            raise RuntimeError(f"Error from Search API with parameters\n{json.dumps(query_data)}\n Response body:\n{respj}")
        return self._process_sample_set_resp(respj['result'], start, query_data)

    def _process_sample_set_resp(self, resp, start, query):
        if resp.get('hits'):
            hits = resp['hits']
            return {
                "num_found": int(resp['count']),
                "start": start,
                "query": query,
                # this should handle empty results list of hits, also sort by feature_id
                "samples": [self._process_sample(h['doc'], h['id']) for h in hits]
            }
        # empty list in response for hits
        elif 'hits' in resp:
            return {
                "num_found": int(resp['count']),
                "start": start,
                "query": query,
                "samples": []
            }
        else:
            # only raise if no hits found at highest level.
            raise RuntimeError(f"no 'hits' with params {json.dumps(params)}\n in http response: {resp}")

    def _process_sample(self, sample_doc, sample_id):
        # remove fields that are not metadata fields.
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
            "sample_set_ids",
            "parent_id",
            "save_date"
        ]
        for field in remove_fields:
            if field in sample_doc:
                del sample_doc[field]
        sample_doc['kbase_sample_id'] = sample_id.split('::')[1].split(":")[0]
        return sample_doc
