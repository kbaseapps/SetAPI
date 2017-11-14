
package us.kbase.setapi;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import us.kbase.common.service.Tuple11;


/**
 * <p>Original spec-file type: GenomeSetItem</p>
 * <pre>
 * When saving an GenomeSet, only 'ref' is required.
 * You should never set 'info'.  'info' is provided optionally when fetching
 * the GenomeSet.
 * ref_path is optionally returned by get_genome_set_v1()
 * when its input parameter 'include_set_item_ref_paths' is set to 1.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "ref",
    "ref_path",
    "label",
    "info"
})
public class GenomeSetItem {

    @JsonProperty("ref")
    private java.lang.String ref;
    @JsonProperty("ref_path")
    private java.lang.String refPath;
    @JsonProperty("label")
    private java.lang.String label;
    @JsonProperty("info")
    private Tuple11 <Long, String, String, String, Long, String, Long, String, String, Long, Map<String, String>> info;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("ref")
    public java.lang.String getRef() {
        return ref;
    }

    @JsonProperty("ref")
    public void setRef(java.lang.String ref) {
        this.ref = ref;
    }

    public GenomeSetItem withRef(java.lang.String ref) {
        this.ref = ref;
        return this;
    }

    @JsonProperty("ref_path")
    public java.lang.String getRefPath() {
        return refPath;
    }

    @JsonProperty("ref_path")
    public void setRefPath(java.lang.String refPath) {
        this.refPath = refPath;
    }

    public GenomeSetItem withRefPath(java.lang.String refPath) {
        this.refPath = refPath;
        return this;
    }

    @JsonProperty("label")
    public java.lang.String getLabel() {
        return label;
    }

    @JsonProperty("label")
    public void setLabel(java.lang.String label) {
        this.label = label;
    }

    public GenomeSetItem withLabel(java.lang.String label) {
        this.label = label;
        return this;
    }

    @JsonProperty("info")
    public Tuple11 <Long, String, String, String, Long, String, Long, String, String, Long, Map<String, String>> getInfo() {
        return info;
    }

    @JsonProperty("info")
    public void setInfo(Tuple11 <Long, String, String, String, Long, String, Long, String, String, Long, Map<String, String>> info) {
        this.info = info;
    }

    public GenomeSetItem withInfo(Tuple11 <Long, String, String, String, Long, String, Long, String, String, Long, Map<String, String>> info) {
        this.info = info;
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
        return ((((((((((("GenomeSetItem"+" [ref=")+ ref)+", refPath=")+ refPath)+", label=")+ label)+", info=")+ info)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
