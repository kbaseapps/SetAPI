
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
 * <p>Original spec-file type: GetSetItemsParams</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "set_refs",
    "include_set_item_ref_paths"
})
public class GetSetItemsParams {

    @JsonProperty("set_refs")
    private List<SetReference> setRefs;
    @JsonProperty("include_set_item_ref_paths")
    private Long includeSetItemRefPaths;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("set_refs")
    public List<SetReference> getSetRefs() {
        return setRefs;
    }

    @JsonProperty("set_refs")
    public void setSetRefs(List<SetReference> setRefs) {
        this.setRefs = setRefs;
    }

    public GetSetItemsParams withSetRefs(List<SetReference> setRefs) {
        this.setRefs = setRefs;
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

    public GetSetItemsParams withIncludeSetItemRefPaths(Long includeSetItemRefPaths) {
        this.includeSetItemRefPaths = includeSetItemRefPaths;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((("GetSetItemsParams"+" [setRefs=")+ setRefs)+", includeSetItemRefPaths=")+ includeSetItemRefPaths)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
