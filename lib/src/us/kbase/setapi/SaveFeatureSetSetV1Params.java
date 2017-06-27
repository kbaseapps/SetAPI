
package us.kbase.setapi;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: SaveFeatureSetSetV1Params</p>
 * <pre>
 * workspace_name or workspace_id - alternative options defining
 *     target workspace,
 * output_object_name - workspace object name (this parameter is
 *     used together with one of workspace params from above)
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "workspace",
    "output_object_name",
    "data"
})
public class SaveFeatureSetSetV1Params {

    @JsonProperty("workspace")
    private String workspace;
    @JsonProperty("output_object_name")
    private String outputObjectName;
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
    @JsonProperty("data")
    private FeatureSetSet data;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("workspace")
    public String getWorkspace() {
        return workspace;
    }

    @JsonProperty("workspace")
    public void setWorkspace(String workspace) {
        this.workspace = workspace;
    }

    public SaveFeatureSetSetV1Params withWorkspace(String workspace) {
        this.workspace = workspace;
        return this;
    }

    @JsonProperty("output_object_name")
    public String getOutputObjectName() {
        return outputObjectName;
    }

    @JsonProperty("output_object_name")
    public void setOutputObjectName(String outputObjectName) {
        this.outputObjectName = outputObjectName;
    }

    public SaveFeatureSetSetV1Params withOutputObjectName(String outputObjectName) {
        this.outputObjectName = outputObjectName;
        return this;
    }

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
    @JsonProperty("data")
    public FeatureSetSet getData() {
        return data;
    }

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
    @JsonProperty("data")
    public void setData(FeatureSetSet data) {
        this.data = data;
    }

    public SaveFeatureSetSetV1Params withData(FeatureSetSet data) {
        this.data = data;
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
        return ((((((((("SaveFeatureSetSetV1Params"+" [workspace=")+ workspace)+", outputObjectName=")+ outputObjectName)+", data=")+ data)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
