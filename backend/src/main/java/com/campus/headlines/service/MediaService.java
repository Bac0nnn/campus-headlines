package com.campus.headlines.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.headlines.common.BusinessException;
import com.campus.headlines.common.PageResult;
import com.campus.headlines.dto.NewsQuery;
import com.campus.headlines.dto.NewsSaveRequest;
import com.campus.headlines.entity.Material;
import com.campus.headlines.entity.News;
import com.campus.headlines.entity.WmUser;
import com.campus.headlines.mapper.MaterialMapper;
import com.campus.headlines.mapper.NewsMapper;
import com.campus.headlines.mapper.WmUserMapper;
import com.campus.headlines.utils.UserContext;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;
import java.util.List;

/**
 * 作者端：素材与文章管理。图片二进制直接写入 material.data。
 */
@Service
@RequiredArgsConstructor
public class MediaService {

    private final WmUserMapper wmUserMapper;
    private final MaterialMapper materialMapper;
    private final NewsMapper newsMapper;
    private final NewsAssembler newsAssembler;

    /** 只有作者（wm_user.role = 0）可以管理素材和文章 */
    private WmUser requireAuthor() {
        Long wmId = UserContext.wmUserId();
        WmUser wm = wmId == null ? null : wmUserMapper.selectById(wmId);
        if (wm == null || wm.getRole() == null || wm.getRole() != 0) {
            throw new BusinessException(403, "只有作者账号可以发布和管理文章");
        }
        return wm;
    }

    public PageResult<Material> pageMaterials(int page, int size, Boolean collected) {
        WmUser author = requireAuthor();
        Page<Material> p = new Page<>(page, size);
        LambdaQueryWrapper<Material> wrapper = new LambdaQueryWrapper<Material>()
                .eq(Material::getWmUserId, author.getId())
                .orderByDesc(Material::getCreateTime);
        if (Boolean.TRUE.equals(collected)) {
            wrapper.eq(Material::getIsCollected, 1);
        }
        materialMapper.selectPage(p, wrapper);
        return new PageResult<>(p.getRecords(), p.getTotal(), page, size);
    }

    /**
     * 素材上传：图片二进制保存到数据库，url 指向数据库读取接口。
     */
    public Material upload(MultipartFile file) {
        WmUser author = requireAuthor();
        if (file == null || file.isEmpty()) {
            throw new BusinessException("请选择要上传的图片");
        }
        if (file.getSize() > 10 * 1024 * 1024) {
            throw new BusinessException("图片不能超过 10MB");
        }
        String contentType = file.getContentType();
        if (contentType == null || !contentType.startsWith("image/")) {
            throw new BusinessException("仅支持 jpg、png、webp、gif 格式的图片");
        }
        try {
            byte[] bytes = file.getBytes();
            Integer width = null;
            Integer height = null;
            BufferedImage image = ImageIO.read(new ByteArrayInputStream(bytes));
            if (image != null) {
                width = image.getWidth();
                height = image.getHeight();
            }
            Material material = new Material();
            material.setWmUserId(author.getId());
            material.setType(0);
            material.setSize((long) bytes.length);
            material.setWidth(width);
            material.setHeight(height);
            material.setContentType(contentType);
            material.setOriginalName(file.getOriginalFilename());
            material.setData(bytes);
            material.setIsCollected(0);
            material.setUrl("/api/files/material/pending");
            materialMapper.insert(material);

            material.setUrl("/api/files/material/" + material.getId());
            materialMapper.updateById(material);
            return material;
        } catch (BusinessException e) {
            throw e;
        } catch (Exception e) {
            throw new BusinessException("图片上传失败，请重试");
        }
    }

    public Material toggleCollect(Long id) {
        Material material = requireOwnMaterial(id);
        material.setIsCollected(material.getIsCollected() != null && material.getIsCollected() == 1 ? 0 : 1);
        materialMapper.updateById(material);
        return material;
    }

    public void deleteMaterial(Long id) {
        requireOwnMaterial(id);
        materialMapper.deleteById(id);
    }

    private Material requireOwnMaterial(Long id) {
        WmUser author = requireAuthor();
        Material material = materialMapper.selectById(id);
        if (material == null || !material.getWmUserId().equals(author.getId())) {
            throw new BusinessException("素材不存在");
        }
        return material;
    }

