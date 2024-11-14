package com.byalif.scraper.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Statistics {
     @JsonProperty("viewCount")
     private String viewCount;
     public String getViewCount() {
		return viewCount;
	}
	public void setViewCount(String viewCount) {
		this.viewCount = viewCount;
	}
	public String getLikeCount() {
		return likeCount;
	}
	public void setLikeCount(String likeCount) {
		this.likeCount = likeCount;
	}
	public String getFavoriteCount() {
		return favoriteCount;
	}
	public void setFavoriteCount(String favoriteCount) {
		this.favoriteCount = favoriteCount;
	}
	public String getCommentCount() {
		return CommentCount;
	}
	public void setCommentCount(String commentCount) {
		CommentCount = commentCount;
	}
	@JsonProperty("likeCount")
     private String likeCount;
     @JsonProperty("favoriteCount")
     private String favoriteCount;
     @JsonProperty("CommentCount")
     private String CommentCount;
}
