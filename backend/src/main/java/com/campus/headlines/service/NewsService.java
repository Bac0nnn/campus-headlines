package com.campus.headlines.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.headlines.common.BusinessException;
import com.campus.headlines.common.PageResult;
import com.campus.headlines.entity.ApUser;
import com.campus.headlines.entity.News;
import com.campus.headlines.entity.NewsComment;
import com.campus.headlines.entity.NewsLike;
import com.campus.headlines.mapper.ApUserMapper;
import com.campus.headlines.mapper.NewsCommentMapper;
import com.campus.headlines.mapper.NewsLikeMapper;
import com.campus.headlines.mapper.NewsMapper;
import com.campus.headlines.utils.UserContext;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class NewsService {

    private final NewsMapper newsMapper;
    private final NewsLikeMapper newsLikeMapper;
    private final NewsCommentMapper newsCommentMapper;
    private final ApUserMapper apUserMapper;
    private final NewsAssembler newsAssembler;

    public PageResult<News> page(Integer channelId, String keyword, int page, int size) {
        Page<News> p = new Page<>(page, size);
        LambdaQueryWrapper<News> wrapper = new LambdaQueryWrapper<News>()
                .eq(News::getStatus, 2);
        if (channelId != null) {
            wrapper.eq(News::getChannelId, channelId);
        }
        if (keyword != null && !keyword.trim().isEmpty()) {
            wrapper.like(News::getTitle, keyword.trim());
        }
        wrapper.orderByDesc(News::getIsTop).orderByDesc(News::getPublishTime);
        newsMapper.selectPage(p, wrapper);
        newsAssembler.enrich(p.getRecords());
        return new PageResult<>(p.getRecords(), p.getTotal(), page, size);
    }

    public News detail(Long id) {
        News news = newsMapper.selectById(id);
        if (news == null || news.getStatus() == null || news.getStatus() != 2) {
            throw new BusinessException(404, "文章不存在或已下架");
        }
        newsMapper.update(null, new LambdaUpdateWrapper<News>()
                .eq(News::getId, id).setSql("views = views + 1"));
        news.setViews(news.getViews() + 1);
        newsAssembler.enrich(news);
        Long userId = UserContext.userId();
        if (userId != null && "USER".equals(UserContext.role())) {
            Long count = newsLikeMapper.selectCount(new LambdaQueryWrapper<NewsLike>()
                    .eq(NewsLike::getNewsId, id).eq(NewsLike::getUserId, userId));
            news.setLiked(count != null && count > 0);
        } else {
            news.setLiked(false);
        }
        return news;
    }

    @Transactional
    public Map<String, Object> toggleLike(Long id) {
        Long userId = UserContext.requireUser().id();
        News news = newsMapper.selectById(id);
        if (news == null || news.getStatus() == null || news.getStatus() != 2) {
            throw new BusinessException("文章不存在或已下架");
        }
        NewsLike exists = newsLikeMapper.selectOne(new LambdaQueryWrapper<NewsLike>()
                .eq(NewsLike::getNewsId, id).eq(NewsLike::getUserId, userId));
        boolean liked;
        if (exists != null) {
            newsLikeMapper.deleteById(exists.getId());
            newsMapper.update(null, new LambdaUpdateWrapper<News>()
                    .eq(News::getId, id).setSql("likes = GREATEST(likes - 1, 0)"));
            liked = false;
        } else {
            NewsLike like = new NewsLike();
            like.setNewsId(id);
            like.setUserId(userId);
            newsLikeMapper.insert(like);
            newsMapper.update(null, new LambdaUpdateWrapper<News>()
                    .eq(News::getId, id).setSql("likes = likes + 1"));
            liked = true;
        }
        News fresh = newsMapper.selectById(id);
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("liked", liked);
        result.put("likes", fresh.getLikes());
        return result;
    }

    public List<NewsComment> comments(Long id) {
        Page<NewsComment> p = new Page<>(1, 100);
        newsCommentMapper.selectPage(p, new LambdaQueryWrapper<NewsComment>()
                .eq(NewsComment::getNewsId, id)
                .eq(NewsComment::getStatus, 1)
                .orderByDesc(NewsComment::getCreateTime));
        List<NewsComment> records = p.getRecords();
        fillUser(records);
        return records;
    }

    @Transactional
    public NewsComment addComment(Long id, String content) {
        Long userId = UserContext.requireUser().id();
        News news = newsMapper.selectById(id);
        if (news == null || news.getStatus() == null || news.getStatus() != 2) {
            throw new BusinessException("文章不存在或已下架");
        }
        NewsComment comment = new NewsComment();
        comment.setNewsId(id);
        comment.setUserId(userId);
        comment.setContent(content.trim());
        comment.setStatus(1);
        newsCommentMapper.insert(comment);
        newsMapper.update(null, new LambdaUpdateWrapper<News>()
                .eq(News::getId, id).setSql("comments = comments + 1"));
        fillUser(List.of(comment));
        return comment;
    }

    private void fillUser(List<NewsComment> comments) {
        if (comments.isEmpty()) {
            return;
        }
        Set<Long> userIds = comments.stream().map(NewsComment::getUserId).collect(Collectors.toSet());
        Map<Long, ApUser> users = apUserMapper.selectBatchIds(userIds).stream()
                .collect(Collectors.toMap(ApUser::getId, Function.identity()));
        for (NewsComment comment : comments) {
            ApUser user = users.get(comment.getUserId());
            if (user != null) {
                comment.setNickname(user.getNickname());
                comment.setAvatar(user.getAvatar());
            }
        }
    }
}
