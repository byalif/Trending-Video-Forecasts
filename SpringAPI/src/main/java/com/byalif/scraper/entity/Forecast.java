package com.byalif.scraper.entity;

import java.sql.Timestamp;
import java.util.List;

import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;


public class Forecast {
    private Long id;

    private String artistType;
    private Double currentViews;
    private Integer fastestRisersRank;
    private Double growthRate;
    private Integer growthRateRank;
    private Double growthSpeed;
    private Double projectedGrowth;
    private Integer topPotentialRank;
    //@Column(name = "timestamp", nullable = false, updatable = false, insertable = false, columnDefinition = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    private Timestamp timestamp;

    // Getters and setters
    public Timestamp getTimestamp() {
        return timestamp;
    }

    @ElementCollection
    private List<Double> forecastValues;

    // Getters and Setters

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getArtistType() {
        return artistType;
    }

    public void setArtistType(String artistType) {
        this.artistType = artistType;
    }

    public Double getCurrentViews() {
        return currentViews;
    }

    public void setCurrentViews(Double currentViews) {
        this.currentViews = currentViews;
    }

    public Integer getFastestRisersRank() {
        return fastestRisersRank;
    }

    public void setFastestRisersRank(Integer fastestRisersRank) {
        this.fastestRisersRank = fastestRisersRank;
    }

    public Double getGrowthRate() {
        return growthRate;
    }

    public void setGrowthRate(Double growthRate) {
        this.growthRate = growthRate;
    }

    public Integer getGrowthRateRank() {
        return growthRateRank;
    }

    public void setGrowthRateRank(Integer growthRateRank) {
        this.growthRateRank = growthRateRank;
    }

    public Double getGrowthSpeed() {
        return growthSpeed;
    }

    public void setGrowthSpeed(Double growthSpeed) {
        this.growthSpeed = growthSpeed;
    }

    public Double getProjectedGrowth() {
        return projectedGrowth;
    }

    public void setProjectedGrowth(Double projectedGrowth) {
        this.projectedGrowth = projectedGrowth;
    }

    public Integer getTopPotentialRank() {
        return topPotentialRank;
    }

    public void setTopPotentialRank(Integer topPotentialRank) {
        this.topPotentialRank = topPotentialRank;
    }

    public List<Double> getForecastValues() {
        return forecastValues;
    }

    public void setForecastValues(List<Double> forecastValues) {
        this.forecastValues = forecastValues;
    }
}
