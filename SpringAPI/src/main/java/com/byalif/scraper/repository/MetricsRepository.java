package com.byalif.scraper.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.byalif.scraper.entity.Metrics;

@Repository
public interface MetricsRepository extends JpaRepository<Metrics, Long> {
}
