package com.byalif.scraper.service;

import java.util.List;

import com.byalif.scraper.entity.Forecast;

public class ArtistForecastResponse {
    private String message;
    private List<Forecast> rankedArtistData;
    private List<String> topRecommendations;

    // Getters and Setters

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public List<Forecast> getRankedArtistData() {
        return rankedArtistData;
    }

    public void setRankedArtistData(List<Forecast> rankedArtistData) {
        this.rankedArtistData = rankedArtistData;
    }

    public List<String> getTopRecommendations() {
        return topRecommendations;
    }

    public void setTopRecommendations(List<String> topRecommendations) {
        this.topRecommendations = topRecommendations;
    }
}
