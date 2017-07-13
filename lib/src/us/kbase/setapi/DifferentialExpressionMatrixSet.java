
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
 * <p>Original spec-file type: DifferentialExpressionMatrixSet</p>
 * <pre>
 * When building a DifferentialExpressionMatrixSet, all DifferentialExpressionMatrices must be
 * built against the same genome. This is not part of the object type, but enforced during a
 * call to save_differential_expression_matrix_set_v1.
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
public class DifferentialExpressionMatrixSet {

    @JsonProperty("description")
    private String description;
    @JsonProperty("items")
    private List<DifferentialExpressionMatrixSetItem> items;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("description")
    public String getDescription() {
        return description;
    }

    @JsonProperty("description")
    public void setDescription(String description) {
        this.description = description;
    }

    public DifferentialExpressionMatrixSet withDescription(String description) {
        this.description = description;
        return this;
    }

    @JsonProperty("items")
    public List<DifferentialExpressionMatrixSetItem> getItems() {
        return items;
    }

    @JsonProperty("items")
    public void setItems(List<DifferentialExpressionMatrixSetItem> items) {
        this.items = items;
    }

    public DifferentialExpressionMatrixSet withItems(List<DifferentialExpressionMatrixSetItem> items) {
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
        return ((((((("DifferentialExpressionMatrixSet"+" [description=")+ description)+", items=")+ items)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
