package com.campus.headlines.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@TableName("news")
public class News {

    @TableId(type = IdType.AUTO)
    private Long id;
    private Long wmUserId;
    private Integer channelId;
    private String title;
    private String content;
    private Integer coverType;
    private String coverImages;
    private String labels;
    private Integer status;
    private Integer isTop;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime publishTime;
    private Integer views;
    private Integer likes;
    private Integer comments;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createTime;
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updateTime;

    @TableField(exist = false)
    private String channelName;
    @TableField(exist = false)
    private String authorName;
    @TableField(exist = false)
    private String authorAvatar;
    @TableField(exist = false)
    private List<String> coverList;
    @TableField(exist = false)
    private Boolean liked;
}
