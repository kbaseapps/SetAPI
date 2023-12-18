"""Various strings used throughout the repo."""

INC_ITEM_INFO = "include_item_info"
INC_ITEM_REF_PATHS = "include_set_item_ref_paths"
REF_PATH_TO_SET = "ref_path_to_set"


ASSEMBLY = "assembly"
ASSEMBLY_SET = "KBaseSets.AssemblySet"
DIFFERENTIAL_EXPRESSION_MATRIX = "differential_expression_matrix"
DIFFERENTIAL_EXPRESSION_MATRIX_SET = "KBaseSets.DifferentialExpressionMatrixSet"
EXPRESSION = "expression"
EXPRESSION_SET = "KBaseSets.ExpressionSet"
FEATURE_SET = "feature_set"
FEATURE_SET_SET = "KBaseSets.FeatureSetSet"
GENOME = "genome"
GENOME_SET = "KBaseSets.GenomeSet"
GENOME_SEARCH = "genome_search"
GENOME_SEARCH_SET = "KBaseSearch.GenomeSet"
READS = "reads"
READS_SET = "KBaseSets.ReadsSet"
READS_ALIGNMENT = "reads_alignment"
READS_ALIGNMENT_SET = "KBaseSets.ReadsAlignmentSet"
RNASEQ_SAMPLE = "rnaseq_sample"
RNASEQ_SAMPLE_SET = "KBaseRNASeq.RNASeqSampleSet"

SAVE_SEARCH_SET = "save_search_set"

# the name of the object as it appears in the `save_***_set` and `get_***_set`
# methods and the corresponding KBase set type
SET_ITEM_NAME_TO_SET_TYPE = {
    ASSEMBLY: ASSEMBLY_SET,
    DIFFERENTIAL_EXPRESSION_MATRIX: DIFFERENTIAL_EXPRESSION_MATRIX_SET,
    EXPRESSION: EXPRESSION_SET,
    FEATURE_SET: FEATURE_SET_SET,
    GENOME: GENOME_SET,
    READS: READS_SET,
    READS_ALIGNMENT: READS_ALIGNMENT_SET,
    # exception: this uses `save_genome_set` / `get_genome_set`
    GENOME_SEARCH: GENOME_SEARCH_SET,
    # another exception: sample sets: `create_sample_set`, no official getter
    RNASEQ_SAMPLE: RNASEQ_SAMPLE_SET,
}
