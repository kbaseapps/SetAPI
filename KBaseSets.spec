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

    /****************************** */
    /* FEATURESET SET */

    /*
        The workspace id for a FeatureSet data object.
        @id ws KBaseCollections.FeatureSet
    */
    typedef string ws_featureset_id;

    typedef structure {
        ws_featureset_id ref;
        string label;
    } FeatureSetSetItem;

    typedef structure {
        string description;
        list<FeatureSetSetItem> items;
    } FeatureSetSet;


    /****************************** */
    /* READS ALIGNMENTS SET */

    /*
        The workspace id for a ReadsAlignment data object.
        @id ws KBaseRNASeq.RNASeqAlignment
    */
    typedef string ws_reads_align_id;

    typedef structure {
        ws_reads_align_id ref;
        string label;
    } ReadsAlignmentSetItem;

    typedef structure {
        string description;
        list<ReadsAlignmentSetItem> items;
    } ReadsAlignmentSet;


    /****************************** */
    /* READS SET */

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
        @metadata ws description as description
        @metadata ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<ReadsSetItem> items;
    } ReadsSet;


    /****************************** */
    /* ASSEMBLY SET */

    /*
        The workspace ID for an Assembly data object.
        @id ws KBaseGenomeAnnotations.Assembly
    */
    typedef string ws_assembly_id;

    /* @optional label */
    typedef structure {
        ws_assembly_id ref;
        string label;
    } AssemblySetItem;

    /*
        @metadata ws description as description
        @metadata ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<AssemblySetItem> items;
    } AssemblySet;



    /*************************************************************** */
    /* GENOME SET */

    /*
        The workspace ID for a Genome data object.
        @id ws KBaseGenomes.Genome
    */
    typedef string ws_genome_id;

    /* @optional label */
    typedef structure {
        ws_genome_id ref;
        string label;
    } GenomeSetItem;

    /*
        @metadata ws description as description
        @metadata ws length(items) as item_count
    */
    typedef structure {
        string description;
        list<GenomeSetItem> items;
    } GenomeSet;

};
