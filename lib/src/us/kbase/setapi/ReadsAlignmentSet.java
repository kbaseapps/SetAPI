
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
 * <p>Original spec-file type: ReadsAlignmentSet</p>
 * <pre>
 * When building a ReadsAlignmentSet, all ReadsAlignments must be aligned against the same
 * genome. This is not part of the object type, but enforced during a call to
 * save_reads_alignment_v1.
 * @meta ws description as description
 * @meta ws length(items) as item_count
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "description",
    "items"
})
public class ReadsAlignmentSet {

    @JsonProperty("description")
    private String description;
    @JsonProperty("items")
    private List<ReadsAlignmentSetItem> items;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("description")
    public String getDescription() {
        return description;
    }

    @JsonProperty("description")
    public void setDescription(String description) {
        this.description = description;
    }

    public ReadsAlignmentSet withDescription(String description) {
        this.description = description;
        return this;
    }

    @JsonProperty("items")
    public List<ReadsAlignmentSetItem> getItems() {
        return items;
    }

    @JsonProperty("items")
    public void setItems(List<ReadsAlignmentSetItem> items) {
        this.items = items;
    }

    public ReadsAlignmentSet withItems(List<ReadsAlignmentSetItem> items) {
        this.items = items;
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
        return ((((((("ReadsAlignmentSet"+" [description=")+ description)+", items=")+ items)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
