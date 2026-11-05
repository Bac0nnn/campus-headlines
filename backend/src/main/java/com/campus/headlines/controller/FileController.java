package com.campus.headlines.controller;

import com.campus.headlines.common.BusinessException;
import com.campus.headlines.entity.Material;
import com.campus.headlines.mapper.MaterialMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.http.CacheControl;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.concurrent.TimeUnit;

/**
 * 公开图片读取：新闻封面、素材图片直接从 material.data 读取。
 */
@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileController {

    private final MaterialMapper materialMapper;

    @GetMapping("/material/{id}")
    public ResponseEntity<byte[]> material(@PathVariable Long id) {
        Material material = materialMapper.selectById(id);
        if (material == null || material.getData() == null || material.getData().length == 0) {
            throw new BusinessException(404, "图片不存在");
        }
        String contentType = material.getContentType() == null ? "image/jpeg" : material.getContentType();
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(contentType))
                .cacheControl(CacheControl.maxAge(7, TimeUnit.DAYS).cachePublic())
                .body(material.getData());
    }
}
