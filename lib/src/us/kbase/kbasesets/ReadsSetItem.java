
package us.kbase.kbasesets;

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
 * <p>Original spec-file type: ReadsSetItem</p>
 * <pre>
 * @optional label data_attachments
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "ref",
    "label",
    "data_attachments"
})
public class ReadsSetItem {

    @JsonProperty("ref")
    private String ref;
    @JsonProperty("label")
    private String label;
    @JsonProperty("data_attachments")
    private List<DataAttachment> dataAttachments;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("ref")
    public String getRef() {
        return ref;
    }

    @JsonProperty("ref")
    public void setRef(String ref) {
        this.ref = ref;
    }

    public ReadsSetItem withRef(String ref) {
        this.ref = ref;
        return this;
    }

    @JsonProperty("label")
    public String getLabel() {
        return label;
    }

    @JsonProperty("label")
    public void setLabel(String label) {
        this.label = label;
    }

    public ReadsSetItem withLabel(String label) {
        this.label = label;
        return this;
    }

    @JsonProperty("data_attachments")
    public List<DataAttachment> getDataAttachments() {
        return dataAttachments;
    }

    @JsonProperty("data_attachments")
    public void setDataAttachments(List<DataAttachment> dataAttachments) {
        this.dataAttachments = dataAttachments;
    }

    public ReadsSetItem withDataAttachments(List<DataAttachment> dataAttachments) {
        this.dataAttachments = dataAttachments;
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
        return ((((((((("ReadsSetItem"+" [ref=")+ ref)+", label=")+ label)+", dataAttachments=")+ dataAttachments)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
