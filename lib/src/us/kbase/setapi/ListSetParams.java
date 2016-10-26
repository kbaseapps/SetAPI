
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
 * <p>Original spec-file type: ListSetParams</p>
 * <pre>
 * workspace - workspace name or ID (alternative to
 *     workspaces parameter),
 * workspaces - list of workspace name ot ID (alternative to
 *     workspace parameter).
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "workspace",
    "workspaces",
    "include_set_item_info"
})
public class ListSetParams {

    @JsonProperty("workspace")
    private String workspace;
    @JsonProperty("workspaces")
    private String workspaces;
    @JsonProperty("include_set_item_info")
    private Long includeSetItemInfo;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("workspace")
    public String getWorkspace() {
        return workspace;
    }

    @JsonProperty("workspace")
    public void setWorkspace(String workspace) {
        this.workspace = workspace;
    }

    public ListSetParams withWorkspace(String workspace) {
        this.workspace = workspace;
        return this;
    }

    @JsonProperty("workspaces")
    public String getWorkspaces() {
        return workspaces;
    }

    @JsonProperty("workspaces")
    public void setWorkspaces(String workspaces) {
        this.workspaces = workspaces;
    }

    public ListSetParams withWorkspaces(String workspaces) {
        this.workspaces = workspaces;
        return this;
    }

    @JsonProperty("include_set_item_info")
    public Long getIncludeSetItemInfo() {
        return includeSetItemInfo;
    }

    @JsonProperty("include_set_item_info")
    public void setIncludeSetItemInfo(Long includeSetItemInfo) {
        this.includeSetItemInfo = includeSetItemInfo;
    }

    public ListSetParams withIncludeSetItemInfo(Long includeSetItemInfo) {
        this.includeSetItemInfo = includeSetItemInfo;
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
        return ((((((((("ListSetParams"+" [workspace=")+ workspace)+", workspaces=")+ workspaces)+", includeSetItemInfo=")+ includeSetItemInfo)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
