package com.campus.headlines.controller;

import com.campus.headlines.common.PageResult;
import com.campus.headlines.common.Result;
import com.campus.headlines.dto.NewsSaveRequest;
import com.campus.headlines.entity.Material;
import com.campus.headlines.entity.News;
import com.campus.headlines.service.MediaService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import javax.validation.Valid;

@RestController
@RequestMapping("/api/media")
@RequiredArgsConstructor
public class MediaController {

    private final MediaService mediaService;

    @GetMapping("/materials")
    public Result<PageResult<Material>> materials(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) Boolean collected) {
        return Result.ok(mediaService.pageMaterials(page, size, collected));
    }

    @PostMapping("/materials")
    public Result<Material> upload(@RequestParam("file") MultipartFile file) {
        return Result.ok(mediaService.upload(file));
    }

    @PutMapping("/materials/{id}/collect")
    public Result<Material> collect(@PathVariable Long id) {
        return Result.ok(mediaService.toggleCollect(id));
    }

    @DeleteMapping("/materials/{id}")
    public Result<Void> deleteMaterial(@PathVariable Long id) {
        mediaService.deleteMaterial(id);
        return Result.ok();
    }

    @PostMapping("/news")
    public Result<News> create(@Valid @RequestBody NewsSaveRequest request) {
        return Result.ok(mediaService.saveNews(request));
    }

    @PutMapping("/news/{id}")
    public Result<News> update(@PathVariable Long id, @Valid @RequestBody NewsSaveRequest request) {
        request.setId(id);
        return Result.ok(mediaService.saveNews(request));
    }

    @PostMapping("/news/{id}/submit")
    public Result<News> submit(@PathVariable Long id) {
        return Result.ok(mediaService.submitNews(id));
    }

    @GetMapping("/news")
    public Result<PageResult<News>> news(
            @RequestParam(required = false) Integer status,
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) Integer channelId,
            @RequestParam(required = false) String startDate,
            @RequestParam(required = false) String endDate,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int size) {
        return Result.ok(mediaService.pageNews(status, keyword, channelId, startDate, endDate, page, size));
    }

    @GetMapping("/news/{id}")
    public Result<News> newsDetail(@PathVariable Long id) {
        return Result.ok(mediaService.getNews(id));
    }

    @DeleteMapping("/news/{id}")
    public Result<Void> deleteNews(@PathVariable Long id) {
        mediaService.deleteNews(id);
        return Result.ok();
    }
}
