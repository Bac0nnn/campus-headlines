package com.campus.headlines.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class NewsQuery {

    private Long wmUserId;
    private Integer status;
    private String keyword;
    private Integer channelId;
    private LocalDateTime startDate;
    private LocalDateTime endDate;
    /** latest / hot，对应 XML 中的 choose 分支 */
    private String sort = "latest";
}
