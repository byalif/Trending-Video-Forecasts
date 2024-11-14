package com.byalif.scraper.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.byalif.scraper.entity.Metrics;
import com.byalif.scraper.entity.Video;
import com.byalif.scraper.repository.MetricsRepository;
import com.byalif.scraper.repository.VideoRepository;

@Service
public class VideoMetricService {

    @Autowired
    private VideoRepository videoRepository;

    @Autowired
    private MetricsRepository metricsRepository;

    public void saveVideoData(Video videoData, Metrics metricsData) {
        // Check if the video already exists in the database
        Video existingVideo = videoRepository.findById(videoData.getVideoId()).orElse(null);
        if (existingVideo == null) {
            // If the video doesn't exist, save the video data
            existingVideo = videoRepository.save(videoData);
        }

        // Link the metrics entry to the existing video
        metricsData.setVideo(existingVideo);
        metricsRepository.save(metricsData);
    }
}
