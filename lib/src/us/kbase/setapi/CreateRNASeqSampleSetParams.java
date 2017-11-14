
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
 * <p>Original spec-file type: CreateRNASeqSampleSetParams</p>
 * <pre>
 * ******* Sample SET METHODS ************
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "ws_id",
    "sampleset_id",
    "sampleset_desc",
    "domain",
    "platform",
    "sample_ids",
    "condition",
    "source",
    "Library_type",
    "publication_id",
    "external_source_date"
})
public class CreateRNASeqSampleSetParams {

    @JsonProperty("ws_id")
    private java.lang.String wsId;
    @JsonProperty("sampleset_id")
    private java.lang.String samplesetId;
    @JsonProperty("sampleset_desc")
    private java.lang.String samplesetDesc;
    @JsonProperty("domain")
    private java.lang.String domain;
    @JsonProperty("platform")
    private java.lang.String platform;
    @JsonProperty("sample_ids")
    private List<String> sampleIds;
    @JsonProperty("condition")
    private List<String> condition;
    @JsonProperty("source")
    private java.lang.String source;
    @JsonProperty("Library_type")
    private java.lang.String LibraryType;
    @JsonProperty("publication_id")
    private java.lang.String publicationId;
    @JsonProperty("external_source_date")
    private java.lang.String externalSourceDate;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("ws_id")
    public java.lang.String getWsId() {
        return wsId;
    }

    @JsonProperty("ws_id")
    public void setWsId(java.lang.String wsId) {
        this.wsId = wsId;
    }

    public CreateRNASeqSampleSetParams withWsId(java.lang.String wsId) {
        this.wsId = wsId;
        return this;
    }

    @JsonProperty("sampleset_id")
    public java.lang.String getSamplesetId() {
        return samplesetId;
    }

    @JsonProperty("sampleset_id")
    public void setSamplesetId(java.lang.String samplesetId) {
        this.samplesetId = samplesetId;
    }

    public CreateRNASeqSampleSetParams withSamplesetId(java.lang.String samplesetId) {
        this.samplesetId = samplesetId;
        return this;
    }

    @JsonProperty("sampleset_desc")
    public java.lang.String getSamplesetDesc() {
        return samplesetDesc;
    }

    @JsonProperty("sampleset_desc")
    public void setSamplesetDesc(java.lang.String samplesetDesc) {
        this.samplesetDesc = samplesetDesc;
    }

    public CreateRNASeqSampleSetParams withSamplesetDesc(java.lang.String samplesetDesc) {
        this.samplesetDesc = samplesetDesc;
        return this;
    }

    @JsonProperty("domain")
    public java.lang.String getDomain() {
        return domain;
    }

    @JsonProperty("domain")
    public void setDomain(java.lang.String domain) {
        this.domain = domain;
    }

    public CreateRNASeqSampleSetParams withDomain(java.lang.String domain) {
        this.domain = domain;
        return this;
    }

    @JsonProperty("platform")
    public java.lang.String getPlatform() {
        return platform;
    }

    @JsonProperty("platform")
    public void setPlatform(java.lang.String platform) {
        this.platform = platform;
    }

    public CreateRNASeqSampleSetParams withPlatform(java.lang.String platform) {
        this.platform = platform;
        return this;
    }

    @JsonProperty("sample_ids")
    public List<String> getSampleIds() {
        return sampleIds;
    }

    @JsonProperty("sample_ids")
    public void setSampleIds(List<String> sampleIds) {
        this.sampleIds = sampleIds;
    }

    public CreateRNASeqSampleSetParams withSampleIds(List<String> sampleIds) {
        this.sampleIds = sampleIds;
        return this;
    }

    @JsonProperty("condition")
    public List<String> getCondition() {
        return condition;
    }

    @JsonProperty("condition")
    public void setCondition(List<String> condition) {
        this.condition = condition;
    }

    public CreateRNASeqSampleSetParams withCondition(List<String> condition) {
        this.condition = condition;
        return this;
    }

    @JsonProperty("source")
    public java.lang.String getSource() {
        return source;
    }

    @JsonProperty("source")
    public void setSource(java.lang.String source) {
        this.source = source;
    }

    public CreateRNASeqSampleSetParams withSource(java.lang.String source) {
        this.source = source;
        return this;
    }

    @JsonProperty("Library_type")
    public java.lang.String getLibraryType() {
        return LibraryType;
    }

    @JsonProperty("Library_type")
    public void setLibraryType(java.lang.String LibraryType) {
        this.LibraryType = LibraryType;
    }

    public CreateRNASeqSampleSetParams withLibraryType(java.lang.String LibraryType) {
        this.LibraryType = LibraryType;
        return this;
    }

    @JsonProperty("publication_id")
    public java.lang.String getPublicationId() {
        return publicationId;
    }

    @JsonProperty("publication_id")
    public void setPublicationId(java.lang.String publicationId) {
        this.publicationId = publicationId;
    }

    public CreateRNASeqSampleSetParams withPublicationId(java.lang.String publicationId) {
        this.publicationId = publicationId;
        return this;
    }

    @JsonProperty("external_source_date")
    public java.lang.String getExternalSourceDate() {
        return externalSourceDate;
    }

    @JsonProperty("external_source_date")
    public void setExternalSourceDate(java.lang.String externalSourceDate) {
        this.externalSourceDate = externalSourceDate;
    }

    public CreateRNASeqSampleSetParams withExternalSourceDate(java.lang.String externalSourceDate) {
        this.externalSourceDate = externalSourceDate;
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
        return ((((((((((((((((((((((((("CreateRNASeqSampleSetParams"+" [wsId=")+ wsId)+", samplesetId=")+ samplesetId)+", samplesetDesc=")+ samplesetDesc)+", domain=")+ domain)+", platform=")+ platform)+", sampleIds=")+ sampleIds)+", condition=")+ condition)+", source=")+ source)+", LibraryType=")+ LibraryType)+", publicationId=")+ publicationId)+", externalSourceDate=")+ externalSourceDate)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
