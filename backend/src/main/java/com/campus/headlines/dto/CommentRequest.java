package com.campus.headlines.dto;

import lombok.Data;

import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Size;

@Data
public class CommentRequest {

    @NotBlank(message = "评论内容不能为空")
    @Size(max = 500, message = "评论不能超过 500 个字")
    private String content;
}
