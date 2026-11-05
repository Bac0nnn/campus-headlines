package com.campus.headlines.task;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.campus.headlines.entity.News;
import com.campus.headlines.mapper.NewsMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;

@Slf4j
@Component
@RequiredArgsConstructor
public class DemoAuditTask {

    private final NewsMapper newsMapper;

    @Value("${campus.demo.auto-audit:true}")
    private boolean enabled;

    /** 只处理本次启动之后新提交的文章，避免种子数据里的待审核文章被自动放行 */
    private final LocalDateTime bootTime = LocalDateTime.now().withNano(0);

    @Scheduled(initialDelay = 15000, fixedDelay = 30000)
    public void autoAudit() {
        if (!enabled) {
            return;
        }
        LocalDateTime threshold = LocalDateTime.now().minusSeconds(30);
        List<News> pending = newsMapper.selectList(new LambdaQueryWrapper<News>()
                .eq(News::getStatus, 1)
                .ge(News::getCreateTime, bootTime)
                .le(News::getUpdateTime, threshold));
        for (News news : pending) {
            news.setStatus(2);
            news.setPublishTime(LocalDateTime.now());
            newsMapper.updateById(news);
            log.info("演示自动审核通过：{} - {}", news.getId(), news.getTitle());
        }
    }
}
