package com.campus.headlines.service;

import com.campus.headlines.entity.Channel;
import com.campus.headlines.entity.News;
import com.campus.headlines.entity.WmUser;
import com.campus.headlines.mapper.ChannelMapper;
import com.campus.headlines.mapper.WmUserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

@Component
@RequiredArgsConstructor
public class NewsAssembler {

    private final ChannelMapper channelMapper;
    private final WmUserMapper wmUserMapper;

    public void enrich(List<News> list) {
        if (list == null || list.isEmpty()) {
            return;
        }
        Set<Integer> channelIds = list.stream().map(News::getChannelId)
                .filter(java.util.Objects::nonNull).collect(Collectors.toSet());
        Map<Integer, Channel> channelMap = channelIds.isEmpty() ? Collections.emptyMap()
                : channelMapper.selectBatchIds(channelIds).stream()
                .collect(Collectors.toMap(Channel::getId, Function.identity()));

        Set<Long> userIds = list.stream().map(News::getWmUserId)
                .filter(java.util.Objects::nonNull).collect(Collectors.toSet());
        Map<Long, WmUser> userMap = userIds.isEmpty() ? Collections.emptyMap()
                : wmUserMapper.selectBatchIds(userIds).stream()
                .collect(Collectors.toMap(WmUser::getId, Function.identity()));

        for (News news : list) {
            Channel channel = channelMap.get(news.getChannelId());
            if (channel != null) {
                news.setChannelName(channel.getName());
            }
            WmUser user = userMap.get(news.getWmUserId());
            if (user != null) {
                news.setAuthorName(user.getName());
                news.setAuthorAvatar(user.getAvatar());
            }
            news.setCoverList(split(news.getCoverImages()));
        }
    }

    public void enrich(News news) {
        enrich(List.of(news));
    }

    public static List<String> split(String value) {
        if (!StringUtils.hasText(value)) {
            return List.of();
        }
        return Arrays.stream(value.split(","))
                .map(String::trim)
                .filter(StringUtils::hasText)
                .collect(Collectors.toList());
    }
}
