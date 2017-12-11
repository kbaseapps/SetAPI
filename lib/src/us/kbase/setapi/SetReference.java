
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
 * <p>Original spec-file type: SetReference</p>
 * <pre>
 * include_set_item_ref_paths - 1 or 0, if 1, additionally provides ref_path for each item
 *                     in the set. The ref_path for each item is either
 *                         ref_path_to_set;item_ref  (if ref_path_to_set is given) or
 *                         set_ref;item_ref
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "ref",
    "ref_path_to_set"
})
public class SetReference {

    @JsonProperty("ref")
    private java.lang.String ref;
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

    public SetReference withRef(java.lang.String ref) {
        this.ref = ref;
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

    public SetReference withRefPathToSet(List<String> refPathToSet) {
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
        return ((((((("SetReference"+" [ref=")+ ref)+", refPathToSet=")+ refPathToSet)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
