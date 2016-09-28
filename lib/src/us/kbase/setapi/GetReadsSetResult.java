
package us.kbase.setapi;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import us.kbase.kbasesets.ReadsSet;


/**
 * <p>Original spec-file type: GetReadsSetResult</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "data"
})
public class GetReadsSetResult {

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

    public GetReadsSetResult withData(ReadsSet data) {
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
        return ((((("GetReadsSetResult"+" [data=")+ data)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
