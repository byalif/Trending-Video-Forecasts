package com.byalif.scraper.controller;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import com.byalif.scraper.models.Item;
import com.byalif.scraper.models.Snippet;
import com.byalif.scraper.models.VideoResponse;
import com.byalif.scraper.models.YoutubeResponse;

@RestController
public class ScarperController {

	@Autowired
	RestTemplate restTemplate;

	private final String apiKey = "";
	private final String baseUrl = "https://www.googleapis.com/youtube/v3/search";
	private final String videosUrl = "https://www.googleapis.com/youtube/v3/videos";

	@GetMapping("/searchTypeBeats")
	public ResponseEntity<Object> searchTypeBeats(@RequestParam String query,
			@RequestParam(defaultValue = "30") int maxResults) {
		String searchUrl = String.format("%s?part=snippet&q=%s&type=video&key=%s&maxResults=%d", baseUrl, query, apiKey,
				maxResults);

		try {
			// Fetch search results
			YoutubeResponse searchResponse = restTemplate.getForObject(searchUrl, YoutubeResponse.class);
			List<String> videoIds = searchResponse.getItems().stream().map(item -> item.getId().getVideoId())
					.collect(Collectors.toList());

			Map<String, Snippet> snippetMap = searchResponse.getItems().stream()
					.collect(Collectors.toMap(item -> item.getId().getVideoId(), Item::getSnippet));

			// Fetch video details including view counts
			String videoDetailsUrl = String.format("%s?part=statistics&id=%s&key=%s", videosUrl,
					String.join(",", videoIds), apiKey);
			VideoResponse videoDetailsResponse = restTemplate.getForObject(videoDetailsUrl, VideoResponse.class);

			videoDetailsResponse.getItems()
					.forEach(videoItem -> videoItem.setSnippet(snippetMap.get(videoItem.getId())));

			return ResponseEntity.ok(videoDetailsResponse); // Return detailed items with view counts
		} catch (RestClientException e) {
			return ResponseEntity.status(500).body("Failed to fetch data from YouTube API");
		}
	}

}
