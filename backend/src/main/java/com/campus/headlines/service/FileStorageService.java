package com.campus.headlines.service;

import com.campus.headlines.common.BusinessException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * 本地文件存储服务：素材上传与用户头像上传共用。
 */
@Slf4j
@Service
public class FileStorageService {

    private static final List<String> ALLOWED_EXT = List.of("jpg", "jpeg", "png", "webp", "gif");

    @Value("${campus.upload.dir:./data/uploads}")
    private String uploadDir;

    public StoredFile store(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new BusinessException("请选择要上传的图片");
        }
        if (file.getSize() > 10 * 1024 * 1024) {
            throw new BusinessException("图片不能超过 10MB");
        }
        String original = file.getOriginalFilename();
        String ext = "";
        if (original != null && original.contains(".")) {
            ext = original.substring(original.lastIndexOf('.') + 1).toLowerCase(Locale.ROOT);
        }
        if (!ALLOWED_EXT.contains(ext)) {
            throw new BusinessException("仅支持 jpg、png、webp、gif 格式的图片");
        }
        String datePath = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM"));
        Path dir = Paths.get(uploadDir, datePath).toAbsolutePath().normalize();
        String filename = UUID.randomUUID().toString().replace("-", "") + "." + ext;
        try {
            Files.createDirectories(dir);
            Path target = dir.resolve(filename);
            try (InputStream in = file.getInputStream()) {
                Files.copy(in, target);
            }
            Integer width = null;
            Integer height = null;
            try (InputStream in = Files.newInputStream(target)) {
                BufferedImage image = ImageIO.read(in);
                if (image != null) {
                    width = image.getWidth();
                    height = image.getHeight();
                }
            } catch (Exception ignored) {
                log.warn("读取图片尺寸失败: {}", filename);
            }
            return new StoredFile("/uploads/" + datePath + "/" + filename, file.getSize(), width, height);
        } catch (Exception e) {
            log.error("图片上传失败", e);
            throw new BusinessException("图片上传失败，请重试");
        }
    }

    public record StoredFile(String url, long size, Integer width, Integer height) {
    }
}
