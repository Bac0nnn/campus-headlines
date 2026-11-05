package com.campus.headlines.controller;

import com.campus.headlines.common.PageResult;
import com.campus.headlines.common.Result;
import com.campus.headlines.dto.CommentRequest;
import com.campus.headlines.entity.News;
import com.campus.headlines.entity.NewsComment;
import com.campus.headlines.service.NewsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.validation.Valid;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/news")
@RequiredArgsConstructor
public class NewsController {

    private final NewsService newsService;

    @GetMapping
    public Result<PageResult<News>> page(
            @RequestParam(required = false) Integer channelId,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return Result.ok(newsService.page(channelId, keyword, page, size));
    }

    @GetMapping("/{id}")
    public Result<News> detail(@PathVariable Long id) {
        return Result.ok(newsService.detail(id));
    }

    @PostMapping("/{id}/like")
    public Result<Map<String, Object>> like(@PathVariable Long id) {
        return Result.ok(newsService.toggleLike(id));
    }

    @GetMapping("/{id}/comments")
    public Result<List<NewsComment>> comments(@PathVariable Long id) {
        return Result.ok(newsService.comments(id));
    }

    @PostMapping("/{id}/comments")
    public Result<NewsComment> addComment(@PathVariable Long id, @Valid @RequestBody CommentRequest request) {
        return Result.ok(newsService.addComment(id, request.getContent()));
    }
}
