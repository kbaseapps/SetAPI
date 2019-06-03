

#include <workspace.spec>


module SetAPI {

    /* A boolean. 0 = false, 1 = true. */
    typedef int boolean;

    /*
        The workspace ID for a any data object.
        @id ws
    */
    typedef string ws_obj_id;

    typedef structure {
        string name;
        ws_obj_id ref;
    } DataAttachment;


    /* ******* DIFFERENTIAL EXPRESSION MATRIX SET METHODS ******* */

    /* NOTE: data type explicitly copied from KBaseSets so type and
    API can evolve independently */

    /*
        The workspace id for a FeatureSet data object.
        @id ws KBaseFeatureValues.DifferentialExpressionMatrix KBaseMatrices.DifferentialExpressionMatrix;
    */
    typedef string ws_diffexpmatrix_id;

    /*
        When saving a DifferentialExpressionMatrixSet, only 'ref' is required.
        You should never set 'info'.  'info' is provided optionally when fetching
        the DifferentialExpressionMatrixSet.
        ref_path is optionally returned by get_differential_expression_matrix_set_v1()
        when its input parameter 'include_set_item_ref_paths' is set to 1.
    */
    typedef structure {
        ws_diffexpmatrix_id ref;
        ws_diffexpmatrix_id ref_path;
        string label;
        Workspace.object_info info;
    } DifferentialExpressionMatrixSetItem;

    /*
        When building a DifferentialExpressionMatrixSet, all DifferentialExpressionMatrices must be
        built against the same genome. This is not part of the object type, but enforced during a
        call to save_differential_expression_matrix_set_v1.
        @meta ws description as description
        @meta ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<DifferentialExpressionMatrixSetItem> items;
    } DifferentialExpressionMatrixSet;

    /*
        ref - workspace reference to DifferentialExpressionMatrixSet object.
        include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                            metadata) for each DifferentialExpressionMatrix object in the Set
        include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
                                     in the set. The ref_path returned for each item is either
                                         ref_path_to_set;item_ref  (if ref_path_to_set is given) or
                                         set_ref;item_ref  (if ref_path_to_set is not given)
    */
    typedef structure {
        string ref;
        boolean include_item_info;
        boolean include_set_item_ref_paths;
        list <string> ref_path_to_set;
    } GetDifferentialExpressionMatrixSetV1Params;

    typedef structure {
        DifferentialExpressionMatrixSet data;
        Workspace.object_info info;
    } GetDifferentialExpressionMatrixSetV1Result;

    funcdef get_differential_expression_matrix_set_v1(GetDifferentialExpressionMatrixSetV1Params params)
        returns (GetDifferentialExpressionMatrixSetV1Result result) authentication optional;

    /*
        workspace_name or workspace_id - alternative options defining
            target workspace,
        output_object_name - workspace object name (this parameter is
            used together with one of workspace params from above)
    */
    typedef structure {
        string workspace;
        string output_object_name;
        DifferentialExpressionMatrixSet data;
    } SaveDifferentialExpressionMatrixSetV1Params;

    typedef structure {
        string set_ref;
        Workspace.object_info set_info;
    } SaveDifferentialExpressionMatrixSetV1Result;

    funcdef save_differential_expression_matrix_set_v1(SaveDifferentialExpressionMatrixSetV1Params params)
        returns (SaveDifferentialExpressionMatrixSetV1Result result) authentication required;




    /* ******* FEATURE SET SET METHODS ******** */

    /* NOTE: data type explicitly copied from KBaseSets so type and
    API can evolve independently */

    /*
        The workspace id for a FeatureSet data object.
        @id ws KBaseCollections.FeatureSet
    */
    typedef string ws_feature_set_id;

    /*
        When saving a FeatureSetSet, only 'ref' is required.
        You should never set 'info'.  'info' is provided optionally when fetching
        the FeatureSetSet.
        ref_path is optionally returned by get_feature_set_set_v1()
        when its input parameter 'include_set_item_ref_paths' is set to 1.
    */
    typedef structure {
        ws_feature_set_id ref;
        ws_feature_set_id ref_path;
        string label;
        Workspace.object_info info;
    } FeatureSetSetItem;

