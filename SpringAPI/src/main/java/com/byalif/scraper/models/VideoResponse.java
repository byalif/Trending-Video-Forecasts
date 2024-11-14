package com.byalif.scraper.models;
import java.util.List;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

@Data
@Getter
@Setter
@AllArgsConstructor
public class VideoResponse {
    private String kind;
    private String etag;
    private String nextPageToken;
	private String regionCode;
    private List<VideoItem> items;
    public String getKind() {
		return kind;
	}
	public void setKind(String kind) {
		this.kind = kind;
	}
	public String getEtag() {
		return etag;
	}
	public void setEtag(String etag) {
		this.etag = etag;
	}
	public String getNextPageToken() {
		return nextPageToken;
	}
	public void setNextPageToken(String nextPageToken) {
		this.nextPageToken = nextPageToken;
	}
	public String getRegionCode() {
		return regionCode;
	}
	public void setRegionCode(String regionCode) {
		this.regionCode = regionCode;
	}
	public void setItems(List<VideoItem> items) {
		this.items = items;
	}
	public List<VideoItem> getItems() {
		// TODO Auto-generated method stub
		return items;
	}
}
