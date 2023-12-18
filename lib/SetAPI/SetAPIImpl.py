# -*- coding: utf-8 -*-
# BEGIN_HEADER

from installed_clients.WorkspaceClient import Workspace

from SetAPI.generic.constants import (
    ASSEMBLY,
    DIFFERENTIAL_EXPRESSION_MATRIX,
    EXPRESSION,
    FEATURE_SET,
    GENOME,
    READS,
    READS_ALIGNMENT,
)
from SetAPI.generic.GenericSetNavigator import GenericSetNavigator
from SetAPI.generic.SetInterfaceV1 import SetInterfaceV1
from SetAPI.sampleset.SampleSearchUtils import SamplesSearchUtils
from SetAPI.sampleset.SampleSetInterface import SampleSetInterface

# END_HEADER


class SetAPI:
    '''
    Module Name:
    SetAPI

    Module Description:

    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.3.5"
    GIT_URL = "https://github.com/kbaseapps/SetAPI.git"
    GIT_COMMIT_HASH = "a1f7531cabcb68639d5af6b26f1e69f2023665ac"

    # BEGIN_CLASS_HEADER
    # END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        # BEGIN_CONSTRUCTOR
        self.workspace_url = config["workspace-url"]
        self.service_wizard_url = config["service-wizard"]
        if config.get("search-url"):
            self.search_url = config.get("search-url")
        else:
            self.search_url = config.get("kbase-endpoint") + "/searchapi2/rpc"
        # END_CONSTRUCTOR
        pass


    def get_differential_expression_matrix_set_v1(self, ctx, params):
        """
        :param params: instance of type "GetSetV1Params" -> structure:
           parameter "ref" of String, parameter "include_item_info" of type
           "boolean" (A boolean. 0 = false, 1 = true.), parameter
           "include_set_item_ref_paths" of type "boolean" (A boolean. 0 =
           false, 1 = true.), parameter "ref_path_to_set" of list of String
        :returns: instance of type
           "GetDifferentialExpressionMatrixSetV1Result" (ref - workspace
           reference to DifferentialExpressionMatrixSet object.
           include_item_info - 1 or 0, if 1 additionally provides workspace
           info (with metadata) for each DifferentialExpressionMatrix object
           in the Set include_set_item_ref_paths - 1 or 0, if 1, additionally
           provides ref_path for each item in the set. The ref_path returned
           for each item is either ref_path_to_set;item_ref  (if
           ref_path_to_set is given) or set_ref;item_ref  (if ref_path_to_set
           is not given)) -> structure: parameter "data" of type
           "DifferentialExpressionMatrixSet" (When building a
           DifferentialExpressionMatrixSet, all
           DifferentialExpressionMatrices must be built against the same
           genome. This is not part of the object type, but enforced during a
           call to save_differential_expression_matrix_set_v1. @meta ws
           description as description @meta ws length(items) as item_count)
           -> structure: parameter "description" of String, parameter "items"
           of list of type "DifferentialExpressionMatrixSetItem" (When saving
           a DifferentialExpressionMatrixSet, only 'ref' is required. You
           should never set 'info'.  'info' is provided optionally when
           fetching the DifferentialExpressionMatrixSet. ref_path is
           optionally returned by get_differential_expression_matrix_set_v1()
           when its input parameter 'include_set_item_ref_paths' is set to
           1.) -> structure: parameter "ref" of type "ws_diffexpmatrix_id"
           (The workspace id for a FeatureSet data object. @id ws
           KBaseFeatureValues.DifferentialExpressionMatrix
           KBaseMatrices.DifferentialExpressionMatrix;), parameter "ref_path"
           of type "ws_diffexpmatrix_id" (The workspace id for a FeatureSet
           data object. @id ws
           KBaseFeatureValues.DifferentialExpressionMatrix
           KBaseMatrices.DifferentialExpressionMatrix;), parameter "label" of
           String, parameter "info" of type "object_info" (Information about
           an object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String, parameter "info" of
           type "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_differential_expression_matrix_set_v1
        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.get_set(params)

        # END get_differential_expression_matrix_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_differential_expression_matrix_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def save_differential_expression_matrix_set_v1(self, ctx, params):
        """
        :param params: instance of type
           "SaveDifferentialExpressionMatrixSetV1Params" (workspace_name or
           workspace_id - alternative options defining target workspace,
           output_object_name - workspace object name (this parameter is used
           together with one of workspace params from above)) -> structure:
           parameter "workspace" of String, parameter "output_object_name" of
           String, parameter "data" of type "DifferentialExpressionMatrixSet"
           (When building a DifferentialExpressionMatrixSet, all
           DifferentialExpressionMatrices must be built against the same
           genome. This is not part of the object type, but enforced during a
           call to save_differential_expression_matrix_set_v1. @meta ws
           description as description @meta ws length(items) as item_count)
           -> structure: parameter "description" of String, parameter "items"
           of list of type "DifferentialExpressionMatrixSetItem" (When saving
           a DifferentialExpressionMatrixSet, only 'ref' is required. You
           should never set 'info'.  'info' is provided optionally when
           fetching the DifferentialExpressionMatrixSet. ref_path is
           optionally returned by get_differential_expression_matrix_set_v1()
           when its input parameter 'include_set_item_ref_paths' is set to
           1.) -> structure: parameter "ref" of type "ws_diffexpmatrix_id"
           (The workspace id for a FeatureSet data object. @id ws
           KBaseFeatureValues.DifferentialExpressionMatrix
           KBaseMatrices.DifferentialExpressionMatrix;), parameter "ref_path"
           of type "ws_diffexpmatrix_id" (The workspace id for a FeatureSet
           data object. @id ws
           KBaseFeatureValues.DifferentialExpressionMatrix
           KBaseMatrices.DifferentialExpressionMatrix;), parameter "label" of
           String, parameter "info" of type "object_info" (Information about
           an object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        :returns: instance of type "SaveSetV1Result" -> structure: parameter
           "set_ref" of String, parameter "set_info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN save_differential_expression_matrix_set_v1
        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.save_set(
            DIFFERENTIAL_EXPRESSION_MATRIX, ctx["provenance"], params
        )
        # END save_differential_expression_matrix_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method save_differential_expression_matrix_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def get_feature_set_set_v1(self, ctx, params):
        """
        :param params: instance of type "GetSetV1Params" -> structure:
           parameter "ref" of String, parameter "include_item_info" of type
           "boolean" (A boolean. 0 = false, 1 = true.), parameter
           "include_set_item_ref_paths" of type "boolean" (A boolean. 0 =
           false, 1 = true.), parameter "ref_path_to_set" of list of String
        :returns: instance of type "GetFeatureSetSetV1Result" (ref -
           workspace reference to FeatureSetSet object. include_item_info - 1
           or 0, if 1 additionally provides workspace info (with metadata)
           for each FeatureSet object in the Set include_set_item_ref_paths -
           1 or 0, if 1, additionally provides ref_path for each item in the
           set. The ref_path returned for each item is either
           ref_path_to_set;item_ref  (if ref_path_to_set is given) or
           set_ref;item_ref  (if ref_path_to_set is not given)) -> structure:
           parameter "data" of type "FeatureSetSet" (When building a
           FeatureSetSet, all FeatureSets must be aligned against the same
           genome. This is not part of the object type, but enforced during a
           call to save_feature_set_set_v1. @meta ws description as
           description @meta ws length(items) as item_count) -> structure:
           parameter "description" of String, parameter "items" of list of
           type "FeatureSetSetItem" (When saving a FeatureSetSet, only 'ref'
           is required. You should never set 'info'.  'info' is provided
           optionally when fetching the FeatureSetSet. ref_path is optionally
           returned by get_feature_set_set_v1() when its input parameter
           'include_set_item_ref_paths' is set to 1.) -> structure: parameter
           "ref" of type "ws_feature_set_id" (The workspace id for a
           FeatureSet data object. @id ws KBaseCollections.FeatureSet),
           parameter "ref_path" of type "ws_feature_set_id" (The workspace id
           for a FeatureSet data object. @id ws KBaseCollections.FeatureSet),
           parameter "label" of String, parameter "info" of type
           "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String, parameter "info" of type "object_info" (Information about
           an object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_feature_set_set_v1
        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.get_set(params)
        # END get_feature_set_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_feature_set_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def save_feature_set_set_v1(self, ctx, params):
        """
        :param params: instance of type "SaveFeatureSetSetV1Params"
           (workspace_name or workspace_id - alternative options defining
           target workspace, output_object_name - workspace object name (this
           parameter is used together with one of workspace params from
           above)) -> structure: parameter "workspace" of String, parameter
           "output_object_name" of String, parameter "data" of type
           "FeatureSetSet" (When building a FeatureSetSet, all FeatureSets
           must be aligned against the same genome. This is not part of the
           object type, but enforced during a call to
           save_feature_set_set_v1. @meta ws description as description @meta
           ws length(items) as item_count) -> structure: parameter
           "description" of String, parameter "items" of list of type
           "FeatureSetSetItem" (When saving a FeatureSetSet, only 'ref' is
           required. You should never set 'info'.  'info' is provided
           optionally when fetching the FeatureSetSet. ref_path is optionally
           returned by get_feature_set_set_v1() when its input parameter
           'include_set_item_ref_paths' is set to 1.) -> structure: parameter
           "ref" of type "ws_feature_set_id" (The workspace id for a
           FeatureSet data object. @id ws KBaseCollections.FeatureSet),
           parameter "ref_path" of type "ws_feature_set_id" (The workspace id
           for a FeatureSet data object. @id ws KBaseCollections.FeatureSet),
           parameter "label" of String, parameter "info" of type
           "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String
        :returns: instance of type "SaveSetV1Result" -> structure: parameter
           "set_ref" of String, parameter "set_info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN save_feature_set_set_v1
        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.save_set(FEATURE_SET, ctx["provenance"], params)
        # END save_feature_set_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method save_feature_set_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def get_expression_set_v1(self, ctx, params):
        """
        :param params: instance of type "GetSetV1Params" -> structure:
           parameter "ref" of String, parameter "include_item_info" of type
           "boolean" (A boolean. 0 = false, 1 = true.), parameter
           "include_set_item_ref_paths" of type "boolean" (A boolean. 0 =
           false, 1 = true.), parameter "ref_path_to_set" of list of String
        :returns: instance of type "GetExpressionSetV1Result" (ref -
           workspace reference to ExpressionSet object. include_item_info - 1
           or 0, if 1 additionally provides workspace info (with metadata)
           for each Expression object in the Set include_set_item_ref_paths -
           1 or 0, if 1, additionally provides ref_path for each item in the
           set. The ref_path returned for each item is either
           ref_path_to_set;item_ref  (if ref_path_to_set is given) or
           set_ref;item_ref  (if ref_path_to_set is not given)) -> structure:
           parameter "data" of type "ExpressionSet" (When building a
           ExpressionSet, all Expression objects must be aligned against the
           same genome. This is not part of the object type, but enforced
           during a call to save_expression_set_v1. @meta ws description as
           description @meta ws length(items) as item_count) -> structure:
           parameter "description" of String, parameter "items" of list of
           type "ExpressionSetItem" (When saving a ExpressionSet, only 'ref'
           is required. You should never set 'info'.  'info' is provided
           optionally when fetching the ExpressionSet. ref_path is optionally
           returned by get_expression_set_v1() when its input parameter
           'include_set_item_ref_paths' is set to 1.) -> structure: parameter
           "ref" of type "ws_expression_id" (The workspace id for a
           ReadsAlignment data object. @id ws KBaseRNASeq.RNASeqExpression),
           parameter "ref_path" of type "ws_expression_id" (The workspace id
           for a ReadsAlignment data object. @id ws
           KBaseRNASeq.RNASeqExpression), parameter "label" of String,
           parameter "data_attachments" of list of type "DataAttachment" ->
           structure: parameter "name" of String, parameter "ref" of type
           "ws_obj_id" (The workspace ID for a any data object. @id ws),
           parameter "info" of type "object_info" (Information about an
           object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String, parameter "info" of
           type "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_expression_set_v1

        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.get_set(params)

        # END get_expression_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_expression_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def save_expression_set_v1(self, ctx, params):
        """
        :param params: instance of type "SaveExpressionSetV1Params"
           (workspace_name or workspace_id - alternative options defining
           target workspace, output_object_name - workspace object name (this
           parameter is used together with one of workspace params from
           above)) -> structure: parameter "workspace" of String, parameter
           "output_object_name" of String, parameter "data" of type
           "ExpressionSet" (When building a ExpressionSet, all Expression
           objects must be aligned against the same genome. This is not part
           of the object type, but enforced during a call to
           save_expression_set_v1. @meta ws description as description @meta
           ws length(items) as item_count) -> structure: parameter
           "description" of String, parameter "items" of list of type
           "ExpressionSetItem" (When saving a ExpressionSet, only 'ref' is
           required. You should never set 'info'.  'info' is provided
           optionally when fetching the ExpressionSet. ref_path is optionally
           returned by get_expression_set_v1() when its input parameter
           'include_set_item_ref_paths' is set to 1.) -> structure: parameter
           "ref" of type "ws_expression_id" (The workspace id for a
           ReadsAlignment data object. @id ws KBaseRNASeq.RNASeqExpression),
           parameter "ref_path" of type "ws_expression_id" (The workspace id
           for a ReadsAlignment data object. @id ws
           KBaseRNASeq.RNASeqExpression), parameter "label" of String,
           parameter "data_attachments" of list of type "DataAttachment" ->
           structure: parameter "name" of String, parameter "ref" of type
           "ws_obj_id" (The workspace ID for a any data object. @id ws),
           parameter "info" of type "object_info" (Information about an
           object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        :returns: instance of type "SaveSetV1Result" -> structure: parameter
           "set_ref" of String, parameter "set_info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN save_expression_set_v1

        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.save_set(EXPRESSION, ctx["provenance"], params)

        # END save_expression_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method save_expression_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def get_reads_alignment_set_v1(self, ctx, params):
        """
        :param params: instance of type "GetSetV1Params" -> structure:
           parameter "ref" of String, parameter "include_item_info" of type
           "boolean" (A boolean. 0 = false, 1 = true.), parameter
           "include_set_item_ref_paths" of type "boolean" (A boolean. 0 =
           false, 1 = true.), parameter "ref_path_to_set" of list of String
        :returns: instance of type "GetReadsAlignmentSetV1Result" (ref -
           workspace reference to ReadsAlignmentSet object. include_item_info
           - 1 or 0, if 1 additionally provides workspace info (with
           metadata) for each ReadsAlignment object in the Set
           include_set_item_ref_paths - 1 or 0, if 1, additionally provides
           ref_path for each item in the set. The ref_path returned for each
           item is either ref_path_to_set;item_ref  (if ref_path_to_set is
           given) or set_ref;item_ref  (if ref_path_to_set is not given)) ->
           structure: parameter "data" of type "ReadsAlignmentSet" (When
           building a ReadsAlignmentSet, all ReadsAlignments must be aligned
           against the same genome. This is not part of the object type, but
           enforced during a call to save_reads_alignment_set_v1. @meta ws
           description as description @meta ws length(items) as item_count)
           -> structure: parameter "description" of String, parameter "items"
           of list of type "ReadsAlignmentSetItem" (When saving a
           ReadsAlignmentSet, only 'ref' is required. You should never set
           'info'.  'info' is provided optionally when fetching the
           ReadsAlignmentSet. ref_path is optionally returned by
           get_reads_alignment_set_v1() when its input parameter
           'include_set_item_ref_paths' is set to 1.) -> structure: parameter
           "ref" of type "ws_reads_align_id" (The workspace id for a
           ReadsAlignment data object. @id ws KBaseRNASeq.RNASeqAlignment),
           parameter "ref_path" of type "ws_reads_align_id" (The workspace id
           for a ReadsAlignment data object. @id ws
           KBaseRNASeq.RNASeqAlignment), parameter "label" of String,
           parameter "info" of type "object_info" (Information about an
           object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String, parameter
           "data_attachments" of list of type "DataAttachment" -> structure:
           parameter "name" of String, parameter "ref" of type "ws_obj_id"
           (The workspace ID for a any data object. @id ws), parameter "info"
           of type "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_reads_alignment_set_v1

        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.get_set(params)

        # END get_reads_alignment_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_reads_alignment_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def save_reads_alignment_set_v1(self, ctx, params):
        """
        :param params: instance of type "SaveReadsAlignmentSetV1Params"
           (workspace_name or workspace_id - alternative options defining
           target workspace, output_object_name - workspace object name (this
           parameter is used together with one of workspace params from
           above)) -> structure: parameter "workspace" of String, parameter
           "output_object_name" of String, parameter "data" of type
           "ReadsAlignmentSet" (When building a ReadsAlignmentSet, all
           ReadsAlignments must be aligned against the same genome. This is
           not part of the object type, but enforced during a call to
           save_reads_alignment_set_v1. @meta ws description as description
           @meta ws length(items) as item_count) -> structure: parameter
           "description" of String, parameter "items" of list of type
           "ReadsAlignmentSetItem" (When saving a ReadsAlignmentSet, only
           'ref' is required. You should never set 'info'.  'info' is
           provided optionally when fetching the ReadsAlignmentSet. ref_path
           is optionally returned by get_reads_alignment_set_v1() when its
           input parameter 'include_set_item_ref_paths' is set to 1.) ->
           structure: parameter "ref" of type "ws_reads_align_id" (The
           workspace id for a ReadsAlignment data object. @id ws
           KBaseRNASeq.RNASeqAlignment), parameter "ref_path" of type
           "ws_reads_align_id" (The workspace id for a ReadsAlignment data
           object. @id ws KBaseRNASeq.RNASeqAlignment), parameter "label" of
           String, parameter "info" of type "object_info" (Information about
           an object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String, parameter
           "data_attachments" of list of type "DataAttachment" -> structure:
           parameter "name" of String, parameter "ref" of type "ws_obj_id"
           (The workspace ID for a any data object. @id ws)
        :returns: instance of type "SaveSetV1Result" -> structure: parameter
           "set_ref" of String, parameter "set_info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN save_reads_alignment_set_v1
        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.save_set(READS_ALIGNMENT, ctx["provenance"], params)
        # END save_reads_alignment_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method save_reads_alignment_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def get_reads_set_v1(self, ctx, params):
        """
        :param params: instance of type "GetSetV1Params" -> structure:
           parameter "ref" of String, parameter "include_item_info" of type
           "boolean" (A boolean. 0 = false, 1 = true.), parameter
           "include_set_item_ref_paths" of type "boolean" (A boolean. 0 =
           false, 1 = true.), parameter "ref_path_to_set" of list of String
        :returns: instance of type "GetReadsSetV1Result" (ref - workspace
           reference to ReadsGroup object. include_item_info - 1 or 0, if 1
           additionally provides workspace info (with metadata) for each
           Reads object in the Set include_set_item_ref_paths - 1 or 0, if 1,
           additionally provides ref_path for each item in the set. The
           ref_path returned for each item is either ref_path_to_set;item_ref
           (if ref_path_to_set is given) or set_ref;item_ref  (if
           ref_path_to_set is not given)) -> structure: parameter "data" of
           type "ReadsSet" (@meta ws description as description @meta ws
           length(items) as item_count) -> structure: parameter "description"
           of String, parameter "items" of list of type "ReadsSetItem" (When
           saving a ReadsSet, only 'ref' is required.  You should never set
           'info'.  'info' is provided optionally when fetching the ReadsSet.
           ref_path is optionally returned by get_reads_set_v1() when its
           input parameter 'include_set_item_ref_paths' is set to 1.) ->
           structure: parameter "ref" of type "ws_reads_id" (The workspace ID
           for a Reads data object. @id ws KBaseFile.PairedEndLibrary
           KBaseFile.SingleEndLibrary), parameter "ref_path" of type
           "ws_reads_id" (The workspace ID for a Reads data object. @id ws
           KBaseFile.PairedEndLibrary KBaseFile.SingleEndLibrary), parameter
           "label" of String, parameter "data_attachments" of list of type
           "DataAttachment" -> structure: parameter "name" of String,
           parameter "ref" of type "ws_obj_id" (The workspace ID for a any
           data object. @id ws), parameter "info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String, parameter "info" of
           type "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_reads_set_v1

        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.get_set(params)

        # END get_reads_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_reads_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def save_reads_set_v1(self, ctx, params):
        """
        :param params: instance of type "SaveReadsSetV1Params"
           (workspace_name or workspace_id - alternative options defining
           target workspace, output_object_name - workspace object name (this
           parameter is used together with one of workspace params from
           above)) -> structure: parameter "workspace" of String, parameter
           "output_object_name" of String, parameter "data" of type
           "ReadsSet" (@meta ws description as description @meta ws
           length(items) as item_count) -> structure: parameter "description"
           of String, parameter "items" of list of type "ReadsSetItem" (When
           saving a ReadsSet, only 'ref' is required.  You should never set
           'info'.  'info' is provided optionally when fetching the ReadsSet.
           ref_path is optionally returned by get_reads_set_v1() when its
           input parameter 'include_set_item_ref_paths' is set to 1.) ->
           structure: parameter "ref" of type "ws_reads_id" (The workspace ID
           for a Reads data object. @id ws KBaseFile.PairedEndLibrary
           KBaseFile.SingleEndLibrary), parameter "ref_path" of type
           "ws_reads_id" (The workspace ID for a Reads data object. @id ws
           KBaseFile.PairedEndLibrary KBaseFile.SingleEndLibrary), parameter
           "label" of String, parameter "data_attachments" of list of type
           "DataAttachment" -> structure: parameter "name" of String,
           parameter "ref" of type "ws_obj_id" (The workspace ID for a any
           data object. @id ws), parameter "info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        :returns: instance of type "SaveSetV1Result" -> structure: parameter
           "set_ref" of String, parameter "set_info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN save_reads_set_v1

        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.save_set(READS, ctx["provenance"], params)

        # END save_reads_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method save_reads_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def get_assembly_set_v1(self, ctx, params):
        """
        :param params: instance of type "GetSetV1Params" -> structure:
           parameter "ref" of String, parameter "include_item_info" of type
           "boolean" (A boolean. 0 = false, 1 = true.), parameter
           "include_set_item_ref_paths" of type "boolean" (A boolean. 0 =
           false, 1 = true.), parameter "ref_path_to_set" of list of String
        :returns: instance of type "GetAssemblySetV1Result" (ref - workspace
           reference to AssemblyGroup object. include_item_info - 1 or 0, if
           1 additionally provides workspace info (with metadata) for each
           Assembly object in the Set include_set_item_ref_paths - 1 or 0, if
           1, additionally provides ref_path for each item in the set. The
           ref_path returned for each item is either ref_path_to_set;item_ref
           (if ref_path_to_set is given) or set_ref;item_ref  (if
           ref_path_to_set is not given)) -> structure: parameter "data" of
           type "AssemblySet" (@meta ws description as description @meta ws
           length(items) as item_count) -> structure: parameter "description"
           of String, parameter "items" of list of type "AssemblySetItem"
           (When saving an AssemblySet, only 'ref' is required. You should
           never set 'info'.  'info' is provided optionally when fetching the
           AssemblySet. ref_path is optionally returned by
           get_assembly_set_v1() when its input parameter
           'include_set_item_ref_paths' is set to 1.) -> structure: parameter
           "ref" of type "ws_assembly_id" (The workspace ID for an Assembly
           object. @id ws KBaseGenomeAnnotations.Assembly), parameter
           "ref_path" of type "ws_assembly_id" (The workspace ID for an
           Assembly object. @id ws KBaseGenomeAnnotations.Assembly),
           parameter "label" of String, parameter "info" of type
           "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String, parameter "info" of type "object_info" (Information about
           an object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_assembly_set_v1

        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.get_set(params)

        # END get_assembly_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_assembly_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def save_assembly_set_v1(self, ctx, params):
        """
        :param params: instance of type "SaveAssemblySetV1Params"
           (workspace_name or workspace_id - alternative options defining
           target workspace, output_object_name - workspace object name (this
           parameter is used together with one of workspace params from
           above)) -> structure: parameter "workspace" of String, parameter
           "output_object_name" of String, parameter "data" of type
           "AssemblySet" (@meta ws description as description @meta ws
           length(items) as item_count) -> structure: parameter "description"
           of String, parameter "items" of list of type "AssemblySetItem"
           (When saving an AssemblySet, only 'ref' is required. You should
           never set 'info'.  'info' is provided optionally when fetching the
           AssemblySet. ref_path is optionally returned by
           get_assembly_set_v1() when its input parameter
           'include_set_item_ref_paths' is set to 1.) -> structure: parameter
           "ref" of type "ws_assembly_id" (The workspace ID for an Assembly
           object. @id ws KBaseGenomeAnnotations.Assembly), parameter
           "ref_path" of type "ws_assembly_id" (The workspace ID for an
           Assembly object. @id ws KBaseGenomeAnnotations.Assembly),
           parameter "label" of String, parameter "info" of type
           "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String
        :returns: instance of type "SaveSetV1Result" -> structure: parameter
           "set_ref" of String, parameter "set_info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN save_assembly_set_v1
        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.save_set(ASSEMBLY, ctx["provenance"], params)

        # END save_assembly_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method save_assembly_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def get_genome_set_v1(self, ctx, params):
        """
        :param params: instance of type "GetSetV1Params" -> structure:
           parameter "ref" of String, parameter "include_item_info" of type
           "boolean" (A boolean. 0 = false, 1 = true.), parameter
           "include_set_item_ref_paths" of type "boolean" (A boolean. 0 =
           false, 1 = true.), parameter "ref_path_to_set" of list of String
        :returns: instance of type "GetGenomeSetV1Result" (ref - workspace
           reference to GenomeGroup object. include_item_info - 1 or 0, if 1
           additionally provides workspace info (with metadata) for each
           Genome object in the Set include_set_item_ref_paths - 1 or 0, if
           1, additionally provides ref_path for each item in the set. The
           ref_path for each item is either ref_path_to_set;item_ref  (if
           ref_path_to_set is given) or set_ref;item_ref) -> structure:
           parameter "data" of type "GenomeSet" (optional 'elements' is only
           used to save 'KBaseSearch.GenomeSet' type @meta ws description as
           description @meta ws length(items) as item_count @option elements)
           -> structure: parameter "description" of String, parameter "items"
           of list of type "GenomeSetItem" (When saving an GenomeSet, only
           'ref' is required. You should never set 'info'.  'info' is
           provided optionally when fetching the GenomeSet. ref_path is
           optionally returned by get_genome_set_v1() when its input
           parameter 'include_set_item_ref_paths' is set to 1.) -> structure:
           parameter "ref" of type "ws_genome_id" (The workspace ID for a
           Genome object. @id ws KBaseGenomes.Genome), parameter "ref_path"
           of type "ws_genome_id" (The workspace ID for a Genome object. @id
           ws KBaseGenomes.Genome), parameter "label" of String, parameter
           "info" of type "object_info" (Information about an object,
           including user provided metadata. obj_id objid - the numerical id
           of the object. obj_name name - the name of the object. type_string
           type - the type of the object. timestamp save_date - the save date
           of the object. obj_ver ver - the version of the object. username
           saved_by - the user that saved or copied the object. ws_id wsid -
           the workspace containing the object. ws_name workspace - the
           workspace containing the object. string chsum - the md5 checksum
           of the object. int size - the size of the object in bytes.
           usermeta meta - arbitrary user-supplied metadata about the
           object.) -> tuple of size 11: parameter "objid" of type "obj_id"
           (The unique, permanent numerical ID of an object.), parameter
           "name" of type "obj_name" (A string used as a name for an object.
           Any string consisting of alphanumeric characters and the
           characters |._- that is not an integer is acceptable.), parameter
           "type" of type "type_string" (A type string. Specifies the type
           and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String, parameter "elements"
           of mapping from String to type "GenomeSetItem" (When saving an
           GenomeSet, only 'ref' is required. You should never set 'info'.
           'info' is provided optionally when fetching the GenomeSet.
           ref_path is optionally returned by get_genome_set_v1() when its
           input parameter 'include_set_item_ref_paths' is set to 1.) ->
           structure: parameter "ref" of type "ws_genome_id" (The workspace
           ID for a Genome object. @id ws KBaseGenomes.Genome), parameter
           "ref_path" of type "ws_genome_id" (The workspace ID for a Genome
           object. @id ws KBaseGenomes.Genome), parameter "label" of String,
           parameter "info" of type "object_info" (Information about an
           object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String, parameter "info" of
           type "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_genome_set_v1
        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.get_set(params)
        # END get_genome_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_genome_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def save_genome_set_v1(self, ctx, params):
        """
        :param params: instance of type "SaveGenomeSetV1Params"
           (workspace_name or workspace_id - alternative options defining
           target workspace, output_object_name - workspace object name (this
           parameter is used together with one of workspace params from
           above) save_search_set - default 'False', save
           'KBaseSets.GenomeSet' data type if set 'True', save
           'KBaseSearch.GenomeSet' data type) -> structure: parameter
           "workspace" of String, parameter "output_object_name" of String,
           parameter "data" of type "GenomeSet" (optional 'elements' is only
           used to save 'KBaseSearch.GenomeSet' type @meta ws description as
           description @meta ws length(items) as item_count @option elements)
           -> structure: parameter "description" of String, parameter "items"
           of list of type "GenomeSetItem" (When saving an GenomeSet, only
           'ref' is required. You should never set 'info'.  'info' is
           provided optionally when fetching the GenomeSet. ref_path is
           optionally returned by get_genome_set_v1() when its input
           parameter 'include_set_item_ref_paths' is set to 1.) -> structure:
           parameter "ref" of type "ws_genome_id" (The workspace ID for a
           Genome object. @id ws KBaseGenomes.Genome), parameter "ref_path"
           of type "ws_genome_id" (The workspace ID for a Genome object. @id
           ws KBaseGenomes.Genome), parameter "label" of String, parameter
           "info" of type "object_info" (Information about an object,
           including user provided metadata. obj_id objid - the numerical id
           of the object. obj_name name - the name of the object. type_string
           type - the type of the object. timestamp save_date - the save date
           of the object. obj_ver ver - the version of the object. username
           saved_by - the user that saved or copied the object. ws_id wsid -
           the workspace containing the object. ws_name workspace - the
           workspace containing the object. string chsum - the md5 checksum
           of the object. int size - the size of the object in bytes.
           usermeta meta - arbitrary user-supplied metadata about the
           object.) -> tuple of size 11: parameter "objid" of type "obj_id"
           (The unique, permanent numerical ID of an object.), parameter
           "name" of type "obj_name" (A string used as a name for an object.
           Any string consisting of alphanumeric characters and the
           characters |._- that is not an integer is acceptable.), parameter
           "type" of type "type_string" (A type string. Specifies the type
           and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String, parameter "elements"
           of mapping from String to type "GenomeSetItem" (When saving an
           GenomeSet, only 'ref' is required. You should never set 'info'.
           'info' is provided optionally when fetching the GenomeSet.
           ref_path is optionally returned by get_genome_set_v1() when its
           input parameter 'include_set_item_ref_paths' is set to 1.) ->
           structure: parameter "ref" of type "ws_genome_id" (The workspace
           ID for a Genome object. @id ws KBaseGenomes.Genome), parameter
           "ref_path" of type "ws_genome_id" (The workspace ID for a Genome
           object. @id ws KBaseGenomes.Genome), parameter "label" of String,
           parameter "info" of type "object_info" (Information about an
           object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String, parameter
           "save_search_set" of type "boolean" (A boolean. 0 = false, 1 =
           true.)
        :returns: instance of type "SaveSetV1Result" -> structure: parameter
           "set_ref" of String, parameter "set_info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN save_genome_set_v1
        ws = Workspace(self.workspace_url, token=ctx["token"])
        set_interface = SetInterfaceV1(ws)
        result = set_interface.save_set(GENOME, ctx["provenance"], params)
        # END save_genome_set_v1

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method save_genome_set_v1 ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def create_sample_set(self, ctx, params):
        """
        :param params: instance of type "CreateRNASeqSampleSetParams"
           (******* Sample SET METHODS ************) -> structure: parameter
           "ws_id" of String, parameter "sampleset_id" of String, parameter
           "sampleset_desc" of String, parameter "domain" of String,
           parameter "platform" of String, parameter "sample_ids" of list of
           String, parameter "condition" of list of String, parameter
           "source" of String, parameter "Library_type" of String, parameter
           "publication_id" of String, parameter "external_source_date" of
           String, parameter "conditionset_ref" of String, parameter
           "sample_n_conditions" of mapping from String to String
        :returns: instance of type "SaveSetV1Result" -> structure: parameter
           "set_ref" of String, parameter "set_info" of type "object_info"
           (Information about an object, including user provided metadata.
           obj_id objid - the numerical id of the object. obj_name name - the
           name of the object. type_string type - the type of the object.
           timestamp save_date - the save date of the object. obj_ver ver -
           the version of the object. username saved_by - the user that saved
           or copied the object. ws_id wsid - the workspace containing the
           object. ws_name workspace - the workspace containing the object.
           string chsum - the md5 checksum of the object. int size - the size
           of the object in bytes. usermeta meta - arbitrary user-supplied
           metadata about the object.) -> tuple of size 11: parameter "objid"
           of type "obj_id" (The unique, permanent numerical ID of an
           object.), parameter "name" of type "obj_name" (A string used as a
           name for an object. Any string consisting of alphanumeric
           characters and the characters |._- that is not an integer is
           acceptable.), parameter "type" of type "type_string" (A type
           string. Specifies the type and its version in a single string in
           the format [module].[typename]-[major].[minor]: module - a string.
           The module name of the typespec containing the type. typename - a
           string. The name of the type as assigned by the typedef statement.
           major - an integer. The major version of the type. A change in the
           major version implies the type has changed in a non-backwards
           compatible way. minor - an integer. The minor version of the type.
           A change in the minor version implies that the type has changed in
           a way that is backwards compatible with previous type definitions.
           In many cases, the major and minor versions are optional, and if
           not provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN create_sample_set
        ws = Workspace(self.workspace_url, token=ctx["token"])
        ssi = SampleSetInterface(ws)
        result = ssi.create_sample_set(ctx, params)
        # END create_sample_set

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method create_sample_set ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def sample_set_to_samples_info(self, ctx, params):
        """
        :param params: instance of type "SampleSetToSamplesInfoParams" ->
           structure: parameter "query" of String, parameter "ref" of String,
           parameter "sort_by" of list of type "column_sorting"
           (KBaseSets.SampleSet Methods column_sorting - tuple (column,
           ascending) - tuple of string, boolean where the former is the name
           of the column on which to sort, and the later is a boolean
           describing whether to sort ascending (true) or descending (false)
           query   - string query to search against all searchable fields ref
           - string workspace reference of the sampleset object sort_by -
           list of column_sorting in order of sorting, 0 index colum_sorting
           tuple highest level of sorting start   - default 0  - starting
           index for pagination limit   - default 10 - number of documents to
           retrieve starting from start pagination) -> tuple of size 2:
           parameter "column" of String, parameter "ascending" of type
           "boolean" (A boolean. 0 = false, 1 = true.), parameter "start" of
           Long, parameter "limit" of Long
        :returns: instance of type "SampleSetToSamplesInfoResult" ->
           structure: parameter "num_found" of Long, parameter "start" of
           Long, parameter "query" of String, parameter "samples" of list of
           unspecified object
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN sample_set_to_samples_info
        sample_search_utils = SamplesSearchUtils(ctx["token"], self.search_url)
        if not params.get("ref"):
            raise ValueError(
                f"Argument 'ref' must be specified, 'ref' = '{params.get('ref')}'"
            )
        result = sample_search_utils.sample_set_to_samples_info(params)
        # END sample_set_to_samples_info

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method sample_set_to_samples_info ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def list_sets(self, ctx, params):
        """
        Use to get the top-level sets in a WS. Optionally can include
        one level down members of those sets.
        NOTE: DOES NOT PRESERVE ORDERING OF ITEM LIST IN DATA
        :param params: instance of type "ListSetParams" (workspace -
           workspace name or ID (alternative to workspaces parameter),
           workspaces - list of workspace name ot ID (alternative to
           workspace parameter), include_metadata - flag for including
           metadata into Set object info and into object info of items (it
           affects DP raw data as well), include_set_item_ref_paths - 1 or 0,
           if 1, additionally provides ref_path for each item in the set. The
           ref_path for each item is either ref_path_to_set;item_ref  (if
           ref_path_to_set is given) or set_ref;item_ref) -> structure:
           parameter "workspace" of String, parameter "workspaces" of String,
           parameter "include_set_item_info" of type "boolean" (A boolean. 0
           = false, 1 = true.), parameter "include_metadata" of type
           "boolean" (A boolean. 0 = false, 1 = true.), parameter
           "include_set_item_ref_paths" of type "boolean" (A boolean. 0 =
           false, 1 = true.)
        :returns: instance of type "ListSetResult" -> structure: parameter
           "sets" of list of type "SetInfo" (ref - the workspace object ref
           for the set info - the Workspace object_info tuple for the set
           items - the SetItemInfo for each of the items in the set) ->
           structure: parameter "ref" of type "ws_obj_id" (The workspace ID
           for a any data object. @id ws), parameter "info" of type
           "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String, parameter "items" of list of type "SetItemInfo" (ref_path
           is optionally returned by list_sets() and get_set_items(), when
           the input parameter 'include_set_item_ref_paths' is set to 1.) ->
           structure: parameter "ref" of type "ws_obj_id" (The workspace ID
           for a any data object. @id ws), parameter "ref_path" of type
           "ws_obj_id" (The workspace ID for a any data object. @id ws),
           parameter "info" of type "object_info" (Information about an
           object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN list_sets

        ws = Workspace(self.workspace_url, token=ctx["token"])
        gsn = GenericSetNavigator(ws, token=ctx["token"])
        result = gsn.list_sets(params)

        # END list_sets

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method list_sets ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def get_set_items(self, ctx, params):
        """
        Use to drill down into one or more sets, the position in the
        return 'sets' list will match the position in the input ref list.
        NOTE: DOES NOT PRESERVE ORDERING OF ITEM LIST IN DATA
        :param params: instance of type "GetSetItemsParams" -> structure:
           parameter "set_refs" of list of type "SetReference"
           (include_set_item_ref_paths - 1 or 0, if 1, additionally provides
           ref_path for each item in the set. The ref_path for each item is
           either ref_path_to_set;item_ref  (if ref_path_to_set is given) or
           set_ref;item_ref) -> structure: parameter "ref" of type
           "ws_obj_id" (The workspace ID for a any data object. @id ws),
           parameter "ref_path_to_set" of list of type "ws_obj_id" (The
           workspace ID for a any data object. @id ws), parameter
           "include_set_item_ref_paths" of type "boolean" (A boolean. 0 =
           false, 1 = true.)
        :returns: instance of type "GetSetItemsResult" -> structure:
           parameter "sets" of list of type "SetInfo" (ref - the workspace
           object ref for the set info - the Workspace object_info tuple for
           the set items - the SetItemInfo for each of the items in the set)
           -> structure: parameter "ref" of type "ws_obj_id" (The workspace
           ID for a any data object. @id ws), parameter "info" of type
           "object_info" (Information about an object, including user
           provided metadata. obj_id objid - the numerical id of the object.
           obj_name name - the name of the object. type_string type - the
           type of the object. timestamp save_date - the save date of the
           object. obj_ver ver - the version of the object. username saved_by
           - the user that saved or copied the object. ws_id wsid - the
           workspace containing the object. ws_name workspace - the workspace
           containing the object. string chsum - the md5 checksum of the
           object. int size - the size of the object in bytes. usermeta meta
           - arbitrary user-supplied metadata about the object.) -> tuple of
           size 11: parameter "objid" of type "obj_id" (The unique, permanent
           numerical ID of an object.), parameter "name" of type "obj_name"
           (A string used as a name for an object. Any string consisting of
           alphanumeric characters and the characters |._- that is not an
           integer is acceptable.), parameter "type" of type "type_string" (A
           type string. Specifies the type and its version in a single string
           in the format [module].[typename]-[major].[minor]: module - a
           string. The module name of the typespec containing the type.
           typename - a string. The name of the type as assigned by the
           typedef statement. major - an integer. The major version of the
           type. A change in the major version implies the type has changed
           in a non-backwards compatible way. minor - an integer. The minor
           version of the type. A change in the minor version implies that
           the type has changed in a way that is backwards compatible with
           previous type definitions. In many cases, the major and minor
           versions are optional, and if not provided the most recent version
           will be used. Example: MyModule.MyType-3.1), parameter "save_date"
           of type "timestamp" (A time in the format YYYY-MM-DDThh:mm:ssZ,
           where Z is either the character Z (representing the UTC timezone)
           or the difference in time to UTC in the format +/-HHMM, eg:
           2012-12-17T23:24:06-0500 (EST time) 2013-04-03T08:56:32+0000 (UTC
           time) 2013-04-03T08:56:32Z (UTC time)), parameter "version" of
           Long, parameter "saved_by" of type "username" (Login name of a
           KBase user account.), parameter "wsid" of type "ws_id" (The
           unique, permanent numerical ID of a workspace.), parameter
           "workspace" of type "ws_name" (A string used as a name for a
           workspace. Any string consisting of alphanumeric characters and
           "_", ".", or "-" that is not an integer is acceptable. The name
           may optionally be prefixed with the workspace owner's user name
           and a colon, e.g. kbasetest:my_workspace.), parameter "chsum" of
           String, parameter "size" of Long, parameter "meta" of type
           "usermeta" (User provided metadata about an object. Arbitrary
           key-value pairs provided by the user.) -> mapping from String to
           String, parameter "items" of list of type "SetItemInfo" (ref_path
           is optionally returned by list_sets() and get_set_items(), when
           the input parameter 'include_set_item_ref_paths' is set to 1.) ->
           structure: parameter "ref" of type "ws_obj_id" (The workspace ID
           for a any data object. @id ws), parameter "ref_path" of type
           "ws_obj_id" (The workspace ID for a any data object. @id ws),
           parameter "info" of type "object_info" (Information about an
           object, including user provided metadata. obj_id objid - the
           numerical id of the object. obj_name name - the name of the
           object. type_string type - the type of the object. timestamp
           save_date - the save date of the object. obj_ver ver - the version
           of the object. username saved_by - the user that saved or copied
           the object. ws_id wsid - the workspace containing the object.
           ws_name workspace - the workspace containing the object. string
           chsum - the md5 checksum of the object. int size - the size of the
           object in bytes. usermeta meta - arbitrary user-supplied metadata
           about the object.) -> tuple of size 11: parameter "objid" of type
           "obj_id" (The unique, permanent numerical ID of an object.),
           parameter "name" of type "obj_name" (A string used as a name for
           an object. Any string consisting of alphanumeric characters and
           the characters |._- that is not an integer is acceptable.),
           parameter "type" of type "type_string" (A type string. Specifies
           the type and its version in a single string in the format
           [module].[typename]-[major].[minor]: module - a string. The module
           name of the typespec containing the type. typename - a string. The
           name of the type as assigned by the typedef statement. major - an
           integer. The major version of the type. A change in the major
           version implies the type has changed in a non-backwards compatible
           way. minor - an integer. The minor version of the type. A change
           in the minor version implies that the type has changed in a way
           that is backwards compatible with previous type definitions. In
           many cases, the major and minor versions are optional, and if not
           provided the most recent version will be used. Example:
           MyModule.MyType-3.1), parameter "save_date" of type "timestamp" (A
           time in the format YYYY-MM-DDThh:mm:ssZ, where Z is either the
           character Z (representing the UTC timezone) or the difference in
           time to UTC in the format +/-HHMM, eg: 2012-12-17T23:24:06-0500
           (EST time) 2013-04-03T08:56:32+0000 (UTC time)
           2013-04-03T08:56:32Z (UTC time)), parameter "version" of Long,
           parameter "saved_by" of type "username" (Login name of a KBase
           user account.), parameter "wsid" of type "ws_id" (The unique,
           permanent numerical ID of a workspace.), parameter "workspace" of
           type "ws_name" (A string used as a name for a workspace. Any
           string consisting of alphanumeric characters and "_", ".", or "-"
           that is not an integer is acceptable. The name may optionally be
           prefixed with the workspace owner's user name and a colon, e.g.
           kbasetest:my_workspace.), parameter "chsum" of String, parameter
           "size" of Long, parameter "meta" of type "usermeta" (User provided
           metadata about an object. Arbitrary key-value pairs provided by
           the user.) -> mapping from String to String
        """
        # ctx is the context object
        # return variables are: result
        # BEGIN get_set_items

        ws = Workspace(self.workspace_url, token=ctx["token"])
        gsn = GenericSetNavigator(ws)
        result = gsn.get_set_items(params)

        # END get_set_items

        # At some point might do deeper type checking...
        if not isinstance(result, dict):
            raise ValueError('Method get_set_items ' +
                             'return value result ' +
                             'is not type dict as required.')
        # return the results
        return [result]

    def status(self, ctx):
        # BEGIN_STATUS
        returnVal = {
            "state": "OK",
            "message": "",
            "version": self.VERSION,
            "git_url": self.GIT_URL,
            "git_commit_hash": self.GIT_COMMIT_HASH,
        }
        # END_STATUS
        return [returnVal]
