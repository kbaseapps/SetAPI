
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
 * raw_data_palettes - optional DP output turned on by 'include_raw_data_palettes'
 *     in input parameters,
 * raw_data_palette_refs - optional DP output (mapping from workspace Id to reference
 *     to DataPalette container existing in particular workspace) turned on by
 *     'include_raw_data_palettes' in input parameters,
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "sets",
    "raw_data_palettes",
    "raw_data_palette_refs"
})
public class ListSetResult {

    @JsonProperty("sets")
    private List<SetInfo> sets;
    @JsonProperty("raw_data_palettes")
    private List<DataInfo> rawDataPalettes;
    @JsonProperty("raw_data_palette_refs")
    private Map<String, String> rawDataPaletteRefs;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

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

    @JsonProperty("raw_data_palette_refs")
    public Map<String, String> getRawDataPaletteRefs() {
        return rawDataPaletteRefs;
    }

    @JsonProperty("raw_data_palette_refs")
    public void setRawDataPaletteRefs(Map<String, String> rawDataPaletteRefs) {
        this.rawDataPaletteRefs = rawDataPaletteRefs;
    }

    public ListSetResult withRawDataPaletteRefs(Map<String, String> rawDataPaletteRefs) {
        this.rawDataPaletteRefs = rawDataPaletteRefs;
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
        return ((((((((("ListSetResult"+" [sets=")+ sets)+", rawDataPalettes=")+ rawDataPalettes)+", rawDataPaletteRefs=")+ rawDataPaletteRefs)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
