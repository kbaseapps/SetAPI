
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
import us.kbase.datapaletteservice.DataInfo;


/**
 * <p>Original spec-file type: ListSetResult</p>
 * <pre>
 * raw_data_palettes - optional output turned on by 'include_raw_data_palettes'
 *     in input parameters.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "sets",
    "raw_data_palettes"
})
public class ListSetResult {

    @JsonProperty("sets")
    private List<SetInfo> sets;
    @JsonProperty("raw_data_palettes")
    private List<DataInfo> rawDataPalettes;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("sets")
    public List<SetInfo> getSets() {
        return sets;
    }

    @JsonProperty("sets")
    public void setSets(List<SetInfo> sets) {
        this.sets = sets;
    }

    public ListSetResult withSets(List<SetInfo> sets) {
        this.sets = sets;
        return this;
    }

    @JsonProperty("raw_data_palettes")
    public List<DataInfo> getRawDataPalettes() {
        return rawDataPalettes;
    }

    @JsonProperty("raw_data_palettes")
    public void setRawDataPalettes(List<DataInfo> rawDataPalettes) {
        this.rawDataPalettes = rawDataPalettes;
    }

    public ListSetResult withRawDataPalettes(List<DataInfo> rawDataPalettes) {
        this.rawDataPalettes = rawDataPalettes;
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
        return ((((((("ListSetResult"+" [sets=")+ sets)+", rawDataPalettes=")+ rawDataPalettes)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