    @Transactional
    public News saveNews(NewsSaveRequest request) {
        WmUser author = requireAuthor();
        News news;
        if (request.getId() == null) {
            news = new News();
            news.setWmUserId(author.getId());
            news.setViews(0);
            news.setLikes(0);
            news.setComments(0);
            news.setIsTop(0);
        } else {
            news = newsMapper.selectById(request.getId());
            if (news == null || !news.getWmUserId().equals(author.getId())) {
                throw new BusinessException("文章不存在");
            }
            if (news.getStatus() != null && news.getStatus() == 2) {
                throw new BusinessException("已发布的文章不能直接修改");
            }
        }

        String title = request.getTitle() == null ? "" : request.getTitle().trim();
        if (title.isEmpty()) {
            throw new BusinessException("请输入标题");
        }
        if (title.length() > 30) {
            throw new BusinessException("标题不能超过 30 个字");
        }
        if (!StringUtils.hasText(request.getContent())) {
            throw new BusinessException("请输入正文");
        }

        int coverType = request.getCoverType() == null ? 0 : request.getCoverType();
        List<String> covers = request.getCoverImages() == null ? List.of() : request.getCoverImages();
        if (coverType == 1 && covers.size() != 1) {
            throw new BusinessException("单图封面需要选择 1 张图片");
        }
        if (coverType == 3 && covers.size() != 3) {
            throw new BusinessException("三图封面需要选择 3 张图片");
        }
        if (coverType == 0) {
            covers = List.of();
        }

        news.setChannelId(request.getChannelId());
        news.setTitle(title);
        news.setContent(request.getContent());
        news.setCoverType(coverType);
        news.setCoverImages(covers.isEmpty() ? null : String.join(",", covers));
        news.setLabels(request.getLabels() == null || request.getLabels().isEmpty()
                ? null : String.join(",", request.getLabels()));
        boolean submit = Boolean.TRUE.equals(request.getSubmit());
        news.setStatus(submit ? 1 : 0);

        if (news.getId() == null) {
            newsMapper.insert(news);
        } else {
            newsMapper.updateById(news);
        }
        return news;
    }

    public News submitNews(Long id) {
        requireAuthor();
        News news = requireOwnNews(id);
        if (news.getStatus() != null && news.getStatus() == 2) {
            throw new BusinessException("文章已发布，无需重复提交");
        }
        news.setStatus(1);
        newsMapper.updateById(news);
        return news;
    }

    public PageResult<News> pageNews(Integer status, String keyword, Integer channelId,
                                     String startDate, String endDate, int page, int size) {
        WmUser author = requireAuthor();
        NewsQuery query = new NewsQuery();
        query.setWmUserId(author.getId());
        query.setStatus(status);
        query.setKeyword(StringUtils.hasText(keyword) ? keyword.trim() : null);
        query.setChannelId(channelId);
        query.setStartDate(parseDate(startDate, true));
        query.setEndDate(parseDate(endDate, false));

        Page<News> p = new Page<>(page, size);
        newsMapper.selectMediaNews(p, query);
        newsAssembler.enrich(p.getRecords());
        return new PageResult<>(p.getRecords(), p.getTotal(), page, size);
    }

    public News getNews(Long id) {
        requireAuthor();
        News news = requireOwnNews(id);
        newsAssembler.enrich(news);
        return news;
    }

    public void deleteNews(Long id) {
        requireAuthor();
        requireOwnNews(id);
        newsMapper.deleteById(id);
    }

    private News requireOwnNews(Long id) {
        Long wmId = UserContext.wmUserId();
        News news = newsMapper.selectById(id);
        if (news == null || !news.getWmUserId().equals(wmId)) {
            throw new BusinessException("文章不存在");
        }
        return news;
    }

    private LocalDateTime parseDate(String value, boolean startOfDay) {
        if (!StringUtils.hasText(value)) {
            return null;
        }
        try {
            LocalDate date = LocalDate.parse(value.trim());
            return startOfDay ? date.atStartOfDay() : date.atTime(23, 59, 59);
        } catch (DateTimeParseException e) {
            throw new BusinessException("日期格式不正确，应为 yyyy-MM-dd");
        }
    }
}
