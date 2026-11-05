package com.campus.headlines.service;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.headlines.common.BusinessException;
import com.campus.headlines.common.PageResult;
import com.campus.headlines.dto.AuditReviewRequest;
import com.campus.headlines.dto.NewsQuery;
import com.campus.headlines.entity.AuditRecord;
import com.campus.headlines.entity.News;
import com.campus.headlines.entity.WmUser;
import com.campus.headlines.mapper.AuditRecordMapper;
import com.campus.headlines.mapper.NewsMapper;
import com.campus.headlines.mapper.WmUserMapper;
import com.campus.headlines.utils.UserContext;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.time.LocalDateTime;

/**
 * 人工审核：审核员查看待审稿件，通过或驳回，并写入审核记录。
 */
@Service
@RequiredArgsConstructor
public class AuditService {

    private final WmUserMapper wmUserMapper;
    private final NewsMapper newsMapper;
    private final AuditRecordMapper auditRecordMapper;
    private final NewsAssembler newsAssembler;

    public PageResult<News> page(Integer status, String keyword, int page, int size) {
        requireReviewer();
        NewsQuery query = new NewsQuery();
        query.setStatus(status == null ? 1 : status);
        query.setKeyword(StringUtils.hasText(keyword) ? keyword.trim() : null);
        Page<News> p = new Page<>(page, size);
        newsMapper.selectMediaNews(p, query);
        newsAssembler.enrich(p.getRecords());
        return new PageResult<>(p.getRecords(), p.getTotal(), page, size);
    }

    public News detail(Long id) {
        requireReviewer();
        News news = newsMapper.selectById(id);
        if (news == null) {
            throw new BusinessException("文章不存在");
        }
        newsAssembler.enrich(news);
        return news;
    }

    /**
     * 审核操作：声明式事务同时更新文章状态并写入审核记录。
     */
    @Transactional
    public News review(Long id, AuditReviewRequest request) {
        WmUser reviewer = requireReviewer();
        News news = newsMapper.selectById(id);
        if (news == null) {
            throw new BusinessException("文章不存在");
        }
        if (news.getStatus() == null || news.getStatus() != 1) {
            throw new BusinessException("该文章不在待审核状态");
        }
        boolean pass = Boolean.TRUE.equals(request.getPass());
        if (!pass && !StringUtils.hasText(request.getReason())) {
            throw new BusinessException("驳回时请填写审核意见");
        }
        news.setStatus(pass ? 2 : 3);
        if (pass) {
            news.setPublishTime(LocalDateTime.now());
        }
        newsMapper.updateById(news);

        AuditRecord record = new AuditRecord();
        record.setNewsId(id);
        record.setAuditorId(reviewer.getId());
        record.setResult(pass ? 1 : 2);
        record.setReason(request.getReason());
        auditRecordMapper.insert(record);

        newsAssembler.enrich(news);
        return news;
    }

    private WmUser requireReviewer() {
        WmUser user = wmUserMapper.selectById(UserContext.wmUserId());
        if (user == null || user.getRole() == null || user.getRole() != 1) {
            throw new BusinessException(403, "只有审核员可以进入审核工作台");
        }
        return user;
    }
}
