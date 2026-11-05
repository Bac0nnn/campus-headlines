package com.campus.headlines.controller;

import com.campus.headlines.common.PageResult;
import com.campus.headlines.common.Result;
import com.campus.headlines.dto.AuditReviewRequest;
import com.campus.headlines.entity.News;
import com.campus.headlines.service.AuditService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.validation.Valid;

@RestController
@RequestMapping("/api/media/audit")
@RequiredArgsConstructor
public class MediaAuditController {

    private final AuditService auditService;

    @GetMapping("/news")
    public Result<PageResult<News>> news(
            @RequestParam(required = false) Integer status,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return Result.ok(auditService.page(status, keyword, page, size));
    }

    @GetMapping("/news/{id}")
    public Result<News> detail(@PathVariable Long id) {
        return Result.ok(auditService.detail(id));
    }

    @PostMapping("/news/{id}/review")
    public Result<News> review(@PathVariable Long id, @Valid @RequestBody AuditReviewRequest request) {
        return Result.ok(auditService.review(id, request));
    }
}