    /*
        When building a FeatureSetSet, all FeatureSets must be aligned against the same
        genome. This is not part of the object type, but enforced during a call to
        save_feature_set_set_v1.
        @meta ws description as description
        @meta ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<FeatureSetSetItem> items;
    } FeatureSetSet;

    /*
        ref - workspace reference to FeatureSetSet object.
        include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                            metadata) for each FeatureSet object in the Set
        include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
                                     in the set. The ref_path returned for each item is either
                                         ref_path_to_set;item_ref  (if ref_path_to_set is given) or
                                         set_ref;item_ref  (if ref_path_to_set is not given)
    */
    typedef structure {
        string ref;
        boolean include_item_info;
        boolean include_set_item_ref_paths;
        list <string> ref_path_to_set;
    } GetFeatureSetSetV1Params;

    typedef structure {
        FeatureSetSet data;
        Workspace.object_info info;
    } GetFeatureSetSetV1Result;

    funcdef get_feature_set_set_v1(GetFeatureSetSetV1Params params)
        returns (GetFeatureSetSetV1Result) authentication optional;

    /*
        workspace_name or workspace_id - alternative options defining
            target workspace,
        output_object_name - workspace object name (this parameter is
            used together with one of workspace params from above)
    */
    typedef structure {
        string workspace;
        string output_object_name;
        FeatureSetSet data;
    } SaveFeatureSetSetV1Params;

    typedef structure {
        string set_ref;
        Workspace.object_info set_info;
    } SaveFeatureSetSetV1Result;

    funcdef save_feature_set_set_v1(SaveFeatureSetSetV1Params params)
        returns (SaveFeatureSetSetV1Result result) authentication required;


    /* ******* EXPRESSION SET METHODS ******** */

    /* NOTE: data type explicitly copied from KBaseSets so type and
    API can evolve independently. */

    /*
        The workspace id for a ReadsAlignment data object.
        @id ws KBaseRNASeq.RNASeqExpression
    */
    typedef string ws_expression_id;

    /*
        When saving a ExpressionSet, only 'ref' is required.
        You should never set 'info'.  'info' is provided optionally when fetching
        the ExpressionSet.
        ref_path is optionally returned by get_expression_set_v1()
        when its input parameter 'include_set_item_ref_paths' is set to 1.
    */
    typedef structure {
        ws_expression_id ref;
        ws_expression_id ref_path;
        string label;
        list<DataAttachment> data_attachments;
        Workspace.object_info info;
    } ExpressionSetItem;

    /*
        When building a ExpressionSet, all Expression objects must be aligned against the same
        genome. This is not part of the object type, but enforced during a call to
        save_expression_set_v1.
        @meta ws description as description
        @meta ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<ExpressionSetItem> items;
    } ExpressionSet;

    /*
        ref - workspace reference to ExpressionSet object.
        include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                            metadata) for each Expression object in the Set
        include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
                                     in the set. The ref_path returned for each item is either
                                         ref_path_to_set;item_ref  (if ref_path_to_set is given) or
                                         set_ref;item_ref  (if ref_path_to_set is not given)
    */
    typedef structure {
        string ref;
        boolean include_item_info;
        boolean include_set_item_ref_paths;
        list <string> ref_path_to_set;
    } GetExpressionSetV1Params;

    typedef structure {
        ExpressionSet data;
        Workspace.object_info info;
    } GetExpressionSetV1Result;

    funcdef get_expression_set_v1(GetExpressionSetV1Params params)
        returns (GetExpressionSetV1Result) authentication optional;

    /*
        workspace_name or workspace_id - alternative options defining
            target workspace,
        output_object_name - workspace object name (this parameter is
            used together with one of workspace params from above)
    */
    typedef structure {
        string workspace;
        string output_object_name;
        ExpressionSet data;
    } SaveExpressionSetV1Params;

    typedef structure {
        string set_ref;
        Workspace.object_info set_info;
    } SaveExpressionSetV1Result;

    funcdef save_expression_set_v1(SaveExpressionSetV1Params params)
        returns (SaveExpressionSetV1Result result) authentication required;


    /* ******* READS ALIGNMENT SET METHODS ******** */

    /* NOTE: data type explicitly copied from KBaseSets so type and
    API can evolve independently */

