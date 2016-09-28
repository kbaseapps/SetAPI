/*


*/
module KBaseSets {

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
        @optional label data_attachments
    */
    typedef structure {
        ws_reads_id ref;
        string label;
        list <DataAttachment> data_attachments;
    } ReadsSetItem;

    /*
        @meta ws description as description
        @meta ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<ReadsSetItem> items;
    } ReadsSet;

};