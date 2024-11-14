package com.byalif.scraper.entity;
import java.util.List;

import jakarta.persistence.*;

@Entity
@Table(name = "videos")
public class Video {
    
    @Id
    @Column(name = "video_id", nullable = false, unique = true)
    private String videoId;

    @Column(name = "title")
    private String title;

    @Column(name = "channel_title")
    private String channelTitle;

    @Column(name = "published_at")
    private String publishedAt;

    // Relationship to Metrics (One-to-Many)
    @OneToMany(mappedBy = "video", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Metrics> metrics;

    // Getters and Setters
    public String getVideoId() {
        return videoId;
    }

    public void setVideoId(String videoId) {
        this.videoId = videoId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getChannelTitle() {
        return channelTitle;
    }

    public void setChannelTitle(String channelTitle) {
        this.channelTitle = channelTitle;
    }

    public String getPublishedAt() {
        return publishedAt;
    }

    public void setPublishedAt(String publishedAt) {
        this.publishedAt = publishedAt;
    }

    public List<Metrics> getMetrics() {
        return metrics;
    }

    public void setMetrics(List<Metrics> metrics) {
        this.metrics = metrics;
    }
}
