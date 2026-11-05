package com.campus.headlines.controller;

import com.campus.headlines.common.Result;
import com.campus.headlines.entity.Channel;
import com.campus.headlines.service.ChannelService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/channels")
@RequiredArgsConstructor
public class ChannelController {

    private final ChannelService channelService;

    @GetMapping
    public Result<List<Channel>> list() {
        return Result.ok(channelService.list());
    }

    @GetMapping("/stats")
    public Result<List<Map<String, Object>>> stats() {
        return Result.ok(channelService.stats());
    }
}
