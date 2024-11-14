package com.byalif.scraper;

import java.time.Duration;

import javax.sql.DataSource;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
@EnableScheduling
public class ScraperApplication {
	
	@Bean
	public RestTemplate restTemplate(RestTemplateBuilder builder) {
		return builder
                .setConnectTimeout(Duration.ofMinutes(15))  // Set connection timeout
                .setReadTimeout(Duration.ofMinutes(15))    // Set read timeout
                .build();
	}
	
	@Bean
	public JdbcTemplate jdbcTemplate(DataSource dataSource) {
	    return new JdbcTemplate(dataSource);
	}

	public static void main(String[] args) {
		SpringApplication.run(ScraperApplication.class, args);
	}

}
