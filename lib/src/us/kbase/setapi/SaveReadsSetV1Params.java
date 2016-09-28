
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
 * <p>Original spec-file type: SaveReadsSetV1Params</p>
 * <pre>
 * workspace_name or workspace_id - alternative options defining 
 *     target workspace,
 * output_object_name - workspace object name (this parameter is
 *     used together with one of workspace params from above),
 * output_ref - optional workspace reference to ReadsGroup object
 *     (alternative to previous params, this way is preferable when 
 *     group object already exists and saving operation overrides it).
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "workspace_name",
    "workspace_id",
    "output_object_name",
    "output_ref",
    "data"
})
public class SaveReadsSetV1Params {

    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("workspace_id")
    private Long workspaceId;
    @JsonProperty("output_object_name")
    private String outputObjectName;
    @JsonProperty("output_ref")
    private String outputRef;
    /**
     * <p>Original spec-file type: ReadsSet</p>
     * <pre>
     * @meta ws description as description
     * @meta ws length(items) as item_count
     * </pre>
     * 
     */
    @JsonProperty("data")
    private ReadsSet data;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("workspace_name")
    public String getWorkspaceName() {
        return workspaceName;
    }

    @JsonProperty("workspace_name")
    public void setWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
    }

    public SaveReadsSetV1Params withWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
        return this;
    }

    @JsonProperty("workspace_id")
    public Long getWorkspaceId() {
        return workspaceId;
    }

    @JsonProperty("workspace_id")
    public void setWorkspaceId(Long workspaceId) {
        this.workspaceId = workspaceId;
    }

    public SaveReadsSetV1Params withWorkspaceId(Long workspaceId) {
        this.workspaceId = workspaceId;
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

    public SaveReadsSetV1Params withOutputObjectName(String outputObjectName) {
        this.outputObjectName = outputObjectName;
        return this;
    }

    @JsonProperty("output_ref")
    public String getOutputRef() {
        return outputRef;
    }

    @JsonProperty("output_ref")
    public void setOutputRef(String outputRef) {
        this.outputRef = outputRef;
    }

    public SaveReadsSetV1Params withOutputRef(String outputRef) {
        this.outputRef = outputRef;
        return this;
    }

    /**
     * <p>Original spec-file type: ReadsSet</p>
     * <pre>
     * @meta ws description as description
     * @meta ws length(items) as item_count
     * </pre>
     * 
     */
    @JsonProperty("data")
    public ReadsSet getData() {
        return data;
    }

    /**
     * <p>Original spec-file type: ReadsSet</p>
     * <pre>
     * @meta ws description as description
     * @meta ws length(items) as item_count
     * </pre>
     * 
     */
    @JsonProperty("data")
    public void setData(ReadsSet data) {
        this.data = data;
    }

    public SaveReadsSetV1Params withData(ReadsSet data) {
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
        return ((((((((((((("SaveReadsSetV1Params"+" [workspaceName=")+ workspaceName)+", workspaceId=")+ workspaceId)+", outputObjectName=")+ outputObjectName)+", outputRef=")+ outputRef)+", data=")+ data)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
