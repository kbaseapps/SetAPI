

#include <workspace.spec>


module SetAPI {

    /* A boolean. 0 = false, 1 = true. */
    typedef int boolean;


    /* ******* READS SET METHODS ************ */

    /* NOTE: data type explicitly copied from KBaseSets so type and
    API can evolve independently */

    /*
        The workspace ID for a any data object.
        @id ws
    */
    typedef string ws_obj_id;

    typedef structure {
        string name;
        ws_obj_id ref;
    } DataAttachment;

    /*
        The workspace ID for a Reads data object.
        @id ws KBaseFile.PairedEndLibrary KBaseFile.SingleEndLibrary 
    */
    typedef string ws_reads_id;

    /*
        When saving a ReadsSet, only 'ref' is required.  You should
        never set 'info'.  'info' is provided optionally when fetching
        the ReadsSet.
    */
    typedef structure {
        ws_reads_id ref;
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
    */
    typedef structure {
        string ref;
        boolean include_item_info;
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
        string workspace_name;
        int workspace_id;
        string output_object_name;
        ReadsSet data;
    } SaveReadsSetV1Params;

    typedef structure {
        string set_ref;
        Workspace.object_info set_info;
    } SaveReadsSetV1Result;

    funcdef save_reads_set_v1(SaveReadsSetV1Params params)
        returns (SaveReadsSetV1Result result) authentication required;



    /* ******* Generic SET METHODS ************ */


    /* 
        workspace - workspace name or ID of 
        include_set_contents 
    */
    typedef structure {
        string workspace;
        boolean include_set_contents;
    } ListSetParams;


    typedef structure {
        ws_obj_id ref;
        Workspace.object_info info;
    } SetItemInfo;

    typedef structure {
        Workspace.object_info info;
        list<SetItemInfo> items;
    } SetInfo;

    typedef structure {
        list <SetInfo> sets;
    } ListSetResult;

    /* Use to get the top-level sets in a WS. Optionally can include
    one level down members of those sets. */
    funcdef list_sets(ListSetParams params)
                returns (ListSetResult result) authentication optional;


    
    typedef structure {
        ws_obj_id ref;
        list <ws_obj_id> path_to_set;
    } SetReference;

    typedef structure {
        list <SetReference> SetReference;
    } GetSetItemsParams;

    typedef structure {
        list <SetInfo> sets;
    } GetSetItemsResult;

    /* Use to drill down into one or more sets, the position in the
    return 'sets' list will match the position in the input ref list */
    funcdef get_set_items(GetSetItemsParams params)
                returns (GetSetItemsResult result) authentication optional;

};
