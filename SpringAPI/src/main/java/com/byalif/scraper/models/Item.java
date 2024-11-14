package com.byalif.scraper.models;


public class Item {
	private String kind;
	private String etag;
    private Id id;
    private Snippet snippet;
    private Statistics statistics; // Add statistics here
    
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

	public Snippet getSnippet() {
		return snippet;
	}

	public void setSnippet(Snippet snippet) {
		this.snippet = snippet;
	}

	public Statistics getStatistics() {
		return statistics;
	}

	public void setStatistics(Statistics statistics) {
		this.statistics = statistics;
	}

	public void setId(Id id) {
		this.id = id;
	}

	public Id getId() {
		return id;
	}
}