    /*
        The workspace id for a ReadsAlignment data object.
        @id ws KBaseRNASeq.RNASeqAlignment
    */
    typedef string ws_reads_align_id;

    /*
        When saving a ReadsAlignmentSet, only 'ref' is required.
        You should never set 'info'.  'info' is provided optionally when fetching
        the ReadsAlignmentSet.
        ref_path is optionally returned by get_reads_alignment_set_v1()
        when its input parameter 'include_set_item_ref_paths' is set to 1.
    */
    typedef structure {
        ws_reads_align_id ref;
        ws_reads_align_id ref_path;
        string label;
        Workspace.object_info info;
        list<DataAttachment> data_attachments;
    } ReadsAlignmentSetItem;

    /*
        When building a ReadsAlignmentSet, all ReadsAlignments must be aligned against the same
        genome. This is not part of the object type, but enforced during a call to
        save_reads_alignment_set_v1.
        @meta ws description as description
        @meta ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<ReadsAlignmentSetItem> items;
    } ReadsAlignmentSet;

    /*
        ref - workspace reference to ReadsAlignmentSet object.
        include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                            metadata) for each ReadsAlignment object in the Set
        include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
                                     in the set. The ref_path returned for each item is either
                                         ref_path_to_set;item_ref  (if ref_path_to_set is given) or
                                         set_ref;item_ref  (if ref_path_to_set is not given)
    */
    typedef structure {
        string ref;
        boolean include_item_info;
        boolean include_set_item_ref_paths;
        list <string> ref_path_to_set;
    } GetReadsAlignmentSetV1Params;

    typedef structure {
        ReadsAlignmentSet data;
        Workspace.object_info info;
    } GetReadsAlignmentSetV1Result;

    funcdef get_reads_alignment_set_v1(GetReadsAlignmentSetV1Params params)
        returns (GetReadsAlignmentSetV1Result) authentication optional;

    /*
        workspace_name or workspace_id - alternative options defining
            target workspace,
        output_object_name - workspace object name (this parameter is
            used together with one of workspace params from above)
    */
    typedef structure {
        string workspace;
        string output_object_name;
        ReadsAlignmentSet data;
    } SaveReadsAlignmentSetV1Params;

    typedef structure {
        string set_ref;
        Workspace.object_info set_info;
    } SaveReadsAlignmentSetV1Result;

    funcdef save_reads_alignment_set_v1(SaveReadsAlignmentSetV1Params params)
        returns (SaveReadsAlignmentSetV1Result result) authentication required;



    /* ******* READS SET METHODS ************ */

    /* NOTE: data type explicitly copied from KBaseSets so type and
    API can evolve independently */

    /*
        The workspace ID for a Reads data object.
        @id ws KBaseFile.PairedEndLibrary KBaseFile.SingleEndLibrary
    */
    typedef string ws_reads_id;

    /*
        When saving a ReadsSet, only 'ref' is required.  You should
        never set 'info'.  'info' is provided optionally when fetching
        the ReadsSet.
        ref_path is optionally returned by get_reads_set_v1()
        when its input parameter 'include_set_item_ref_paths' is set to 1.
    */
    typedef structure {
        ws_reads_id ref;
        ws_reads_id ref_path;
        string label;
        list <DataAttachment> data_attachments;
        Workspace.object_info info;
    } ReadsSetItem;

    /*
        @meta ws description as description
        @meta ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<ReadsSetItem> items;
    } ReadsSet;


    /*
        ref - workspace reference to ReadsGroup object.
        include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                            metadata) for each Reads object in the Set
        include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
                                     in the set. The ref_path returned for each item is either
                                         ref_path_to_set;item_ref  (if ref_path_to_set is given) or
                                         set_ref;item_ref  (if ref_path_to_set is not given)
    */
    typedef structure {
        string ref;
        boolean include_item_info;
        boolean include_set_item_ref_paths;
        list <string> ref_path_to_set;
    } GetReadsSetV1Params;

    typedef structure {
        ReadsSet data;
        Workspace.object_info info;
    } GetReadsSetV1Result;

    funcdef get_reads_set_v1(GetReadsSetV1Params params)
        returns (GetReadsSetV1Result result) authentication optional;

