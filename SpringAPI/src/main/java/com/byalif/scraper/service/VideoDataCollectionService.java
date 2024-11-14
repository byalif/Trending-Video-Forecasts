package com.byalif.scraper.service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.byalif.scraper.entity.Metrics;
import com.byalif.scraper.entity.Video;
import com.byalif.scraper.models.Snippet;
import com.byalif.scraper.models.VideoItem;
import com.byalif.scraper.models.VideoResponse;
import com.byalif.scraper.models.YoutubeResponse;

@Service
public class VideoDataCollectionService {

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private VideoMetricService videoMetricsService;

    private final String API_KEY = "AIzaSyDbv58AOz4AIbgHUEjBFt3mfMr1XUCFVqY"; // Replace with your actual API key
    private final String SEARCH_URL = "https://www.googleapis.com/youtube/v3/search?part=snippet&q=type+beat&maxResults=30&key="
            + API_KEY;
    private final String VIDEO_DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=%s&key="
            + API_KEY;

    // Scheduled method that runs every 6 hours
    @Scheduled(fixedRate = 3600000) // Every 6 hours (6 * 60 * 60 * 1000 ms)
    public void collectAndStoreMetrics() {
        try {
            // Step 1: Retrieve search results to get video IDs
            YoutubeResponse searchResponse = restTemplate.getForObject(SEARCH_URL, YoutubeResponse.class);
            List<String> videoIds = searchResponse.getItems().stream()
                    .map(item -> item.getId().getVideoId())
                    .collect(Collectors.toList());

            // Create a map for Snippets using videoId as key
            Map<String, Snippet> snippetMap = searchResponse.getItems().stream()
                    .collect(Collectors.toMap(item -> item.getId().getVideoId(), item -> item.getSnippet()));

            // Step 2: Fetch detailed data including statistics
            String videoIdsParam = String.join(",", videoIds);
            String videoDetailsUrl = String.format(VIDEO_DETAILS_URL, videoIdsParam);
            VideoResponse videoResponse = restTemplate.getForObject(videoDetailsUrl, VideoResponse.class);

            // Step 3: Save video and metrics data
            for (VideoItem item : videoResponse.getItems()) {
                // Use video ID to get snippet data
                Snippet snippet = snippetMap.get(item.getId());

                Video videoData = new Video();
                videoData.setVideoId(item.getId());
                videoData.setTitle(snippet.getTitle());
                videoData.setChannelTitle(snippet.getChannelTitle());
                videoData.setPublishedAt(snippet.getPublishedAt());

                Metrics metricsData = new Metrics();
                metricsData.setViewCount(Integer.parseInt(item.getStatistics().getViewCount()));
                metricsData.setLikeCount(Integer.parseInt(item.getStatistics().getLikeCount()));
                metricsData.setFavoriteCount(Integer.parseInt(item.getStatistics().getFavoriteCount()));
                metricsData.setCommentCount(Integer.parseInt(item.getStatistics().getCommentCount()));
                metricsData.setTimestamp(LocalDateTime.now());

                // Save data to the database
                videoMetricsService.saveVideoData(videoData, metricsData);
            }

            System.out.println("Data collection and storage complete at " + LocalDateTime.now());
            System.out.println("Status: 200");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
