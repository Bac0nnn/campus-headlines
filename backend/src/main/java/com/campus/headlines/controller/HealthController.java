package com.campus.headlines.controller;

import com.campus.headlines.common.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class HealthController {

    private final JdbcTemplate jdbcTemplate;

    @GetMapping("/health")
    public Result<Map<String, Object>> health() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("status", "UP");
        try {
            Integer one = jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            data.put("database", one != null && one == 1 ? "UP" : "DOWN");
        } catch (Exception e) {
            data.put("database", "DOWN");
        }
        data.put("time", LocalDateTime.now().toString());
        return Result.ok(data);
    }
}
