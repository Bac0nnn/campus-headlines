package com.campus.headlines.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.campus.headlines.entity.Channel;
import com.campus.headlines.mapper.ChannelMapper;
import com.campus.headlines.mapper.NewsMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ChannelService {

    private final ChannelMapper channelMapper;
    private final NewsMapper newsMapper;

    public List<Channel> list() {
        return channelMapper.selectList(new LambdaQueryWrapper<Channel>()
                .eq(Channel::getStatus, 1)
                .orderByAsc(Channel::getSort));
    }

    /**
     * 频道统计：调用 NewsMapper.xml 中带 foreach 的动态 SQL。
     */
    public List<Map<String, Object>> stats() {
        List<Channel> channels = list();
        if (channels.isEmpty()) {
            return List.of();
        }
        List<Integer> ids = channels.stream().map(Channel::getId).collect(Collectors.toList());
        Map<Integer, Long> counts = newsMapper.countByChannelIds(ids).stream()
                .collect(Collectors.toMap(
                        row -> toInt(row.get("channelId") != null ? row.get("channelId") : row.get("channel_id")),
                        row -> toLong(row.get("total") != null ? row.get("total") : row.get("TOTAL")),
                        (a, b) -> a));
        return channels.stream().map(channel -> {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("id", channel.getId());
            item.put("name", channel.getName());
            item.put("total", counts.getOrDefault(channel.getId(), 0L));
            return item;
        }).collect(Collectors.toList());
    }

    private Integer toInt(Object value) {
        return value == null ? 0 : ((Number) value).intValue();
    }

    private Long toLong(Object value) {
        return value == null ? 0L : ((Number) value).longValue();
    }
}
