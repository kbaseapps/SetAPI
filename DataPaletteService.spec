
#include <workspace.spec>

/*

*/
module DataPaletteService {

    /* @id ws */
    typedef string ws_ref;

    typedef structure {
        ws_ref ref;
        Workspace.object_info info;
    } DataInfo;

    typedef structure {
        list <DataInfo> data;
    } DataList;


    typedef string ws_name_or_id;

    /* todo: pagination? */
    typedef structure {
        list <ws_name_or_id> workspaces;
    } ListDataParams;

    funcdef list_data(ListDataParams params)
        returns (DataList data_list) authentication optional;


    /* todo: allow passing in a reference chain */
    typedef structure {
        ws_ref ref;
    } ObjectReference;

    typedef structure {
        ws_name_or_id workspace;
        list <ObjectReference> new_refs;
    } AddToPaletteParams;

    typedef structure {
    } AddToPaletteResult;

    funcdef add_to_palette(AddToPaletteParams params)
        returns (AddToPaletteResult result) authentication required;


    typedef structure {
        ws_name_or_id workspace;
        list <ws_ref> refs;
    } RemoveFromPaletteParams;

    typedef structure {
    } RemoveFromPaletteResult;

    /* Note: right now you must provide the exact, absolute reference of the
    item to delete (e.g. 2524/3/1) and matched exactly to be removed.  Relative
    refs will not be matched.  Currently, this method will throw an error
    if a provided reference was not found in the palette. */
    funcdef remove_from_palette(RemoveFromPaletteParams params)
        returns (RemoveFromPaletteResult result) authentication required;


    typedef structure {
        ws_name_or_id from_workspace;
        ws_name_or_id to_workspace;
    } CopyPaletteParams;


    typedef structure {
    } CopyPaletteResult;

    funcdef copy_palette(CopyPaletteParams params)
        returns (CopyPaletteResult result) authentication required;


    typedef structure {
        ws_name_or_id workspace;
        string palette_name_or_id;
    } SetPaletteForWsParams;

    typedef structure {

    } SetPaletteForWsResult;

    /* In case the WS metadata is corrupted, or there was a manual
    setup of the data palette, this function can be used to set
    the workspace metadata to the specified palette in that workspace
    by name or ID.  If you omit the name_or_id, then the code will
    search for an existing data palette in that workspace.  Be careful
    with this one- you could thrash your palette! */
    funcdef set_palette_for_ws(SetPaletteForWsParams params)
        returns (SetPaletteForWsResult result) authentication required;
};
