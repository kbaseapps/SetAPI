
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
    "SetReference"
})
public class GetSetItemsParams {

    @JsonProperty("SetReference")
    private List<us.kbase.setapi.SetReference> SetReference;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("SetReference")
    public List<us.kbase.setapi.SetReference> getSetReference() {
        return SetReference;
    }

    @JsonProperty("SetReference")
    public void setSetReference(List<us.kbase.setapi.SetReference> SetReference) {
        this.SetReference = SetReference;
    }

    public GetSetItemsParams withSetReference(List<us.kbase.setapi.SetReference> SetReference) {
        this.SetReference = SetReference;
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
        return ((((("GetSetItemsParams"+" [SetReference=")+ SetReference)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
