
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
 * <p>Original spec-file type: FeatureSetSet</p>
 * <pre>
 * When building a FeatureSetSet, all FeatureSets must be aligned against the same
 * genome. This is not part of the object type, but enforced during a call to
 * save_featureset_set_v1.
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
public class FeatureSetSet {

    @JsonProperty("description")
    private String description;
    @JsonProperty("items")
    private List<FeatureSetSetItem> items;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("description")
    public String getDescription() {
        return description;
    }

    @JsonProperty("description")
    public void setDescription(String description) {
        this.description = description;
    }

    public FeatureSetSet withDescription(String description) {
        this.description = description;
        return this;
    }

    @JsonProperty("items")
    public List<FeatureSetSetItem> getItems() {
        return items;
    }

    @JsonProperty("items")
    public void setItems(List<FeatureSetSetItem> items) {
        this.items = items;
    }

    public FeatureSetSet withItems(List<FeatureSetSetItem> items) {
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
        return ((((((("FeatureSetSet"+" [description=")+ description)+", items=")+ items)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