    /*
        workspace_name or workspace_id - alternative options defining
            target workspace,
        output_object_name - workspace object name (this parameter is
            used together with one of workspace params from above)
    */
    typedef structure {
        string workspace;
        string output_object_name;
        ReadsSet data;
    } SaveReadsSetV1Params;

    typedef structure {
        string set_ref;
        Workspace.object_info set_info;
    } SaveReadsSetV1Result;

    funcdef save_reads_set_v1(SaveReadsSetV1Params params)
        returns (SaveReadsSetV1Result result) authentication required;




    /* ******* Assembly SET METHODS ************ */

    /* NOTE: data type explicitly copied from KBaseSets so type and
    API can evolve independently */

    /*
        The workspace ID for an Assembly object.
        @id ws KBaseGenomeAnnotations.Assembly
    */
    typedef string ws_assembly_id;

    /*
        When saving an AssemblySet, only 'ref' is required.
        You should never set 'info'.  'info' is provided optionally when fetching
        the AssemblySet.
        ref_path is optionally returned by get_assembly_set_v1()
        when its input parameter 'include_set_item_ref_paths' is set to 1.
    */
    typedef structure {
        ws_assembly_id ref;
        ws_assembly_id ref_path;
        string label;
        Workspace.object_info info;
    } AssemblySetItem;

    /*
        @meta ws description as description
        @meta ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<AssemblySetItem> items;
    } AssemblySet;


    /*
        ref - workspace reference to AssemblyGroup object.
        include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                            metadata) for each Assembly object in the Set
        include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
                                     in the set. The ref_path returned for each item is either
                                         ref_path_to_set;item_ref  (if ref_path_to_set is given) or
                                         set_ref;item_ref  (if ref_path_to_set is not given)
    */
    typedef structure {
        string ref;
        boolean include_item_info;
        boolean include_set_item_ref_paths;
        list <string> ref_path_to_set;
    } GetAssemblySetV1Params;

    typedef structure {
        AssemblySet data;
        Workspace.object_info info;
    } GetAssemblySetV1Result;

    funcdef get_assembly_set_v1(GetAssemblySetV1Params params)
        returns (GetAssemblySetV1Result result) authentication optional;

    /*
        workspace_name or workspace_id - alternative options defining
            target workspace,
        output_object_name - workspace object name (this parameter is
            used together with one of workspace params from above)
    */
    typedef structure {
        string workspace;
        string output_object_name;
        AssemblySet data;
    } SaveAssemblySetV1Params;

    typedef structure {
        string set_ref;
        Workspace.object_info set_info;
    } SaveAssemblySetV1Result;

    funcdef save_assembly_set_v1(SaveAssemblySetV1Params params)
        returns (SaveAssemblySetV1Result result) authentication required;



    /* ******* Genome SET METHODS ************ */

    /* NOTE: data type explicitly copied from KBaseSets so type and
    API can evolve independently */

    /*
        The workspace ID for a Genome object.
        @id ws KBaseGenomes.Genome
    */
    typedef string ws_genome_id;

    /*
        When saving an GenomeSet, only 'ref' is required.
        You should never set 'info'.  'info' is provided optionally when fetching
        the GenomeSet.
        ref_path is optionally returned by get_genome_set_v1()
        when its input parameter 'include_set_item_ref_paths' is set to 1.
    */
    typedef structure {
        ws_genome_id ref;
        ws_genome_id ref_path;
        string label;
        Workspace.object_info info;
    } GenomeSetItem;

    /*
        optional 'elements' is only used to save 'KBaseSearch.GenomeSet' type
        @meta ws description as description
        @meta ws length(items) as item_count
        @option elements
    */
    typedef structure {
        string description;
        list<GenomeSetItem> items;
        mapping<string, GenomeSetItem> elements;
    } GenomeSet;


    /*
        ref - workspace reference to GenomeGroup object.
        include_item_info - 1 or 0, if 1 additionally provides workspace info (with
                            metadata) for each Genome object in the Set
        include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
                            in the set. The ref_path for each item is either
                                ref_path_to_set;item_ref  (if ref_path_to_set is given) or
                                set_ref;item_ref
    */
    typedef structure {
        string ref;
        boolean include_item_info;
        boolean include_set_item_ref_paths;
        list <string> ref_path_to_set;
    } GetGenomeSetV1Params;

