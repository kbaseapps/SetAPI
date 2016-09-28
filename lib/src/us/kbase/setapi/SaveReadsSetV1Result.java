
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
 * <p>Original spec-file type: SaveReadsSetV1Result</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "set_ref"
})
public class SaveReadsSetV1Result {

    @JsonProperty("set_ref")
    private String setRef;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("set_ref")
    public String getSetRef() {
        return setRef;
    }

    @JsonProperty("set_ref")
    public void setSetRef(String setRef) {
        this.setRef = setRef;
    }

    public SaveReadsSetV1Result withSetRef(String setRef) {
        this.setRef = setRef;
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
        return ((((("SaveReadsSetV1Result"+" [setRef=")+ setRef)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
