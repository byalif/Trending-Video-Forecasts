package com.byalif.scraper.controller;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.Arrays;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ForecastController {

    @Autowired
    JdbcTemplate jdbcTemplate;

    @GetMapping("/latest-forecasts")
    public List<Map<String, Object>> getLatestForecasts() {
        // Step 1: Fetch the 30 most recent forecasts
        String query = "SELECT forecast_id, artist_type, current_views, projected_growth, growth_rate, " +
                "growth_speed, top_potential_rank, growth_rate_rank, fastest_risers_rank, forecast_values, timestamp " +
                "FROM artist_forecasts ORDER BY timestamp DESC LIMIT 30";

        List<Map<String, Object>> forecasts = jdbcTemplate.query(query, new RowMapper<Map<String, Object>>() {
            @Override
            public Map<String, Object> mapRow(ResultSet rs, int rowNum) throws SQLException {
                // Use a mutable HashMap instead of an immutable map
                Map<String, Object> result = new HashMap<>();

                // Map the forecast metadata
                result.put("forecast_id", rs.getInt("forecast_id"));
                result.put("artist_type", rs.getString("artist_type"));
                result.put("current_views", rs.getDouble("current_views"));
                result.put("projected_growth", rs.getDouble("projected_growth"));
                result.put("growth_rate", rs.getDouble("growth_rate"));
                result.put("growth_speed", rs.getDouble("growth_speed"));
                result.put("top_potential_rank", rs.getInt("top_potential_rank"));
                result.put("growth_rate_rank", rs.getInt("growth_rate_rank"));
                result.put("fastest_risers_rank", rs.getInt("fastest_risers_rank"));
                result.put("timestamp", rs.getTimestamp("timestamp").toString()); // Convert timestamp to string

                // Step 3: Parse forecast values from comma-separated string to List<Double>
                String forecastValuesStr = rs.getString("forecast_values");
                List<Double> forecastValues = Arrays.stream(forecastValuesStr.split(","))
                        .map(Double::parseDouble)
                        .collect(Collectors.toList());
                result.put("forecast_values", forecastValues);

                return result;
            }
        });

        return forecasts;
    }
}
