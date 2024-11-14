package com.byalif.scraper.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.byalif.scraper.entity.Video;

@Repository
public interface VideoRepository extends JpaRepository<Video, String> {
}
