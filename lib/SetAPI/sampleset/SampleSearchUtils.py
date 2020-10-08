import os
import requests
import json
import uuid

from installed_clients.DataFileUtilClient import DataFileUtil


_DEFAULT_QUERY_FIELDS = [
    'age_max', 'age_min', 'aodc', 'aquifer', 'area_name', 'average_water_level', 'biomass_carbon', 'biome',
    'boncat_activity', 'boring', 'boring_diameter', 'boring_refusal', 'city_township', 'classification',
    'collection_date', 'collection_date_end', 'collection_date_precision', 'collection_method',
    'collection_method_description', 'collection_time', 'collection_time_end', 'collector_chief_scientist',
    'collector_chief_scientist_address', 'condition', 'conductivity', 'continent', 'coordinate_precision?',
    'country', 'county', 'current_archive', 'current_archive_contact', 'dapi_cell_count', 'date', 'depth',
    'depth_in_core_max', 'depth_in_core_min', 'depth_scale', 'description', 'dna_picogreen_total',
    'drive_casing_end_depth', 'drive_casing_id', 'drive_casing_od', 'drive_casing_start_depth',
    'drive_casing_type', 'easting', 'elevation', 'elevation_end', 'elevation_start', 'env_package',
    'environmental_package', 'experiment_name', 'feature', 'field_name_informal_classification',
    'field_program_cruise', 'filter', 'fraction', 'fractures_cavities_waterbreaks', 'functional_area',
    'geological_age', 'geological_zone', 'ground_elevation', 'id', 'igsn', 'installation_method', 'latitude',
    'launch_id', 'launch_platform_name', 'leucine_activity_ngc_day_cell', 'locality', 'locality_description',
    'location_description', 'longitude', 'lower_seal_end_depth', 'lower_seal_start_depth', 'logwer_seal_type',
    'material', 'maturation_time', 'max_water_level', 'method', 'min_water_level', 'moisture', 'name',
    'name_of_physiographic_feature', 'navigation_type', 'northing', 'open', 'open_casing_depth',
    'open_casing_id', 'open_casing_od', 'open_casing_type', 'open_hole_depth', 'open_hole_diameter',
    'open_interval_diameter', 'open_interval_end_depth', 'open_interval_start_depth', 'organic_carbon',
    'original_archive', 'original_archive_contact', 'origination_or_plug_abandon', 'other_name', 'other_names',
    'packing_depth_end', 'packing_depth_start', 'packing_type', 'parent_id', 'parent_igsn', 'ph',
    'platform_name', 'platform_type', 'pore_water_extraction', 'primary_physiographic_feature', 'purpose',
    'recovery_factor', 'redox_potential_?', 'region', 'related_identifiers', 'relation_type', 'release_date',
    'replicate', 'rock_formation', 'sample_description', 'sample_name', 'sampleid',
    'screen_bottom_elevation', 'screen_end_depth', 'screen_start_depth', 'screen_top_elevation', 'screen_type',
    'screened', 'screened_interval', 'size', 'state_province', 'sub-object_type', 'temperature', 'time',
    'time_zone', 'timezone', 'top_of_casing_elevation', 'top_of_casing_stickup', 'top_of_fresh_bedrock',
    'top_of_weathered_bedrock', 'total_carbon', 'total_nitrogen', 'treatment', 'type_of_well',
    'upper_seal_end_depth', 'upper_seal_start_depth', 'upper_seal_type', 'vertical_datum', 'well',
    'well_casing_depth', 'well_casing_id', 'well_casing_od', 'well_casing_type', 'well_name', 'well_status','zone'
]

_DEFAULT_QUERY_FIELDS = [
    "state_province"
]

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
            shoulds = [
                {"match": {"all_sample_metadata_field": str(params['query'])}}
                # {"match": {"all_sample_metadata_field": params['query']}}  # {"value": params['query']}}}
            ]
            extra_must.append({"match": {"all_sample_metadata_field": str(params['query'])}})
            # extra_must.append({'bool': {'should': shoulds}})
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
            print(f'respone from query: {respj}')
        if respj.get('error'):
            raise Exception(f"Error from Search API with parameters\n{json.dumps(query_data)}\n Response body:\n{respj}")
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
            if sample_doc.get(field):
                sample_doc.pop(field)
        sample_doc['kbase_sample_id'] = sample_id.split('::')[1].split(":")[0]
        return sample_doc
