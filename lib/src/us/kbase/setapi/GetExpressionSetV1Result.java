
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
 * <p>Original spec-file type: GetExpressionSetV1Result</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "data",
    "info"
})
public class GetExpressionSetV1Result {

    /**
     * <p>Original spec-file type: ExpressionSet</p>
     * <pre>
     * When building a ExpressionSet, all Expression objects must be aligned against the same
     * genome. This is not part of the object type, but enforced during a call to
     * save_expression_set_v1.
     * @meta ws description as description
     * @meta ws length(items) as item_count
     * </pre>
     * 
     */
    @JsonProperty("data")
    private ExpressionSet data;
    @JsonProperty("info")
    private Tuple11 <Long, String, String, String, Long, String, Long, String, String, Long, Map<String, String>> info;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    /**
     * <p>Original spec-file type: ExpressionSet</p>
     * <pre>
     * When building a ExpressionSet, all Expression objects must be aligned against the same
     * genome. This is not part of the object type, but enforced during a call to
     * save_expression_set_v1.
     * @meta ws description as description
     * @meta ws length(items) as item_count
     * </pre>
     * 
     */
    @JsonProperty("data")
    public ExpressionSet getData() {
        return data;
    }

    /**
     * <p>Original spec-file type: ExpressionSet</p>
     * <pre>
     * When building a ExpressionSet, all Expression objects must be aligned against the same
     * genome. This is not part of the object type, but enforced during a call to
     * save_expression_set_v1.
     * @meta ws description as description
     * @meta ws length(items) as item_count
     * </pre>
     * 
     */
    @JsonProperty("data")
    public void setData(ExpressionSet data) {
        this.data = data;
    }

    public GetExpressionSetV1Result withData(ExpressionSet data) {
        this.data = data;
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

    public GetExpressionSetV1Result withInfo(Tuple11 <Long, String, String, String, Long, String, Long, String, String, Long, Map<String, String>> info) {
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
        return ((((((("GetExpressionSetV1Result"+" [data=")+ data)+", info=")+ info)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
