
package us.kbase.setapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: GetReadsSetV1Params</p>
 * <pre>
 * ref - workspace reference to ReadsGroup object.
 * include_item_info - 1 or 0, if 1 additionally provides workspace info (with
 *                     metadata) for each Reads object in the Set
 * include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
 *                              in the set. The ref_path returned for each item is either
 *                                  ref_path_to_set;item_ref  (if ref_path_to_set is given) or
 *                                  set_ref;item_ref  (if ref_path_to_set is not given)
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "ref",
    "include_item_info",
    "include_set_item_ref_paths",
    "ref_path_to_set"
})
public class GetReadsSetV1Params {

    @JsonProperty("ref")
    private java.lang.String ref;
    @JsonProperty("include_item_info")
    private Long includeItemInfo;
    @JsonProperty("include_set_item_ref_paths")
    private Long includeSetItemRefPaths;
    @JsonProperty("ref_path_to_set")
    private List<String> refPathToSet;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("ref")
    public java.lang.String getRef() {
        return ref;
    }

    @JsonProperty("ref")
    public void setRef(java.lang.String ref) {
        this.ref = ref;
    }

    public GetReadsSetV1Params withRef(java.lang.String ref) {
        this.ref = ref;
        return this;
    }

    @JsonProperty("include_item_info")
    public Long getIncludeItemInfo() {
        return includeItemInfo;
    }

    @JsonProperty("include_item_info")
    public void setIncludeItemInfo(Long includeItemInfo) {
        this.includeItemInfo = includeItemInfo;
    }

    public GetReadsSetV1Params withIncludeItemInfo(Long includeItemInfo) {
        this.includeItemInfo = includeItemInfo;
        return this;
    }

    @JsonProperty("include_set_item_ref_paths")
    public Long getIncludeSetItemRefPaths() {
        return includeSetItemRefPaths;
    }

    @JsonProperty("include_set_item_ref_paths")
    public void setIncludeSetItemRefPaths(Long includeSetItemRefPaths) {
        this.includeSetItemRefPaths = includeSetItemRefPaths;
    }

    public GetReadsSetV1Params withIncludeSetItemRefPaths(Long includeSetItemRefPaths) {
        this.includeSetItemRefPaths = includeSetItemRefPaths;
        return this;
    }

    @JsonProperty("ref_path_to_set")
    public List<String> getRefPathToSet() {
        return refPathToSet;
    }

    @JsonProperty("ref_path_to_set")
    public void setRefPathToSet(List<String> refPathToSet) {
        this.refPathToSet = refPathToSet;
    }

    public GetReadsSetV1Params withRefPathToSet(List<String> refPathToSet) {
        this.refPathToSet = refPathToSet;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((((("GetReadsSetV1Params"+" [ref=")+ ref)+", includeItemInfo=")+ includeItemInfo)+", includeSetItemRefPaths=")+ includeSetItemRefPaths)+", refPathToSet=")+ refPathToSet)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