    typedef structure {
        GenomeSet data;
        Workspace.object_info info;
    } GetGenomeSetV1Result;

    funcdef get_genome_set_v1(GetGenomeSetV1Params params)
        returns (GetGenomeSetV1Result result) authentication optional;

    /*
        workspace_name or workspace_id - alternative options defining
            target workspace,
        output_object_name - workspace object name (this parameter is
            used together with one of workspace params from above)
        save_search_set - default 'False', save 'KBaseSets.GenomeSet' data type
                          if set 'True', save 'KBaseSearch.GenomeSet' data type
    */
    typedef structure {
        string workspace;
        string output_object_name;
        GenomeSet data;
        boolean save_search_set;
    } SaveGenomeSetV1Params;

    typedef structure {
        string set_ref;
        Workspace.object_info set_info;
    } SaveGenomeSetV1Result;

    funcdef save_genome_set_v1(SaveGenomeSetV1Params params)
        returns (SaveGenomeSetV1Result result) authentication required;


    /* ******* Sample SET METHODS ************ */

    typedef structure{
        string ws_id;
        string sampleset_id;
        string sampleset_desc;
        string domain;
        string platform;
        list<string> sample_ids;
        list<string> condition;
        string source;
        string Library_type;
        string publication_id;
        string external_source_date;
        string conditionset_ref;
    } CreateRNASeqSampleSetParams;

    typedef structure{
        string set_ref;
        Workspace.object_info set_info;
    } CreateRNASeqSampleSetResult;

    funcdef create_sample_set(CreateRNASeqSampleSetParams params)
                      returns(CreateRNASeqSampleSetResult) authentication required;





    /* ******* Generic SET METHODS ************ */


    /*
        workspace - workspace name or ID (alternative to
            workspaces parameter),
        workspaces - list of workspace name ot ID (alternative to
            workspace parameter),
        include_metadata - flag for including metadata into Set object info
            and into object info of items (it affects DP raw data as well),
        include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
                            in the set. The ref_path for each item is either
                                ref_path_to_set;item_ref  (if ref_path_to_set is given) or
                                set_ref;item_ref
    */
    typedef structure {
        string workspace;
        string workspaces;
        boolean include_set_item_info;
        boolean include_metadata;
        boolean include_set_item_ref_paths;
    } ListSetParams;

    /*
        ref_path is optionally returned by list_sets() and get_set_items(),
        when the input parameter 'include_set_item_ref_paths' is set to 1.
    */

    typedef structure {
        ws_obj_id ref;
        ws_obj_id ref_path;
        Workspace.object_info info;
    } SetItemInfo;

    /*
        ref - the workspace object ref for the set
        info - the Workspace object_info tuple for the set
        items - the SetItemInfo for each of the items in the set
    */
    typedef structure {
        ws_obj_id ref;
        Workspace.object_info info;
        list<SetItemInfo> items;
    } SetInfo;



    typedef structure {
        list <SetInfo> sets;
    } ListSetResult;

    /* Use to get the top-level sets in a WS. Optionally can include
    one level down members of those sets.
    NOTE: DOES NOT PRESERVE ORDERING OF ITEM LIST IN DATA */
    funcdef list_sets(ListSetParams params)
              returns(ListSetResult result) authentication optional;

    /*
        include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
                            in the set. The ref_path for each item is either
                                ref_path_to_set;item_ref  (if ref_path_to_set is given) or
                                set_ref;item_ref
     */

    typedef structure {
        ws_obj_id ref;
        list <ws_obj_id> ref_path_to_set;
    } SetReference;

    typedef structure {
        list <SetReference> set_refs;
        boolean include_set_item_ref_paths;
    } GetSetItemsParams;

    typedef structure {
        list <SetInfo> sets;
    } GetSetItemsResult;

    /* Use to drill down into one or more sets, the position in the
    return 'sets' list will match the position in the input ref list.
    NOTE: DOES NOT PRESERVE ORDERING OF ITEM LIST IN DATA */
    funcdef get_set_items(GetSetItemsParams params)
                  returns(GetSetItemsResult result) authentication optional;

};
